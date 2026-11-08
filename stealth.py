"""
stealth.py - Anti-Bot & Multi-Device Stealth Evasion Engine for Playwright.
Features:
  1. 📱 Dynamic Device Fingerprints (Android Mobile, iOS iPhone, Windows Desktop)
  2. ⚡ In-App Social Browser Emulation (Facebook FB_IAB / Chrome Mobile) for Top CPM
  3. 🛡️ Prototype-level webdriver cleanup, userAgentData, hardware, plugins & WebGL spoofing
  4. 👁️ Always-Visible / Document Focus hooks for 100% Ad Viewability Beacon triggers
"""

import random

# Real-world Android devices from high-CPM regions
ANDROID_DEVICES = [
    {"model": "SM-S918B", "brand": "Samsung", "name": "Galaxy S23 Ultra", "width": 412, "height": 915, "scale": 3},
    {"model": "SM-S911B", "brand": "Samsung", "name": "Galaxy S23", "width": 393, "height": 851, "scale": 3},
    {"model": "SM-S908B", "brand": "Samsung", "name": "Galaxy S22 Ultra", "width": 412, "height": 915, "scale": 3},
    {"model": "SM-A546B", "brand": "Samsung", "name": "Galaxy A54 5G", "width": 412, "height": 915, "scale": 2.5},
    {"model": "Pixel 8 Pro", "brand": "Google", "name": "Pixel 8 Pro", "width": 412, "height": 892, "scale": 3.5},
    {"model": "Pixel 7", "brand": "Google", "name": "Pixel 7", "width": 412, "height": 915, "scale": 2.6},
    {"model": "Redmi Note 12", "brand": "Xiaomi", "name": "Redmi Note 12", "width": 393, "height": 873, "scale": 2.75},
    {"model": "POCO X5 Pro", "brand": "Xiaomi", "name": "POCO X5 Pro", "width": 393, "height": 873, "scale": 2.75},
    {"model": "OnePlus 11", "brand": "OnePlus", "name": "OnePlus 11", "width": 412, "height": 919, "scale": 3.5},
]

# Real-world iPhones
IPHONE_DEVICES = [
    {"model": "iPhone 15 Pro Max", "width": 430, "height": 932, "scale": 3, "ios": "17_2"},
    {"model": "iPhone 15 Pro", "width": 393, "height": 852, "scale": 3, "ios": "17_1"},
    {"model": "iPhone 14 Pro Max", "width": 430, "height": 932, "scale": 3, "ios": "16_6"},
    {"model": "iPhone 14", "width": 390, "height": 844, "scale": 3, "ios": "16_6"},
    {"model": "iPhone 13 Pro", "width": 390, "height": 844, "scale": 3, "ios": "16_5"},
    {"model": "iPhone 13", "width": 390, "height": 844, "scale": 3, "ios": "16_5"},
]

CHROME_MOBILE_VERSIONS = [
    "124.0.6367.82", "125.0.6422.165", "126.0.6478.122",
    "127.0.6533.100", "128.0.6613.88", "129.0.6668.70"
]

FB_APP_VERSIONS = [
    "480.0.0.45.109", "482.0.0.38.109", "484.0.0.39.110", "485.0.0.42.110"
]

WINDOWS_RESOLUTIONS = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
]

