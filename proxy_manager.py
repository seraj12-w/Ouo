"""
proxy_manager.py - Scrapes public proxy lists (including hide.mn / hidemy.name)
and validates them concurrently against target shorteners (ouo.press).
Harvests thousands of fresh proxies across HTTP, HTTPS, and SOCKS5.
"""

import sys
import os
import re
import time
import random
import socket
import threading
import collections
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

PRIMARY_PROXY_SOURCES = [
    # hide.mn and hidemy.name live proxy lists
    "https://hide.mn/en/proxy-list/",
    "https://hidemy.name/en/proxy-list/",
    "https://hide.mn/ru/proxy-list/",
    "https://hide.mn/es/proxy-list/",

    # High-volume verified global proxy feeds
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks5_proxies.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt",
    "https://spys.me/socks.txt",
    "https://spys.me/proxy.txt",
]

def fetch_all_raw_proxies(sources=None, limit=None) -> list:
    """
    Scrapes thousands of fresh candidate proxies from hide.mn and high-volume live feeds.
    """
    if sources is None:
        sources = PRIMARY_PROXY_SOURCES

    candidates = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    print("🌐 Harvesting proxies from hide.mn and live online repositories...")

    for src in sources:
        try:
            req = urllib.request.Request(src, headers=headers)
            with urllib.request.urlopen(req, timeout=7) as resp:
                text = resp.read().decode("utf-8", errors="ignore")

                is_socks = "socks5" in src.lower()
                prefix = "socks5://" if is_socks else "http://"

                # 1. Check HTML table format (hide.mn / hidemy.name tables)
                html_matches = re.findall(r"<tr><td>(\d+\.\d+\.\d+\.\d+)</td>\s*<td>(\d+)</td>", text)
                if html_matches:
                    for ip, port in html_matches:
                        candidates.append(f"http://{ip}:{port}")

                # 2. Check raw IP:PORT format
                raw_matches = re.findall(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b)", text)
                if raw_matches:
                    for p in raw_matches:
                        candidates.append(f"{prefix}{p}")

                label = "hide.mn / hidemy.name" if "hide" in src else src.split("/")[-1]
                count = len(html_matches) if html_matches else len(raw_matches)
                print(f"   📥 Scraped {count:5d} proxies from: {label}")

        except Exception:
            pass

    # Deduplicate by pure IP so we don't pick multiple ports from the same host
    unique_by_ip = {}
    for p in candidates:
        clean_ip = p.split("://")[-1].split(":")[0]
        if clean_ip not in unique_by_ip:
            unique_by_ip[clean_ip] = p

    deduped = list(unique_by_ip.values())
    if limit:
        deduped = deduped[:limit]

    print(f"✨ Aggregation complete! Total unique IP proxies gathered: {len(deduped)}\n")
    return deduped

