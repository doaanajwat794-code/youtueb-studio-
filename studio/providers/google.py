"""Google Gemini API adapters: Veo video, Gemini image, Gemini TTS.

STATUS: UNTESTED — written against the public Gemini API REST docs; no real call has been
made yet. Verify model IDs and response shapes during the pilot, then set the provider
status to TESTED in config/providers.yaml.

Every function takes a SpendGuard and charges it BEFORE the paid request is sent.
"""
from __future__ import annotations

import base64
import time
import wave
from pathlib import Path

import requests

from ..budget import SpendGuard
from ..config import secret

API = "https://generativelanguage.googleapis.com/v1beta"
TIMEOUT = 120


def _headers() -> dict:
    return {"x-goog-api-key": secret("GEMINI_API_KEY"), "Content-Type": "application/json"}


def _check(resp: requests.Response) -> dict:
    if resp.status_code >= 400:
        raise RuntimeError(f"Gemini API {resp.status_code}: {resp.text[:800]}")
    return resp.json()


def _inline_image(path: Path) -> dict:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return {"bytesBase64Encoded": base64.b64encode(path.read_bytes()).decode(), "mimeType": mime}


# ------------------------------------------------------------------ video (Veo)

def generate_video(guard: SpendGuard, *, model: str, prompt: str, out: Path, usd: float,
                   negative_prompt: str = "", first_frame: Path | None = None,
                   reference_images: list[Path] | None = None, seconds: int = 8,
                   resolution: str = "1080p", aspect_ratio: str = "9:16", poll_every: int = 10, max_wait: int = 900) -> Path:
    """Generate one clip with Veo via the long-running predict endpoint and save it to `out`."""
    instance: dict = {"prompt": prompt}
    if first_frame:
        instance["image"] = _inline_image(first_frame)
    if reference_images:
        instance["referenceImages"] = [{"image": _inline_image(p), "referenceType": "asset"}
                                       for p in reference_images]
    params = {"aspectRatio": aspect_ratio, "resolution": resolution, "durationSeconds": seconds}
    if negative_prompt:
        params["negativePrompt"] = negative_prompt

    guard.charge(usd, provider=model, note=f"{out.name}")
    op = _check(requests.post(f"{API}/models/{model}:predictLongRunning", headers=_headers(),
                              json={"instances": [instance], "parameters": params}, timeout=TIMEOUT))
    name, waited = op["name"], 0
    while not op.get("done"):
        if waited > max_wait:
            raise TimeoutError(f"Veo operation {name} not done after {max_wait}s")
        time.sleep(poll_every)
        waited += poll_every
        op = _check(requests.get(f"{API}/{name}", headers=_headers(), timeout=TIMEOUT))
    if "error" in op:
        raise RuntimeError(f"Veo error: {op['error']}")
    samples = op["response"]["generateVideoResponse"]["generatedSamples"]
    uri = samples[0]["video"]["uri"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(uri, headers=_headers(), stream=True, timeout=TIMEOUT, allow_redirects=True) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    return out


# ------------------------------------------------------------------ images

def generate_image(guard: SpendGuard, *, model: str, prompt: str, out: Path, usd: float,
                   references: list[Path] | None = None, aspect_ratio: str = "9:16") -> Path:
    parts: list[dict] = [{"text": prompt}]
    for ref in references or []:
        img = _inline_image(ref)
        parts.append({"inlineData": {"mimeType": img["mimeType"], "data": img["bytesBase64Encoded"]}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect_ratio}}}
    guard.charge(usd, provider=model, note=out.name)
    data = _check(requests.post(f"{API}/models/{model}:generateContent", headers=_headers(),
                                json=body, timeout=TIMEOUT))
    for part in data["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(base64.b64decode(part["inlineData"]["data"]))
            return out
    raise RuntimeError("No image returned")


# ------------------------------------------------------------------ speech

def synthesize_speech(guard: SpendGuard, *, model: str, text: str, voice: str, out: Path, usd: float,
                      style: str = "") -> Path:
    """Gemini TTS returns raw 24 kHz 16-bit mono PCM; wrap it in a WAV file."""
    prompt = f"{style}: {text}" if style else text
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    guard.charge(usd, provider=model, note=out.name)
    data = _check(requests.post(f"{API}/models/{model}:generateContent", headers=_headers(),
                                json=body, timeout=TIMEOUT))
    pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(pcm)
    return out


# Music (Lyria) is intentionally not implemented yet: its Gemini API request shape must be
# confirmed from the official docs during setup rather than guessed.
