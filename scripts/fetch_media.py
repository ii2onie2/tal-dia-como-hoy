#!/usr/bin/env python3
"""Fetch Commons images only after a fail-closed metadata/integrity audit.

This gate does not certify commercial rights or authorize publication.
Non-Commons assets require their own rights review.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

import requests

from audit_commons_licenses import check as check_commons_credit

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    "User-Agent": "TalDiaComoHoy/1.0 (https://github.com/ii2onie2/tal-dia-como-hoy; contact: ii2onie@gmail.com)"
}
MAX_MEDIA_BYTES = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def media_path(path, root):
    resolved = path.resolve()
    media_root = (root / "media").resolve()
    if not resolved.is_relative_to(media_root):
        raise RuntimeError("Commons output must be inside repository media/")
    return resolved.relative_to(root).as_posix()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", default="media")
    args = ap.parse_args()

    root = Path.cwd().resolve()
    content_path = Path(args.content)
    data = json.loads(content_path.read_text(encoding="utf-8"))
    items = data.get("media") or []
    if not isinstance(items, list):
        raise RuntimeError("Invalid media list")
    out = Path(args.out)
    media_path(out, root)
    out.mkdir(parents=True, exist_ok=True)
    pending = []

    # Stage all downloads; do not mutate declared content or published media
    # when any Commons image fails its validation.
    with TemporaryDirectory(prefix=".commons-staging-", dir=out) as tmp:
        staging = Path(tmp)
        with requests.Session() as session:
            session.headers.update(HEADERS)
            for index, item in enumerate(items, 1):
                if not isinstance(item, dict):
                    raise RuntimeError("Invalid media entry")
                title = item.get("commons_title")
                if title is None:
                    continue  # AI/user assets have a different, unresolved rights gate.
                if not isinstance(title, str) or not title.startswith("File:"):
                    raise RuntimeError(f"Invalid Commons title: {title!r}")
                params = {
                    "action": "query", "format": "json", "formatversion": "2",
                    "prop": "imageinfo", "iiprop": "url|extmetadata", "titles": title,
                }
                response = session.get(API, params=params, timeout=30)
                response.raise_for_status()
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise RuntimeError(f"Invalid Commons API JSON for {title!r}") from exc
                pages = payload.get("query", {}).get("pages", [])
                if len(pages) != 1 or not pages[0].get("imageinfo"):
                    raise RuntimeError(f"No Commons imageinfo for {title!r}")
                page = pages[0]
                page_title = page.get("title", "")
                if page.get("ns") != 6 or page_title.replace("_", " ").casefold() != title.replace("_", " ").casefold():
                    raise RuntimeError(f"Commons title mismatch: {title!r}")
                info = page["imageinfo"][0]
                url = info.get("url", "")
                ext = Path(urlsplit(url).path).suffix.lower()
                if ext not in ALLOWED_EXTENSIONS:
                    raise RuntimeError(f"Unsupported Commons media extension: {ext!r}")
                downloaded = session.get(url, timeout=60)
                downloaded.raise_for_status()
                final_url = getattr(downloaded, "url", url)
                if final_url != url:
                    raise RuntimeError("Commons download redirected; manual review required")
                payload_bytes = downloaded.content
                if not payload_bytes or len(payload_bytes) > MAX_MEDIA_BYTES:
                    raise RuntimeError("Commons media empty or exceeds safe size cap")
                staged_file = staging / f"{index:02d}{ext}"
                staged_file.write_bytes(payload_bytes)
                credit = {
                    "commons_title": title,
                    "path": media_path(staged_file, root),
                    "source": url,
                    "metadata": info.get("extmetadata", {}),
                    "sha256": hashlib.sha256(payload_bytes).hexdigest(),
                }
                ok, reason = check_commons_credit(credit, root=root)
                if not ok:
                    raise RuntimeError(f"Commons image rejected: {reason} ({title})")
                pending.append((item, staged_file, out / f"{index:02d}{ext}", credit))

        # Only commit downloaded media after every Commons item passes.
        credits = []
        for item, staged_file, final_file, credit in pending:
            os.replace(staged_file, final_file)
            final_relative = media_path(final_file, root)
            item["path"] = final_relative
            credit["path"] = final_relative
            credits.append(credit)

    # This is provenance evidence, not rights clearance for publication.
    (out / "credits.json").write_text(
        json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    content_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
