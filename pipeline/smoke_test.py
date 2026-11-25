# # # import os
# # # import time
# # # import requests
# # # from dotenv import load_dotenv
# # # from google import genai
# # # from pipeline.core import log_run

# # # load_dotenv()


# # # def test_gemini():
# # #     t0 = time.perf_counter()
# # #     client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
# # #     resp = client.models.generate_content(model="gemini-3.8-flash", contents="Reply with OK.")
# # #     ms = round((time.perf_counter() - t0) * 1000, 2)
# # #     log_run({"stage": "smoke_test", "item_id": "gemini", "model": "gemini-3.8-flash", "params": {}, "seed": 0, "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False})
# # #     print(f"[OK] Gemini smoke test ({ms} ms): {resp.text.strip()}")


# # # def test_cloudflare():
# # #     t0 = time.perf_counter()
# # #     acct = os.environ["CLOUDFLARE_ACCOUNT_ID"]
# # #     token = os.environ["CLOUDFLARE_API_TOKEN"]
# # #     url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell"
# # #     r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json={"prompt": "a simple wooden cup", "num_steps": 2}, timeout=60)
# # #     r.raise_for_status()
# # #     ms = round((time.perf_counter() - t0) * 1000, 2)
# # #     log_run({"stage": "smoke_test", "item_id": "cloudflare", "model": "@cf/black-forest-labs/flux-1-schnell", "params": {"num_steps": 2}, "seed": 0, "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False})
# # #     print(f"[OK] Cloudflare smoke test ({ms} ms)")


# # # if __name__ == "__main__":
# # #     test_gemini()
# # #     test_cloudflare()

# # import os
# # import time
# # import requests
# # from dotenv import load_dotenv
# # from google import genai
# # from pipeline.core import log_run

# # load_dotenv()


# # def test_gemini():
# #     client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
# #     models = ["gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-3.0-flash"]
# #     last_err = None

# #     for model in models:
# #         for attempt in range(1, 4):
# #             t0 = time.perf_counter()
# #             try:
# #                 resp = client.models.generate_content(model=model, contents="Reply with OK.")
# #                 ms = round((time.perf_counter() - t0) * 1000, 2)
# #                 log_run({
# #                     "stage": "smoke_test", "item_id": "gemini", "model": model,
# #                     "params": {"attempt": attempt}, "seed": 0,
# #                     "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False
# #                 })
# #                 print(f"[OK] Gemini smoke test ({model}, {ms} ms): {resp.text.strip()}")
# #                 return
# #             except Exception as exc:
# #                 last_err = exc
# #                 print(f"[WARN] {model} attempt {attempt} failed: {exc}")
# #                 time.sleep(2 ** attempt)

# #     raise RuntimeError(f"All Gemini smoke test attempts failed: {last_err}")


# # def test_cloudflare():
# #     t0 = time.perf_counter()
# #     acct = os.environ["CLOUDFLARE_ACCOUNT_ID"]
# #     token = os.environ["CLOUDFLARE_API_TOKEN"]
# #     url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell"
# #     r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json={"prompt": "a simple wooden cup", "num_steps": 2}, timeout=60)
# #     r.raise_for_status()
# #     ms = round((time.perf_counter() - t0) * 1000, 2)
# #     log_run({"stage": "smoke_test", "item_id": "cloudflare", "model": "@cf/black-forest-labs/flux-1-schnell", "params": {"num_steps": 2}, "seed": 0, "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False})
# #     print(f"[OK] Cloudflare smoke test ({ms} ms)")


# # if __name__ == "__main__":
# #     test_gemini()
# #     test_cloudflare()

# import os
# import time
# import requests
# from dotenv import load_dotenv
# from google import genai
# from pipeline.core import log_run

# load_dotenv()


# def test_gemini():
#     client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
#     available = [
#         m.name.replace("models/", "")
#         for m in client.models.list()
#         if "generateContent" in (m.supported_actions or [])
#     ]
#     print("[INFO] Available Gemini models:", [m for m in available if "gemini" in m][:10])

#     # Prioritize flash / tts / pro models that are currently active
#     candidates = [m for m in available if "flash" in m and "tts" not in m and "image" not in m]
#     if not candidates:
#         candidates = available[:3]

#     last_err = None
#     for model in candidates[:4]:
#         for attempt in range(1, 3):
#             t0 = time.perf_counter()
#             try:
#                 resp = client.models.generate_content(model=model, contents="Reply with OK.")
#                 ms = round((time.perf_counter() - t0) * 1000, 2)
#                 log_run({
#                     "stage": "smoke_test", "item_id": "gemini", "model": model,
#                     "params": {"attempt": attempt}, "seed": 0,
#                     "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False
#                 })
#                 print(f"[OK] Gemini smoke test ({model}, {ms} ms): {resp.text.strip()}")
#                 return
#             except Exception as exc:
#                 last_err = exc
#                 print(f"[WARN] {model} attempt {attempt}: {exc}")
#                 time.sleep(2)

#     raise RuntimeError(f"Gemini smoke test failed: {last_err}")


# def test_cloudflare():
#     t0 = time.perf_counter()
#     acct = os.environ["CLOUDFLARE_ACCOUNT_ID"]
#     token = os.environ["CLOUDFLARE_API_TOKEN"]
#     url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell"
#     r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json={"prompt": "a simple wooden cup", "num_steps": 2}, timeout=60)
#     r.raise_for_status()
#     ms = round((time.perf_counter() - t0) * 1000, 2)
#     log_run({"stage": "smoke_test", "item_id": "cloudflare", "model": "@cf/black-forest-labs/flux-1-schnell", "params": {"num_steps": 2}, "seed": 0, "latency_ms": ms, "cost_usd": 0.0, "cache_hit": False})
#     print(f"[OK] Cloudflare smoke test ({ms} ms)")


# if __name__ == "__main__":
#     test_gemini()
#     test_cloudflare()
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