def test_proxy(proxy_str: str, test_url: str = "https://ouo.press", timeout: int = 4):
    """
    Tests if a proxy is live.
    Supports HTTP/HTTPS via urllib and SOCKS5 via raw socket handshake.
    """
    raw = proxy_str.strip()
    is_socks5 = raw.startswith("socks5://")

    if is_socks5:
        # Full SOCKS5 handshake & connect verification to ouo.press:443
        try:
            target = raw.replace("socks5://", "")
            if "@" in target:
                target = target.split("@")[-1]
            host, port = target.split(":")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, int(port)))
            # Step 1: Greeting
            s.sendall(b'\x05\x01\x00')
            resp = s.recv(2)
            if resp != b'\x05\x00':
                s.close()
                return None
            # Step 2: CONNECT to ouo.press:443
            domain_b = b"ouo.press"
            req = b'\x05\x01\x00\x03' + len(domain_b).to_bytes(1, 'big') + domain_b + (443).to_bytes(2, 'big')
            s.sendall(req)
            resp2 = s.recv(10)
            s.close()
            if len(resp2) >= 2 and resp2[0] == 5 and resp2[1] == 0:
                return raw
        except Exception:
            return None
        return None

    if not (raw.startswith("http://") or raw.startswith("https://")):
        raw = f"http://{raw}"

    proxy_handler = urllib.request.ProxyHandler({
        "http": raw,
        "https": raw
    })
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(
        test_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            if resp.status == 200:
                body = resp.read(500).decode("utf-8", errors="ignore")
                if "Just a moment" not in body:
                    return raw
    except Exception:
        return None
    return None

def scrape_and_validate_proxies(limit: int = 10, max_workers: int = 50, timeout: int = 4, test_url: str = "https://ouo.press"):
    """
    Scrapes thousands of proxies from hide.mn & mirrors, then validates them
    concurrently to return fast, verified active proxies.
    """
    candidates = fetch_all_raw_proxies()
    if not candidates:
        print("⚠️ No proxy candidates found.")
        return []

    print(f"🔍 Validating proxies specifically against {test_url} (threads={max_workers}, timeout={timeout}s)...")

    valid_proxies = []
    seen_ips = set()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_proxy, p, test_url, timeout): p for p in candidates}
        for future in as_completed(futures):
            res = future.result()
            if res:
                clean_ip = res.split("://")[-1].split(":")[0]
                if clean_ip in seen_ips:
                    continue
                seen_ips.add(clean_ip)
                valid_proxies.append(res)
                print(f"   🎯 Verified UNIQUE live proxy [{len(valid_proxies)}/{limit}]: {res}")
                if len(valid_proxies) >= limit:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

    print(f"🎉 Validation complete: {len(valid_proxies)} live proxies ready!\n")
    return valid_proxies

