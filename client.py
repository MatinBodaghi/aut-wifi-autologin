"""
AUT Wi-Fi & Internet Client
Built using Python Standard Library (zero external dependencies).
Handles captive portal detection, Wi-Fi SSID identification, and authentication against login.aut.ac.ir / internet.aut.ac.ir
"""

import subprocess
import re
import urllib.request
import urllib.parse
import ssl

PROBE_URL = "http://connectivitycheck.gstatic.com/generate_204"

class AutWifiClient:
    def __init__(self, config: dict):
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.gateway_url = config.get("gateway_url", "https://login.aut.ac.ir/login")
        self.status_url = config.get("status_url", "https://login.aut.ac.ir/status")
        self.logout_url = config.get("logout_url", "https://login.aut.ac.ir/logout")
        self.wifi_ssids = config.get("wifi_ssids", ["AUT", "AUT-Student", "AUT-Dorm", "Amirkabir"])
        
        # SSL context ignoring verification for captive portal gateways
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

    def get_current_wifi_ssid(self) -> str | None:
        """
        Retrieves the SSID of the currently connected Wi-Fi network on Windows.
        """
        try:
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                shell=False
            ).decode("utf-8", errors="ignore")

            for line in output.splitlines():
                line = line.strip()
                if re.match(r"^SSID\s*:\s*(.+)$", line, re.IGNORECASE):
                    ssid = line.split(":", 1)[1].strip()
                    if ssid:
                        return ssid
        except Exception:
            pass
        return None

    def is_aut_wifi(self) -> bool:
        """
        Checks if the currently connected Wi-Fi is an AUT network.
        If no Wi-Fi interface is found (e.g., ethernet cable in dorm/lab), returns True to allow login check.
        """
        ssid = self.get_current_wifi_ssid()
        if not ssid:
            # Might be connected via LAN/Ethernet in university labs or dorms
            return True
        return any(keyword.lower() in ssid.lower() for keyword in self.wifi_ssids)

    def is_internet_accessible(self) -> bool:
        """
        Checks whether full internet access is available (returns HTTP 204 from probe server).
        """
        try:
            req = urllib.request.Request(PROBE_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 204
        except urllib.error.HTTPError as e:
            return e.code == 204
        except Exception:
            return False

    def is_behind_captive_portal(self) -> bool:
        """
        Determines whether internet traffic is being hijacked by the university captive portal.
        """
        return not self.is_internet_accessible()

    def login(self) -> tuple[bool, str]:
        """
        Submits login credentials to the AUT login gateway.
        """
        if not self.username or not self.password:
            return False, "نام کاربری یا رمز عبور تنظیم نشده است (فایل config.json را بررسی کنید)."

        post_data = urllib.parse.urlencode({
            "username": self.username,
            "password": self.password,
            "erase-cookie": "false",
            "popup": "false"
        }).encode("utf-8")

        urls_to_try = [self.gateway_url, "https://internet.aut.ac.ir/login", "http://login.aut.ac.ir/login"]
        last_error = ""

        for url in urls_to_try:
            try:
                req = urllib.request.Request(
                    url,
                    data=post_data,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AUT-Wifi-AutoLogin/1.0",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                
                with urllib.request.urlopen(req, timeout=5, context=self.ssl_ctx) as resp:
                    resp_body = resp.read().decode("utf-8", errors="ignore").lower()

                # Check if internet opened up
                if self.is_internet_accessible():
                    return True, "ورود با موفقیت انجام شد و اینترنت فعال گردید ✅"
                
                if "invalid" in resp_body or "incorrect" in resp_body or "اشتباه" in resp_body:
                    return False, "نام کاربری یا کلمه عبور نادرست است."
                
            except urllib.error.HTTPError as e:
                # Some gateways redirect with 302 upon successful login
                if e.code in (301, 302, 303, 307):
                    if self.is_internet_accessible():
                        return True, "ورود با موفقیت انجام شد ✅"
                last_error = f"HTTP {e.code}"
            except Exception as e:
                last_error = str(e)
                continue

        if self.is_internet_accessible():
            return True, "ورود با موفقیت انجام شد ✅"

        return False, f"عدم برقراری ارتباط با درگاه لاگین: {last_error or 'پاسخ نامعتبر'}"

    def logout(self) -> tuple[bool, str]:
        """
        Terminates the active network session.
        """
        try:
            req = urllib.request.Request(self.logout_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5, context=self.ssl_ctx) as resp:
                return True, "نشست اینترنت با موفقیت بسته شد."
        except Exception as e:
            return False, f"خطا در بستن نشست: {e}"

    def get_status(self) -> dict:
        """
        Fetches current session and usage status if available.
        """
        try:
            req = urllib.request.Request(self.status_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5, context=self.ssl_ctx) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
                return {
                    "accessible": True,
                    "status_code": resp.status,
                    "content_preview": text[:300]
                }
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e)
            }
