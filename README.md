<div align="center">

<img src="https://imgup.softkeybazar.com/uploads/1795537740_38e5c513281c.svg" alt="SCITBOSS WEBSITE BACKUP & CLONER PRO BANNER" width="100%" />

<br/>

# 🌐 SCITBOSS WEBSITE BACKUP & CLONER PRO
### *Production-Grade Windows Desktop Static Website Downloader, Deep Mirroring Engine & Automated Full ZIP Packager*

<br/>

[![Version](https://img.shields.io/badge/Version-2.0.0%20Pro%20Full%20Edition-F97316?style=for-the-badge&logo=rocket&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![GUI](https://img.shields.io/badge/GUI-Tkinter%20Dark%20Theme-0f172a?style=for-the-badge&logo=materialdesignicons&logoColor=38bdf8)](https://docs.python.org/3/library/tkinter.html)
[![Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-10B981?style=for-the-badge&logo=checkmarx&logoColor=white)](#)
[![Developer](https://img.shields.io/badge/Developer-SCITBOSS-F97316?style=for-the-badge&logo=github&logoColor=white)](https://github.com/scitboss)

<br/>

[🚀 Quick Start](#-quick-start) •
[✨ Key Features](#-key-features) •
[🧠 How It Works](#-how-it-works) •
[📦 Executable (.exe)](#-windows-standalone-executable-exe) •
[⚙️ Configuration](#-configuration--settings-guide) •
[🛡️ Responsible Use](#️-security--responsible-use-policy) •
[👤 Developer Credit](#-developer-credit)

---

</div>

## 🌟 Executive Summary

**SCITBOSS WEBSITE BACKUP & CLONER PRO** is an advanced, commercial-grade Windows desktop application engineered for deep crawling, static website cloning, local offline preservation, and **automated full ZIP archive bundling**.

Built entirely in a **single self-contained Python file** using Python's standard libraries and native Tkinter, it runs out of the box with **ZERO external pip module dependencies**. It includes high-speed multi-threaded asset downloading, automatic Gzip/Deflate HTTP decompression, lazy-loaded media detection, and complete relative link rewriting for 100% offline browsing.

---

## ✨ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>📦 Automated Full ZIP Packaging</h3>
      <p>Every backup or cloning operation automatically compiles the entire downloaded website into a compressed, ready-to-share <code>.zip</code> archive. Includes one-click <b>"Open ZIP"</b> shortcuts in the Dashboard and History panels.</p>
    </td>
    <td width="50%">
      <h3>⚡ Unlimited Deep Crawling Engine</h3>
      <p>No artificial page limits. Equipped with an <b>Unlimited Crawling Mode</b> that recursively navigates internal hyperlinks until every discovered page and resource on the domain is fully mirrored.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🖼️ Lazy-Loaded Media & All File Types</h3>
      <p>Specialized handling for modern frameworks (WordPress, Shopify, Webflow, React). Detects <code>data-src</code>, <code>data-srcset</code>, <code>data-original</code>, and <code>data-bg</code>, converting them into direct static offline images.</p>
    </td>
    <td width="50%">
      <h3>🚀 Multi-Threaded Parallel Downloader</h3>
      <p>Powered by <code>concurrent.futures.ThreadPoolExecutor</code>. Downloads dozens of images, stylesheets, scripts, and webfonts concurrently, accelerating download speeds up to <b>10x</b>.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🔄 100% Offline Static Site Rewriting</h3>
      <p>Transforms absolute and remote references into local relative paths in all HTML files and CSS stylesheets. Double-clicking the generated <code>index.html</code> opens the entire site offline in any web browser.</p>
    </td>
    <td width="50%">
      <h3>🎨 Modern Dark Theme Windows GUI</h3>
      <p>Features an ultra-sleek dark interface with native Windows 10/11 DWM dark title bars, High-DPI screen awareness, real-time KPI metric cards, and a live color-coded activity terminal.</p>
    </td>
  </tr>
</table>

---

## 📊 Mode Comparison: Backup vs. Cloner

| Capability | 💾 Website Backup Mode | ⚡ Website Cloner Mode |
| :--- | :---: | :---: |
| **Download HTML Web Pages** | ✅ Yes | ✅ Yes |
| **Download CSS, JS & Media Assets** | ✅ Yes | ✅ Yes |
| **Preserve Original Remote Server Structure** | ✅ Exact Mirror | ✅ Sanitized Offline Structure |
| **Rewrite Hyperlinks (`<a href>`) to Local HTML** | ❌ Raw URLs Kept | ✅ Rewritten to Local `.html` |
| **Rewrite CSS `url(...)` & `@import` to Assets** | ❌ Raw URLs Kept | ✅ Rewritten to Local Assets |
| **Mirror External CDNs (Google Fonts, cdnjs)** | ❌ Skipped | ✅ Saved into `assets/external/` |
| **Fix Lazy Images (`data-src` -> `src`)** | ❌ As-is | ✅ Converted for Offline Viewing |
| **Generate Root `index.html` Launcher** | ❌ Only if at root | ✅ Always Guaranteed |
| **Automated Full ZIP Archive (.zip)** | ✅ Included | ✅ Included |
| **Comprehensive `backup_report.txt`** | ✅ Generated | ✅ Generated |

---

## 🧠 How It Works

```mermaid
flowchart TD
    A["Target URL Entered"] --> B{"URL Validation & Normalization"}
    B -->|Prepend https:// & Verify| C["Deep Crawler Engine"]
    C --> D["Fetch HTML Pages (Gzip/Deflate Auto-Decompress)"]
    D --> E["HTML Parser & Asset Discovery"]
    
    E --> F["Internal Hyperlinks (<a href>)"]
    E --> G["Lazy Media (data-src, srcset)"]
    E --> H["Assets (CSS, JS, Fonts, Images)"]
    
    F -->|Recursive Scope Check| C
    G --> I["Parallel Multi-Threaded Worker Pool"]
    H --> I
    
    I --> J["Save Assets to Disk"]
    J --> K{"Mode Check"}
    
    K -->|Website Cloner| L["Static Link & CSS Rewriter"]
    K -->|Website Backup| M["Preserve Server Hierarchy"]
    
    L --> N["Generate Root index.html"]
    M --> O["Compile backup_report.txt"]
    N --> O
    
    O --> P["📦 Automated Full ZIP Archive Bundling"]
    P --> Q["Save to History (backup_history.json)"]
    Q --> R["🎉 Ready for 100% Offline Browsing!"]

    style A fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#fff
    style C fill:#1e293b,stroke:#f97316,stroke-width:2px,color:#fff
    style I fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#fff
    style L fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#fff
    style P fill:#0f172a,stroke:#f97316,stroke-width:3px,color:#fff
    style R fill:#047857,stroke:#10b981,stroke-width:3px,color:#fff
```

---

## 📁 Generated Output Directory & ZIP Archive Structure

When a backup or clone completes, the output directory and ZIP file are structured cleanly:

```
SCITBOSS_Backups/
│
├── Clone_example_com_20261124_221130/          <-- Unpacked Website Folder
│   ├── index.html                              <-- Double-click to browse offline!
│   ├── about.html
│   ├── contact.html
│   ├── assets/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── fonts.css
│   │   ├── js/
│   │   │   ├── app.bundle.js
│   │   │   └── vendor.min.js
│   │   ├── images/
│   │   │   ├── hero.webp
│   │   │   ├── logo.svg
│   │   │   └── banner.jpg
│   │   ├── fonts/
│   │   │   ├── inter-bold.woff2
│   │   │   └── roboto.woff2
│   │   └── external/                           <-- Mirrored external CDNs
│   │       ├── cdnjs.cloudflare.com/
│   │       └── fonts.googleapis.com/
│   └── backup_report.txt                       <-- Detailed execution audit
│
└── Clone_example_com_20261124_221130_FULL.zip  <-- 📦 Complete Compressed ZIP Archive
```

---

## 🚀 Quick Start


---

### Option 1: Run from Python Source Code
Requires Python 3.8+ on Windows:
```powershell
# Clone or download this repository
git clone https://github.com/scitboss/WEBSITE-BACKUP-CLONER-PRO.git
cd WEBSITE-BACKUP-CLONER-PRO

# Run the single-file application directly
python WEBSITE-BACKUP-CLONER-PRO.py
```


---


---

## 🖥️ Application Interface Tour

<div align="center">

| Navigation Panel | Features & Controls |
| :--- | :--- |
| **📊 Dashboard** | Real-time KPI cards (Pages Scanned, Files Downloaded, Size, Speed), progress percentage, live color-coded activity terminal, and quick-action buttons (`Open ZIP`, `Open Folder`, `Export Log`). |
| **💾 Website Backup** | Full server folder structure preservation, asset toggles (Images, CSS, JS, Fonts, Docs, Media), directory tree preview, and backup execution controls. |
| **⚡ Website Cloner** | Static offline mirroring with relative hyperlink rewriting, lazy image conversion, external CDN mirroring, and direct `Open Cloned Site in Browser` button. |
| **🕒 Backup History** | Persistent local JSON history tracking previous projects with one-click actions: `Open ZIP`, `Open Folder`, `Launch Website`, `View Report`, and `Delete Entry`. |
| **⚙️ Settings** | Performance sliders (Max Pages, Crawl Depth, Parallel Threads, Delay, Timeout, File Size), scope options (Unlimited Crawl, Subdomains, SSL Bypass), and default storage selector. |
| **ℹ️ About Software** | Developer credentials, GitHub links, PyInstaller compile tools, and responsible use policies. |

</div>

---

## ⚙️ Configuration & Settings Guide

The application stores user preferences locally in `~/.scitboss_backup_cloner/config.json`:

| Setting Key | Default Value | Description |
| :--- | :---: | :--- |
| `unlimited_crawl` | `False` | When enabled, removes page limits and crawls every discovered page on the domain. |
| `max_pages` | `500` | Maximum number of HTML pages to discover and download. |
| `max_depth` | `8` | Maximum recursion crawl depth from the root URL. |
| `thread_workers` | `6` | Number of concurrent worker threads for parallel asset downloading. |
| `auto_create_zip` | `True` | Automatically compiles the complete website into a `.zip` archive upon completion. |
| `request_delay` | `0.05s` | Politeness delay between HTTP requests to avoid rate-limiting. |
| `timeout` | `20s` | Connection timeout threshold in seconds. |
| `max_file_size_mb` | `150 MB` | Skips oversized single files exceeding this threshold to protect disk space. |
| `download_images` | `True` | Downloads PNG, JPG, JPEG, WebP, SVG, GIF, ICO, AVIF, TIFF. |
| `download_css` | `True` | Downloads CSS stylesheets, parses inline styles, and fetches embedded fonts. |
| `download_js` | `True` | Downloads JavaScript files, bundles, modules, and scripts. |
| `download_fonts` | `True` | Downloads WebFonts (WOFF, WOFF2, TTF, OTF, EOT). |
| `download_docs` | `True` | Downloads publicly linked documents (PDF, DOCX, TXT, CSV). |
| `download_media` | `True` | Downloads public audio and video files (MP4, MP3, WebM, WAV). |
| `ignore_ssl_errors`| `True` | Bypasses SSL certificate errors for self-signed, test, or legacy sites. |
| `respect_robots_txt`| `False` | When disabled, allows comprehensive full-site archiving without robot exclusions. |

---

## 🛡️ Security & Responsible Use Policy

**SCITBOSS WEBSITE BACKUP & CLONER PRO** is developed strictly for:
- Personal website backups and data ownership preservation.
- Authorized website migration and static archiving.
- Public web preservation and offline reference.
- Educational web architecture analysis and offline design inspection.

> [!IMPORTANT]
> **Strict Security Boundaries:**
> - The application operates exclusively through standard public HTTP/HTTPS client requests.
> - It **does NOT** bypass authentication gates, paywalls, or CAPTCHA challenges.
> - It **does NOT** attempt to access private backend code, database credentials, or server files.
> - Users are solely responsible for ensuring they have authorization to backup or clone target websites.

---

## 👤 Developer Credit

<div align="center">

```
================================================================================
                    PROJECT NAME: SCITBOSS WEBSITE BACKUP & CLONER PRO
                    DEVELOPED BY: SCITBOSS
                    GITHUB:       https://github.com/scitboss
                    EDITION:      2.0.0 Pro Full Edition
================================================================================
```

<br/>

[![GitHub Profile](https://img.shields.io/badge/GitHub-SCITBOSS-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/scitboss)
[![Repository](https://img.shields.io/badge/Repository-Web--Clone-F97316?style=for-the-badge&logo=git&logoColor=white)](https://github.com/scitboss)

<br/>

⭐ **If you find this project useful, consider giving it a Star on GitHub!** ⭐

</div>
