#!/usr/bin/env python3
import argparse
import json
import pathlib
import requests
import urllib.parse

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    "User-Agent": "TalDiaComoHoy/1.0 (https://github.com/ii2onie2/tal-dia-como-hoy; contact: ii2onie@gmail.com)"
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", default="media")
    args = ap.parse_args()

    content_path = pathlib.Path(args.content)
    data = json.loads(content_path.read_text(encoding="utf-8"))
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    downloaded = []

    with requests.Session() as session:
        session.headers.update(HEADERS)

        for i, item in enumerate(data.get("media") or [], 1):
            if not isinstance(item, dict):
                continue
            title = item.get("commons_title")
            if not title:
                continue

            params = {
                "action": "query",
                "format": "json",
                "formatversion": "2",
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "titles": title,
                "origin": "*",
            }
            response = session.get(API, params=params, timeout=30)
            response.raise_for_status()

            try:
                payload = response.json()
            except requests.exceptions.JSONDecodeError as exc:
                preview = response.text[:500].replace("\n", " ")
                raise RuntimeError(
                    f"Wikimedia API did not return JSON for {title!r}: "
                    f"HTTP {response.status_code}; body={preview!r}"
                ) from exc

            pages = payload.get("query", {}).get("pages", [])
            if not pages:
                raise RuntimeError(f"No Wikimedia Commons page found for {title!r}")

            page = pages[0]
            info_list = page.get("imageinfo") or []
            if not info_list:
                raise RuntimeError(
                    f"No downloadable imageinfo for {title!r}; "
                    f"page may be missing or not a file"
                )

            info = info_list[0]
            url = info.get("url")
            if not url:
                raise RuntimeError(f"No media URL returned for {title!r}")

            ext = pathlib.Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
            dest = out / f"{i:02d}{ext}"

            media_response = session.get(url, timeout=60)
            media_response.raise_for_status()
            dest.write_bytes(media_response.content)

            downloaded.append(
                {
                    "commons_title": title,
                    "path": str(dest),
                    "source": url,
                    "metadata": info.get("extmetadata", {}),
                }
            )
            item["path"] = str(dest)

    content_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "credits.json").write_text(
        json.dumps(downloaded, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
