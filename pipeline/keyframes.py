import base64
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from pipeline.core import run_with_cache
from pipeline.validate import load_and_validate

load_dotenv()


def cf_generate_image(prompt: str, seed: int, steps: int = 6) -> bytes:
    acct = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    token = os.environ["CLOUDFLARE_API_TOKEN"].strip()
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": prompt, "seed": seed, "steps": steps},
        timeout=90,
    )
    if not r.ok:
        raise RuntimeError(f"Cloudflare FLUX {r.status_code}: {r.text}")

    ctype = r.headers.get("content-type", "")
    if "application/json" in ctype:
        b64 = r.json()["result"]["image"]
        return base64.b64decode(b64)
    return r.content


def generate_keyframes(sb: dict) -> None:
    model_id = "@cf/black-forest-labs/flux-1-schnell"

    # 1. Generate character & style reference sheet first
    char_cfg = sb["character_sheet"]
    sheet_path = Path("outputs/keyframes/character_sheet.png")
    run_with_cache(
        stage="keyframes",
        item_id="character_sheet",
        model=model_id,
        params={"prompt": char_cfg["prompt"], "steps": 6},
        seed=char_cfg["seed"],
        output_path=sheet_path,
        cost_usd=0.0,
        fn=lambda: cf_generate_image(char_cfg["prompt"], char_cfg["seed"], steps=6),
    )

    # 2. Generate shot keyframes conditioned on character consistency descriptions
    char_anchor = (
        "Consistent characters from reference sheet: Ethiopian elder wise man in late 60s with silver beard and white cotton gabi shawl; "
        "young Ethiopian man in late 20s in earthy linen tunic. "
    )
    for shot in sb["shots"]:
        sid = shot["id"]
        out_png = Path(f"outputs/keyframes/{sid}.png")
        full_prompt = char_anchor + shot["image_prompt"]
        run_with_cache(
            stage="keyframes",
            item_id=sid,
            model=model_id,
            params={"prompt": full_prompt, "steps": 6, "ref": str(sheet_path)},
            seed=shot["seed"],
            output_path=out_png,
            cost_usd=0.0,
            fn=lambda p=full_prompt, s=shot["seed"]: cf_generate_image(p, s, steps=6),
        )
    print("[OK] Character sheet and all 8 shot keyframes ready in outputs/keyframes/.")


if __name__ == "__main__":
    generate_keyframes(load_and_validate())