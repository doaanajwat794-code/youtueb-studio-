"""YouTube Data API v3: research statistics (API key) and private uploads (OAuth).

STATUS: UNTESTED — needs YOUTUBE_API_KEY (research) and OAuth client + refresh token (upload).
Uploads are ALWAYS private. There is deliberately no code path that publishes publicly;
the owner flips visibility in YouTube Studio (or a later, explicitly approved command).
"""
from __future__ import annotations

import datetime as dt
import re
import statistics
from pathlib import Path

import requests

from . import config

API = "https://www.googleapis.com/youtube/v3"
UPLOAD_SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
                 "https://www.googleapis.com/auth/youtube.force-ssl"]


# ------------------------------------------------------------------ research stats

def _get(path: str, **params) -> dict:
    params["key"] = config.secret("YOUTUBE_API_KEY")
    r = requests.get(f"{API}/{path}", params=params, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"YouTube API {r.status_code}: {r.text[:500]}")
    return r.json()


def _iso_duration(text: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", text)
    d, h, mi, s = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def _channel_median_views(channel_id: str, n: int = 30) -> float | None:
    ch = _get("channels", part="contentDetails", id=channel_id)["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = [i["contentDetails"]["videoId"] for i in
           _get("playlistItems", part="contentDetails", playlistId=uploads, maxResults=min(n, 50))["items"]]
    stats = _get("videos", part="statistics", id=",".join(ids))["items"]
    views = [int(v["statistics"].get("viewCount", 0)) for v in stats]
    return statistics.median(views) if views else None


def refresh_research_stats() -> list[dict]:
    """Fill pending fields in research/sources.yaml with verified API data."""
    path = config.ROOT / "research" / "sources.yaml"
    data = config.load_yaml(path)
    ids = [v["id"] for v in data["videos"]]
    items = {i["id"]: i for i in _get("videos", part="snippet,statistics,contentDetails",
                                      id=",".join(ids))["items"]}
    today = dt.date.today()
    medians: dict[str, float | None] = {}
    for video in data["videos"]:
        item = items.get(video["id"])
        if not item:
            video["api_status"] = "not found / private"
            continue
        sn, st = item["snippet"], item["statistics"]
        published = dt.date.fromisoformat(sn["publishedAt"][:10])
        views = int(st.get("viewCount", 0))
        age = max((today - published).days, 1)
        cid = sn["channelId"]
        if cid not in medians:
            medians[cid] = _channel_median_views(cid)
        video.update({
            "title": sn["title"], "channel": sn["channelTitle"], "published": published.isoformat(),
            "duration_seconds": _iso_duration(item["contentDetails"]["duration"]),
            "views": views, "likes": int(st.get("likeCount", 0)), "comments": int(st.get("commentCount", 0)),
            "views_per_day": round(views / age, 1),
            "channel_median_views_last30": medians[cid],
            "vs_channel_median": round(views / medians[cid], 2) if medians[cid] else None,
            "api_status": "verified",
        })
    data["stats_verified_on"] = today.isoformat()
    config.save_yaml(path, data)
    return data["videos"]


# ------------------------------------------------------------------ OAuth + upload

def authorize_interactively(client_secrets: Path) -> str:
    """Run ONCE on the owner's own computer (opens a browser). Prints the refresh token to store
    as the YOUTUBE_REFRESH_TOKEN secret. The token is never written into the repository."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), UPLOAD_SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    return creds.refresh_token


def _credentials():
    from google.oauth2.credentials import Credentials

    return Credentials(None, refresh_token=config.secret("YOUTUBE_REFRESH_TOKEN"),
                       token_uri="https://oauth2.googleapis.com/token",
                       client_id=config.secret("YOUTUBE_CLIENT_ID"),
                       client_secret=config.secret("YOUTUBE_CLIENT_SECRET"), scopes=UPLOAD_SCOPES)


def upload_private(slug: str) -> str:
    """Upload media/<slug>/final.mp4 as PRIVATE with metadata, captions and thumbnail."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    meta = config.load_yaml(config.project_dir(slug) / "metadata.yaml")
    media = config.media_dir(slug)
    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    body = {
        "snippet": {"title": meta["title"][:100], "description": meta["description"][:5000],
                    "tags": meta.get("tags", []), "categoryId": str(meta.get("category_id", 24)),
                    "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": bool(meta.get("contains_synthetic_media", True))},
    }
    request = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=MediaFileUpload(str(media / "final.mp4"), chunksize=16 << 20,
                                                            resumable=True))
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]
    srt = media / "final.en.srt"
    if srt.exists():
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": video_id, "language": "en",
                                                               "name": "English"}},
                             media_body=MediaFileUpload(str(srt))).execute()
    thumb = media / "thumbnail.jpg"
    if thumb.exists():
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb))).execute()
    project = config.project_dir(slug) / "project.yaml"
    info = config.load_yaml(project)
    info.update({"youtube_video_id": video_id, "youtube_privacy": "private",
                 "uploaded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    config.save_yaml(project, info)
    return video_id
