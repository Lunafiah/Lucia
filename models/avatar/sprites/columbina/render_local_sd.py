"""
Local Batch Sprite Renderer for Columbina (SD WebUI / Forge / ComfyUI)
Automatically sends 10 expression prompts with locked seed, retrieves images,
and runs rembg background removal to export transparent PNGs.
"""

import os
import json
import base64
import urllib.request
import urllib.parse
from PIL import Image
import io

try:
    from rembg import new_session, remove
    session = new_session('isnet-anime')
    REMBG_AVAILABLE = True
except Exception:
    REMBG_AVAILABLE = False

CONFIG = {
    "api_url": "http://127.0.0.1:7860/sdapi/v1/txt2img",
    "seed": 88889999,
    "steps": 28,
    "cfg_scale": 6.0,
    "width": 1024,
    "height": 1024,
    "lora_name": "columbina_2a_naiVpred-000039",
    "lora_weight": 0.8,
    "output_dir": os.path.dirname(os.path.abspath(__file__)),
}

BASE_PROMPT = (
    "masterpiece, best quality, highres, anime official art, 1girl, solo, columbina genshin impact, "
    "damselette, fatui harbinger, half body portrait, upper body, facing viewer, "
    "white background, simple white background, "
    "wing hair ornament, small white feather wings on head, "
    "white lace ruffled gothic dress, pale skin, "
    "dark black hair with smooth pink inner color streaks, clean gradient black to rose pink, "
    "NO fishnet texture, NO mesh pattern in hair, smooth hair coloring, solid hair color, "
    "wearing white ornate eye blindfold with lace trim, white decorative eye bandage, "
    "eyes completely covered by blindfold, no visible eyes, "
    f"<lora:{CONFIG['lora_name']}:{CONFIG['lora_weight']}>, "
    "cel shaded, crisp clean lines"
)

NEGATIVE_PROMPT = (
    "worst quality, low quality, normal quality, blurry, bad anatomy, bad hands, "
    "missing fingers, complex background, scenery, text, watermark, signature, "
    "open eyes, visible eyes, pupils, irises, "
    "fishnet, mesh texture in hair, striped hair, grid pattern hair, "
    "jagged edges, aliasing artifacts"
)

EXPRESSIONS = {
    # 3 already done via Gemini image gen (v2 sprites)
    "idle.png":     "neutral calm expressionless, closed mouth, serene peaceful, head straight",
    "speaking.png": "open mouth, parted lips, talking, gentle calm speech, slight open expression",
    "smile.png":    "gentle warm closed-mouth smile, sweet happy expression, subtle curves up at corners",
    # 7 remaining - to be generated via SD API
    "excited.png":  "wide bright open-mouth smile showing teeth, very happy joyful excited, cheerful big grin",
    "blush.png":    "heavy pink blush on cheeks, shy embarrassed flustered, cute slight closed-mouth smile",
    "relaxed.png":  "peaceful serene tranquil, soft gentle slight smile, resting calm, head slightly tilted back",
    "thinking.png": "one gloved hand raised near chin thoughtfully, puzzled curious, head slightly tilted, closed mouth",
    "concerned.png":"slightly open mouth, worried empathetic caring expression, lower lip slightly trembling",
    "sad.png":      "downcast face, subtle small frown, melancholy grief, closed mouth, slight droop at corners",
    "angry.png":    "cute pout, lower lip pushed out, furrowed brow visible above blindfold, stern determined annoyed",
}

def render_sprite(filename, keywords):
    full_prompt = f"{BASE_PROMPT}, {keywords}"
    payload = {
        "prompt": full_prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": CONFIG["steps"],
        "cfg_scale": CONFIG["cfg_scale"],
        "width": CONFIG["width"],
        "height": CONFIG["height"],
        "seed": CONFIG["seed"],
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        CONFIG["api_url"],
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"[SD-Render] Requesting {filename} with seed {CONFIG['seed']}...")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            img_b64 = res_data["images"][0]
            raw_img = Image.open(io.BytesIO(base64.b64decode(img_b64)))
            
            # Post-processing: Advanced Anime-Safe Background Matting
            if REMBG_AVAILABLE:
                print(f"[Rembg] Removing background with anime-safe matting for {filename}...")
                import numpy as np
                from scipy.ndimage import binary_fill_holes, gaussian_filter, label
                
                raw_rgb = np.array(raw_img.convert("RGB"))
                seg = remove(raw_img, session=session)
                raw_alpha = np.array(seg)[:, :, 3]
                
                # Fill holes in white wings, dress ruffles, and pale skin
                fg_mask = raw_alpha > 25
                core = binary_fill_holes(fg_mask)
                
                # Clean stray exterior specks
                lbl, num = label(core)
                if num > 1:
                    sizes = [np.sum(lbl == i) for i in range(1, num + 1)]
                    max_size = max(sizes)
                    for i, s in enumerate(sizes, 1):
                        if s < max_size * 0.005:
                            core[lbl == i] = False
                            
                # Antialias outer contours smoothly
                # sigma=1.2 for smoother antialiased edges (reduced jaggies vs 0.6)
                smooth = gaussian_filter(core.astype(float) * 255.0, sigma=1.2)
                smooth = np.clip(smooth, 0, 255).astype(np.uint8)
                smooth[core] = 255
                
                out_arr = np.dstack([raw_rgb, smooth])
                processed_img = Image.fromarray(out_arr, "RGBA")
            else:
                print("[Rembg] Warning: rembg not detected, saving raw image.")
                processed_img = raw_img
                
            out_path = os.path.join(CONFIG["output_dir"], filename)
            processed_img.save(out_path, "PNG")
            print(f"[Done] Saved (Zero-Erosion RGBA): {out_path}")
    except Exception as e:
        print(f"[Error] Failed rendering {filename}: {e}")

if __name__ == "__main__":
    print("=== Columbina SD Batch Renderer ===")
    for fname, kw in EXPRESSIONS.items():
        render_sprite(fname, kw)
    print("=== Batch Generation Complete ===")
