import base64
import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests
from pipeline.core import run_with_cache
from pipeline.validate import load_and_validate

load_dotenv()

CANONICAL_STYLE = (
    "Consistent painterly 2D storybook illustration style across the entire film, "
    "warm natural Ethiopian highland daylight, clean linework, rich earthy tones, "
    "same camera/rendering medium in every frame. "
)

CANONICAL_ELDER = (
    "ELDER MAN (exact same person in every shot): Ethiopian man in his late 60s, "
    "warm weathered dark-brown skin, short neat silver-white hair, trimmed silver-white beard and mustache, "
    "kind calm eyes, wearing a draped off-white handwoven cotton gabi shawl with subtle woven border stripes. "
)

CANONICAL_YOUNG_MAN = (
    "YOUNG MAN (exact same person in every shot): Ethiopian man in his late 20s, "
    "medium-dark warm brown skin, short black curly hair, clean-shaven or very light stubble, "
    "expressive brow, wearing a simple earthy olive-brown linen tunic. "
)

CANONICAL_SIEVE = (
    "SIEVE / WONFIT (exact same object in every shot): traditional circular Ethiopian woven reed and split-bamboo "
    "sieve with a raised circular rim and fine perforated mesh center; "
    "when dirty/clogged it has dark black soot and dried mud coating the reeds and mesh; "
    "when clean it has natural golden-tan reeds with open, clear mesh holes. "
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def cf_generate_image(prompt: str, steps: int = 6) -> bytes:
    acct = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    token = os.environ["CLOUDFLARE_API_TOKEN"].strip()
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": prompt, "steps": steps},
        timeout=90,
    )
    if not r.ok:
        raise RuntimeError(f"Cloudflare FLUX {r.status_code}: {r.text}")

    ctype = r.headers.get("content-type", "")
    if "application/json" in ctype:
        b64 = r.json()["result"]["image"]
        return base64.b64decode(b64)
    return r.content


def gemini_generate_consistent_image(
    prompt: str,
    ref_images: list[tuple[bytes, str]] | None = None,
) -> bytes:
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
        http_options={"api_version": "v1beta"},
    )
    contents: list = []
    if ref_images:
        contents.append(
            "Use the attached reference image(s) as the strict visual ground truth for character faces, "
            "clothing, art style, and the circular woven sieve. Do not change facial identity or sieve structure:"
        )
        for img_bytes, label in ref_images:
            contents.append(f"Reference ({label}):")
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
    contents.append(prompt)

    for img_model in ["gemini-2.5-flash-image", "gemini-3.1-flash-image"]:
        try:
            resp = client.models.generate_content(
                model=img_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                ),
            )
            for part in resp.candidates[0].content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    raw = part.inline_data.data
                    if isinstance(raw, bytes):
                        return raw
                    return base64.b64decode(raw)
        except Exception as exc:
            print(f"[WARN] {img_model} failed: {exc}")

    # Last-resort fallback if Gemini image quota/endpoint is unavailable
    return cf_generate_image(prompt, steps=6)


def generate_keyframes(sb: dict) -> None:
    model_id = "gemini-image-ref-locked"

    # 1. Character turnaround sheet
    char_cfg = sb["character_sheet"]
    char_prompt = (
        f"{CANONICAL_STYLE}{CANONICAL_ELDER}{CANONICAL_YOUNG_MAN}"
        f"Character reference turnaround sheet on neutral warm parchment background: {char_cfg['prompt']}"
    )
    sheet_path = Path("outputs/keyframes/character_sheet.png")
    run_with_cache(
        stage="keyframes",
        item_id="character_sheet",
        model=model_id,
        params={"prompt": char_prompt, "v": 2},
        seed=char_cfg["seed"],
        output_path=sheet_path,
        cost_usd=0.0,
        fn=lambda: gemini_generate_consistent_image(char_prompt),
    )

    # 2. Canonical sieve reference (dirty vs clean side-by-side / clear view)
    sieve_prompt = (
        f"{CANONICAL_STYLE}{CANONICAL_SIEVE}"
        "Clean studio-style reference view of the circular Ethiopian woven reed sieve (wonfit), "
        "showing exact circular rim, woven reeds, and mesh holes clearly on a warm neutral background."
    )
    sieve_path = Path("outputs/keyframes/sieve_reference.png")
    run_with_cache(
        stage="keyframes",
        item_id="sieve_reference",
        model=model_id,
        params={"prompt": sieve_prompt, "v": 2},
        seed=9001,
        output_path=sieve_path,
        cost_usd=0.0,
        fn=lambda: gemini_generate_consistent_image(sieve_prompt),
    )

    sheet_bytes = sheet_path.read_bytes()
    sieve_bytes = sieve_path.read_bytes()
    ref_pair = [(sheet_bytes, "characters"), (sieve_bytes, "sieve")]
    ref_digest = f"{_sha256_bytes(sheet_bytes)}_{_sha256_bytes(sieve_bytes)}"

    # 3. Generate all 8 shot keyframes conditioned on both reference images + canonical lock
    for shot in sb["shots"]:
        sid = shot["id"]
        out_png = Path(f"outputs/keyframes/{sid}.png")
        full_prompt = (
            f"{CANONICAL_STYLE}{CANONICAL_ELDER}{CANONICAL_YOUNG_MAN}{CANONICAL_SIEVE}"
            f"Scene action: {shot['image_prompt']}"
        )
        run_with_cache(
            stage="keyframes",
            item_id=sid,
            model=model_id,
            params={"prompt": full_prompt, "refs": ref_digest, "v": 2},
            seed=shot["seed"],
            output_path=out_png,
            cost_usd=0.0,
            fn=lambda p=full_prompt: gemini_generate_consistent_image(p, ref_images=ref_pair),
        )

    print("[OK] Regenerated character sheet, sieve reference, and all 8 consistent shot keyframes.")


if __name__ == "__main__":
    generate_keyframes(load_and_validate())