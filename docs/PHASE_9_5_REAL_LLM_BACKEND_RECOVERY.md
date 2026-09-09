# Phase 9.5 — Real LLM Backend Recovery (RTX 3050 Ti / CUDA)

> **Environment Compatibility Audit, Root Cause Isolation, Binary Remediation, and Empirical Inference Validation**  
> *Executed: September 2026*  
> *Target Hardware: NVIDIA GeForce RTX 3050 Ti Laptop GPU (4 GB VRAM) + AMD Ryzen 7 4800H (Zen 2)*

---

## 1. Executive Summary & Hard Scope Boundary

Prior to launching the planned **Ablation Test v1**, execution was explicitly halted because the local `llama-cpp-python` backend crashed during context initialization with:
```text
WinError 0xc000001d (STATUS_ILLEGAL_INSTRUCTION)
```
In adherence to the **Hard Scope Boundary**:
- Ablation Test v1 was **NOT** executed;
- `ControlledLLMBackend` was **NOT** used as an artificial substitute;
- Lucia's cognitive pipeline and Phase 9 production code were **NOT** altered;
- Zero cloud API substitutions or synthetic responses were introduced;
- Real local inference was verified from first principles:
  $$\text{RTX 3050 Ti Laptop GPU} \longrightarrow \text{CUDA 12.1/12.6} \longrightarrow \text{llama.cpp} \longrightarrow \text{GGUF Model} \longrightarrow \text{Real Local Tokens}$$

---

## 2. Environment Ground Truth Audit

### Hardware Specifications
* **CPU**: AMD Ryzen 7 4800H with Radeon Graphics (8 Cores, 16 Threads, Zen 2 architecture, Renoir microarchitecture).
* **CPU ISA Capabilities**: SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, AVX, AVX2, FMA3, BMI1, BMI2, F16C.
  * **AVX-512 Support**: **NONE** (Hardware lacks EVEX instruction encoding).
* **GPU**: NVIDIA GeForce RTX 3050 Ti Laptop GPU (PCIe Bus 01:00.0, WDDM Driver Model).
* **VRAM**: 4096 MiB (4 GB physical GDDR6).
* **NVIDIA Driver**: Version 581.15 (Supports CUDA runtime up to 13.0).
* **CUDA Toolkit**: CUDA 12.6 installed at `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin` (`nvcc.exe` V12.6.20).

