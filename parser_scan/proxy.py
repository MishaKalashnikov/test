import zipfile

PROXY_HOST = "res.proxy-seller.io"  # IP прокси
PROXY_PORT = "10000"          # Порт прокси
PROXY_USER = "3b5e2cdf3f7f72b9" # Логин
PROXY_PASS = "RNW78Fm5" # Пароль

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = f"""
var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{PROXY_HOST}",
                port: parseInt({PROXY_PORT})
            }},
            bypassList: ["localhost"]
        }}
    }};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
function callbackFn(details) {{
    return {{
        authCredentials: {{
            username: "{PROXY_USER}",
            password: "{PROXY_PASS}"
        }}
    }};
}}
chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
);
"""

plugin_file = "proxy_auth_plugin.zip"

with zipfile.ZipFile(plugin_file, 'w') as zp:
    zp.writestr("manifest.json", manifest_json)
    zp.writestr("background.js", background_js)

print(f"✅ Плагин прокси `{plugin_file}` создан.")
