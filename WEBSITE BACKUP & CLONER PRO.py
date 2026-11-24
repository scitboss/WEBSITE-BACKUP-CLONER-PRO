#!/usr/bin/env python3
"""
================================================================================
SCITBOSS WEBSITE BACKUP & CLONER PRO (FULL PRODUCTION EDITION)
================================================================================
Developer: SCITBOSS
GitHub:    https://github.com/scitboss
Version:   2.0.0 Pro Full Edition
Platform:  Windows 10 / Windows 11 (Python 3.8+ & Tkinter)

A complete, production-grade desktop application for deep crawling, backing up,
and creating static offline clones of any website. Supports full website cloning,
lazy-loaded media handling, automated ZIP archive bundling, multi-threaded asset
downloading, and offline link rewriting.

PROJECT CREDIT:
DEVELOP BY SCITBOSS
GITHUB: HTTPS://GITHUB.COM/SCITBOSS
================================================================================
"""

import sys
import os
import re
import json
import time
import datetime
import threading
import queue
import hashlib
import shutil
import socket
import ssl
import gzip
import zlib
import zipfile
import urllib.request
import urllib.parse
import urllib.error
import urllib.robotparser
import webbrowser
import collections
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed

# GUI Imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont

# Windows High-DPI and Dark Mode Title Bar
IS_WINDOWS = sys.platform.startswith('win')
if IS_WINDOWS:
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# ==============================================================================
# CONSTANTS & THEME PALETTE
# ==============================================================================

APP_NAME = "SCITBOSS WEBSITE BACKUP & CLONER PRO"
APP_VERSION = "2.0.0 Pro Full Edition"
DEVELOPER_CREDIT = "DEVELOP BY SCITBOSS"
GITHUB_URL = "https://github.com/scitboss"

# Modern Dark Theme Colors
COLOR_BG_DARK = "#090d16"         # Main window background
COLOR_SIDEBAR = "#0f172a"         # Navigation sidebar background
COLOR_CARD = "#1e293b"            # Content card background
COLOR_CARD_BORDER = "#334155"     # Card border
COLOR_INPUT_BG = "#0b1120"        # Input fields and log background
COLOR_INPUT_BORDER = "#3b475e"    # Border for input elements

# Typography Colors
COLOR_TEXT_WHITE = "#f8fafc"      # Primary text
COLOR_TEXT_MUTED = "#94a3b8"      # Secondary text
COLOR_TEXT_DIM = "#64748b"        # Dim text / timestamps

# Accent Colors
COLOR_BLUE = "#3b82f6"            # Primary brand blue
COLOR_BLUE_HOVER = "#2563eb"
COLOR_BLUE_ACTIVE = "#1d4ed8"

COLOR_ORANGE = "#f97316"          # Vibrant clone orange
COLOR_ORANGE_HOVER = "#ea580c"
COLOR_ORANGE_ACTIVE = "#c2410c"

COLOR_GREEN = "#10b981"           # Success emerald
COLOR_GREEN_HOVER = "#059669"
COLOR_GREEN_ACTIVE = "#047857"

COLOR_RED = "#ef4444"             # Danger/Stop rose
COLOR_RED_HOVER = "#dc2626"
COLOR_RED_ACTIVE = "#b91c1c"

COLOR_CYAN = "#06b6d4"
COLOR_PURPLE = "#a855f7"

# Windows reserved filename names
WINDOWS_RESERVED = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

# User-Agent Presets
USER_AGENTS = {
    "Chrome 131 on Windows 11 (Recommended)": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Edge 131 on Windows 11": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    ),
    "Firefox 133 on Windows 11": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
    ),
    "SCITBOSS Bot 2.0": "SCITBOSS-BackupCloner/2.0 (+https://github.com/scitboss)",
}


# ==============================================================================
# SETTINGS & CONFIGURATION MANAGER
# ==============================================================================

class AppConfig:
    """Manages application settings with persistent JSON storage."""

    DEFAULT_SETTINGS = {
        "max_pages": 500,                  # Production default for complete site copy
        "max_depth": 8,                    # Deep crawl depth
        "unlimited_crawl": False,          # Toggle to crawl all discovered pages
        "request_delay": 0.05,             # Fast politeness delay
        "timeout": 20,                     # Robust connection timeout
        "max_file_size_mb": 150,           # High file size limit (150MB)
        "thread_workers": 6,               # Parallel download threads
        "auto_create_zip": True,           # Automatically generate full ZIP archive
        "download_images": True,
        "download_css": True,
        "download_js": True,
        "download_fonts": True,
        "download_docs": True,
        "download_media": True,
        "include_subdomains": False,
        "preserve_structure": True,
        "respect_robots_txt": False,       # Allow full archiving without artificial blocks
        "ignore_ssl_errors": True,         # Automatically handle self-signed or legacy SSL
        "rewrite_links": True,             # Local relative link conversion
        "mirror_external_assets": True,    # Mirror CDNs locally for 100% offline viewing
        "user_agent_preset": "Chrome 131 on Windows 11 (Recommended)",
        "custom_user_agent": "",
        "download_dir": str(Path.home() / "Downloads" / "SCITBOSS_Backups"),
    }

    def __init__(self):
        self.config_dir = Path.home() / ".scitboss_backup_cloner"
        self.config_file = self.config_dir / "config.json"
        self.settings = dict(self.DEFAULT_SETTINGS)
        self.load()

    def load(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.settings.update(saved)
        except Exception as e:
            print(f"[Config] Error loading settings: {e}")

    def save(self):
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[Config] Error saving settings: {e}")

    def reset_defaults(self):
        self.settings = dict(self.DEFAULT_SETTINGS)
        self.save()

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    def get_effective_user_agent(self):
        preset = self.settings.get("user_agent_preset", "")
        custom = self.settings.get("custom_user_agent", "").strip()
        if custom:
            return custom
        return USER_AGENTS.get(preset, USER_AGENTS["Chrome 131 on Windows 11 (Recommended)"])


# ==============================================================================
# BACKUP HISTORY MANAGER
# ==============================================================================

class HistoryManager:
    """Stores and retrieves backup and clone project history in a local JSON file."""

    def __init__(self):
        self.history_dir = Path.home() / ".scitboss_backup_cloner"
        self.history_file = self.history_dir / "backup_history.json"
        self.items = []
        self.load()

    def load(self):
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
            else:
                self.items = []
        except Exception as e:
            print(f"[History] Error loading history: {e}")
            self.items = []

    def save(self):
        try:
            self.history_dir.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=4)
        except Exception as e:
            print(f"[History] Error saving history: {e}")

    def add_entry(self, entry):
        self.items.insert(0, entry)
        if len(self.items) > 150:
            self.items = self.items[:150]
        self.save()

    def delete_entry(self, entry_id):
        self.items = [item for item in self.items if item.get("id") != entry_id]
        self.save()

    def clear_all(self):
        self.items = []
        self.save()


# ==============================================================================
# UTILITIES: URL, FILE SYSTEM & DECOMPRESSION
# ==============================================================================

def validate_and_normalize_url(url_text):
    """
    Validates user input URL and ensures proper scheme and hostname.
    Returns (is_valid, normalized_url, error_message).
    """
    url_text = url_text.strip()
    if not url_text:
        return False, "", "Website URL cannot be empty."

    # Automatically add https:// if scheme is missing
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', url_text):
        url_text = "https://" + url_text

    try:
        parsed = urllib.parse.urlparse(url_text)
        if parsed.scheme.lower() not in ("http", "https"):
            return False, "", "Only HTTP and HTTPS protocols are supported."

        netloc = parsed.netloc.strip()
        if not netloc:
            return False, "", "Invalid URL: Host domain is missing."

        host = netloc.split(':')[0]
        if host != "localhost" and not re.match(r'^[a-zA-Z0-9.\-]+$', host):
            return False, "", f"Invalid characters in domain name: '{host}'"

        path = parsed.path or "/"
        clean_url = urllib.parse.urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            parsed.query,
            ""  # Strip fragment for crawling
        ))
        return True, clean_url, ""
    except Exception as e:
        return False, "", f"URL Parsing error: {str(e)}"


def sanitize_filename_segment(segment):
    """Sanitizes a single folder or file name segment for Windows filesystems."""
    clean = re.sub(r'[<>:"/\\|?*]', '_', segment)
    clean = clean.strip('. ')
    if not clean:
        clean = "item"
    if clean.upper() in WINDOWS_RESERVED:
        clean = f"_{clean}"
    if len(clean) > 120:
        clean = clean[:120]
    return clean


