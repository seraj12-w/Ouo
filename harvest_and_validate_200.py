#!/data/data/com.termux/files/usr/bin/env python3
"""
harvest_and_validate_200.py
Fast proxy scraper and multi-threaded validator.
Scrapes thousands of fresh candidates from top SOCKS5 & HTTP feeds,
validates each candidate for live TCP and proxy tunneling,
and writes 200 unique verified proxies to proxies.txt and clean_proxies.txt.
"""

import os
import re
import sys
import time
import socket
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROXIES_TXT = os.path.join(SCRIPT_DIR, "proxies.txt")
CLEAN_PROXIES_TXT = os.path.join(SCRIPT_DIR, "clean_proxies.txt")
RAW_PROXIES_TXT = os.path.join(SCRIPT_DIR, "proxies_raw.txt")

SOCKS5_FEEDS = [
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
    "https://spys.me/socks.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks5_proxies.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
]

HTTP_FEEDS = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt",
    "https://spys.me/proxy.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
]

def fetch_feed(url, prefix):
    results = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b)", text)
            for m in matches:
                results.append(f"{prefix}{m}")
    except Exception:
        pass
    return results

def scrape_all_candidates():
    print("🌐 Scraping thousands of fresh proxies from online feeds...")
    candidates = []
    seen = set()

    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = []
        for url in SOCKS5_FEEDS:
            futs.append(ex.submit(fetch_feed, url, "socks5://"))
        for url in HTTP_FEEDS:
            futs.append(ex.submit(fetch_feed, url, "http://"))

        for f in as_completed(futs):
            for item in f.result():
                ip = item.split("://")[-1].split(":")[0]
                if ip not in seen:
                    seen.add(ip)
                    candidates.append(item)

    print(f"✨ Total unique fresh candidates gathered: {len(candidates)}\n")
    return candidates

def validate_socks5(host, port, timeout=2.5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, int(port)))
        s.sendall(b'\x05\x01\x00')
        resp = s.recv(2)
        if resp != b'\x05\x00':
            s.close()
            return False
        # Tunnel to ouo.press on port 443
        domain_b = b'ouo.press'
        req = b'\x05\x01\x00\x03' + len(domain_b).to_bytes(1, 'big') + domain_b + (443).to_bytes(2, 'big')
        s.sendall(req)
        resp2 = s.recv(10)
        s.close()
        return len(resp2) >= 2 and resp2[0] == 5 and resp2[1] == 0
    except Exception:
        return False

def validate_http(raw_proxy, timeout=3.0):
    try:
        h = urllib.request.ProxyHandler({"http": raw_proxy, "https": raw_proxy})
        opener = urllib.request.build_opener(h)
        req = urllib.request.Request("http://checkip.amazonaws.com", headers={"User-Agent": "Mozilla/5.0"})
        with opener.open(req, timeout=timeout) as resp:
            if resp.status == 200:
                return True
    except Exception:
        return False
    return False

def test_proxy(proxy_entry):
    t0 = time.time()
    if proxy_entry.startswith("socks5://"):
        target = proxy_entry.replace("socks5://", "")
        host, port = target.split(":")
        ok = validate_socks5(host, port, timeout=2.0)
    else:
        ok = validate_http(proxy_entry, timeout=2.5)

    if ok:
        latency = round((time.time() - t0) * 1000)
        return proxy_entry, latency
    return None

def main():
    target_count = 200
    if len(sys.argv) > 1:
        try:
            target_count = int(sys.argv[1])
        except ValueError:
            pass

    candidates = scrape_all_candidates()
    if not candidates:
        print("❌ No candidate proxies could be retrieved.")
        sys.exit(1)

    # Save candidates to RAW_PROXIES_TXT for background replenishment pool
    try:
        with open(RAW_PROXIES_TXT, "w", encoding="utf-8") as f:
            for c in candidates:
                f.write(f"{c}\n")
        print(f"💾 Saved {len(candidates)} raw candidates to {RAW_PROXIES_TXT}\n")
    except Exception:
        pass

    print(f"🔍 Validating proxies concurrently to reach {target_count} live proxies...")
    valid_proxies = []
    seen_ips = set()

    # Clear old proxies file immediately
    with open(PROXIES_TXT, "w", encoding="utf-8") as f_act, open(CLEAN_PROXIES_TXT, "w", encoding="utf-8") as f_cln:
        f_act.flush()
        f_cln.flush()

        batch_size = 500
        for i in range(0, len(candidates), batch_size):
            if len(valid_proxies) >= target_count:
                break

            batch = candidates[i:i + batch_size]
            t_batch0 = time.time()

            with ThreadPoolExecutor(max_workers=80) as executor:
                futs = [executor.submit(test_proxy, c) for c in batch]
                for f in as_completed(futs):
                    res = f.result()
                    if res:
                        p, lat = res
                        ip = p.split("://")[-1].split(":")[0]
                        if ip not in seen_ips:
                            seen_ips.add(ip)
                            valid_proxies.append(p)
                            f_act.write(f"{p}\n")
                            f_act.flush()
                            f_cln.write(f"{p}\n")
                            f_cln.flush()
                            print(f"   🎯 [{len(valid_proxies):3d}/{target_count}] Live ({lat:4d}ms): {p}")

                            if len(valid_proxies) >= target_count:
                                executor.shutdown(wait=False, cancel_futures=True)
                                break

            t_elapsed = round(time.time() - t_batch0, 1)
            print(f"   ℹ️ Batch [{i//batch_size + 1}] processed {len(batch)} candidates in {t_elapsed}s | Live so far: {len(valid_proxies)}")

    print("\n" + "=" * 65)
    print(f"🎉 Validation Complete! Total verified working proxies: {len(valid_proxies)}")
    print(f"💾 Written to: {PROXIES_TXT}")
    print(f"💾 Written to: {CLEAN_PROXIES_TXT}")
    print("=" * 65)

if __name__ == "__main__":
    main()
