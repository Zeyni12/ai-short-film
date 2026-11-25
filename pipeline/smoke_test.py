import os
import time
import requests
from dotenv import load_dotenv
from google import genai
from pipeline.core import log_run

load_dotenv()


def test_gemini():
    t0 = time.perf_counter()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(model="gemini-3.1-flash-lite", contents="Reply with OK.")
    ms = round((time.perf_counter() - t0) * 1000, 2)
    log_run({
        "stage": "smoke_test", "item_id": "gemini", "model": "gemini-3.1-flash-lite",
        "params": {}, "seed": 0, "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False
    })
    print(f"[OK] Gemini smoke test ({ms} ms): {resp.text.strip()}")


def test_cloudflare():
    t0 = time.perf_counter()
    acct = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    token = os.environ["CLOUDFLARE_API_TOKEN"].strip()
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "a simple wooden cup", "steps": 4},
        timeout=60,
    )
    if not r.ok:
        raise RuntimeError(f"Cloudflare {r.status_code}: {r.text}")
    ms = round((time.perf_counter() - t0) * 1000, 2)
    log_run({
        "stage": "smoke_test", "item_id": "cloudflare",
        "model": "@cf/black-forest-labs/flux-1-schnell",
        "params": {"steps": 4}, "seed": 0, "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False
    })
    print(f"[OK] Cloudflare smoke test ({ms} ms)")


if __name__ == "__main__":
    test_gemini()
    test_cloudflare()