def format_bytes(size_bytes):
    """Formats raw bytes into readable B, KB, MB, GB strings."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def decompress_response_content(raw_bytes, content_encoding=""):
    """
    Decompresses HTTP response body if gzipped, deflated, or raw compressed.
    Crucial for modern servers (Cloudflare, Nginx, Apache) that return compressed responses.
    """
    if not raw_bytes:
        return raw_bytes

    enc = (content_encoding or "").lower().strip()

    # Check gzip magic bytes (0x1f 0x8b) or gzip header
    if "gzip" in enc or raw_bytes[:2] == b'\x1f\x8b':
        try:
            return gzip.decompress(raw_bytes)
        except Exception:
            pass

    # Check deflate
    if "deflate" in enc:
        try:
            return zlib.decompress(raw_bytes)
        except Exception:
            try:
                return zlib.decompress(raw_bytes, -zlib.MAX_WBITS)
            except Exception:
                pass

    return raw_bytes


def create_zip_archive(source_dir, output_zip_path):
    """
    Recursively compresses the entire cloned/backup folder into a portable .zip archive.
    """
    source_path = Path(source_dir).resolve()
    zip_path = Path(output_zip_path).resolve()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            for file in files:
                abs_file = Path(root) / file
                # Do not zip the output zip if it resides in the same directory
                if abs_file.resolve() == zip_path:
                    continue
                rel_file = abs_file.relative_to(source_path)
                zipf.write(abs_file, str(rel_file))
    return zip_path


# ==============================================================================
# HTML & CSS PARSER / ASSET EXTRACTOR
# ==============================================================================

class HTMLAssetExtractor(HTMLParser):
    """
    High-performance HTML parser using standard library html.parser.
    Extracts hyperlinks, stylesheet links, script sources, images (including lazy-loaded
    data-src/data-srcset/data-original), webfonts, media, and inline CSS blocks.
    """

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.page_links = []
        self.asset_links = []
        self.inline_css = []
        self._in_style_tag = False
        self._current_style_text = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        tag = tag.lower()

        # Page navigation links: <a>, <area>
        if tag in ('a', 'area'):
            href = attr_dict.get('href')
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
                full_url = urllib.parse.urljoin(self.base_url, href.strip())
                self.page_links.append(full_url)

        # Stylesheets, icons, favicons, manifests, webfonts
        elif tag == 'link':
            href = attr_dict.get('href')
            if href and not href.startswith(('data:', 'javascript:', 'mailto:', 'tel:')):
                full_url = urllib.parse.urljoin(self.base_url, href.strip())
                self.asset_links.append(full_url)

        # Scripts (regular and modules)
        elif tag == 'script':
            src = attr_dict.get('src')
            if src and not src.startswith(('data:', 'javascript:')):
                full_url = urllib.parse.urljoin(self.base_url, src.strip())
                self.asset_links.append(full_url)

        # Images & Media (Standard + Lazy-loaded attributes)
        elif tag in ('img', 'source', 'video', 'audio', 'iframe', 'embed', 'object', 'track', 'image'):
            # Check standard sources
            src_candidates = [
                attr_dict.get('src'),
                attr_dict.get('data-src'),
                attr_dict.get('data-original'),
                attr_dict.get('data-lazy-src'),
                attr_dict.get('data-high-res-src'),
                attr_dict.get('data-fallback-src'),
                attr_dict.get('poster'),
                attr_dict.get('data'),
                attr_dict.get('href'),       # SVG <image href="...">
                attr_dict.get('xlink:href'),
            ]
            for candidate in src_candidates:
                if candidate and not candidate.startswith(('data:', 'javascript:')):
                    full_url = urllib.parse.urljoin(self.base_url, candidate.strip())
                    self.asset_links.append(full_url)

            # Responsive srcset + lazy srcset
            for s_attr in ('srcset', 'data-srcset', 'data-lazy-srcset'):
                srcset_val = attr_dict.get(s_attr)
                if srcset_val:
                    for item in srcset_val.split(','):
                        parts = item.strip().split()
                        if parts and not parts[0].startswith('data:'):
                            full_url = urllib.parse.urljoin(self.base_url, parts[0])
                            self.asset_links.append(full_url)

        # Inline style attributes: style="..."
        style_attr = attr_dict.get('style')
        if style_attr:
            self.inline_css.append(style_attr)

        # Lazy background attributes: data-bg, data-background
        for bg_attr in ('data-bg', 'data-background'):
            bg_val = attr_dict.get(bg_attr)
            if bg_val and not bg_val.startswith('data:'):
                m = re.search(r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', bg_val)
                raw_u = m.group(1) if m else bg_val.strip()
                if raw_u:
                    self.asset_links.append(urllib.parse.urljoin(self.base_url, raw_u))

        # Style tags: <style>...</style>
        if tag == 'style':
            self._in_style_tag = True
            self._current_style_text = []

    def handle_endtag(self, tag):
        if tag.lower() == 'style' and self._in_style_tag:
            self._in_style_tag = False
            full_text = "".join(self._current_style_text)
            if full_text.strip():
                self.inline_css.append(full_text)

    def handle_data(self, data):
        if self._in_style_tag:
            self._current_style_text.append(data)


def extract_css_urls(css_text, base_url):
    """
    Extracts all url(...) and @import targets from CSS text.
    Handles fonts, background images, icons, and nested stylesheets.
    """
    discovered = []
    # Match url('...') or url("...") or url(...)
    url_matches = re.findall(r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', css_text, re.IGNORECASE)
    for u in url_matches:
        u_clean = u.strip()
        if u_clean and not u_clean.startswith(('data:', '#')):
            discovered.append(urllib.parse.urljoin(base_url, u_clean))

    # Match @import '...' or @import "..."
    import_matches = re.findall(r'@import\s+(?:url\s*\(\s*)?[\'"]([^\'"]+)[\'"]', css_text, re.IGNORECASE)
    for imp in import_matches:
        imp_clean = imp.strip()
        if imp_clean and not imp_clean.startswith(('data:', '#')):
            discovered.append(urllib.parse.urljoin(base_url, imp_clean))

    return discovered


# ==============================================================================
# STATIC SITE REWRITER (OFFLINE CLONING ENGINE)
# ==============================================================================

class StaticSiteRewriter:
    """
    Rewrites absolute and remote URLs in downloaded HTML and CSS files
    into relative local disk paths so the entire website can be browsed offline.
    """

    @staticmethod
    def rewrite_css(css_text, css_url, url_to_relpath, output_css_relpath):
        """Rewrites url(...) and @import statements in CSS files to relative paths."""
        css_dir = os.path.dirname(output_css_relpath)

        def replace_url_call(match):
            prefix = match.group(1)   # e.g. 'url('
            quote = match.group(2)    # e.g. "'" or '"' or ''
            raw_url = match.group(3).strip()
            suffix = match.group(4)   # e.g. ')'

            if raw_url.startswith(('data:', '#')):
                return match.group(0)

            abs_url = urllib.parse.urljoin(css_url, raw_url)
            clean_abs = abs_url.split('#')[0]

            target_rel = url_to_relpath.get(clean_abs) or url_to_relpath.get(abs_url)
            if target_rel:
                rel_to_asset = os.path.relpath(target_rel, css_dir).replace('\\', '/')
                return f"{prefix}{quote}{rel_to_asset}{quote}{suffix}"
            return match.group(0)

        pattern = re.compile(r'(\burl\s*\(\s*)([\'"]?)([^\'")]+)\2(\s*\))', re.IGNORECASE)
        res = pattern.sub(replace_url_call, css_text)

        # Rewrite @import
        import_pattern = re.compile(r'(@import\s+(?:url\s*\(\s*)?)([\'"])([^\'"]+)([\'"])(\s*\)?)', re.IGNORECASE)
        def replace_import(m):
            raw_url = m.group(3).strip()
            abs_url = urllib.parse.urljoin(css_url, raw_url)
            clean_abs = abs_url.split('#')[0]
            target_rel = url_to_relpath.get(clean_abs) or url_to_relpath.get(abs_url)
            if target_rel:
                rel_to_asset = os.path.relpath(target_rel, css_dir).replace('\\', '/')
                return f"{m.group(1)}{m.group(2)}{rel_to_asset}{m.group(4)}{m.group(5)}"
            return m.group(0)

        return import_pattern.sub(replace_import, res)

    @staticmethod
    def rewrite_html(html_text, page_url, url_to_relpath, output_page_relpath):
        """
        Rewrites HTML tag attributes (href, src, data-src, poster, srcset, inline CSS)
        to relative local file paths.
        """
        page_dir = os.path.dirname(output_page_relpath)

        def get_local_relative(raw_val):
            if not raw_val or raw_val.startswith(('data:', 'javascript:', 'mailto:', 'tel:', '#')):
                return None

            abs_url = urllib.parse.urljoin(page_url, raw_val)
            clean_abs = abs_url.split('#')[0]
            fragment = abs_url.split('#')[1] if '#' in abs_url else ''

            target_rel = url_to_relpath.get(clean_abs) or url_to_relpath.get(abs_url)
            if target_rel:
                rel_path = os.path.relpath(target_rel, page_dir).replace('\\', '/')
                if fragment:
                    rel_path += f"#{fragment}"
                return rel_path
            return None

        # 1. Replace attributes: href, src, data-src, data-original, poster, data
        attr_regex = re.compile(
            r'(<(?:a|link|script|img|source|video|audio|iframe|embed|object|track|image)\b[^>]*?\b(?:href|src|data-src|data-original|data-lazy-src|poster|data)\s*=\s*)(["\'])(.*?)\2',
            re.IGNORECASE | re.DOTALL
        )
        def repl_attr(m):
            prefix = m.group(1)
            quote = m.group(2)
            val = m.group(3)
            local_rel = get_local_relative(val)
            if local_rel:
                return f"{prefix}{quote}{local_rel}{quote}"
            return m.group(0)

        res = attr_regex.sub(repl_attr, html_text)

        # 2. For lazy-loaded images, if data-src was rewritten, ensure src also points to the local asset
        lazy_img_regex = re.compile(
            r'(<img\b[^>]*?\b(?:data-src|data-original)\s*=\s*["\']([^"\']+)["\'][^>]*?)>',
            re.IGNORECASE | re.DOTALL
        )
        def fix_lazy_img(m):
            tag_content = m.group(1)
            local_target = m.group(2)
            if 'src=' in tag_content:
                fixed = re.sub(r'\bsrc\s*=\s*["\'][^"\']*["\']', f'src="{local_target}"', tag_content)
                return f"{fixed}>"
            else:
                return f'{tag_content} src="{local_target}">'

        res = lazy_img_regex.sub(fix_lazy_img, res)

        # 3. Replace srcset & data-srcset
        srcset_regex = re.compile(r'(\b(?:srcset|data-srcset)\s*=\s*)(["\'])(.*?)\2', re.IGNORECASE | re.DOTALL)
        def repl_srcset(m):
            prefix = m.group(1)
            quote = m.group(2)
            val = m.group(3)
            parts = val.split(',')
            new_parts = []
            for p in parts:
                p_strip = p.strip()
                tokens = p_strip.split(None, 1)
                if tokens:
                    sub_url = tokens[0]
                    local_rel = get_local_relative(sub_url)
                    if local_rel:
                        descriptor = f" {tokens[1]}" if len(tokens) > 1 else ""
                        new_parts.append(f"{local_rel}{descriptor}")
                    else:
                        new_parts.append(p_strip)
                else:
                    new_parts.append(p_strip)
            return f"{prefix}{quote}{', '.join(new_parts)}{quote}"

        res = srcset_regex.sub(repl_srcset, res)

        # 4. Replace inline style="..."
        style_attr_regex = re.compile(r'(\bstyle\s*=\s*)(["\'])(.*?)\2', re.IGNORECASE | re.DOTALL)
        def repl_style_attr(m):
            prefix = m.group(1)
            quote = m.group(2)
            val = m.group(3)
            rewritten_css = StaticSiteRewriter.rewrite_css(val, page_url, url_to_relpath, output_page_relpath)
            return f"{prefix}{quote}{rewritten_css}{quote}"

        res = style_attr_regex.sub(repl_style_attr, res)

        # 5. Replace <style>...</style> blocks
        style_block_regex = re.compile(r'(<style\b[^>]*>)(.*?)(</style>)', re.IGNORECASE | re.DOTALL)
        def repl_style_block(m):
            tag_open = m.group(1)
            content = m.group(2)
            tag_close = m.group(3)
            rewritten_css = StaticSiteRewriter.rewrite_css(content, page_url, url_to_relpath, output_page_relpath)
            return f"{tag_open}{rewritten_css}{tag_close}"

        res = style_block_regex.sub(repl_style_block, res)
        return res


# ==============================================================================
# FULL PRODUCTION ENGINE (MULTI-THREADED CRAWLER & CLONER)
# ==============================================================================

class WebsiteBackupEngine:
    """
    Multi-threaded website crawling, asset downloading, offline cloning,
    and automatic ZIP bundling engine.
    """

    def __init__(self, target_url, mode="backup", config=None, callbacks=None):
        self.target_url = target_url
        self.mode = mode.lower()  # "backup" or "cloner"
        self.config = config or AppConfig()
        self.callbacks = callbacks or {}

        parsed = urllib.parse.urlparse(target_url)
        self.base_scheme = parsed.scheme.lower()
        self.base_netloc = parsed.netloc.lower()
        self.base_domain = self.base_netloc.split(':')[0]

        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        self.visited_urls = set()
        self.queued_urls = set()
        self.discovered_assets = set()
        self.downloaded_files = {}   # url -> local_abs_path
        self.url_to_relpath = {}     # url -> relative path from project root
        self.failed_downloads = []   # list of (url, reason)
        self.skipped_files = []      # list of (url, reason)

        self.pages_discovered = 0
        self.pages_downloaded = 0
        self.files_downloaded = 0
        self.bytes_downloaded = 0
        self.start_time = 0.0
        self.current_url = ""
        self.current_file = ""

        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_domain = re.sub(r'[^a-zA-Z0-9_\-]', '_', self.base_domain)
        folder_prefix = "Clone_" if self.mode == "cloner" else "Backup_"
        self.project_dir_name = f"{folder_prefix}{safe_domain}_{timestamp_str}"
        base_dir = Path(self.config.get("download_dir"))
        self.project_dir = base_dir / self.project_dir_name
        self.zip_file_path = base_dir / f"{self.project_dir_name}_FULL.zip"

        self.robot_parser = None
        if self.config.get("respect_robots_txt"):
            self._init_robots_txt()

    def _init_robots_txt(self):
        try:
            robots_url = f"{self.base_scheme}://{self.base_netloc}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.robot_parser = rp
            self._log(f"Parsed robots.txt from {robots_url}", "INFO")
        except Exception:
            self.robot_parser = None

    def _can_fetch(self, url):
        if self.robot_parser:
            try:
                ua = self.config.get_effective_user_agent()
                return self.robot_parser.can_fetch(ua, url)
            except Exception:
                return True
        return True

    def _log(self, message, level="INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if "on_log" in self.callbacks:
            self.callbacks["on_log"](ts, level, message)

    def _update_progress(self):
        with self._lock:
            elapsed = max(0.001, time.time() - self.start_time)
            speed = self.bytes_downloaded / elapsed

            stats = {
                "target_url": self.target_url,
                "current_url": self.current_url,
                "current_file": self.current_file,
                "pages_discovered": self.pages_discovered,
                "pages_downloaded": self.pages_downloaded,
                "files_downloaded": self.files_downloaded,
                "bytes_downloaded": self.bytes_downloaded,
                "bytes_formatted": format_bytes(self.bytes_downloaded),
                "speed_bps": speed,
                "speed_formatted": f"{format_bytes(int(speed))}/s",
                "elapsed_seconds": int(elapsed),
                "failed_count": len(self.failed_downloads),
                "skipped_count": len(self.skipped_files),
            }
        if "on_progress" in self.callbacks:
            self.callbacks["on_progress"](stats)

    def is_in_scope(self, url):
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc.lower().split(':')[0]
            if not host:
                return False
            if host == self.base_domain:
                return True
            if self.config.get("include_subdomains"):
                if host.endswith('.' + self.base_domain):
                    return True
            return False
        except Exception:
            return False

    def categorize_asset(self, url, content_type=""):
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower()
        ext = os.path.splitext(path)[1]

        # Images
        if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico', '.bmp', '.avif', '.tiff', '.jfif') or 'image/' in content_type:
            return "image", self.config.get("download_images")

        # CSS
        if ext == '.css' or 'text/css' in content_type:
            return "css", self.config.get("download_css")

        # JS
        if ext in ('.js', '.mjs', '.cjs') or 'javascript' in content_type:
            return "js", self.config.get("download_js")

        # Fonts
        if ext in ('.woff', '.woff2', '.ttf', '.otf', '.eot') or 'font' in content_type:
            return "font", self.config.get("download_fonts")

        # Documents
        if ext in ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.xml', '.json'):
            return "doc", self.config.get("download_docs")

        # Media
        if ext in ('.mp4', '.mp3', '.wav', '.ogg', '.webm', '.avi', '.mov', '.flac', '.m4a') or 'video/' in content_type or 'audio/' in content_type:
            return "media", self.config.get("download_media")

        # HTML
        if ext in ('.html', '.htm', '.xhtml', '.php', '.asp', '.aspx', '.jsp') or 'text/html' in content_type:
            return "html", True

        return "other", True

    def url_to_relative_path(self, url, is_html=False):
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        host = parsed.netloc.lower().split(':')[0]
        is_external = host and host != self.base_domain and not host.endswith('.' + self.base_domain)

        segments = [s for s in path.split('/') if s]

        if is_external:
            ext_segments = ['assets', 'external', sanitize_filename_segment(host)]
            for seg in segments:
                ext_segments.append(sanitize_filename_segment(seg))
            if not segments or not ('.' in segments[-1]):
                ext_segments.append('index.html' if is_html else 'asset.bin')
            rel = '/'.join(ext_segments)
        else:
            if not segments:
                rel = 'index.html'
            else:
                clean_segments = [sanitize_filename_segment(s) for s in segments]
                last_seg = clean_segments[-1]
                if path.endswith('/'):
                    clean_segments.append('index.html')
                elif is_html and '.' not in last_seg:
                    clean_segments[-1] = last_seg + '.html'
                rel = '/'.join(clean_segments)

        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode()).hexdigest()[:6]
            stem, ext = os.path.splitext(rel)
            rel = f"{stem}_{query_hash}{ext}"

        return rel

    def start(self):
        worker = threading.Thread(target=self._run, daemon=True)
        worker.start()

    def stop(self):
        self._stop_event.set()
        self._log("Cancellation requested by user. Finalizing active downloads...", "WARNING")

    def _create_ssl_context(self):
        if self.config.get("ignore_ssl_errors", True):
            ctx = ssl._create_unverified_context()
        else:
            ctx = ssl.create_default_context()
        return ctx

    def _download_resource(self, url, is_html=False, retry=2):
        """
        Downloads a single URL in chunks with gzip/deflate decompression and retry support.
        """
        if self._stop_event.is_set():
            return False, None, ""

        if not self._can_fetch(url):
            self.skipped_files.append((url, "Blocked by robots.txt"))
            self._log(f"Skipping {url} (robots.txt disallow)", "WARNING")
            return False, None, ""

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.config.get_effective_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }
        )

        ssl_ctx = self._create_ssl_context()
        timeout = self.config.get("timeout", 20)
        max_bytes = self.config.get("max_file_size_mb", 150) * 1024 * 1024

        for attempt in range(retry + 1):
            if self._stop_event.is_set():
                return False, None, ""

            try:
                with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as response:
                    content_type = response.headers.get("Content-Type", "").lower()
                    content_encoding = response.headers.get("Content-Encoding", "").lower()
                    content_length = response.headers.get("Content-Length")

                    if content_length:
                        size = int(content_length)
                        if size > max_bytes:
                            self.skipped_files.append((url, f"File exceeds size limit ({format_bytes(size)})"))
                            self._log(f"Skipping {url}: File size ({format_bytes(size)}) exceeds limit", "WARNING")
                            return False, None, content_type

                    chunks = []
                    total_read = 0
                    while not self._stop_event.is_set():
                        chunk = response.read(64 * 1024)
                        if not chunk:
                            break
                        chunks.append(chunk)
                        total_read += len(chunk)
                        with self._lock:
                            self.bytes_downloaded += len(chunk)
                        self._update_progress()

                        if total_read > max_bytes:
                            self.skipped_files.append((url, "Exceeded maximum file size during download"))
                            self._log(f"Aborting {url}: Exceeded maximum size", "WARNING")
                            return False, None, content_type

                    if self._stop_event.is_set():
                        return False, None, content_type

                    raw_content = b"".join(chunks)
                    # Decompress gzip / deflate
                    content = decompress_response_content(raw_content, content_encoding)
                    return True, content, content_type

            except urllib.error.HTTPError as e:
                if attempt == retry:
                    self.failed_downloads.append((url, f"HTTP Error {e.code}: {e.reason}"))
                    self._log(f"Failed {url} - HTTP {e.code}", "ERROR")
                    return False, None, ""
                time.sleep(0.5)

            except (urllib.error.URLError, socket.timeout, ConnectionResetError) as e:
                if attempt == retry:
                    err_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
                    self.failed_downloads.append((url, err_msg))
                    self._log(f"Failed {url} - {err_msg}", "ERROR")
                    return False, None, ""
                time.sleep(0.5)

            except Exception as e:
                if attempt == retry:
                    self.failed_downloads.append((url, str(e)))
                    self._log(f"Failed {url} - {str(e)}", "ERROR")
                    return False, None, ""
                time.sleep(0.5)

        return False, None, ""

    def _save_file(self, rel_path, data):
        dest_path = self.project_dir / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(data)
        return str(dest_path)

    def _run(self):
        self.start_time = time.time()
        self.project_dir.mkdir(parents=True, exist_ok=True)

        mode_title = "Website Static Cloner (Full Mirror)" if self.mode == "cloner" else "Website Backup Engine"
        self._log("==================================================", "INFO")
        self._log(f"Starting {mode_title}", "INFO")
        self._log(f"Target URL: {self.target_url}", "INFO")
        self._log(f"Destination: {self.project_dir}", "INFO")
        self._log("==================================================", "INFO")

        crawl_queue = collections.deque([(self.target_url, 0)])
        self.queued_urls.add(self.target_url)
        self.pages_discovered = 1

        pending_assets = set()
        downloaded_html_files = [] # list of (url, rel_path, content_str)
        downloaded_css_files = []  # list of (url, rel_path, content_str)

        unlimited_crawl = self.config.get("unlimited_crawl", False)
        max_pages = 999999 if unlimited_crawl else self.config.get("max_pages", 500)
        max_depth = 999 if unlimited_crawl else self.config.get("max_depth", 8)
        delay = self.config.get("request_delay", 0.05)

        # -------------------------------------------------------------
        # PHASE 1: Deep Crawl HTML Pages
        # -------------------------------------------------------------
        while crawl_queue and not self._stop_event.is_set():
            if self.pages_downloaded >= max_pages:
                self._log(f"Reached page limit ({max_pages}). Stopping link discovery.", "WARNING")
                break

            current_page_url, depth = crawl_queue.popleft()
            if current_page_url in self.visited_urls:
                continue

            self.visited_urls.add(current_page_url)
            self.current_url = current_page_url
            self.current_file = current_page_url
            self._log(f"Scanning Page ({self.pages_downloaded + 1}/{max_pages if not unlimited_crawl else '∞'}, depth {depth}): {current_page_url}", "INFO")
            self._update_progress()

            success, content, content_type = self._download_resource(current_page_url, is_html=True)
            if not success or content is None:
                continue

            rel_path = self.url_to_relative_path(current_page_url, is_html=True)
            self.url_to_relpath[current_page_url] = rel_path
            clean_url = current_page_url.split('#')[0]
            self.url_to_relpath[clean_url] = rel_path

            local_abs = self._save_file(rel_path, content)
            self.downloaded_files[current_page_url] = local_abs
            self.pages_downloaded += 1
            self.files_downloaded += 1
            self._log(f"Downloaded Page -> {rel_path}", "SUCCESS")
            self._update_progress()

            try:
                html_text = content.decode("utf-8", errors="replace")
                downloaded_html_files.append((current_page_url, rel_path, html_text))

                parser = HTMLAssetExtractor(current_page_url)
                parser.feed(html_text)

                if depth + 1 <= max_depth:
                    for link in parser.page_links:
                        clean_link = link.split('#')[0].rstrip('/')
                        if self.is_in_scope(link) and clean_link not in self.visited_urls and clean_link not in self.queued_urls:
                            if self.pages_discovered < max_pages:
                                self.pages_discovered += 1
                                self.queued_urls.add(clean_link)
                                crawl_queue.append((link, depth + 1))
                                self._update_progress()

                for asset in parser.asset_links:
                    if asset not in self.discovered_assets:
                        self.discovered_assets.add(asset)
                        pending_assets.add((asset, current_page_url))

                for style_chunk in parser.inline_css:
                    css_urls = extract_css_urls(style_chunk, current_page_url)
                    for cu in css_urls:
                        if cu not in self.discovered_assets:
                            self.discovered_assets.add(cu)
                            pending_assets.add((cu, current_page_url))

            except Exception as e:
                self._log(f"Error parsing HTML from {current_page_url}: {e}", "WARNING")

            if delay > 0 and not self._stop_event.is_set():
                time.sleep(delay)

        # -------------------------------------------------------------
        # PHASE 2: Multi-Threaded Asset Downloading (CSS, JS, Images, Fonts)
        # -------------------------------------------------------------
        total_assets = len(pending_assets)
        self._log(f"Discovered {total_assets} static assets. Starting parallel multi-threaded download...", "INFO")

        thread_workers = self.config.get("thread_workers", 6)
        asset_queue = list(pending_assets)
        downloaded_assets_count = 0

        def download_single_asset(asset_tuple):
            if self._stop_event.is_set():
                return None
            asset_url, parent_page = asset_tuple
            category, is_enabled = self.categorize_asset(asset_url)
            if not is_enabled:
                with self._lock:
                    self.skipped_files.append((asset_url, f"Asset type '{category}' disabled"))
                return None

            rel_path = self.url_to_relative_path(asset_url, is_html=False)
            with self._lock:
                self.url_to_relpath[asset_url] = rel_path
                self.url_to_relpath[asset_url.split('#')[0]] = rel_path
                self.current_file = asset_url

            success, content, content_type = self._download_resource(asset_url, is_html=False)
            if not success or content is None:
                return None

            local_abs = self._save_file(rel_path, content)
            with self._lock:
                self.downloaded_files[asset_url] = local_abs
                self.files_downloaded += 1

            return (asset_url, rel_path, content, content_type, category)

        nested_css_assets = set()
        with ThreadPoolExecutor(max_workers=thread_workers) as executor:
            future_to_asset = {executor.submit(download_single_asset, item): item for item in asset_queue}
            for future in as_completed(future_to_asset):
                if self._stop_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                res = future.result()
                if res:
                    a_url, a_rel, a_content, a_ctype, a_cat = res
                    downloaded_assets_count += 1
                    self._log(f"Downloaded asset ({downloaded_assets_count}/{total_assets}) -> {a_rel}", "DOWNLOAD")
                    self._update_progress()

                    if a_cat == "css" or (a_ctype and "text/css" in a_ctype):
                        try:
                            css_text = a_content.decode("utf-8", errors="replace")
                            downloaded_css_files.append((a_url, a_rel, css_text))
                            nested_urls = extract_css_urls(css_text, a_url)
                            for nu in nested_urls:
                                if nu not in self.discovered_assets:
                                    self.discovered_assets.add(nu)
                                    nested_css_assets.add((nu, a_url))
                        except Exception as e:
                            self._log(f"Error inspecting CSS {a_url}: {e}", "WARNING")

        if nested_css_assets and not self._stop_event.is_set():
            self._log(f"Downloading {len(nested_css_assets)} nested font/image assets from stylesheets...", "INFO")
            with ThreadPoolExecutor(max_workers=thread_workers) as executor:
                list(executor.map(download_single_asset, nested_css_assets))

        # -------------------------------------------------------------
        # PHASE 3: Static Link Rewriting (Website Cloner Mode)
        # -------------------------------------------------------------
        if self.mode == "cloner" and not self._stop_event.is_set():
            self._log("Rewriting hyperlinks and asset references for offline browsing...", "CLONE")

            # 1. Rewrite CSS files
            for css_url, rel_path, css_text in downloaded_css_files:
                try:
                    rewritten_css = StaticSiteRewriter.rewrite_css(
                        css_text, css_url, self.url_to_relpath, rel_path
                    )
                    dest_path = self.project_dir / rel_path
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(rewritten_css)
                except Exception as e:
                    self._log(f"Error rewriting CSS {rel_path}: {e}", "WARNING")

            # 2. Rewrite HTML files
            for page_url, rel_path, html_text in downloaded_html_files:
                try:
                    rewritten_html = StaticSiteRewriter.rewrite_html(
                        html_text, page_url, self.url_to_relpath, rel_path
                    )
                    dest_path = self.project_dir / rel_path
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(rewritten_html)
                except Exception as e:
                    self._log(f"Error rewriting HTML {rel_path}: {e}", "WARNING")

            # 3. Ensure root index.html exists
            root_index = self.project_dir / "index.html"
            if not root_index.exists() and downloaded_html_files:
                first_rel = downloaded_html_files[0][1]
                first_path = self.project_dir / first_rel
                if first_path.exists():
                    shutil.copy(first_path, root_index)
                    self._log(f"Created root index.html launcher pointing to {first_rel}", "SUCCESS")

        # -------------------------------------------------------------
        # PHASE 4: Generate Report
        # -------------------------------------------------------------
        status = "Stopped by user" if self._stop_event.is_set() else "Completed successfully"
        report_path = self._generate_report(status, str(self.zip_file_path))

        # -------------------------------------------------------------
        # PHASE 5: Automatic Full ZIP Archive Creation
        # -------------------------------------------------------------
        zip_path_str = ""
        if self.config.get("auto_create_zip", True) and not self._stop_event.is_set():
            self._log(f"Creating full ZIP archive: {self.zip_file_path.name} ...", "INFO")
            try:
                created_zip = create_zip_archive(self.project_dir, self.zip_file_path)
                zip_size = created_zip.stat().st_size
                zip_path_str = str(created_zip)
                self._log(f"Created full ZIP archive successfully! ({format_bytes(zip_size)})", "SUCCESS")
            except Exception as e:
                self._log(f"Warning: Failed to create ZIP archive: {e}", "WARNING")

        # -------------------------------------------------------------
        # PHASE 6: Finalize History & Notify
        # -------------------------------------------------------------
        history = HistoryManager()
        index_file = self.project_dir / "index.html"
        has_index = index_file.exists()

        history_entry = {
            "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "url": self.target_url,
            "mode": self.mode,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "folder": str(self.project_dir),
            "zip_file": zip_path_str,
            "index_file": str(index_file) if has_index else "",
            "total_pages": self.pages_downloaded,
            "total_files": self.files_downloaded,
            "total_size_bytes": self.bytes_downloaded,
            "total_size_formatted": format_bytes(self.bytes_downloaded),
            "status": "Completed" if not self._stop_event.is_set() else "Stopped",
            "report_file": str(report_path),
        }
        history.add_entry(history_entry)

        self._log("==================================================", "SUCCESS")
        self._log(f"Operation Finished: {status}", "SUCCESS")
        self._log(f"Total Pages Downloaded: {self.pages_downloaded}", "SUCCESS")
        self._log(f"Total Files Downloaded: {self.files_downloaded}", "SUCCESS")
        self._log(f"Total Data Downloaded: {format_bytes(self.bytes_downloaded)}", "SUCCESS")
        if zip_path_str:
            self._log(f"Full ZIP Archive: {zip_path_str}", "SUCCESS")
        self._log(f"Report Generated: {report_path}", "SUCCESS")
        self._log("==================================================", "SUCCESS")

        if "on_finished" in self.callbacks:
            self.callbacks["on_finished"](not self._stop_event.is_set(), str(report_path), history_entry)

    def _generate_report(self, status, zip_path=""):
        report_file = self.project_dir / "backup_report.txt"
        elapsed_str = str(datetime.timedelta(seconds=int(time.time() - self.start_time)))

        lines = [
            "================================================================================",
            "                   SCITBOSS WEBSITE BACKUP & CLONER PRO REPORT                  ",
            "================================================================================",
            f"Project Name:        SCITBOSS WEBSITE BACKUP & CLONER PRO",
            f"Operation Mode:      {self.mode.upper()}",
            f"Target Website URL:  {self.target_url}",
            f"Execution Date:      {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Elapsed Duration:    {elapsed_str}",
            f"Completion Status:   {status}",
            f"Backup Destination:  {self.project_dir.resolve()}",
            f"Full ZIP Archive:    {zip_path if zip_path else 'None'}",
            "--------------------------------------------------------------------------------",
            "STATISTICS SUMMARY:",
            f"  - Total Pages Discovered:    {self.pages_discovered}",
            f"  - Total Pages Downloaded:    {self.pages_downloaded}",
            f"  - Total Files Downloaded:    {self.files_downloaded}",
            f"  - Total Data Volume:         {format_bytes(self.bytes_downloaded)}",
            f"  - Failed Downloads:          {len(self.failed_downloads)}",
            f"  - Skipped Files:             {len(self.skipped_files)}",
            "--------------------------------------------------------------------------------",
            "CONFIGURATION SETTINGS USED:",
            f"  - Max Pages Limit:           {self.config.get('max_pages')}",
            f"  - Max Crawl Depth:           {self.config.get('max_depth')}",
            f"  - Unlimited Crawl:           {self.config.get('unlimited_crawl')}",
            f"  - Request Delay:             {self.config.get('request_delay')} seconds",
            f"  - Parallel Workers:          {self.config.get('thread_workers')}",
            f"  - Auto ZIP Archive:          {self.config.get('auto_create_zip')}",
            f"  - Offline Link Rewriting:    {self.mode == 'cloner'}",
            "--------------------------------------------------------------------------------",
        ]

        if self.failed_downloads:
            lines.append("FAILED DOWNLOADS:")
            for url, reason in self.failed_downloads[:50]:
                lines.append(f"  [X] {url} -> {reason}")
            if len(self.failed_downloads) > 50:
                lines.append(f"  ... and {len(self.failed_downloads) - 50} more failures.")
            lines.append("--------------------------------------------------------------------------------")

        if self.skipped_files:
            lines.append("SKIPPED FILES:")
            for url, reason in self.skipped_files[:30]:
                lines.append(f"  [-] {url} -> {reason}")
            if len(self.skipped_files) > 30:
                lines.append(f"  ... and {len(self.skipped_files) - 30} more skipped items.")
            lines.append("--------------------------------------------------------------------------------")

        lines.extend([
            "PROJECT CREDIT:",
            f"  DEVELOP BY SCITBOSS",
            f"  GITHUB: {GITHUB_URL}",
            "================================================================================",
        ])

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return report_file


# ==============================================================================
# MODERN CUSTOM GUI COMPONENTS
# ==============================================================================

class ModernButton(tk.Canvas):
    """
    Sleek, rounded modern button built on Tkinter Canvas.
    Supports antialiased-style rounded corners, gradient hover effects,
    and responsive click actions.
    """

    def __init__(self, parent, text, command=None, bg_color=COLOR_BLUE,
                 hover_color=COLOR_BLUE_HOVER, active_color=COLOR_BLUE_ACTIVE,
                 text_color=COLOR_TEXT_WHITE, width=140, height=36,
                 radius=8, font=("Segoe UI", 10, "bold"), icon=""):
        super().__init__(parent, width=width, height=height, bg=parent["bg"],
                         highlightthickness=0, cursor="hand2")
        self.text = text
        self.icon = icon
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.btn_width = width
        self.btn_height = height
        self.radius = radius
        self.font = font
        self.is_enabled = True

        self._draw_button(self.bg_color)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw_button(self, color):
        self.delete("all")
        w, h, r = self.btn_width, self.btn_height, self.radius

        points = [
            r, 0,
            w - r, 0,
            w, r,
            w, h - r,
            w - r, h,
            r, h,
            0, h - r,
            0, r
        ]
        self.create_polygon(points, fill=color, outline="", smooth=True)

        display_text = f"{self.icon} {self.text}".strip() if self.icon else self.text
        self.create_text(
            w / 2, h / 2,
            text=display_text,
            fill=self.text_color if self.is_enabled else COLOR_TEXT_DIM,
            font=self.font
        )

    def _on_enter(self, event):
        if self.is_enabled:
            self._draw_button(self.hover_color)

    def _on_leave(self, event):
        if self.is_enabled:
            self._draw_button(self.bg_color)

    def _on_press(self, event):
        if self.is_enabled:
            self._draw_button(self.active_color)

    def _on_release(self, event):
        if self.is_enabled:
            self._draw_button(self.hover_color)
            if self.command:
                self.command()

    def set_enabled(self, enabled):
        self.is_enabled = enabled
        self.config(cursor="hand2" if enabled else "arrow")
        self._draw_button(self.bg_color if enabled else COLOR_CARD_BORDER)


class MetricCard(tk.Frame):
    """Modern dashboard KPI metric card."""

    def __init__(self, parent, title, initial_value, icon="📊", accent_color=COLOR_BLUE):
        super().__init__(parent, bg=COLOR_CARD, highlightthickness=1,
                         highlightbackground=COLOR_CARD_BORDER, padx=16, pady=12)
        self.accent_color = accent_color

        top_frame = tk.Frame(self, bg=COLOR_CARD)
        top_frame.pack(fill="x", expand=True)

        lbl_title = tk.Label(top_frame, text=title.upper(), font=("Segoe UI", 8, "bold"),
                             fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
        lbl_title.pack(side="left")

        lbl_icon = tk.Label(top_frame, text=icon, font=("Segoe UI", 12),
                            fg=accent_color, bg=COLOR_CARD)
        lbl_icon.pack(side="right")

        self.lbl_value = tk.Label(self, text=initial_value, font=("Segoe UI", 16, "bold"),
                                  fg=COLOR_TEXT_WHITE, bg=COLOR_CARD)
        self.lbl_value.pack(anchor="w", pady=(6, 4))

        accent_bar = tk.Frame(self, bg=accent_color, height=3)
        accent_bar.pack(fill="x", side="bottom")

    def update_value(self, new_value):
        self.lbl_value.config(text=str(new_value))


# ==============================================================================
# MAIN APPLICATION GUI CLASS
# ==============================================================================

class ScitbossApp:
    """Main Application Controller and Tkinter Desktop Interface."""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1240x800")
        self.root.minsize(1050, 680)
        self.root.configure(bg=COLOR_BG_DARK)

        self._enable_windows_dark_titlebar()

        self.config = AppConfig()
        self.history = HistoryManager()
        self.current_engine = None
        self.is_running = False
        self.latest_history_entry = None

        self.gui_queue = queue.Queue()

        self._setup_styles()
        self._build_layout()

        self.root.after(50, self._process_gui_queue)
        self._load_app_icon()

    def _enable_windows_dark_titlebar(self):
        if IS_WINDOWS:
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                val = ctypes.c_int(1)
                res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(val), ctypes.sizeof(val)
                )
                if res != 0:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, 19, ctypes.byref(val), ctypes.sizeof(val)
                    )
            except Exception:
                pass

    def _load_app_icon(self):
        ico_path = Path("app_icon.ico")
        if ico_path.exists():
            try:
                self.root.iconbitmap(str(ico_path))
            except Exception:
                pass

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=COLOR_INPUT_BG,
            background=COLOR_BLUE,
            bordercolor=COLOR_CARD_BORDER,
            lightcolor=COLOR_BLUE,
            darkcolor=COLOR_BLUE_HOVER,
            thickness=12
        )

        style.configure(
            "Dark.Treeview",
            background=COLOR_CARD,
            foreground=COLOR_TEXT_WHITE,
            fieldbackground=COLOR_CARD,
            bordercolor=COLOR_CARD_BORDER,
            font=("Segoe UI", 9),
            rowheight=28
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", COLOR_BLUE)],
            foreground=[("selected", COLOR_TEXT_WHITE)]
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=COLOR_SIDEBAR,
            foreground=COLOR_TEXT_MUTED,
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        style.map(
            "Dark.Treeview.Heading",
            background=[("active", COLOR_CARD_BORDER)]
        )

        style.configure(
            "Dark.TCheckbutton",
            background=COLOR_CARD,
            foreground=COLOR_TEXT_WHITE,
            font=("Segoe UI", 9)
        )

    def _build_layout(self):
        self.main_container = tk.Frame(self.root, bg=COLOR_BG_DARK)
        self.main_container.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.main_container, bg=COLOR_SIDEBAR, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.right_container = tk.Frame(self.main_container, bg=COLOR_BG_DARK)
        self.right_container.pack(side="right", fill="both", expand=True)

        self._build_top_action_bar()

        self.content_area = tk.Frame(self.right_container, bg=COLOR_BG_DARK)
        self.content_area.pack(fill="both", expand=True, padx=20, pady=(10, 10))

        self._build_bottom_footer()
        self._build_sidebar()
        self._build_pages()

        self.switch_page("dashboard")

    # --------------------------------------------------------------------------
    # TOP ACTION BAR
    # --------------------------------------------------------------------------
    def _build_top_action_bar(self):
        top_bar = tk.Frame(self.right_container, bg=COLOR_CARD, highlightthickness=1,
                           highlightbackground=COLOR_CARD_BORDER, padx=16, pady=12)
        top_bar.pack(fill="x", padx=20, pady=(16, 0))

        lbl = tk.Label(top_bar, text="TARGET URL:", font=("Segoe UI", 9, "bold"),
                       fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
        lbl.pack(side="left", padx=(0, 10))

        entry_frame = tk.Frame(top_bar, bg=COLOR_INPUT_BG, highlightthickness=1,
                               highlightbackground=COLOR_INPUT_BORDER, padx=6, pady=4)
        entry_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.url_var = tk.StringVar(value="https://example.com")
        self.url_entry = tk.Entry(entry_frame, textvariable=self.url_var, font=("Segoe UI", 11),
                                  fg=COLOR_TEXT_WHITE, bg=COLOR_INPUT_BG, insertbackground=COLOR_BLUE,
                                  relief="flat", borderwidth=0)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(4, 4))

        btn_paste = tk.Button(entry_frame, text="📋 Paste", font=("Segoe UI", 8),
                              fg=COLOR_TEXT_MUTED, bg=COLOR_INPUT_BG, activeforeground=COLOR_TEXT_WHITE,
                              activebackground=COLOR_CARD, relief="flat", borderwidth=0, cursor="hand2",
                              command=self._paste_clipboard)
        btn_paste.pack(side="right", padx=(2, 0))

        btn_clear = tk.Button(entry_frame, text="✕", font=("Segoe UI", 9),
                              fg=COLOR_TEXT_MUTED, bg=COLOR_INPUT_BG, activeforeground=COLOR_RED,
                              activebackground=COLOR_CARD, relief="flat", borderwidth=0, cursor="hand2",
                              command=lambda: self.url_var.set(""))
        btn_clear.pack(side="right")

        self.btn_start_backup = ModernButton(
            top_bar, text="Start Backup", command=lambda: self._start_engine("backup"),
            bg_color=COLOR_GREEN, hover_color=COLOR_GREEN_HOVER, active_color=COLOR_GREEN_ACTIVE,
            width=120, height=34, icon="▶"
        )
        self.btn_start_backup.pack(side="left", padx=4)

        self.btn_start_clone = ModernButton(
            top_bar, text="Clone Website", command=lambda: self._start_engine("cloner"),
            bg_color=COLOR_ORANGE, hover_color=COLOR_ORANGE_HOVER, active_color=COLOR_ORANGE_ACTIVE,
            width=130, height=34, icon="⚡"
        )
        self.btn_start_clone.pack(side="left", padx=4)

        self.btn_stop = ModernButton(
            top_bar, text="Stop", command=self._stop_engine,
            bg_color=COLOR_RED, hover_color=COLOR_RED_HOVER, active_color=COLOR_RED_ACTIVE,
            width=80, height=34, icon="⏹"
        )
        self.btn_stop.pack(side="left", padx=4)
        self.btn_stop.set_enabled(False)

    def _paste_clipboard(self):
        try:
            clip = self.root.clipboard_get().strip()
            if clip:
                self.url_var.set(clip)
        except Exception:
            pass

    # --------------------------------------------------------------------------
    # SIDEBAR NAVIGATION
    # --------------------------------------------------------------------------
    def _build_sidebar(self):
        header = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR, pady=20, padx=16)
        header.pack(fill="x")

        logo_canvas = tk.Canvas(header, width=44, height=44, bg=COLOR_SIDEBAR, highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 10))
        logo_canvas.create_oval(4, 4, 40, 40, fill="#1e293b", outline=COLOR_BLUE, width=2)
        logo_canvas.create_arc(8, 8, 36, 36, start=30, extent=240, outline=COLOR_ORANGE, width=2)
        logo_canvas.create_text(22, 22, text="🌐", font=("Segoe UI", 14), fill=COLOR_TEXT_WHITE)

        title_frame = tk.Frame(header, bg=COLOR_SIDEBAR)
        title_frame.pack(side="left", fill="both", expand=True)

        lbl_app = tk.Label(title_frame, text="SCITBOSS", font=("Segoe UI", 13, "bold"),
                           fg=COLOR_TEXT_WHITE, bg=COLOR_SIDEBAR)
        lbl_app.pack(anchor="w")

        lbl_sub = tk.Label(title_frame, text="CLONER PRO FULL", font=("Segoe UI", 7, "bold"),
                           fg=COLOR_ORANGE, bg=COLOR_SIDEBAR)
        lbl_sub.pack(anchor="w")

        div = tk.Frame(self.sidebar, bg=COLOR_CARD_BORDER, height=1)
        div.pack(fill="x", padx=16, pady=(0, 16))

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("backup", "💾  Website Backup"),
            ("cloner", "⚡  Website Cloner"),
            ("history", "🕒  Backup History"),
            ("settings", "⚙  Settings"),
            ("about", "ℹ  About Software"),
        ]

        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar, text=label, anchor="w", font=("Segoe UI", 10, "bold"),
                fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR, activebackground=COLOR_CARD,
                activeforeground=COLOR_TEXT_WHITE, relief="flat", borderwidth=0,
                padx=20, pady=10, cursor="hand2",
                command=lambda k=key: self.switch_page(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        status_panel = tk.Frame(self.sidebar, bg=COLOR_CARD, highlightthickness=1,
                                highlightbackground=COLOR_CARD_BORDER, padx=12, pady=10)
        status_panel.pack(side="bottom", fill="x", padx=16, pady=16)

        lbl_stat_title = tk.Label(status_panel, text="ENGINE STATUS", font=("Segoe UI", 7, "bold"),
                                  fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
        lbl_stat_title.pack(anchor="w")

        self.lbl_sidebar_status = tk.Label(status_panel, text="● READY", font=("Segoe UI", 9, "bold"),
                                           fg=COLOR_GREEN, bg=COLOR_CARD)
        self.lbl_sidebar_status.pack(anchor="w", pady=(2, 0))

        self.lbl_sidebar_speed = tk.Label(status_panel, text="Speed: 0 B/s", font=("Segoe UI", 8),
                                          fg=COLOR_TEXT_DIM, bg=COLOR_CARD)
        self.lbl_sidebar_speed.pack(anchor="w")

    # --------------------------------------------------------------------------
    # BOTTOM FOOTER
    # --------------------------------------------------------------------------
    def _build_bottom_footer(self):
        footer = tk.Frame(self.right_container, bg=COLOR_SIDEBAR, padx=16, pady=6)
        footer.pack(side="bottom", fill="x")

        self.lbl_footer_status = tk.Label(footer, text="System Ready", font=("Segoe UI", 8),
                                          fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR)
        self.lbl_footer_status.pack(side="left")

        lbl_credit = tk.Label(footer, text=f"{DEVELOPER_CREDIT}  |", font=("Segoe UI", 8, "bold"),
                              fg=COLOR_ORANGE, bg=COLOR_SIDEBAR)
        lbl_credit.pack(side="right", padx=(4, 0))

        lbl_github = tk.Label(footer, text="github.com/scitboss", font=("Segoe UI", 8, "underline"),
                              fg=COLOR_BLUE, bg=COLOR_SIDEBAR, cursor="hand2")
        lbl_github.pack(side="right")
        lbl_github.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

        lbl_version = tk.Label(footer, text=f"{APP_VERSION}  •  ", font=("Segoe UI", 8),
                               fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR)
        lbl_version.pack(side="right")

    # --------------------------------------------------------------------------
    # PAGE SWITCHING
    # --------------------------------------------------------------------------
    def switch_page(self, page_name):
        for name, frame in self.pages.items():
            if name == page_name:
                frame.pack(fill="both", expand=True)
                self.nav_buttons[name].config(
                    bg=COLOR_CARD, fg=COLOR_TEXT_WHITE,
                    font=("Segoe UI", 10, "bold")
                )
            else:
                frame.pack_forget()
                self.nav_buttons[name].config(
                    bg=COLOR_SIDEBAR, fg=COLOR_TEXT_MUTED,
                    font=("Segoe UI", 10)
                )

        if page_name == "history":
            self._refresh_history_table()

    # --------------------------------------------------------------------------
    # CONTENT PAGES SETUP
    # --------------------------------------------------------------------------
    def _build_pages(self):
        self.pages = {}
        self.pages["dashboard"] = self._create_dashboard_page()
        self.pages["backup"] = self._create_backup_page()
        self.pages["cloner"] = self._create_cloner_page()
        self.pages["history"] = self._create_history_page()
        self.pages["settings"] = self._create_settings_page()
        self.pages["about"] = self._create_about_page()

    # --------------------------------------------------------------------------
    # 1. DASHBOARD PAGE
    # --------------------------------------------------------------------------
    def _create_dashboard_page(self):
        page = tk.Frame(self.content_area, bg=COLOR_BG_DARK)

        metrics_frame = tk.Frame(page, bg=COLOR_BG_DARK)
        metrics_frame.pack(fill="x", pady=(0, 12))

        self.card_pages = MetricCard(metrics_frame, "Pages Scanned", "0", icon="📄", accent_color=COLOR_BLUE)
        self.card_pages.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.card_files = MetricCard(metrics_frame, "Files Downloaded", "0", icon="📦", accent_color=COLOR_ORANGE)
        self.card_files.pack(side="left", fill="both", expand=True, padx=6)

        self.card_size = MetricCard(metrics_frame, "Downloaded Size", "0 B", icon="💾", accent_color=COLOR_GREEN)
        self.card_size.pack(side="left", fill="both", expand=True, padx=6)

        self.card_speed = MetricCard(metrics_frame, "Download Speed", "0 B/s", icon="⚡", accent_color=COLOR_CYAN)
        self.card_speed.pack(side="left", fill="both", expand=True, padx=6)

        self.card_status = MetricCard(metrics_frame, "Engine Mode", "IDLE", icon="⚙", accent_color=COLOR_PURPLE)
        self.card_status.pack(side="left", fill="both", expand=True, padx=(6, 0))

        prog_card = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                             highlightbackground=COLOR_CARD_BORDER, padx=16, pady=12)
        prog_card.pack(fill="x", pady=(0, 12))

        lbl_row = tk.Frame(prog_card, bg=COLOR_CARD)
        lbl_row.pack(fill="x", pady=(0, 6))

        self.lbl_current_task = tk.Label(lbl_row, text="Current Task: Ready", font=("Segoe UI", 9, "bold"),
                                         fg=COLOR_TEXT_WHITE, bg=COLOR_CARD)
        self.lbl_current_task.pack(side="left")

        self.lbl_progress_pct = tk.Label(lbl_row, text="0%", font=("Segoe UI", 9, "bold"),
                                         fg=COLOR_BLUE, bg=COLOR_CARD)
        self.lbl_progress_pct.pack(side="right")

        self.progress_bar = ttk.Progressbar(prog_card, style="Modern.Horizontal.TProgressbar",
                                            orient="horizontal", mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(2, 6))

        self.lbl_current_file = tk.Label(prog_card, text="File: None", font=("Segoe UI", 8),
                                         fg=COLOR_TEXT_DIM, bg=COLOR_CARD, anchor="w")
        self.lbl_current_file.pack(fill="x")

        log_card = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                            highlightbackground=COLOR_CARD_BORDER, padx=16, pady=12)
        log_card.pack(fill="both", expand=True)

        log_header = tk.Frame(log_card, bg=COLOR_CARD)
        log_header.pack(fill="x", pady=(0, 8))

        lbl_log_title = tk.Label(log_header, text="REAL-TIME ACTIVITY LOG", font=("Segoe UI", 9, "bold"),
                                 fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
        lbl_log_title.pack(side="left")

        btn_open_zip = tk.Button(log_header, text="📦 Open ZIP", font=("Segoe UI", 8, "bold"),
                                 fg=COLOR_TEXT_WHITE, bg=COLOR_ORANGE, activeforeground=COLOR_TEXT_WHITE,
                                 activebackground=COLOR_ORANGE_HOVER, relief="flat", borderwidth=0, cursor="hand2",
                                 command=self._open_current_project_zip)
        btn_open_zip.pack(side="right", padx=(4, 0))

        btn_open_folder = tk.Button(log_header, text="📂 Open Folder", font=("Segoe UI", 8),
                                    fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR, activeforeground=COLOR_TEXT_WHITE,
                                    activebackground=COLOR_CARD_BORDER, relief="flat", borderwidth=0, cursor="hand2",
                                    command=self._open_current_project_folder)
        btn_open_folder.pack(side="right", padx=(4, 0))

        btn_export_log = tk.Button(log_header, text="💾 Export Log", font=("Segoe UI", 8),
                                   fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR, activeforeground=COLOR_TEXT_WHITE,
                                   activebackground=COLOR_CARD_BORDER, relief="flat", borderwidth=0, cursor="hand2",
                                   command=self._export_log_file)
        btn_export_log.pack(side="right", padx=(4, 0))

        btn_clear_log = tk.Button(log_header, text="🧹 Clear Log", font=("Segoe UI", 8),
                                  fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR, activeforeground=COLOR_TEXT_WHITE,
                                  activebackground=COLOR_CARD_BORDER, relief="flat", borderwidth=0, cursor="hand2",
                                  command=self._clear_activity_log)
        btn_clear_log.pack(side="right")

        self.log_text = tk.Text(log_card, bg=COLOR_INPUT_BG, fg=COLOR_TEXT_WHITE,
                                font=("Consolas", 9), insertbackground=COLOR_BLUE,
                                relief="flat", borderwidth=0, wrap="word")
        log_scroll = ttk.Scrollbar(log_card, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        log_scroll.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        self.log_text.tag_config("TIME", foreground=COLOR_TEXT_DIM)
        self.log_text.tag_config("INFO", foreground="#38bdf8")
        self.log_text.tag_config("SUCCESS", foreground=COLOR_GREEN)
        self.log_text.tag_config("WARNING", foreground="#fbbf24")
        self.log_text.tag_config("ERROR", foreground=COLOR_RED)
        self.log_text.tag_config("DOWNLOAD", foreground=COLOR_CYAN)
        self.log_text.tag_config("CLONE", foreground=COLOR_ORANGE)

        self._append_log("System", "INFO", f"Welcome to {APP_NAME} (Full Production Edition). Ready to backup or clone.")
        return page

    # --------------------------------------------------------------------------
    # 2. WEBSITE BACKUP PAGE
    # --------------------------------------------------------------------------
    def _create_backup_page(self):
        page = tk.Frame(self.content_area, bg=COLOR_BG_DARK)

        banner = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                          highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        banner.pack(fill="x", pady=(0, 16))

        lbl_b_title = tk.Label(banner, text="WEBSITE BACKUP ENGINE", font=("Segoe UI", 12, "bold"),
                               fg=COLOR_GREEN, bg=COLOR_CARD)
        lbl_b_title.pack(anchor="w")

        lbl_b_desc = tk.Label(
            banner,
            text="Downloads all public website files while strictly preserving the remote server's folder structure.\n"
                 "Includes HTML, CSS, JavaScript, media assets, documents, and generates a structured backup directory with backup_report.txt and a complete ZIP archive.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, justify="left"
        )
        lbl_b_desc.pack(anchor="w", pady=(6, 0))

        ctrl_frame = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                              highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        ctrl_frame.pack(fill="x", pady=(0, 16))

        lbl_res = tk.Label(ctrl_frame, text="ASSET CATEGORIES TO BACKUP", font=("Segoe UI", 9, "bold"),
                           fg=COLOR_TEXT_WHITE, bg=COLOR_CARD)
        lbl_res.pack(anchor="w", pady=(0, 10))

        chk_grid = tk.Frame(ctrl_frame, bg=COLOR_CARD)
        chk_grid.pack(fill="x", pady=(0, 12))

        self.cb_images = ttk.Checkbutton(chk_grid, text="Images & SVG Icons", style="Dark.TCheckbutton")
        self.cb_images.grid(row=0, column=0, sticky="w", padx=10, pady=4)
        self.cb_images.state(['selected' if self.config.get("download_images") else '!selected'])

        self.cb_css = ttk.Checkbutton(chk_grid, text="CSS Stylesheets", style="Dark.TCheckbutton")
        self.cb_css.grid(row=0, column=1, sticky="w", padx=10, pady=4)
        self.cb_css.state(['selected' if self.config.get("download_css") else '!selected'])

        self.cb_js = ttk.Checkbutton(chk_grid, text="JavaScript Files", style="Dark.TCheckbutton")
        self.cb_js.grid(row=0, column=2, sticky="w", padx=10, pady=4)
        self.cb_js.state(['selected' if self.config.get("download_js") else '!selected'])

        self.cb_fonts = ttk.Checkbutton(chk_grid, text="Web Fonts (WOFF/TTF)", style="Dark.TCheckbutton")
        self.cb_fonts.grid(row=1, column=0, sticky="w", padx=10, pady=4)
        self.cb_fonts.state(['selected' if self.config.get("download_fonts") else '!selected'])

        self.cb_docs = ttk.Checkbutton(chk_grid, text="Public Documents (PDF/DOC)", style="Dark.TCheckbutton")
        self.cb_docs.grid(row=1, column=1, sticky="w", padx=10, pady=4)
        self.cb_docs.state(['selected' if self.config.get("download_docs") else '!selected'])

        self.cb_media = ttk.Checkbutton(chk_grid, text="Media (Audio/Video)", style="Dark.TCheckbutton")
        self.cb_media.grid(row=1, column=2, sticky="w", padx=10, pady=4)
        self.cb_media.state(['selected' if self.config.get("download_media") else '!selected'])

        btn_row = tk.Frame(ctrl_frame, bg=COLOR_CARD)
        btn_row.pack(fill="x", pady=(10, 0))

        btn_run = ModernButton(
            btn_row, text="Start Full Website Backup",
            command=lambda: self._start_engine("backup"),
            bg_color=COLOR_GREEN, hover_color=COLOR_GREEN_HOVER, active_color=COLOR_GREEN_ACTIVE,
            width=220, height=38, icon="▶"
        )
        btn_run.pack(side="left")

        struct_card = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                               highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        struct_card.pack(fill="both", expand=True)

        lbl_s_title = tk.Label(struct_card, text="OUTPUT STRUCTURE PREVIEW", font=("Segoe UI", 9, "bold"),
                               fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
        lbl_s_title.pack(anchor="w", pady=(0, 8))

        preview_text = (
            "WebsiteBackup/\n"
            "├── index.html\n"
            "├── about.html\n"
            "├── contact.html\n"
            "├── assets/\n"
            "│   ├── css/\n"
            "│   ├── js/\n"
            "│   ├── images/\n"
            "│   └── fonts/\n"
            "├── backup_report.txt\n"
            "└── WebsiteBackup_FULL.zip   <-- Complete Compressed Archive\n"
        )
        lbl_preview = tk.Label(struct_card, text=preview_text, font=("Consolas", 10),
                               fg=COLOR_CYAN, bg=COLOR_INPUT_BG, justify="left", padx=16, pady=12)
        lbl_preview.pack(fill="both", expand=True)

        return page

    # --------------------------------------------------------------------------
    # 3. WEBSITE CLONER PAGE
    # --------------------------------------------------------------------------
    def _create_cloner_page(self):
        page = tk.Frame(self.content_area, bg=COLOR_BG_DARK)

        banner = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                          highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        banner.pack(fill="x", pady=(0, 16))

        lbl_c_title = tk.Label(banner, text="WEBSITE CLONER MODE (FULL STATIC MIRROR)", font=("Segoe UI", 12, "bold"),
                               fg=COLOR_ORANGE, bg=COLOR_CARD)
        lbl_c_title.pack(anchor="w")

        lbl_c_desc = tk.Label(
            banner,
            text="Downloads website resources and converts all remote URLs and stylesheet links into relative local paths.\n"
                 "Produces a standalone static website copy that can be opened and navigated offline via index.html, bundled with an automated ZIP package.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, justify="left"
        )
        lbl_c_desc.pack(anchor="w", pady=(6, 0))

        feat_card = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                             highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        feat_card.pack(fill="x", pady=(0, 16))

        lbl_feat_title = tk.Label(feat_card, text="OFFLINE STATIC MIRRORING FEATURES", font=("Segoe UI", 9, "bold"),
                                  fg=COLOR_TEXT_WHITE, bg=COLOR_CARD)
        lbl_feat_title.pack(anchor="w", pady=(0, 10))

        features_info = [
            "✔  HTML Page Hyperlinks (<a href>) are rewritten to local .html relative files.",
            "✔  CSS files and inline <style> blocks (url(...) and @import) are rewritten to local asset paths.",
            "✔  Lazy-loaded images (data-src, data-original, data-srcset) are converted to offline static images.",
            "✔  External CDN assets (Google Fonts, CDN scripts) are mirrored locally into assets/external/.",
            "✔  Automated full ZIP archive generation upon completion for easy sharing or storage.",
            "✔  Generated index.html file allows instant one-click offline browser launching.",
        ]
        for f in features_info:
            lbl_f = tk.Label(feat_card, text=f, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
            lbl_f.pack(anchor="w", pady=2)

        action_box = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                              highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        action_box.pack(fill="both", expand=True)

        lbl_act_title = tk.Label(action_box, text="EXECUTE WEBSITE CLONE", font=("Segoe UI", 9, "bold"),
                                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD)
        lbl_act_title.pack(anchor="w", pady=(0, 12))

        btn_row = tk.Frame(action_box, bg=COLOR_CARD)
        btn_row.pack(anchor="w", pady=(0, 16))

        btn_run_clone = ModernButton(
            btn_row, text="Start Website Clone", command=lambda: self._start_engine("cloner"),
            bg_color=COLOR_ORANGE, hover_color=COLOR_ORANGE_HOVER, active_color=COLOR_ORANGE_ACTIVE,
            width=200, height=38, icon="⚡"
        )
        btn_run_clone.pack(side="left", padx=(0, 10))

        self.btn_open_cloned_site = ModernButton(
            btn_row, text="Open Cloned Site in Browser", command=self._open_latest_cloned_website,
            bg_color=COLOR_BLUE, hover_color=COLOR_BLUE_HOVER, active_color=COLOR_BLUE_ACTIVE,
            width=230, height=38, icon="🌐"
        )
        self.btn_open_cloned_site.pack(side="left", padx=(0, 10))

        btn_open_zip = ModernButton(
            btn_row, text="Open Full ZIP Archive", command=self._open_current_project_zip,
            bg_color=COLOR_GREEN, hover_color=COLOR_GREEN_HOVER, active_color=COLOR_GREEN_ACTIVE,
            width=200, height=38, icon="📦"
        )
        btn_open_zip.pack(side="left")

        lbl_disc = tk.Label(
            action_box,
            text="Note: Static website cloning replicates public client-side HTML, CSS, JavaScript, and assets.\n"
                 "Dynamic server-side backends (PHP, databases, active authentication sessions) cannot be retrieved over public HTTP.",
            font=("Segoe UI", 8, "italic"), fg=COLOR_TEXT_DIM, bg=COLOR_CARD, justify="left"
        )
        lbl_disc.pack(anchor="w", side="bottom")

        return page

    # --------------------------------------------------------------------------
    # 4. BACKUP HISTORY PAGE
    # --------------------------------------------------------------------------
    def _create_history_page(self):
        page = tk.Frame(self.content_area, bg=COLOR_BG_DARK)

        header = tk.Frame(page, bg=COLOR_BG_DARK)
        header.pack(fill="x", pady=(0, 10))

        lbl_title = tk.Label(header, text="BACKUP & CLONE HISTORY", font=("Segoe UI", 12, "bold"),
                             fg=COLOR_TEXT_WHITE, bg=COLOR_BG_DARK)
        lbl_title.pack(side="left")

        btn_open_zip = tk.Button(header, text="📦 Open ZIP", font=("Segoe UI", 9, "bold"),
                                 fg=COLOR_TEXT_WHITE, bg=COLOR_ORANGE, activebackground=COLOR_ORANGE_HOVER,
                                 relief="flat", borderwidth=0, padx=10, pady=4, cursor="hand2",
                                 command=self._open_selected_history_zip)
        btn_open_zip.pack(side="right", padx=4)

        btn_open = tk.Button(header, text="📂 Open Folder", font=("Segoe UI", 9),
                             fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, activebackground=COLOR_CARD_BORDER,
                             relief="flat", borderwidth=0, padx=10, pady=4, cursor="hand2",
                             command=self._open_selected_history_folder)
        btn_open.pack(side="right", padx=4)

        btn_view_site = tk.Button(header, text="🌐 Launch Website", font=("Segoe UI", 9),
                                  fg=COLOR_TEXT_WHITE, bg=COLOR_BLUE, activebackground=COLOR_BLUE_HOVER,
                                  relief="flat", borderwidth=0, padx=10, pady=4, cursor="hand2",
                                  command=self._launch_selected_history_site)
        btn_view_site.pack(side="right", padx=4)

        btn_report = tk.Button(header, text="📄 View Report", font=("Segoe UI", 9),
                               fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, activebackground=COLOR_CARD_BORDER,
                               relief="flat", borderwidth=0, padx=10, pady=4, cursor="hand2",
                               command=self._view_selected_history_report)
        btn_report.pack(side="right", padx=4)

        btn_del = tk.Button(header, text="🗑 Delete", font=("Segoe UI", 9),
                            fg=COLOR_RED, bg=COLOR_CARD, activebackground=COLOR_CARD_BORDER,
                            relief="flat", borderwidth=0, padx=10, pady=4, cursor="hand2",
                            command=self._delete_selected_history_entry)
        btn_del.pack(side="right", padx=4)

        table_frame = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                               highlightbackground=COLOR_CARD_BORDER)
        table_frame.pack(fill="both", expand=True)

        columns = ("date", "mode", "url", "files", "size", "status", "folder")
        self.tree_history = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         style="Dark.Treeview", selectmode="browse")

        self.tree_history.heading("date", text="Date & Time")
        self.tree_history.heading("mode", text="Mode")
        self.tree_history.heading("url", text="Target URL")
        self.tree_history.heading("files", text="Total Files")
        self.tree_history.heading("size", text="Data Size")
        self.tree_history.heading("status", text="Status")
        self.tree_history.heading("folder", text="Local Path")

        self.tree_history.column("date", width=140, anchor="w")
        self.tree_history.column("mode", width=80, anchor="center")
        self.tree_history.column("url", width=220, anchor="w")
        self.tree_history.column("files", width=80, anchor="center")
        self.tree_history.column("size", width=90, anchor="center")
        self.tree_history.column("status", width=90, anchor="center")
        self.tree_history.column("folder", width=300, anchor="w")

        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_history.yview)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_history.xview)
        self.tree_history.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        self.tree_history.pack(side="left", fill="both", expand=True)

        self.tree_history.bind("<Double-1>", lambda e: self._launch_selected_history_site())
        return page

    def _refresh_history_table(self):
        self.tree_history.delete(*self.tree_history.get_children())
        self.history.load()
        for item in self.history.items:
            self.tree_history.insert(
                "", "end", iid=item.get("id"),
                values=(
                    item.get("date", ""),
                    item.get("mode", "").upper(),
                    item.get("url", ""),
                    item.get("total_files", 0),
                    item.get("total_size_formatted", "0 B"),
                    item.get("status", ""),
                    item.get("folder", "")
                )
            )

    def _get_selected_history_item(self):
        sel = self.tree_history.selection()
        if not sel:
            messagebox.showinfo("Selection Required", "Please select a backup history entry from the list.")
            return None
        sel_id = sel[0]
        for item in self.history.items:
            if item.get("id") == sel_id:
                return item
        return None

    def _open_selected_history_folder(self):
        item = self._get_selected_history_item()
        if item:
            folder = item.get("folder", "")
            if os.path.exists(folder):
                if IS_WINDOWS:
                    os.startfile(folder)
                else:
                    webbrowser.open(folder)
            else:
                messagebox.showwarning("Folder Not Found", f"The directory does not exist on disk:\n{folder}")

    def _open_selected_history_zip(self):
        item = self._get_selected_history_item()
        if item:
            zip_file = item.get("zip_file", "")
            if zip_file and os.path.exists(zip_file):
                if IS_WINDOWS:
                    os.startfile(zip_file)
                else:
                    webbrowser.open(zip_file)
            else:
                messagebox.showwarning("ZIP Not Found", f"ZIP archive not found or not created for this item.")

    def _launch_selected_history_site(self):
        item = self._get_selected_history_item()
        if item:
            folder = item.get("folder", "")
            index_file = item.get("index_file", "") or os.path.join(folder, "index.html")
            if os.path.exists(index_file):
                webbrowser.open(f"file:///{os.path.abspath(index_file).replace(os.sep, '/')}")
            elif os.path.exists(folder):
                if IS_WINDOWS:
                    os.startfile(folder)
                else:
                    webbrowser.open(folder)
            else:
                messagebox.showwarning("Not Found", f"Cannot find index.html in:\n{folder}")

    def _view_selected_history_report(self):
        item = self._get_selected_history_item()
        if item:
            folder = item.get("folder", "")
            rep = item.get("report_file", "") or os.path.join(folder, "backup_report.txt")
            if os.path.exists(rep):
                if IS_WINDOWS:
                    os.startfile(rep)
                else:
                    webbrowser.open(rep)
            else:
                messagebox.showwarning("Report Not Found", f"Report file not found at:\n{rep}")

    def _delete_selected_history_entry(self):
        item = self._get_selected_history_item()
        if item:
            if messagebox.askyesno("Confirm Delete", f"Delete history record for:\n{item.get('url')}?"):
                self.history.delete_entry(item.get("id"))
                self._refresh_history_table()

    # --------------------------------------------------------------------------
    # 5. SETTINGS PAGE
    # --------------------------------------------------------------------------
    def _create_settings_page(self):
        page = tk.Frame(self.content_area, bg=COLOR_BG_DARK)

        canvas = tk.Canvas(page, bg=COLOR_BG_DARK, highlightthickness=0)
        scroll = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLOR_BG_DARK)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        card1 = tk.Frame(scroll_frame, bg=COLOR_CARD, highlightthickness=1,
                         highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        card1.pack(fill="x", pady=(0, 16))

        lbl_s1 = tk.Label(card1, text="CRAWLER LIMITS & PERFORMANCE CONTROLS", font=("Segoe UI", 10, "bold"),
                          fg=COLOR_BLUE, bg=COLOR_CARD)
        lbl_s1.pack(anchor="w", pady=(0, 12))

        self.cb_unlimited = ttk.Checkbutton(card1, text="Unlimited Full Site Crawl (Crawl all discovered pages without limits)", style="Dark.TCheckbutton")
        self.cb_unlimited.pack(anchor="w", pady=(0, 10))
        self.cb_unlimited.state(['selected' if self.config.get("unlimited_crawl") else '!selected'])

        r1 = tk.Frame(card1, bg=COLOR_CARD)
        r1.pack(fill="x", pady=4)
        tk.Label(r1, text="Maximum Pages to Download:", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, width=32, anchor="w").pack(side="left")
        self.spin_max_pages = tk.Spinbox(r1, from_=10, to=50000, font=("Segoe UI", 9),
                                         bg=COLOR_INPUT_BG, fg=COLOR_TEXT_WHITE, width=10, relief="flat")
        self.spin_max_pages.delete(0, "end")
        self.spin_max_pages.insert(0, str(self.config.get("max_pages", 500)))
        self.spin_max_pages.pack(side="left")

        r2 = tk.Frame(card1, bg=COLOR_CARD)
        r2.pack(fill="x", pady=4)
        tk.Label(r2, text="Maximum Crawl Depth:", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, width=32, anchor="w").pack(side="left")
        self.spin_max_depth = tk.Spinbox(r2, from_=1, to=30, font=("Segoe UI", 9),
                                         bg=COLOR_INPUT_BG, fg=COLOR_TEXT_WHITE, width=10, relief="flat")
        self.spin_max_depth.delete(0, "end")
        self.spin_max_depth.insert(0, str(self.config.get("max_depth", 8)))
        self.spin_max_depth.pack(side="left")

        r_threads = tk.Frame(card1, bg=COLOR_CARD)
        r_threads.pack(fill="x", pady=4)
        tk.Label(r_threads, text="Parallel Download Threads:", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, width=32, anchor="w").pack(side="left")
        self.spin_threads = tk.Spinbox(r_threads, from_=1, to=20, font=("Segoe UI", 9),
                                       bg=COLOR_INPUT_BG, fg=COLOR_TEXT_WHITE, width=10, relief="flat")
        self.spin_threads.delete(0, "end")
        self.spin_threads.insert(0, str(self.config.get("thread_workers", 6)))
        self.spin_threads.pack(side="left")

        r3 = tk.Frame(card1, bg=COLOR_CARD)
        r3.pack(fill="x", pady=4)
        tk.Label(r3, text="Request Delay (sec):", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, width=32, anchor="w").pack(side="left")
        self.spin_delay = tk.Spinbox(r3, from_=0.0, to=5.0, increment=0.05, font=("Segoe UI", 9),
                                     bg=COLOR_INPUT_BG, fg=COLOR_TEXT_WHITE, width=10, relief="flat")
        self.spin_delay.delete(0, "end")
        self.spin_delay.insert(0, str(self.config.get("request_delay", 0.05)))
        self.spin_delay.pack(side="left")

        r4 = tk.Frame(card1, bg=COLOR_CARD)
        r4.pack(fill="x", pady=4)
        tk.Label(r4, text="Connection Timeout (sec):", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, width=32, anchor="w").pack(side="left")
        self.spin_timeout = tk.Spinbox(r4, from_=5, to=120, font=("Segoe UI", 9),
                                       bg=COLOR_INPUT_BG, fg=COLOR_TEXT_WHITE, width=10, relief="flat")
        self.spin_timeout.delete(0, "end")
        self.spin_timeout.insert(0, str(self.config.get("timeout", 20)))
        self.spin_timeout.pack(side="left")

        r5 = tk.Frame(card1, bg=COLOR_CARD)
        r5.pack(fill="x", pady=4)
        tk.Label(r5, text="Maximum File Size Limit (MB):", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD, width=32, anchor="w").pack(side="left")
        self.spin_max_size = tk.Spinbox(r5, from_=5, to=2000, font=("Segoe UI", 9),
                                        bg=COLOR_INPUT_BG, fg=COLOR_TEXT_WHITE, width=10, relief="flat")
        self.spin_max_size.delete(0, "end")
        self.spin_max_size.insert(0, str(self.config.get("max_file_size_mb", 150)))
        self.spin_max_size.pack(side="left")

        card2 = tk.Frame(scroll_frame, bg=COLOR_CARD, highlightthickness=1,
                         highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        card2.pack(fill="x", pady=(0, 16))

        lbl_s2 = tk.Label(card2, text="SCOPE, ARCHIVE & SECURITY", font=("Segoe UI", 10, "bold"),
                          fg=COLOR_ORANGE, bg=COLOR_CARD)
        lbl_s2.pack(anchor="w", pady=(0, 10))

        self.cb_auto_zip = ttk.Checkbutton(card2, text="Automatically Create Full ZIP Archive (.zip) upon completion", style="Dark.TCheckbutton")
        self.cb_auto_zip.pack(anchor="w", pady=4)
        self.cb_auto_zip.state(['selected' if self.config.get("auto_create_zip") else '!selected'])

        self.cb_subdomains = ttk.Checkbutton(card2, text="Include Subdomains (e.g., blog.example.com)", style="Dark.TCheckbutton")
        self.cb_subdomains.pack(anchor="w", pady=4)
        self.cb_subdomains.state(['selected' if self.config.get("include_subdomains") else '!selected'])

        self.cb_robots = ttk.Checkbutton(card2, text="Respect robots.txt Rules (Uncheck for complete backup)", style="Dark.TCheckbutton")
        self.cb_robots.pack(anchor="w", pady=4)
        self.cb_robots.state(['selected' if self.config.get("respect_robots_txt") else '!selected'])

        self.cb_structure = ttk.Checkbutton(card2, text="Preserve Original Remote Server Folder Hierarchy", style="Dark.TCheckbutton")
        self.cb_structure.pack(anchor="w", pady=4)
        self.cb_structure.state(['selected' if self.config.get("preserve_structure") else '!selected'])

        self.cb_ssl = ttk.Checkbutton(card2, text="Ignore SSL Certificate Errors (Allow self-signed / expired certs)", style="Dark.TCheckbutton")
        self.cb_ssl.pack(anchor="w", pady=4)
        self.cb_ssl.state(['selected' if self.config.get("ignore_ssl_errors") else '!selected'])

        card3 = tk.Frame(scroll_frame, bg=COLOR_CARD, highlightthickness=1,
                         highlightbackground=COLOR_CARD_BORDER, padx=20, pady=16)
        card3.pack(fill="x", pady=(0, 16))

        lbl_s3 = tk.Label(card3, text="STORAGE & USER-AGENT SETTINGS", font=("Segoe UI", 10, "bold"),
                          fg=COLOR_GREEN, bg=COLOR_CARD)
        lbl_s3.pack(anchor="w", pady=(0, 10))

        tk.Label(card3, text="Default Backup Storage Location:", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD).pack(anchor="w", pady=(2, 4))

        dir_row = tk.Frame(card3, bg=COLOR_CARD)
        dir_row.pack(fill="x", pady=(0, 10))

        self.entry_dir = tk.Entry(dir_row, font=("Segoe UI", 9), fg=COLOR_TEXT_WHITE,
                                  bg=COLOR_INPUT_BG, relief="flat")
        self.entry_dir.insert(0, str(self.config.get("download_dir")))
        self.entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse = tk.Button(dir_row, text="Browse...", font=("Segoe UI", 8),
                               fg=COLOR_TEXT_WHITE, bg=COLOR_SIDEBAR, activebackground=COLOR_CARD_BORDER,
                               relief="flat", borderwidth=0, padx=12, pady=4, cursor="hand2",
                               command=self._browse_backup_dir)
        btn_browse.pack(side="right")

        tk.Label(card3, text="Browser User-Agent Preset:", font=("Segoe UI", 9),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD).pack(anchor="w", pady=(4, 4))

        self.ua_preset_var = tk.StringVar(value=self.config.get("user_agent_preset", "Chrome 131 on Windows 11 (Recommended)"))
        ua_combo = ttk.Combobox(card3, textvariable=self.ua_preset_var, values=list(USER_AGENTS.keys()),
                                font=("Segoe UI", 9), state="readonly")
        ua_combo.pack(fill="x", pady=(0, 10))

        btn_box = tk.Frame(scroll_frame, bg=COLOR_BG_DARK)
        btn_box.pack(fill="x", pady=(0, 20))

        btn_save = ModernButton(
            btn_box, text="Save Settings", command=self._save_settings,
            bg_color=COLOR_BLUE, hover_color=COLOR_BLUE_HOVER, active_color=COLOR_BLUE_ACTIVE,
            width=140, height=36, icon="💾"
        )
        btn_save.pack(side="left", padx=(0, 10))

        btn_reset = ModernButton(
            btn_box, text="Reset to Defaults", command=self._reset_settings,
            bg_color=COLOR_CARD_BORDER, hover_color=COLOR_CARD, active_color=COLOR_BG_DARK,
            width=150, height=36, icon="🔄"
        )
        btn_reset.pack(side="left")

        return page

    def _browse_backup_dir(self):
        curr = self.entry_dir.get()
        chosen = filedialog.askdirectory(initialdir=curr, title="Select Backup Destination Folder")
        if chosen:
            self.entry_dir.delete(0, "end")
            self.entry_dir.insert(0, chosen)

    def _save_settings(self):
        try:
            self.config.set("unlimited_crawl", self.cb_unlimited.instate(['selected']))
            self.config.set("max_pages", int(self.spin_max_pages.get()))
            self.config.set("max_depth", int(self.spin_max_depth.get()))
            self.config.set("thread_workers", int(self.spin_threads.get()))
            self.config.set("request_delay", float(self.spin_delay.get()))
            self.config.set("timeout", int(self.spin_timeout.get()))
            self.config.set("max_file_size_mb", int(self.spin_max_size.get()))
            self.config.set("auto_create_zip", self.cb_auto_zip.instate(['selected']))
            self.config.set("include_subdomains", self.cb_subdomains.instate(['selected']))
            self.config.set("respect_robots_txt", self.cb_robots.instate(['selected']))
            self.config.set("preserve_structure", self.cb_structure.instate(['selected']))
            self.config.set("ignore_ssl_errors", self.cb_ssl.instate(['selected']))
            self.config.set("download_dir", self.entry_dir.get().strip())
            self.config.set("user_agent_preset", self.ua_preset_var.get())

            self.config.save()
            messagebox.showinfo("Settings Saved", "Application settings have been successfully updated.")
            self._append_log("Config", "SUCCESS", "Application settings updated.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving settings: {e}")

    def _reset_settings(self):
        if messagebox.askyesno("Reset Defaults", "Reset all settings to safe default values?"):
            self.config.reset_defaults()
            self.spin_max_pages.delete(0, "end")
            self.spin_max_pages.insert(0, str(self.config.get("max_pages")))
            self.spin_max_depth.delete(0, "end")
            self.spin_max_depth.insert(0, str(self.config.get("max_depth")))
            self.spin_threads.delete(0, "end")
            self.spin_threads.insert(0, str(self.config.get("thread_workers")))
            self.spin_delay.delete(0, "end")
            self.spin_delay.insert(0, str(self.config.get("request_delay")))
            self.spin_timeout.delete(0, "end")
            self.spin_timeout.insert(0, str(self.config.get("timeout")))
            self.spin_max_size.delete(0, "end")
            self.spin_max_size.insert(0, str(self.config.get("max_file_size_mb")))
            self.entry_dir.delete(0, "end")
            self.entry_dir.insert(0, str(self.config.get("download_dir")))
            messagebox.showinfo("Reset Complete", "Settings reset to defaults.")

    # --------------------------------------------------------------------------
    # 6. ABOUT SOFTWARE PAGE
    # --------------------------------------------------------------------------
    def _create_about_page(self):
        page = tk.Frame(self.content_area, bg=COLOR_BG_DARK)

        card = tk.Frame(page, bg=COLOR_CARD, highlightthickness=1,
                        highlightbackground=COLOR_CARD_BORDER, padx=24, pady=20)
        card.pack(fill="both", expand=True)

        lbl_title = tk.Label(card, text=APP_NAME, font=("Segoe UI", 14, "bold"),
                             fg=COLOR_TEXT_WHITE, bg=COLOR_CARD)
        lbl_title.pack(anchor="w")

        lbl_ver = tk.Label(card, text=f"Version {APP_VERSION}  |  Windows Desktop Edition",
                           font=("Segoe UI", 9, "bold"), fg=COLOR_ORANGE, bg=COLOR_CARD)
        lbl_ver.pack(anchor="w", pady=(2, 16))

        credit_box = tk.Frame(card, bg=COLOR_INPUT_BG, highlightthickness=1,
                              highlightbackground=COLOR_INPUT_BORDER, padx=16, pady=12)
        credit_box.pack(fill="x", pady=(0, 16))

        tk.Label(credit_box, text="PROJECT CREDIT:", font=("Segoe UI", 8, "bold"),
                 fg=COLOR_TEXT_MUTED, bg=COLOR_INPUT_BG).pack(anchor="w")

        tk.Label(credit_box, text=DEVELOPER_CREDIT, font=("Segoe UI", 12, "bold"),
                 fg=COLOR_GREEN, bg=COLOR_INPUT_BG).pack(anchor="w", pady=(2, 4))

        github_link = tk.Label(credit_box, text=f"GITHUB: {GITHUB_URL}",
                               font=("Segoe UI", 10, "underline"), fg=COLOR_BLUE,
                               bg=COLOR_INPUT_BG, cursor="hand2")
        github_link.pack(anchor="w")
        github_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

        sec_box = tk.Frame(card, bg=COLOR_CARD)
        sec_box.pack(fill="x", pady=(0, 16))

        tk.Label(sec_box, text="SECURITY & RESPONSIBLE USE POLICY:", font=("Segoe UI", 9, "bold"),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD).pack(anchor="w", pady=(0, 6))

        sec_text = (
            "This software is engineered exclusively for authorized website backups, public archiving, "
            "offline static site development, and authorized migration.\n"
            "• Does NOT bypass security gates, CAPTCHAs, or authentication mechanisms.\n"
            "• Does NOT attempt to access private backend code, databases, or cookies.\n"
            "• Respects web standards, polite request throttling, and robots.txt rules.\n"
            "Users must ensure they have authorization to backup or archive target websites."
        )
        tk.Label(sec_box, text=sec_text, font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED,
                 bg=COLOR_CARD, justify="left").pack(anchor="w")

        exe_box = tk.Frame(card, bg=COLOR_CARD)
        exe_box.pack(fill="x", pady=(0, 10))

        tk.Label(exe_box, text="WINDOWS STANDALONE EXE BUILD SUPPORT:", font=("Segoe UI", 9, "bold"),
                 fg=COLOR_TEXT_WHITE, bg=COLOR_CARD).pack(anchor="w", pady=(0, 4))

        tk.Label(exe_box, text="Build standalone executable with PyInstaller using the command below:",
                 font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD).pack(anchor="w")

        cmd_entry = tk.Entry(exe_box, font=("Consolas", 9), fg=COLOR_CYAN,
                             bg=COLOR_INPUT_BG, relief="flat")
        cmd_entry.insert(0, 'pyinstaller --onefile --windowed --name "SCITBOSS Website Backup Cloner" website_backup_cloner.py')
        cmd_entry.configure(state="readonly")
        cmd_entry.pack(fill="x", pady=(4, 8))

        btn_gen_bat = tk.Button(
            exe_box, text="⚙ Generate Windows Build Script (build_exe.bat)", font=("Segoe UI", 8, "bold"),
            fg=COLOR_TEXT_WHITE, bg=COLOR_BLUE, activebackground=COLOR_BLUE_HOVER,
            relief="flat", borderwidth=0, padx=12, pady=6, cursor="hand2",
            command=self._generate_build_bat
        )
        btn_gen_bat.pack(side="left")

        return page

    def _generate_build_bat(self):
        bat_content = (
            "@echo off\n"
            "echo ====================================================================\n"
            "echo           SCITBOSS WEBSITE BACKUP & CLONER PRO EXE BUILDER          \n"
            "echo ====================================================================\n"
            "echo Checking for PyInstaller...\n"
            "python -m pip install --upgrade pyinstaller\n"
            "echo Building standalone Windows Executable...\n"
            'pyinstaller --onefile --windowed --name "SCITBOSS Website Backup Cloner" website_backup_cloner.py\n'
            "echo.\n"
            "if exist dist\\ ( echo Build complete! Find your executable inside the 'dist' folder. ) else ( echo Build failed. )\n"
            "pause\n"
        )
        try:
            with open("build_exe.bat", "w") as f:
                f.write(bat_content)
            messagebox.showinfo("Build Script Created", "Successfully generated 'build_exe.bat'.\nDouble-click build_exe.bat to compile the standalone EXE.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create build_exe.bat: {e}")

    # --------------------------------------------------------------------------
    # ENGINE LIFECYCLE & EXECUTION
    # --------------------------------------------------------------------------
    def _start_engine(self, mode):
        if self.is_running:
            messagebox.showwarning("Task Active", "A website backup or cloning operation is currently in progress.")
            return

        url_input = self.url_var.get()
        is_valid, normalized_url, err_msg = validate_and_normalize_url(url_input)
        if not is_valid:
            messagebox.showerror("Invalid URL", err_msg)
            return

        self.url_var.set(normalized_url)

        self.config.set("download_images", self.cb_images.instate(['selected']))
        self.config.set("download_css", self.cb_css.instate(['selected']))
        self.config.set("download_js", self.cb_js.instate(['selected']))
        self.config.set("download_fonts", self.cb_fonts.instate(['selected']))
        self.config.set("download_docs", self.cb_docs.instate(['selected']))
        self.config.set("download_media", self.cb_media.instate(['selected']))

        self.is_running = True
        self.btn_start_backup.set_enabled(False)
        self.btn_start_clone.set_enabled(False)
        self.btn_stop.set_enabled(True)
        self.progress_bar.start(10)

        mode_name = "CLONER" if mode == "cloner" else "BACKUP"
        self.card_status.update_value(mode_name)
        self.lbl_sidebar_status.config(text=f"● {mode_name}", fg=COLOR_ORANGE if mode == "cloner" else COLOR_GREEN)
        self.lbl_current_task.config(text=f"Current Task: Initializing {mode.title()} for {normalized_url}")
        self.switch_page("dashboard")

        callbacks = {
            "on_log": lambda ts, level, msg: self.gui_queue.put(("log", ts, level, msg)),
            "on_progress": lambda stats: self.gui_queue.put(("progress", stats)),
            "on_finished": lambda success, rep, hist: self.gui_queue.put(("finished", success, rep, hist)),
        }

        self.current_engine = WebsiteBackupEngine(
            target_url=normalized_url,
            mode=mode,
            config=self.config,
            callbacks=callbacks
        )
        self.current_engine.start()

    def _stop_engine(self):
        if self.current_engine and self.is_running:
            self.current_engine.stop()
            self.lbl_current_task.config(text="Stopping operation... please wait.")
            self.btn_stop.set_enabled(False)

    def _process_gui_queue(self):
        try:
            while not self.gui_queue.empty():
                evt = self.gui_queue.get_nowait()
                evt_type = evt[0]

                if evt_type == "log":
                    _, ts, level, msg = evt
                    self._append_log(ts, level, msg)

                elif evt_type == "progress":
                    _, stats = evt
                    self.card_pages.update_value(f"{stats['pages_downloaded']} / {stats['pages_discovered']}")
                    self.card_files.update_value(stats["files_downloaded"])
                    self.card_size.update_value(stats["bytes_formatted"])
                    self.card_speed.update_value(stats["speed_formatted"])
                    self.lbl_sidebar_speed.config(text=f"Speed: {stats['speed_formatted']}")
                    self.lbl_current_file.config(text=f"Current: {stats['current_file'][:90]}")

                    discovered = max(1, stats["pages_discovered"])
                    downloaded = stats["pages_downloaded"]
                    pct = min(100, int((downloaded / discovered) * 100))
                    self.lbl_progress_pct.config(text=f"{pct}%")
                    self.lbl_footer_status.config(text=f"Downloading {stats['current_file'][:60]}")

                elif evt_type == "finished":
                    _, success, rep_path, hist_entry = evt
                    self._on_operation_completed(success, rep_path, hist_entry)

        except Exception as e:
            print(f"[GUI Queue] Error: {e}")

        self.root.after(50, self._process_gui_queue)

    def _on_operation_completed(self, success, report_path, hist_entry):
        self.is_running = False
        self.progress_bar.stop()
        self.progress_bar["value"] = 100
        self.btn_start_backup.set_enabled(True)
        self.btn_start_clone.set_enabled(True)
        self.btn_stop.set_enabled(False)

        self.lbl_sidebar_status.config(text="● COMPLETED", fg=COLOR_GREEN)
        self.card_status.update_value("READY")
        self.lbl_current_task.config(text="Status: Completed successfully" if success else "Status: Stopped")
        self.lbl_footer_status.config(text="Operation Finished")

        self.latest_history_entry = hist_entry

        title = "Operation Completed" if success else "Operation Stopped"
        mode_str = hist_entry.get("mode", "backup").title()
        zip_info = f"\nFull ZIP Archive:\n{hist_entry.get('zip_file')}" if hist_entry.get('zip_file') else ""
        msg = (
            f"{mode_str} Finished!\n\n"
            f"Pages Downloaded: {hist_entry.get('total_pages')}\n"
            f"Files Downloaded: {hist_entry.get('total_files')}\n"
            f"Data Size: {hist_entry.get('total_size_formatted')}\n"
            f"{zip_info}\n\n"
            f"Destination Folder:\n{hist_entry.get('folder')}"
        )
        messagebox.showinfo(title, msg)

    # --------------------------------------------------------------------------
    # LOGGING & UTILITIES
    # --------------------------------------------------------------------------
    def _append_log(self, ts, level, message):
        self.log_text.insert("end", f"[{ts}] ", "TIME")
        self.log_text.insert("end", f"[{level}] ", level)
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

    def _clear_activity_log(self):
        self.log_text.delete("1.0", "end")

    def _export_log_file(self):
        try:
            content = self.log_text.get("1.0", "end")
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Activity Log"
            )
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Exported", f"Log saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def _open_current_project_folder(self):
        if hasattr(self, "latest_history_entry") and self.latest_history_entry:
            folder = self.latest_history_entry.get("folder", "")
            if os.path.exists(folder):
                if IS_WINDOWS:
                    os.startfile(folder)
                else:
                    webbrowser.open(folder)
                return

        base_dir = self.config.get("download_dir")
        if os.path.exists(base_dir):
            if IS_WINDOWS:
                os.startfile(base_dir)
            else:
                webbrowser.open(base_dir)
        else:
            messagebox.showinfo("Notice", "No project directory created yet.")

    def _open_current_project_zip(self):
        if hasattr(self, "latest_history_entry") and self.latest_history_entry:
            zip_file = self.latest_history_entry.get("zip_file", "")
            if zip_file and os.path.exists(zip_file):
                if IS_WINDOWS:
                    os.startfile(zip_file)
                else:
                    webbrowser.open(zip_file)
                return
        messagebox.showinfo("Notice", "No ZIP archive available yet. Complete a backup or clone first.")

    def _open_latest_cloned_website(self):
        if hasattr(self, "latest_history_entry") and self.latest_history_entry:
            folder = self.latest_history_entry.get("folder", "")
            index_file = self.latest_history_entry.get("index_file", "") or os.path.join(folder, "index.html")
            if os.path.exists(index_file):
                webbrowser.open(f"file:///{os.path.abspath(index_file).replace(os.sep, '/')}")
                return
        messagebox.showinfo("Notice", "No cloned website available yet. Run 'Clone Website' first.")


# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================

def main():
    root = tk.Tk()
    app = ScitbossApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
