"""
Columbina Sprite Batch Regenerator v2
Regenerates remaining 7 sprites via SD WebUI/Forge API (or manually via Gemini)
with improved prompts: blindfold, no fishnet hair, no visible eyes.

Run this when:
  - SD WebUI/Forge is running locally at http://127.0.0.1:7860
  - OR your image generation quota has reset

Usage:
  python regenerate_v2.py

All sprites will be saved to the same columbina/ directory and zip updated.
"""

import os
import json
import base64
import urllib.request
import io
import zipfile
import shutil
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes, gaussian_filter, label

try:
    from rembg import new_session, remove
    session = new_session('isnet-anime')
    REMBG_AVAILABLE = True
    print('[rembg] isnet-anime session loaded.')
except Exception as e:
    REMBG_AVAILABLE = False
    print(f'[rembg] Not available: {e}')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(os.path.dirname(OUTPUT_DIR), 'columbina_sprites.zip')

CONFIG = {
    "api_url": "http://127.0.0.1:7860/sdapi/v1/txt2img",
    "seed": 88889999,
    "steps": 28,
    "cfg_scale": 6.0,
    "width": 1024,
    "height": 1024,
    "lora_name": "columbina_2a_naiVpred-000039",
    "lora_weight": 0.8,
}

BASE_PROMPT = (
    "masterpiece, best quality, highres, anime style, 1girl, solo, columbina genshin impact, "
    "damselette, fatui harbinger, half body portrait, upper body, facing viewer, white background, "
    "simple white background, wing hair ornament, small white feather wings on head, "
    "white lace ruffled gothic dress, pale skin, "
    "dark black hair with smooth pink inner color streaks, clean gradient black to rose pink, "
    "NO fishnet texture, NO mesh pattern, smooth hair coloring, "
    "wearing white ornate eye blindfold with lace trim, white decorative eye bandage, "
    "eyes completely covered by blindfold, no visible eyes, "
    f"<lora:{CONFIG['lora_name']}:{CONFIG['lora_weight']}>, "
    "cel shaded, crisp clean lines, no jagged edges"
)

NEGATIVE_PROMPT = (
    "worst quality, low quality, normal quality, blurry, bad anatomy, bad hands, "
    "missing fingers, complex background, scenery, text, watermark, signature, "
    "open eyes, visible eyes, pupils, irises, fishnet, mesh texture in hair, "
    "striped artifacts, jagged edges"
)

# Only the 7 remaining sprites (idle/speaking/smile already done with v2)
EXPRESSIONS_REMAINING = {
    "excited.png":  "wide bright open-mouth smile showing teeth, very happy joyful excited, cheerful big grin",
    "blush.png":    "heavy blush on cheeks, shy embarrassed flustered, cute slight closed-mouth smile, cheeks red",
    "relaxed.png":  "peaceful serene tranquil, soft gentle slight smile, resting calm",
    "thinking.png": "one gloved hand raised near chin thoughtfully, puzzled curious, head slightly tilted, closed mouth",
    "concerned.png": "slightly open mouth, lower lip slightly trembling, worried empathetic caring expression",
    "sad.png":      "downcast face, subtle small frown, melancholy grief, closed mouth, slight droop at corners",
    "angry.png":    "cute pout, lower lip pushed out, furrowed brow visible above blindfold, stern determined annoyed",
}

def remove_background(raw_img):
    """Apply anime-safe matting with hole filling and smooth antialiasing."""
    raw_rgb = np.array(raw_img.convert("RGB"))
    seg = remove(raw_img, session=session)
    raw_alpha = np.array(seg)[:, :, 3]
    
    fg_mask = raw_alpha > 25
    core = binary_fill_holes(fg_mask)
    
    lbl, num = label(core)
    if num > 1:
        sizes = [np.sum(lbl == i) for i in range(1, num + 1)]
        max_size = max(sizes)
        for i, s in enumerate(sizes, 1):
            if s < max_size * 0.005:
                core[lbl == i] = False
    
    # sigma=1.2 for smooth antialiasing (no jagged edges)
    smooth = gaussian_filter(core.astype(float) * 255.0, sigma=1.2)
    smooth = np.clip(smooth, 0, 255).astype(np.uint8)
    smooth[core] = 255  # interior 100% opaque
    
    out_arr = np.dstack([raw_rgb, smooth])
    return Image.fromarray(out_arr, 'RGBA')


def render_via_sd_api(filename, expression_keywords):
    """Render a single sprite via Stable Diffusion WebUI API."""
    prompt = f"{BASE_PROMPT}, {expression_keywords}"
    payload = {
        "prompt": prompt,
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
    
    print(f"[SD] Rendering {filename}...")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            img_b64 = res_data["images"][0]
            raw_img = Image.open(io.BytesIO(base64.b64decode(img_b64)))
            
            if REMBG_AVAILABLE:
                print(f"  -> Removing background (anime-safe matting)...")
                processed = remove_background(raw_img)
            else:
                print("  -> rembg not available, saving raw.")
                processed = raw_img
            
            out_path = os.path.join(OUTPUT_DIR, filename)
            processed.save(out_path, "PNG")
            print(f"  -> Saved: {out_path}")
            return True
    except Exception as e:
        print(f"  [ERROR] {filename}: {e}")
        return False


def rebuild_zip():
    """Rebuild the columbina_sprites.zip from current directory contents."""
    all_sprites = [
        "idle.png", "speaking.png", "smile.png", "excited.png", "blush.png",
        "relaxed.png", "thinking.png", "concerned.png", "sad.png", "angry.png"
    ]
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for fname in all_sprites:
            fpath = os.path.join(OUTPUT_DIR, fname)
            if os.path.exists(fpath):
                zipf.write(fpath, os.path.join('columbina', fname))
    print(f"[ZIP] Rebuilt: {ZIP_PATH} ({os.path.getsize(ZIP_PATH)} bytes)")


if __name__ == "__main__":
    print("=== Columbina Sprite Regenerator v2 ===")
    print(f"Generating {len(EXPRESSIONS_REMAINING)} remaining sprites...")
    
    success_count = 0
    for fname, kw in EXPRESSIONS_REMAINING.items():
        if render_via_sd_api(fname, kw):
            success_count += 1
    
    print(f"\n[Done] {success_count}/{len(EXPRESSIONS_REMAINING)} sprites rendered.")
    
    if success_count > 0:
        rebuild_zip()
    
    print("\n=== SPRITE STATUS ===")
    all_sprites = [
        "idle.png", "speaking.png", "smile.png", "excited.png", "blush.png",
        "relaxed.png", "thinking.png", "concerned.png", "sad.png", "angry.png"
    ]
    for fname in all_sprites:
        path = os.path.join(OUTPUT_DIR, fname)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  [OK] {fname} ({size} bytes)")
        else:
            print(f"  [MISSING] {fname}")
