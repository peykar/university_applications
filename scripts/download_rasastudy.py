#!/usr/bin/env python3
"""
download_rasastudy.py

Download the public Rasa Study catalogue data and associated public assets.

Downloads:
- universities
- programs
- FAQ categories
- FAQs
- same-site assets referenced by the downloaded JSON, including images,
  documents, video/audio files, etc.

The FAQ endpoints have changed across Rasa Study versions, so this downloader
tries a small set of known/likely public endpoint variants and validates the
response shape instead of hard-coding only one path.

Usage:
    uv run python scripts/download_rasastudy.py

Examples:
    uv run python scripts/download_rasastudy.py --output data/rasa
    uv run python scripts/download_rasastudy.py --limit 100
    uv run python scripts/download_rasastudy.py --skip-assets

If Rasa changes its FAQ URLs, they can be supplied explicitly:
    uv run python scripts/download_rasastudy.py \
        --faq-url https://rasastudy.com/api/v1/faq \
        --faq-categories-url https://rasastudy.com/api/v1/faq/cats
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import mimetypes
import re
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

import httpx


BASE_URL = "https://rasastudy.com"
API_BASE = f"{BASE_URL}/api/v1"

UNIVERSITIES_URL = f"{API_BASE}/universities"
PROGRAMS_URL = f"{API_BASE}/programs"

# Historical/current Rasa deployments may use different FAQ route spellings.
FAQ_CATEGORY_CANDIDATES = (
    f"{API_BASE}/faq/cats",
    f"{API_BASE}/faq/categories",
    f"{API_BASE}/faq-categories",
    f"{API_BASE}/faq_cats",
    f"{API_BASE}/faqs/categories",
)

FAQ_CANDIDATES = (
    f"{API_BASE}/faq",
    f"{API_BASE}/faqs",
)

DEFAULT_LIMIT = 100
DEFAULT_DELAY = 0.2
DEFAULT_CONCURRENCY = 5

DOWNLOADABLE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".svg",
    ".avif",
    ".ico",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".zip",
    ".mp4",
    ".webm",
    ".mov",
    ".mp3",
    ".wav",
    ".ogg",
    ".m4a",
}

ASSET_FIELD_HINTS = {
    "logo",
    "logo_url",
    "banner",
    "banner_url",
    "image",
    "image_url",
    "photo",
    "photo_url",
    "thumbnail",
    "thumbnail_url",
    "cover",
    "cover_url",
    "file",
    "file_url",
    "document",
    "document_url",
    "attachment",
    "attachment_url",
    "video",
    "video_url",
    "audio",
    "audio_url",
}


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    temp.replace(path)


def safe_filename(value: str, fallback: str = "item") -> str:
    value = unquote(value).strip()
    value = re.sub(r"[^\w.\-]+", "_", value, flags=re.UNICODE)
    value = value.strip("._")
    return value[:180] or fallback


def object_filename(obj: dict[str, Any], prefix: str) -> str:
    object_id = obj.get("id")
    slug = (
        obj.get("slug")
        or obj.get("key")
        or obj.get("name_en")
        or obj.get("name_fa")
        or obj.get("question_en")
        or obj.get("question_fa")
        or str(object_id or "")
    )
    slug = safe_filename(str(slug), prefix)
    if object_id is not None:
        return f"{object_id}_{slug}.json"
    return f"{slug}.json"


def is_same_site(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc:
        return True
    return parsed.netloc.lower() in {"rasastudy.com", "www.rasastudy.com"}


def is_probable_asset(value: str, key: str | None = None) -> bool:
    value = value.strip()
    if not value or value.startswith("data:"):
        return False

    lower_key = (key or "").lower()
    parsed = urlparse(value)
    suffix = PurePosixPath(parsed.path).suffix.lower()

    if suffix in DOWNLOADABLE_EXTENSIONS:
        return True

    if lower_key in ASSET_FIELD_HINTS:
        return True

    if any(
        hint in lower_key
        for hint in (
            "image",
            "logo",
            "banner",
            "photo",
            "thumbnail",
            "cover",
            "attachment",
            "document",
            "audio",
            "video",
        )
    ):
        return value.startswith("/") or value.startswith("http")

    if value.startswith("/ep/"):
        return True

    return False


def discover_assets(
    obj: Any,
    *,
    parent_key: str | None = None,
    json_path: str = "$",
) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            found.extend(
                discover_assets(
                    value,
                    parent_key=key,
                    json_path=f"{json_path}.{key}",
                )
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            found.extend(
                discover_assets(
                    value,
                    parent_key=parent_key,
                    json_path=f"{json_path}[{index}]",
                )
            )

    elif isinstance(obj, str):
        value = obj.strip()

        if is_probable_asset(value, parent_key):
            absolute_url = urljoin(BASE_URL, value)
            if is_same_site(absolute_url):
                found.append(
                    {
                        "url": absolute_url,
                        "source_field": parent_key or "",
                        "json_path": json_path,
                    }
                )

        # Some descriptions may contain inline URLs.
        for match in re.findall(r'https?://[^\s"\'<>]+', value, flags=re.IGNORECASE):
            cleaned = match.rstrip(".,);]}")
            if is_same_site(cleaned) and is_probable_asset(cleaned, parent_key):
                found.append(
                    {
                        "url": cleaned,
                        "source_field": parent_key or "",
                        "json_path": json_path,
                    }
                )

    return found


def extract_list(data: Any, keys: tuple[str, ...]) -> list[dict[str, Any]] | None:
    if isinstance(data, list):
        return data if all(isinstance(item, dict) for item in data) else None

    if not isinstance(data, dict):
        return None

    for key in keys:
        value = data.get(key)
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return value

    return None


class RasaDownloader:
    def __init__(
        self,
        *,
        output: Path,
        limit: int,
        delay: float,
        concurrency: int,
        faq_url: str | None,
        faq_categories_url: str | None,
        download_assets: bool,
    ):
        self.output = output
        self.limit = limit
        self.delay = delay
        self.faq_url = faq_url
        self.faq_categories_url = faq_categories_url
        self.should_download_assets = download_assets

        self.raw_dir = output / "raw"
        self.university_dir = output / "universities"
        self.program_dir = output / "programs"
        self.faq_category_dir = output / "faq_categories"
        self.faq_dir = output / "faqs"
        self.asset_dir = output / "assets"

        self.semaphore = asyncio.Semaphore(concurrency)

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; TurkDemy-RasaArchiver/1.0)",
                "Accept": "application/json,text/plain,*/*",
                "Referer": BASE_URL + "/",
            },
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        retries: int = 5,
        allow_not_found: bool = False,
    ) -> httpx.Response | None:
        last_error: Exception | None = None

        for attempt in range(1, retries + 1):
            try:
                response = await self.client.get(url, params=params)

                if allow_not_found and response.status_code in {404, 405}:
                    return None

                if response.status_code == 429:
                    wait = min(2**attempt, 30)
                    print(f"Rate limited. Waiting {wait}s: {response.url}")
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()

                if self.delay:
                    await asyncio.sleep(self.delay)

                return response

            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_error = exc

                if allow_not_found and isinstance(exc, httpx.HTTPStatusError):
                    if exc.response.status_code in {404, 405}:
                        return None

                if attempt == retries:
                    break

                wait = min(2**attempt, 20)
                print(
                    f"Request failed ({attempt}/{retries}): {url}\n"
                    f"  {exc}\n"
                    f"Retrying in {wait}s..."
                )
                await asyncio.sleep(wait)

        if allow_not_found:
            return None

        assert last_error is not None
        raise last_error

    async def fetch_universities(self) -> list[dict[str, Any]]:
        print("\nFetching universities...")

        response = await self.get(UNIVERSITIES_URL)
        assert response is not None
        data = response.json()

        dump_json(self.raw_dir / "universities_response.json", data)

        universities = extract_list(data, ("universities",))
        if universities is None:
            raise RuntimeError("Unexpected /universities response format.")

        print(f"Found {len(universities)} universities.")

        dump_json(self.output / "universities.json", {"universities": universities})

        for university in universities:
            dump_json(
                self.university_dir / object_filename(university, "university"),
                university,
            )

        return universities

    async def fetch_program_page(self, page: int) -> dict[str, Any]:
        response = await self.get(
            PROGRAMS_URL,
            params={"page": page, "limit": self.limit},
        )
        assert response is not None
        data = response.json()
        dump_json(self.raw_dir / "program_pages" / f"{page:05d}.json", data)
        return data

    async def fetch_all_programs(self) -> list[dict[str, Any]]:
        print("\nFetching programs...")

        first = await self.fetch_program_page(1)
        first_programs = extract_list(first, ("programs",))
        if first_programs is None:
            raise RuntimeError("Unexpected /programs response format.")

        total = int(first.get("total", len(first_programs)))
        actual_limit = int(first.get("limit", self.limit)) or self.limit
        pages = max(1, (total + actual_limit - 1) // actual_limit)

        print(
            f"Programs reported by API: {total}\n"
            f"Page size: {actual_limit}\n"
            f"Pages: {pages}"
        )

        all_programs = list(first_programs)

        for page in range(2, pages + 1):
            print(f"Fetching program page {page}/{pages}...")
            data = await self.fetch_program_page(page)
            programs = extract_list(data, ("programs",))
            if not programs:
                print(f"Page {page} returned no programs; stopping.")
                break
            all_programs.extend(programs)

        deduplicated: dict[Any, dict[str, Any]] = {}
        anonymous_index = 0

        for program in all_programs:
            key = program.get("id")
            if key is None:
                anonymous_index += 1
                key = f"anonymous-{anonymous_index}"
            deduplicated[key] = program

        programs = list(deduplicated.values())

        print(f"Downloaded {len(programs)} unique programs.")

        dump_json(self.output / "programs.json", {"programs": programs})

        for program in programs:
            dump_json(
                self.program_dir / object_filename(program, "program"),
                program,
            )

        return programs

    async def fetch_first_matching_endpoint(
        self,
        *,
        explicit_url: str | None,
        candidates: tuple[str, ...],
        expected_keys: tuple[str, ...],
        raw_filename: str,
        label: str,
    ) -> tuple[str | None, dict[str, Any] | list[Any] | None, list[dict[str, Any]]]:
        urls = (explicit_url,) if explicit_url else candidates

        for url in urls:
            if not url:
                continue

            print(f"Trying {label} endpoint: {url}")

            response = await self.get(
                url,
                allow_not_found=explicit_url is None,
                retries=2 if explicit_url is None else 5,
            )

            if response is None:
                continue

            try:
                data = response.json()
            except ValueError:
                print(f"  Skipping: response is not JSON.")
                continue

            rows = extract_list(data, expected_keys)
            if rows is None:
                print(
                    f"  Skipping: JSON did not contain any of "
                    f"{', '.join(expected_keys)}."
                )
                continue

            dump_json(self.raw_dir / raw_filename, data)
            print(f"Using {label} endpoint: {url}")
            return url, data, rows

        return None, None, []

    async def fetch_faq_categories(self) -> list[dict[str, Any]]:
        print("\nFetching FAQ categories...")

        url, _data, categories = await self.fetch_first_matching_endpoint(
            explicit_url=self.faq_categories_url,
            candidates=FAQ_CATEGORY_CANDIDATES,
            expected_keys=("cats", "categories", "faq_categories"),
            raw_filename="faq_categories_response.json",
            label="FAQ categories",
        )

        if not url:
            print(
                "WARNING: No public FAQ-category endpoint was detected. "
                "Use --faq-categories-url if Rasa has changed the route."
            )
            dump_json(self.output / "faq_categories.json", {"cats": []})
            return []

        dump_json(self.output / "faq_categories.json", {"cats": categories})

        for category in categories:
            dump_json(
                self.faq_category_dir / object_filename(category, "faq_category"),
                category,
            )

        print(f"Found {len(categories)} FAQ categories.")
        return categories

    async def fetch_faqs(self) -> list[dict[str, Any]]:
        print("\nFetching FAQs...")

        url, data, first_rows = await self.fetch_first_matching_endpoint(
            explicit_url=self.faq_url,
            candidates=FAQ_CANDIDATES,
            expected_keys=("faqs", "faq"),
            raw_filename="faq_page_00001.json",
            label="FAQ",
        )

        if not url or data is None:
            print(
                "WARNING: No public FAQ API endpoint was detected. "
                "Use --faq-url if Rasa has changed the route."
            )
            dump_json(self.output / "faqs.json", {"faqs": []})
            return []

        all_faqs = list(first_rows)

        # Some versions may paginate FAQs just like programs.
        if isinstance(data, dict):
            total = data.get("total")
            page = data.get("page")
            limit = data.get("limit")

            if (
                isinstance(total, int)
                and isinstance(page, int)
                and isinstance(limit, int)
                and limit > 0
            ):
                pages = max(1, (total + limit - 1) // limit)

                for current_page in range(page + 1, pages + 1):
                    print(f"Fetching FAQ page {current_page}/{pages}...")

                    response = await self.get(
                        url,
                        params={"page": current_page, "limit": limit},
                    )
                    assert response is not None
                    page_data = response.json()

                    dump_json(
                        self.raw_dir / f"faq_page_{current_page:05d}.json",
                        page_data,
                    )

                    rows = extract_list(page_data, ("faqs", "faq"))
                    if not rows:
                        break

                    all_faqs.extend(rows)

        deduplicated: dict[Any, dict[str, Any]] = {}
        anonymous_index = 0

        for faq in all_faqs:
            key = faq.get("id")
            if key is None:
                anonymous_index += 1
                key = f"anonymous-{anonymous_index}"
            deduplicated[key] = faq

        faqs = list(deduplicated.values())

        dump_json(self.output / "faqs.json", {"faqs": faqs})

        for faq in faqs:
            dump_json(
                self.faq_dir / object_filename(faq, "faq"),
                faq,
            )

        print(f"Found {len(faqs)} FAQs.")
        return faqs

    def collect_assets(
        self,
        datasets: dict[str, list[dict[str, Any]]],
    ) -> dict[str, dict[str, Any]]:
        print("\nDiscovering assets...")

        result: dict[str, dict[str, Any]] = {}

        for object_type, items in datasets.items():
            for item in items:
                object_id = item.get("id")
                slug = item.get("slug") or item.get("key")

                for discovered in discover_assets(item):
                    url = discovered["url"]

                    record = result.setdefault(
                        url,
                        {
                            "url": url,
                            "references": [],
                        },
                    )

                    record["references"].append(
                        {
                            "object_type": object_type,
                            "object_id": object_id,
                            "slug": slug,
                            "source_field": discovered["source_field"],
                            "json_path": discovered["json_path"],
                        }
                    )

        print(f"Discovered {len(result)} unique assets.")
        return result

    def local_asset_path(
        self,
        url: str,
        content_type: str | None = None,
    ) -> Path:
        parsed = urlparse(url)
        url_path = unquote(parsed.path)

        parts = [
            safe_filename(part)
            for part in PurePosixPath(url_path).parts
            if part not in {"", "/"}
        ]

        if not parts:
            digest = hashlib.sha256(url.encode()).hexdigest()[:16]
            parts = [digest]

        filename = parts[-1]

        if "." not in filename and content_type:
            mime = content_type.split(";")[0].strip()
            extension = mimetypes.guess_extension(mime)
            if extension:
                filename += extension
                parts[-1] = filename

        if parsed.query:
            digest = hashlib.sha256(parsed.query.encode()).hexdigest()[:10]
            path = Path(parts[-1])
            parts[-1] = f"{path.stem}_{digest}{path.suffix}"

        return self.asset_dir.joinpath(*parts)

    async def download_asset(
        self,
        url: str,
        info: dict[str, Any],
    ) -> None:
        async with self.semaphore:
            try:
                response = await self.get(url, retries=4)
                assert response is not None

                content_type = response.headers.get("content-type", "")

                if "text/html" in content_type.lower():
                    info["status"] = "skipped_html"
                    print(f"Skipping HTML asset candidate: {url}")
                    return

                local_path = self.local_asset_path(url, content_type)
                local_path.parent.mkdir(parents=True, exist_ok=True)

                if local_path.exists():
                    existing_size = local_path.stat().st_size
                    if existing_size == len(response.content):
                        info.update(
                            {
                                "status": "existing",
                                "local_path": str(local_path.relative_to(self.output)),
                                "content_type": content_type,
                                "size": existing_size,
                            }
                        )
                        return

                local_path.write_bytes(response.content)

                info.update(
                    {
                        "status": "downloaded",
                        "local_path": str(local_path.relative_to(self.output)),
                        "content_type": content_type,
                        "size": len(response.content),
                        "sha256": hashlib.sha256(response.content).hexdigest(),
                    }
                )

                print(f"Downloaded: {local_path.relative_to(self.output)}")

            except Exception as exc:
                info["status"] = "failed"
                info["error"] = str(exc)
                print(f"FAILED asset: {url}\n  {exc}")

    async def download_assets(
        self,
        assets: dict[str, dict[str, Any]],
    ) -> None:
        dump_json(
            self.output / "assets_discovered.json",
            list(assets.values()),
        )

        if not self.should_download_assets:
            print("\nAsset download disabled (--skip-assets).")
            return

        print("\nDownloading assets...")

        await asyncio.gather(
            *(self.download_asset(url, info) for url, info in assets.items())
        )

        manifest = list(assets.values())
        dump_json(self.output / "assets_manifest.json", manifest)

        downloaded = sum(
            1
            for item in manifest
            if item.get("status") in {"downloaded", "existing"}
        )
        failed = sum(1 for item in manifest if item.get("status") == "failed")

        print(f"Assets available locally: {downloaded}")
        if failed:
            print(f"Failed assets: {failed}")

    async def run(self) -> None:
        self.output.mkdir(parents=True, exist_ok=True)

        universities = await self.fetch_universities()
        programs = await self.fetch_all_programs()
        faq_categories = await self.fetch_faq_categories()
        faqs = await self.fetch_faqs()

        datasets = {
            "university": universities,
            "program": programs,
            "faq_category": faq_categories,
            "faq": faqs,
        }

        assets = self.collect_assets(datasets)
        await self.download_assets(assets)

        summary = {
            "source": BASE_URL,
            "universities": len(universities),
            "programs": len(programs),
            "faq_categories": len(faq_categories),
            "faqs": len(faqs),
            "assets_discovered": len(assets),
        }
        dump_json(self.output / "summary.json", summary)

        print("\n" + "=" * 72)
        print("COMPLETE")
        print("=" * 72)
        print(f"Universities   : {len(universities)}")
        print(f"Programs       : {len(programs)}")
        print(f"FAQ categories : {len(faq_categories)}")
        print(f"FAQs           : {len(faqs)}")
        print(f"Assets         : {len(assets)}")
        print(f"Output         : {self.output.resolve()}")


async def async_main(args: argparse.Namespace) -> None:
    downloader = RasaDownloader(
        output=Path(args.output),
        limit=args.limit,
        delay=args.delay,
        concurrency=args.concurrency,
        faq_url=args.faq_url,
        faq_categories_url=args.faq_categories_url,
        download_assets=not args.skip_assets,
    )

    try:
        await downloader.run()
    finally:
        await downloader.close()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default="data/rasa",
        help="Output directory (default: data/rasa)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Programs per API request (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay after requests in seconds (default: {DEFAULT_DELAY})",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Concurrent asset downloads (default: {DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--faq-url",
        help="Explicit FAQ API URL. Normally auto-detected.",
    )
    parser.add_argument(
        "--faq-categories-url",
        help="Explicit FAQ-category API URL. Normally auto-detected.",
    )
    parser.add_argument(
        "--skip-assets",
        action="store_true",
        help="Fetch JSON data but do not download referenced assets.",
    )

    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