def generate_device_profile(device_type: str = "auto") -> dict:
    """
    Generates an authentic device fingerprint matching real mobile/desktop specs.
    device_type: 'auto' (70% Android, 25% iOS, 5% Windows), 'android', 'ios', 'mobile', or 'desktop'.
    """
    mode = (device_type or "auto").lower()
    if mode in ("auto", "random"):
        # 70% Android, 25% iOS, 5% Windows (Mobile yields highest CPM & easiest Cloudflare pass)
        chosen_type = random.choices(["android", "ios", "windows"], weights=[70, 25, 5], k=1)[0]
    elif mode == "mobile":
        chosen_type = random.choices(["android", "ios"], weights=[75, 25], k=1)[0]
    elif mode in ("android", "ios", "windows"):
        chosen_type = mode
    else:
        chosen_type = "android"

    if chosen_type == "android":
        dev = random.choice(ANDROID_DEVICES)
        chrome_ver = random.choice(CHROME_MOBILE_VERSIONS)
        major_ver = chrome_ver.split(".")[0]
        android_ver = random.choice(["13", "14"])

        # 40% chance of Facebook In-App Browser (common for referral shortlink traffic)
        if random.random() < 0.40:
            fb_ver = random.choice(FB_APP_VERSIONS)
            ua = (f"Mozilla/5.0 (Linux; Android {android_ver}; {dev['model']} Build/UP1A.231005.007; wv) "
                  f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_ver} "
                  f"Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/{fb_ver};]")
            label = f"{dev['name']} (Android {android_ver} - FB In-App)"
        else:
            ua = (f"Mozilla/5.0 (Linux; Android {android_ver}; {dev['model']}) "
                  f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/537.36")
            label = f"{dev['name']} (Android {android_ver} - Chrome {major_ver})"

        return {
            "device_os": "android",
            "label": label,
            "viewport": {"width": dev["width"], "height": dev["height"]},
            "screen_width": int(dev["width"] * dev["scale"]),
            "screen_height": int(dev["height"] * dev["scale"]),
            "is_mobile": True,
            "has_touch": True,
            "device_scale_factor": dev["scale"],
            "max_touch_points": 5,
            "user_agent": ua,
            "platform": "Linux armv8l",
            "webgl_vendor": "Qualcomm",
            "webgl_renderer": "ANGLE (Qualcomm, Adreno (TM) 740, OpenGL ES 3.2)",
            "major_version": major_ver
        }

    elif chosen_type == "ios":
        dev = random.choice(IPHONE_DEVICES)
        ios_ver = dev["ios"]
        ios_dot = ios_ver.replace("_", ".")

        if random.random() < 0.35:
            fb_ver = random.choice(FB_APP_VERSIONS)
            ua = (f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_ver} like Mac OS X) "
                  f"AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
                  f"[FBAN/FBIOS;FBDV/{dev['model']};FBMD/iPhone;FBSN/iOS;FBSV/{ios_dot};FBSS/3;FBLC/en_US;FBAV/{fb_ver};]")
            label = f"{dev['model']} (iOS {ios_dot} - FB In-App)"
        else:
            ua = (f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_ver} like Mac OS X) "
                  f"AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
            label = f"{dev['model']} (iOS {ios_dot} - Safari)"

        return {
            "device_os": "ios",
            "label": label,
            "viewport": {"width": dev["width"], "height": dev["height"]},
            "screen_width": int(dev["width"] * dev["scale"]),
            "screen_height": int(dev["height"] * dev["scale"]),
            "is_mobile": True,
            "has_touch": True,
            "device_scale_factor": dev["scale"],
            "max_touch_points": 5,
            "user_agent": ua,
            "platform": "iPhone",
            "webgl_vendor": "Apple Inc.",
            "webgl_renderer": "Apple GPU",
            "major_version": "17"
        }

    else:
        res = random.choice(WINDOWS_RESOLUTIONS)
        chrome_ver = random.choice(CHROME_MOBILE_VERSIONS)
        major_ver = chrome_ver.split(".")[0]
        ua = (f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              f"(KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36")
        return {
            "device_os": "windows",
            "label": f"Windows 10/11 PC ({res['width']}x{res['height']})",
            "viewport": {"width": res["width"], "height": res["height"]},
            "screen_width": res["width"],
            "screen_height": res["height"],
            "is_mobile": False,
            "has_touch": False,
            "device_scale_factor": 1,
            "max_touch_points": 0,
            "user_agent": ua,
            "platform": "Win32",
            "webgl_vendor": "Intel Inc.",
            "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "major_version": major_ver
        }