class DynamicProxyPool:
    """
    Thread-safe dynamic proxy pool that:
      1. Rotates valid proxies round-robin across concurrent workers.
      2. Continuously maintains 15-25 live verified proxies in the background.
      3. Discards failing proxies immediately (max_failures=1) and replaces them.
      4. Cycles through all raw archive candidates without re-testing dead ones.
      5. Auto-scrapes from live feeds if local archives are depleted.
    """
    def __init__(self, initial_proxies=None, min_threshold=8, target_size=20,
                 raw_file=None, active_file=None, max_failures=1):
        self.lock = threading.Lock()
        self.active_proxies = collections.deque(initial_proxies or [])
        self.failures = collections.defaultdict(int)
        self.successes = collections.defaultdict(int)
        self.min_threshold = min_threshold
        self.target_size = target_size
        self.max_failures = max_failures
        self.raw_file = raw_file
        self.active_file = active_file
        self.is_refilling = False
        self.candidate_index = 0
        self.raw_candidates = []

        self._load_raw_candidates()

        # If pool size is below target, start background refill immediately
        if len(self.active_proxies) < self.target_size:
            self.is_refilling = True
            threading.Thread(target=self._background_refill, daemon=True).start()

    def _load_raw_candidates(self):
        candidates = []
        if self.raw_file and os.path.isfile(self.raw_file):
            try:
                with open(self.raw_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and ":" in line and not line.startswith("#"):
                            candidates.append(line)
            except Exception:
                pass

        if len(candidates) < 100:
            candidates = fetch_all_raw_proxies(limit=2000)

        random.shuffle(candidates)
        self.raw_candidates = candidates
        self.candidate_index = 0

    def size(self) -> int:
        with self.lock:
            return len(self.active_proxies)

    def get_proxy(self):
        """
        Retrieves the next healthy proxy and rotates it to the end of queue.
        Triggers auto-refill if pool drops below threshold.
        """
        should_refill = False
        with self.lock:
            if not self.active_proxies:
                if not self.is_refilling:
                    self.is_refilling = True
                    should_refill = True
                p = None
            else:
                p = self.active_proxies[0]
                self.active_proxies.rotate(-1)
                if len(self.active_proxies) < self.min_threshold and not self.is_refilling:
                    self.is_refilling = True
                    should_refill = True

        if should_refill:
            threading.Thread(target=self._background_refill, daemon=True).start()

        return p

    def report_success(self, proxy_dict):
        """
        Records a successful operation using this proxy and resets failures.
        """
        if not proxy_dict:
            return
        server = proxy_dict.get("server")
        with self.lock:
            self.failures[server] = 0
            self.successes[server] += 1

    def report_failure(self, proxy_dict, reason=None):
        """
        Records a failure for this proxy. Discards it if max_failures reached.
        """
        if not proxy_dict:
            return
        server = proxy_dict.get("server")
        display = proxy_dict.get("display", server)

        should_refill = False
        with self.lock:
            self.failures[server] += 1
            fails = self.failures[server]

            if fails >= self.max_failures:
                self.active_proxies = collections.deque(
                    p for p in self.active_proxies if p.get("server") != server
                )
                print(f"⚠️ [Proxy Discarded] {display} removed from pool ({reason or 'dropped'})")
                print(f"   ℹ️ Active proxies remaining in pool: {len(self.active_proxies)}")

                if len(self.active_proxies) < self.min_threshold and not self.is_refilling:
                    self.is_refilling = True
                    should_refill = True

        if should_refill:
            threading.Thread(target=self._background_refill, daemon=True).start()

    def _background_refill(self):
        """
        Background worker that continuously harvests and validates fresh proxies
        from raw archives or live feeds to maintain target_size.
        """
        try:
            print(f"\n🔄 [Auto-Refill] Active proxies below target ({self.size()}/{self.target_size}). Harvesting & validating fresh proxies...")
            batch_size = 50

            while self.size() < self.target_size:
                if self.candidate_index >= len(self.raw_candidates):
                    self._load_raw_candidates()
                    if not self.raw_candidates:
                        break

                batch = self.raw_candidates[self.candidate_index:self.candidate_index + batch_size]
                self.candidate_index += batch_size

                if not batch:
                    break

                newly_verified = []
                with ThreadPoolExecutor(max_workers=35) as ex:
                    futs = {ex.submit(test_proxy, p, "https://ouo.press", 3): p for p in batch}
                    for f in as_completed(futs):
                        res = f.result()
                        if res:
                            clean = res if "://" in res else f"http://{res}"
                            newly_verified.append({
                                "server": clean,
                                "display": clean
                            })
                            print(f"   🎯 [Auto-Refill] Verified fresh proxy: {clean}")

                if newly_verified:
                    with self.lock:
                        for p in newly_verified:
                            if not any(x.get("server") == p.get("server") for x in self.active_proxies):
                                self.active_proxies.append(p)
                        total_active = len(self.active_proxies)
                    print(f"🎉 [Auto-Refill] Added {len(newly_verified)} proxies! Current pool: {total_active} active\n")

                    if self.active_file:
                        with self.lock:
                            current_active = list(self.active_proxies)
                        if current_active:
                            try:
                                with open(self.active_file, "w", encoding="utf-8") as af:
                                    for p in current_active:
                                        af.write(f"{p.get('server')}\n")
                            except Exception:
                                pass

                time.sleep(1)

        except Exception:
            pass
        finally:
            with self.lock:
                self.is_refilling = False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape and validate thousands of proxies from hide.mn & global feeds.")
    parser.add_argument("--save-thousands", action="store_true", help="Download thousands of raw proxies and save to proxies_raw.txt")
    parser.add_argument("--validate", type=int, default=5, metavar="N", help="Validate and save N working proxies (default: 5)")
    parser.add_argument("-o", "--output", default="proxies.txt", help="Output file path (default: proxies.txt)")
    args = parser.parse_args()

    if args.save_thousands:
        raw = fetch_all_raw_proxies()
        out = "proxies_raw.txt" if args.output == "proxies.txt" else args.output
        with open(out, "w", encoding="utf-8") as f:
            for p in raw:
                f.write(f"{p}\n")
        print(f"💾 Saved {len(raw)} raw proxies to: {out}")
    else:
        live = scrape_and_validate_proxies(limit=args.validate)
        if live:
            with open(args.output, "w", encoding="utf-8") as f:
                for p in live:
                    f.write(f"{p}\n")
            print(f"💾 Saved {len(live)} validated working proxies to: {args.output}")
