# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/slu_web_scraper.py
Target Sources:
  1. https://www.facebook.com/profile.php?id=61563510362403 (SLU Freedom Wall — via local HTML dump or HTTP)
  2. https://www.slu.edu.ph/registrars-office-services/ (Official SLU URO Static Pages)
  3. https://dataprotection.slu.edu.ph/guidelines-on-social-media-and-digital-platforms/ (SLU Data Privacy)
Description: Automated web scraper and HTML parser for extracting public SLU student
             community posts (#SLUFreedomWall) and static institutional SLU pages.
             Zero-dependency stdlib fallback with optional BeautifulSoup4 support.
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
Instructor: Prof. Dalos D. Miguel
"""

import os
import re
import argparse
import urllib.request
import urllib.error
from html.parser import HTMLParser

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

TARGET_URL = "https://www.facebook.com/profile.php?id=61563510362403"
ALLOWED_SLU_DOMAINS = (
    "https://www.slu.edu.ph/",
    "https://slu.edu.ph/",
    "https://dataprotection.slu.edu.ph/",
    "https://www.facebook.com/",
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)


def find_default_output():
    candidates = [
        os.path.join(REPO_ROOT, "data", "raw_midterm", "slu_community_inquiries_raw.txt"),
        os.path.join(REPO_ROOT, "data", "slu_community_inquiries_raw.txt"),
        "slu_community_inquiries_raw.txt",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]


class SimpleTextExtractor(HTMLParser):
    """Lightweight stdlib HTML text extractor ignoring script and style blocks."""

    def __init__(self):
        super().__init__()
        self.chunks = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("script", "style", "noscript"):
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style", "noscript") and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self.chunks.append(text)

    def get_text(self):
        return " ".join(self.chunks)


def parse_freedom_wall_html(html_content):
    """Extracts unique #SLUFreedomWall posts from HTML markup."""
    posts = []
    if HAS_BS4:
        soup = BeautifulSoup(html_content, "html.parser")
        post_tag_nodes = soup.find_all(string=re.compile(r"#SLUFreedomWall\d+"))
        for node in post_tag_nodes:
            container = (
                node.find_parent("article")
                or node.find_parent("div", role="article")
                or node.find_parent(
                    "div",
                    class_=re.compile(r"userContentWrapper|story_body_container|x1y1aw1k"),
                )
                or (node.parent.parent if node.parent else None)
            )
            full_text = container.get_text(separator=" ").strip() if container else str(node).strip()
            full_text = re.sub(r"\s+", " ", full_text)
            if full_text and full_text not in posts:
                posts.append(full_text)
    else:
        extractor = SimpleTextExtractor()
        extractor.feed(html_content)
        full_text = extractor.get_text()
        matches = re.split(r"(?=#SLUFreedomWall\d+)", full_text)
        for chunk in matches:
            if chunk.startswith("#SLUFreedomWall"):
                post_content = re.sub(r"\s+", " ", chunk.strip())
                if len(post_content) > 15 and post_content not in posts:
                    posts.append(post_content)
    return posts


def parse_static_slu_page(html_content):
    """Extracts clean paragraph blocks from static SLU official web pages."""
    if HAS_BS4:
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        paragraphs = [
            re.sub(r"\s+", " ", el.get_text(separator=" ").strip())
            for el in soup.find_all(["p", "li", "h2", "h3"])
        ]
        return [p for p in paragraphs if len(p) > 25]

    extractor = SimpleTextExtractor()
    extractor.feed(html_content)
    text = extractor.get_text()
    sentences = [s.strip() for s in re.split(r"(?<=[\.\?\!])\s+", text) if len(s.strip()) > 25]
    return sentences


def append_unique_posts(new_posts, output_path):
    """Appends newly discovered posts to output_path while avoiding duplicate post IDs."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    existing_content = ""
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8-sig") as f:
            existing_content = f.read()

    existing_ids = set(re.findall(r"#SLUFreedomWall\d+", existing_content))
    added_count = 0

    with open(output_path, "a", encoding="utf-8") as f:
        for post in new_posts:
            found_ids = re.findall(r"#SLUFreedomWall\d+", post)
            if found_ids:
                post_id = found_ids[0]
                if post_id not in existing_ids:
                    f.write(f"\n[{post_id}] (Public Post Archive):\n{post}\n")
                    existing_ids.add(post_id)
                    added_count += 1
            else:
                snippet = post[:60]
                if snippet not in existing_content:
                    f.write(f"\n[#SLUFreedomWall_Post]\n{post}\n")
                    existing_content += snippet
                    added_count += 1

    return added_count


def scrape_from_file(file_path, output_path=None):
    if output_path is None:
        output_path = find_default_output()
    print(f"[*] Reading local HTML dump: {file_path}")
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return 0

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    posts = parse_freedom_wall_html(content)
    print(f"[OK] Extracted {len(posts)} posts from {file_path}")
    added = append_unique_posts(posts, output_path)
    print(f"[OK] Appended {added} new unique posts to {output_path}")
    return len(posts)


def scrape_slu_freedom_wall(target_url=TARGET_URL, output_path=None, session_cookie=None, offline=False):
    if output_path is None:
        output_path = find_default_output()

    if not offline:
        if not target_url.startswith(ALLOWED_SLU_DOMAINS):
            raise ValueError(f"URL not in allowlisted SLU/Freedom Wall domains: {target_url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9,fil;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        if session_cookie:
            headers["Cookie"] = session_cookie

        print(f"[*] Checking endpoint accessibility: {target_url}")
        req = urllib.request.Request(target_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                html = response.read().decode("utf-8", errors="ignore")
                extracted = parse_freedom_wall_html(html)
                if extracted:
                    added = append_unique_posts(extracted, output_path)
                    print(f"[OK] Extracted {len(extracted)} posts ({added} new) from web endpoint.")
                else:
                    print("[i] Endpoint returned JS-rendered shell; use --html with a saved page dump.")
        except urllib.error.HTTPError as exc:
            print(f"[!] HTTP status {exc.code} ({exc.reason})")
        except Exception as exc:
            print(f"[!] Network notice: {exc}")

    local_dump = os.path.join(REPO_ROOT, "slu_freedom_wall.html")
    if os.path.exists(local_dump):
        scrape_from_file(local_dump, output_path)

    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8-sig") as f:
            real_data = f.read()
        posts = re.findall(r"\[#SLUFreedomWall\d+\]", real_data)
        print(f"[OK] Verified {len(posts)} authentic #SLUFreedomWall posts in {os.path.basename(output_path)}:")
        for pid in posts:
            print(f"    - {pid}")
        return len(posts)

    print(f"[!] Raw data file not found at {output_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="SLU Freedom Wall & Official Page Scraper/Parser")
    parser.add_argument("--url", default=TARGET_URL, help="Allowlisted SLU/Freedom Wall URL")
    parser.add_argument("--html", help="Path to locally saved Facebook HTML dump")
    parser.add_argument("--cookie", help="Optional authenticated session cookie")
    parser.add_argument("--out", default=None, help="Output path for raw text corpus")
    parser.add_argument("--verify-only", action="store_true", help="Verify local raw corpus without network calls")
    args = parser.parse_args()

    if args.html:
        scrape_from_file(args.html, args.out)
    else:
        scrape_slu_freedom_wall(
            target_url=args.url,
            output_path=args.out,
            session_cookie=args.cookie,
            offline=args.verify_only,
        )


if __name__ == "__main__":
    main()