### Software Environment
* **Operating System**: Windows 11 Home 64-bit (`win_amd64`).
* **Python Runtime**: Python 3.12.10 (`tags/v3.12.10:0cc8128`, MSC v.1943 64-bit AMD64).
* **PyTorch Version**: `2.14.0+cpu` (CPU-only build, preserving zero GPU VRAM contention for background ODE loops).
* **Active GGUF Model**: `models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (730,895,168 bytes, architecture `lfm2`).

---

## 3. Root Cause Isolation & Failure Analysis

### The Failure Signature
Running `llama_init_from_model` on the pre-installed `llama-cpp-python 0.3.35` raised:
```text
OSError: [WinError -1073741795] Windows Error 0xc000001d
```
A Win32 Vectored Exception Handler (VEH) hooked the exact hardware exception:
* **Fault Address**: `0x7ff83e5a9829` inside `.venv\Lib\site-packages\llama_cpp\lib\ggml-cpu.dll`.
* **Faulting Instruction Bytes**:
  ```text
  0x62 0xf1 0x7c 0x48 0x10 0x05 0x0d 0x59 0x0c 0x00 ...
  ```
* **Disassembly Root Cause**:
  Byte `0x62` is the EVEX prefix byte introduced by Intel for the **AVX-512** instruction set (here `vmovups zmm0, ...`). The upstream GitHub Actions build script for `llama-cpp-python` wheels compiled `ggml-cpu.dll` with `/arch:AVX512` without CPU dispatch. Because the AMD Ryzen 7 4800H is a Zen 2 processor lacking AVX-512 support, the CPU threw `STATUS_ILLEGAL_INSTRUCTION` the moment `ggml_backend_cpu_init` was invoked.

### CUDA Backend Health
Notably, `llama_load_model_from_file` had already succeeded and offloaded layers to CUDA:
```text
load_tensors: offloaded 17/17 layers to GPU
load_tensors:   CPU_Mapped model buffer size =   105.00 MiB
load_tensors:        CUDA0 model buffer size =   694.76 MiB
```
The CUDA driver, kernels, and VRAM offload path on the RTX 3050 Ti were operational; the process aborted solely because `llama.cpp` unconditionally registers the CPU fallback backend during `llama_init_from_model`.

---

## 4. Remediation: Native AVX2 Compilation & Stack Synthesis

### Path Taken: Hybrid Ampere CUDA / AVX2 CPU Stack
1. **CUDA Stack Acquisition**:
   * Acquired `llama-cpp-python 0.3.20` prebuilt for NVIDIA Ampere (`sm_86` / RTX 3050 Ti) and CUDA 12.1+ from `dougeeai/llama-cpp-python-wheels`.
   * Verified `ggml-cuda.dll` successfully initialized the RTX 3050 Ti:
     ```text
     ggml_cuda_init: found 1 CUDA devices (Total VRAM: 4095 MiB):
       Device 0: NVIDIA GeForce RTX 3050 Ti Laptop GPU, compute capability 8.6, VMM: yes, VRAM: 4095 MiB
     ```
2. **Native AVX2 Compilation for CPU Backend**:
   * Identified exact `llama.cpp` submodule commit for `v0.3.20`: `f49e9178767d557a522618b16ce8694f9ddac628`.
   * Checked out commit `f49e917` and compiled `ggml-cpu.dll` locally using MSVC 18 + Ninja with explicit SIMD constraints:
     ```powershell
     cmake -B scratch\build_cpu_exact -S scratch\llama_cpp -G Ninja `
       -DCMAKE_BUILD_TYPE=Release `
       -DGGML_AVX512=OFF -DGGML_AVX512_VBMI=OFF -DGGML_AVX512_VNNI=OFF -DGGML_AVX512_BF16=OFF `
       -DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_AVX=ON `
       -DGGML_CUDA=OFF -DBUILD_SHARED_LIBS=ON -DLLAMA_CURL=OFF
     ninja -C scratch\build_cpu_exact ggml-cpu
     ```
   * Result: A native, zero-EVEX `ggml-cpu.dll` exporting the exact ABI required by `llama.dll` and `ggml-base.dll`.
3. **Synthesis**:
   * Replaced `.venv\Lib\site-packages\llama_cpp\lib\ggml-cpu.dll` with the compiled AVX2 binary.
   * Retained `llama.dll`, `ggml-cuda.dll`, and `ggml-base.dll` from the CUDA `sm_86` build.
   * All 5 libraries (`ggml-base.dll`, `ggml.dll`, `ggml-cpu.dll`, `ggml-cuda.dll`, `llama.dll`) load and link cleanly without symbol errors or CPU faults.

---

## 5. CUDA Offload & Empirical Inference Validation

### Standalone Inference Verification (`scratch/smoke_cuda_real.py`)
* **Execution**: Direct invocation of `llama_cpp.Llama` on `models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf`.
* **Offload Status**:
  * Offloaded layers: **17 / 17 layers (100% full model offload)**.
  * VRAM utilization:
    * `CUDA0 model buffer size`: **694.76 MiB**
    * `CUDA0 compute buffer size`: **139.01 MiB**
    * `CUDA_Host compute buffer size`: **11.01 MiB**
    * **Total VRAM Consumption**: $\approx \mathbf{845\text{ MiB}}$ out of $4096\text{ MiB}$ physical limit ($20.6\%$ capacity).
  * Hardware Acceleration: CUDA Graph execution verified (`CUDA graph warmup complete`, 578 graph nodes, 30 reused graphs).
* **Generation Metrics**:
  * Prompt Evaluation Speed: **$135.44$ to $139.43$ tokens/second**.
  * Token Generation Speed: **$119.84$ to $152.00$ tokens/second**.
  * Turn Latency: $0.40\text{s}$ for 48 tokens; $0.09\text{s}$ for 12 tokens.
* **Output Sample**:
  > *"a well-designed and carefully implemented reinforcement learning system. This approach allows the AI to learn and adapt in real-time, providing a more natural and engaging interaction. By incorporating a reward function that prioritizes user satisfaction and emotional connection..."*

---

## 6. Integration with Lucia Production Backend

### Production Test (`scratch/test_lucia_llmbackend_integration.py`)
Tested through Lucia's un-modified `LLMBackend` (`src/core/language/llm_backend.py`) conditioned with real `BehavioralConstraints`:
```python
backend = LLMBackend(LLMConfig(
    model_path="models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
    n_gpu_layers=17,
    n_ctx=512
))
assert backend.is_ready() == True

constraints = BehavioralConstraints(max_tokens=32, temperature=0.7, latency_ms=0, reasoning_depth=0)
result = backend.generate("The stars at night shine brightly because", constraints)
backend.shutdown()
assert backend.is_ready() == False
```
* **Result**: **PASS**. Output generated in $0.29\text{s}$.
* **Architecture Integrity**: Zero code changes required in `src/core/` or `src/api/`.

---

## 7. Regression & Safety Audit

| Test Suite | Scope | Result | Status |
|---|---|---|---|
| **Standalone CUDA Smoke Test** | `scratch/smoke_cuda_real.py` | 3 sequential prompts generated | **PASS** |
| **Lucia LLMBackend Integration** | `scratch/test_lucia_llmbackend_integration.py` | Full generation cycle + shutdown | **PASS** |
| **Python Regression Suite** | `pytest tests/ -q` | 511 passed, 7 skipped | **PASS** |
| **Electron Desktop Suite** | `cd electron && npm test` | 119 passed across 11 suites | **PASS** |
| **Simulation / Activation Isolation** | SHA-256 state & disk audit | 0 contamination of `data/` | **PASS** |

---

## 8. Reproducible Setup Instructions

If the Python virtual environment is ever recreated from scratch:
1. Install base requirements (`pip install -r requirements.txt`).
2. Download/install the CUDA `sm_86` wheel:
   ```powershell
   pip install --no-deps scratch\llama_cpp_python-0.3.20+cuda12.1.sm86.ampere-py3-none-win_amd64.whl
   ```
3. Replace the AVX-512 binary with the compiled AVX2 binary:
   ```powershell
   Copy-Item "scratch\build_cpu_exact\bin\ggml-cpu.dll" ".venv\Lib\site-packages\llama_cpp\lib\ggml-cpu.dll" -Force
   ```
4. Verify using:
   ```powershell
   .venv\Scripts\python -c "import llama_cpp; print('GPU offload:', llama_cpp.llama_supports_gpu_offload())"
   ```
   (Must output `GPU offload: True`).
