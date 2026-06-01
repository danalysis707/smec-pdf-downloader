import json
import subprocess
import sys
from pathlib import Path

YOUTUBE_CONFIG = Path("youtube_config.json")
THEME_MAP_PATH = Path("docs/data/theme_map.json")
OUTPUT_PATH = Path("docs/data/youtube_data.json")
MAX_VIDEOS_PER_THEME = 5


def fetch_channel_videos(channel_url: str) -> list[dict]:
    """yt-dlp でチャンネルの動画タイトルとURLを取得する。"""
    result = subprocess.run(
        [
            sys.executable, "-m", "yt_dlp",
            "--flat-playlist", "--print", "%(title)s\t%(webpage_url)s",
            "--no-warnings",
            channel_url,
        ],
        capture_output=True, text=True, encoding="utf-8",
    )
    videos = []
    for line in result.stdout.splitlines():
        if "\t" in line:
            title, url = line.split("\t", 1)
            videos.append({"title": title.strip(), "url": url.strip()})
    return videos


def match_video_to_theme(title: str, theme_keywords: dict) -> tuple[str, str] | None:
    """動画タイトルにキーワードが含まれれば (subject, theme) を返す。"""
    for subject, themes in theme_keywords.items():
        for theme, keywords in themes.items():
            if any(kw in title for kw in keywords):
                return subject, theme
    return None


def main() -> None:
    config = json.loads(YOUTUBE_CONFIG.read_text(encoding="utf-8"))
    theme_keywords = json.loads(THEME_MAP_PATH.read_text(encoding="utf-8"))
    result: dict[str, dict[str, list[dict]]] = {}

    for ch in config["channels"]:
        print(f"Fetching: {ch['name']} ...")
        videos = fetch_channel_videos(ch["url"])
        print(f"  {len(videos)} videos found")
        matched = 0
        for video in videos:
            match = match_video_to_theme(video["title"], theme_keywords)
            if match:
                subject, theme = match
                bucket = result.setdefault(subject, {}).setdefault(theme, [])
                if len(bucket) < MAX_VIDEOS_PER_THEME:
                    bucket.append({
                        "title": video["title"],
                        "url": video["url"],
                        "channel": ch["name"],
                    })
                    matched += 1
        print(f"  {matched} videos matched to themes")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(len(v) for themes in result.values() for v in themes.values())
    print(f"\nDone: {OUTPUT_PATH} ({total} videos across {len(result)} subjects)")


if __name__ == "__main__":
    main()
