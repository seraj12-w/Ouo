# 🌐 Universal Stealth Link Resolver

Fast, fully background Playwright tool to resolve, bypass shorteners, and extract final destination links in Termux.

## ✨ Features
1. **⚡ Multi-Device Stealth Evasion**: Dynamic mobile & desktop device fingerprints (Android Galaxy S23/S22/Pixel, iPhone 15/14, Facebook In-App Browser `[FB_IAB/FB4A]`) with prototype webdriver cleanup, WebGL & userAgentData spoofing.
2. **👆 Touch Swipe & Human Interaction Engine**: Real mobile touchscreen swipe gestures, smooth scroll acceleration, natural reading pauses, and margin taps to achieve 0.8+ reCAPTCHA v3 scores.
3. **🪟 Smart Ad-Popup Handling**: Allows new-tab ad popups to load for 1.2–2.5s (genuine user glance) before closing, satisfying ad network viewability checks without stalling the session.
4. **⏳ Monetization Impression Dwell (`--dwell`)**: Configurable post-destination dwell time (15–30s) on landing pages to fire viewable beacons (IntersectionObserver) and register 100% valid ad impressions.
5. **🌐 Universal Shorteners Engine**: Supports OuO (`ouo.io`, `ouo.press`), standard redirect shorteners (`TinyURL`, `Bitly`, `Cuttly`, etc.), and countdown shorteners (`Droplink`, `GPLinks`, `Shrinkme`, etc.).
6. **🚀 Multi-Threading (Parallel Processing)**: Process multiple links concurrently (`-c 2` or `-c 3`) for 3x–5x faster execution.
7. **🛡️ Live Public Proxy Scraping & Validation**: Auto-scrapes and validates live HTTPS proxies online with parallel multi-threading.
8. **🔄 Auto-Rotation & Failover**: Automatically rotates through proxies and falls back to direct connection if a proxy drops.

## 📂 Project Structure
```text
~/link/
├── main.py          # Main Engine & Parallel Worker
├── stealth.py       # Anti-Detection & Cloudflare evasion scripts
├── solvers.py       # Universal Multi-Shortener solvers & recursive hops
├── proxy_manager.py # Public proxy scraper & concurrent HTTPS tester
├── links.txt        # Input links list (one per line)
├── proxies.txt      # Custom proxies list (optional)
├── requirements.txt # Dependencies
└── README.md        # Documentation & usage guide
```

## 🚀 How to Run

### 1. 🔄 Infinite Automated Loop Mode (`--loop`)
Runs continuously in an automated loop rotating through valid proxies across links:
```bash
link --loop -c 3 --delay 5
```

### 2. 🔢 Multi-Round Cycling (`--rounds`)
Runs a specified number of rounds (e.g., 10 cycles) across different proxies:
```bash
link --rounds 10 -c 3 --delay 4 -o impressions.txt
```

### 3. ⚡ Parallel Multi-Proxy Automation (`-c 3` or `-c 4`)
Runs 3 or 4 proxies simultaneously in parallel on separate links:
```bash
link -c 3
```

### 4. 💾 Save Output Destinations (`-o`)
Save all resolved target URLs into a clean text file:
```bash
link -c 2 -o resolved.txt
```

### 5. 🧹 Auto-Prune Non-Working Links (`--clean`)
Automatically removes dead/expired links from your input file (`links.txt`):
```bash
link --clean
```

### 6. 🌐 Harvest Thousands of Proxies (`--fetch-proxies`)
Scrapes and stores 12,000+ proxies from `hide.mn` and global feeds into `proxies_raw.txt`:
```bash
link --fetch-proxies
```

### 7. 🛡️ Auto-Validate Live Public Proxies (`-P`)
Auto-scrapes fresh working proxies, validates them against the target, and resolves through them:
```bash
link -P --proxy-limit 15
```

### 8. ⏳ High-Quality Monetization Dwell (`--dwell`)
Spends 20 seconds on destination reading content, triggering viewability beacons for valid impressions:
```bash
link --loop -c 2 --dwell 20
```

### 9. 📱 Target Specific Device Fingerprint (`--device`)
Simulate authentic mobile (Android / iOS) or desktop fingerprints:
```bash
link --device android -c 2
```

### 10. Single Link
```bash
link https://ouo.io/9dqjngQ
```

### 11. Custom Single Proxy
```bash
link https://ouo.io/rqbnyo7 -p http://user:pass@ip:port
```