def build_stealth_js(profile: dict = None) -> str:
    """
    Generates dynamic stealth injection script matching the specified profile.
    """
    if not profile:
        profile = generate_device_profile("android")

    platform = profile.get("platform", "Linux armv8l")
    is_mobile = "true" if profile.get("is_mobile", True) else "false"
    max_touch = profile.get("max_touch_points", 5 if is_mobile == "true" else 0)
    webgl_vendor = profile.get("webgl_vendor", "Qualcomm")
    webgl_renderer = profile.get("webgl_renderer", "Adreno (TM) 740")
    screen_w = profile.get("screen_width", profile["viewport"]["width"])
    screen_h = profile.get("screen_height", profile["viewport"]["height"])
    major_ver = profile.get("major_version", "128")

    return f"""
(function() {{
    // 1. Prototype-level webdriver cleanup
    try {{
        const proto = Object.getPrototypeOf(navigator);
        if (proto) {{
            delete proto.webdriver;
            Object.defineProperty(proto, 'webdriver', {{
                get: () => undefined,
                configurable: true,
                enumerable: true
            }});
        }}
        delete navigator.webdriver;
    }} catch (e) {{}}

    // 2. Mock clean window.chrome object
    if (!window.chrome) {{
        window.chrome = {{
            app: {{
                isInstalled: false,
                InstallState: {{ DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' }},
                RunningState: {{ CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }}
            }},
            loadTimes: function() {{}},
            csi: function() {{}}
        }};
    }}

    // 3. Dynamic Navigator platform & touch properties
    try {{
        const proto = Object.getPrototypeOf(navigator);
        Object.defineProperty(proto, 'platform', {{ get: () => '{platform}', configurable: true }});
        Object.defineProperty(proto, 'vendor', {{ get: () => 'Google Inc.', configurable: true }});
        Object.defineProperty(proto, 'languages', {{ get: () => ['en-US', 'en'], configurable: true }});
        Object.defineProperty(proto, 'hardwareConcurrency', {{ get: () => 8, configurable: true }});
        Object.defineProperty(proto, 'deviceMemory', {{ get: () => 8, configurable: true }});
        Object.defineProperty(proto, 'maxTouchPoints', {{ get: () => {max_touch}, configurable: true }});

        // Mock navigator.userAgentData
        const userAgentDataMock = {{
            brands: [
                {{ brand: 'Chromium', version: '{major_ver}' }},
                {{ brand: 'Not;A=Brand', version: '24' }},
                {{ brand: 'Google Chrome', version: '{major_ver}' }}
            ],
            mobile: {is_mobile},
            platform: '{profile["device_os"].capitalize()}',
            getHighEntropyValues: function(hints) {{
                return Promise.resolve({{
                    architecture: 'arm',
                    bitness: '64',
                    brands: this.brands,
                    mobile: {is_mobile},
                    model: '',
                    platform: '{profile["device_os"].capitalize()}',
                    platformVersion: '14.0.0',
                    uaFullVersion: '{major_ver}.0.0.0'
                }});
            }}
        }};
        Object.defineProperty(proto, 'userAgentData', {{ get: () => userAgentDataMock, configurable: true }});
    }} catch (e) {{}}

    // 4. Mock Screen dimensions
    try {{
        Object.defineProperty(window.screen, 'availWidth', {{ get: () => {screen_w}, configurable: true }});
        Object.defineProperty(window.screen, 'availHeight', {{ get: () => {screen_h}, configurable: true }});
        Object.defineProperty(window.screen, 'width', {{ get: () => {screen_w}, configurable: true }});
        Object.defineProperty(window.screen, 'height', {{ get: () => {screen_h}, configurable: true }});
        Object.defineProperty(window.screen, 'colorDepth', {{ get: () => 24, configurable: true }});
    }} catch (e) {{}}

    // 5. Ensure document is focused and visible for Ad Viewability beacons (IntersectionObserver)
    try {{
        Object.defineProperty(document, 'hasFocus', {{ value: () => true, configurable: true }});
        Object.defineProperty(document, 'visibilityState', {{ get: () => 'visible', configurable: true }});
        Object.defineProperty(document, 'hidden', {{ get: () => false, configurable: true }});
    }} catch (e) {{}}

    // 6. Mock WebGL Vendor & Renderer
    try {{
        const getParam1 = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{webgl_vendor}';
            if (param === 37446) return '{webgl_renderer}';
            return getParam1.apply(this, arguments);
        }};

        if (typeof WebGL2RenderingContext !== 'undefined') {{
            const getParam2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(param) {{
                if (param === 37445) return '{webgl_vendor}';
                if (param === 37446) return '{webgl_renderer}';
                return getParam2.apply(this, arguments);
            }};
        }}
    }} catch (e) {{}}

    // 7. Mock Notification permissions
    if (window.navigator.permissions && window.navigator.permissions.query) {{
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = function(parameters) {{
            return parameters && parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission || 'default' }}) :
                originalQuery.apply(this, arguments);
        }};
    }}
}})();
"""

STEALTH_CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=IsolateOrigins,site-per-process",
]

DEFAULT_USER_AGENT = "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.88 Mobile Safari/537.36"

DEFAULT_VIEWPORT = {
    "width": 393,
    "height": 851
}

STEALTH_JS = build_stealth_js()

def apply_stealth(context, profile: dict = None):
    """
    Applies enhanced multi-device stealth scripts to a Playwright browser context.
    """
    script = build_stealth_js(profile) if profile else STEALTH_JS
    context.add_init_script(script)
