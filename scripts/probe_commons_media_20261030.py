#!/usr/bin/env python3
"""Read-only Commons original media probe. No rights approval or publishing."""
import hashlib
import json
import pathlib
import sys
import urllib.parse
import urllib.request

INVENTORY = pathlib.Path("content/research/2026-10-30.media-rights-inventory.json")
OUT = pathlib.Path("commons-media-probe-report.json")
MAX_BYTES = 40 * 1024 * 1024

def request(url):
    return urllib.request.Request(url, headers={"User-Agent": "TalDiaEditorialPreflight/1.0 (GitHub Actions; noncommercial verification)"})

def main():
    slots = json.loads(INVENTORY.read_text(encoding="utf-8"))["slots"]
    results = []
    failures = []
    for slot in slots:
        record = {"slot": slot["slot"], "source_page": slot["exact_file_url"], "status": "BLOCKED"}
        try:
            parsed = urllib.parse.urlparse(slot["exact_file_url"])
            if parsed.scheme != "https" or parsed.netloc != "commons.wikimedia.org" or not parsed.path.startswith("/wiki/File:"):
                raise ValueError("not an exact Wikimedia Commons file page")
            title = urllib.parse.unquote(parsed.path.removeprefix("/wiki/"))
            api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
                "action": "query", "format": "json", "prop": "imageinfo",
                "iiprop": "url|size|mime|sha1|extmetadata", "titles": title,
            })
            with urllib.request.urlopen(request(api), timeout=25) as response:
                payload = json.load(response)
            if not isinstance(payload, dict) or "query" not in payload:
                raise ValueError("unexpected Commons API response")
            pages = payload["query"]["pages"]
            page = next(iter(pages.values()))
            info = page["imageinfo"][0]
            original = info["url"]
            url = urllib.parse.urlparse(original)
            if url.scheme != "https" or url.hostname not in {"upload.wikimedia.org", "commons.wikimedia.org"}:
                raise ValueError("untrusted original media host")
            size = int(info["size"])
            if size <= 0 or size > MAX_BYTES:
                raise ValueError("original size outside bounded limits")
            digest = hashlib.sha256()
            actual = 0
            with urllib.request.urlopen(request(original), timeout=60) as response:
                resolved = urllib.parse.urlparse(response.geturl())
                if resolved.scheme != 'https' or resolved.hostname not in {'upload.wikimedia.org', 'commons.wikimedia.org'}:
                    raise ValueError('untrusted download redirect')
                if info.get('mime') not in {'image/jpeg', 'image/png'}:
                    raise ValueError('unexpected media MIME')
                if response.headers.get_content_type() not in {'image/jpeg', 'image/png', 'application/octet-stream'}:
                    raise ValueError('unexpected download content type')
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    actual += len(chunk)
                    if actual > MAX_BYTES:
                        raise ValueError("download exceeded limit")
                    digest.update(chunk)
            if actual != size:
                raise ValueError("download size differs from Commons metadata")
            record.update(status="DOWNLOADED_HASHED_RIGHTS_NOT_APPROVED", original_url=original,
                          size_bytes=actual, sha256=digest.hexdigest(), commons_sha1=info.get("sha1"),
                          mime=info.get("mime"), license_metadata={
                              k: v.get("value") for k, v in info.get("extmetadata", {}).items()
                              if k in {"LicenseShortName", "LicenseUrl", "Artist", "Credit", "AttributionRequired"}
                          })
        except Exception as exc:
            record["error"] = str(exc)[:250]
            failures.append(slot["slot"])
        results.append(record)
    OUT.write_text(json.dumps({"status": "PASS_HASH_ONLY" if not failures else "BLOCKED",
                                "rights_approved": False, "render_authorized": False,
                                "publication_authorized": False, "results": results},
                               ensure_ascii=False, indent=2) + chr(10), encoding="utf-8")
    print(f"REPORT={OUT} RESULT={'PASS_HASH_ONLY' if not failures else 'BLOCKED'}")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
