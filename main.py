"""
AUT Wi-Fi Auto-Login CLI and Background Daemon
Usage:
    python main.py run       # Run background daemon to monitor Wi-Fi and auto-login
    python main.py login     # Perform a single manual login
    python main.py logout    # Terminate active internet session
    python main.py status    # Check network connectivity and portal status
"""

import sys
import os
import json
import time
import argparse
from client import AutWifiClient

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
EXAMPLE_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.example.json")

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(EXAMPLE_CONFIG_FILE):
            print(f"[!] فایل config.json یافت نشد. یک نمونه از روی {EXAMPLE_CONFIG_FILE} بسازید.")
        else:
            print("[!] فایل config.json یافت نشد.")
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] خطا در خواندن فایل config.json: {e}")
        return {}

def cmd_login(client: AutWifiClient):
    print("[*] در حال تلاش برای ورود به اینترنت دانشگاه...")
    success, msg = client.login()
    if success:
        print(f"[+] {msg}")
    else:
        print(f"[-] {msg}")

def cmd_logout(client: AutWifiClient):
    print("[*] در حال پایان دادن به نشست اینترنت...")
    success, msg = client.logout()
    print(f"[{'+' if success else '-'}] {msg}")

def cmd_status(client: AutWifiClient):
    ssid = client.get_current_wifi_ssid()
    print(f"[*] شبکه وای‌فای متصل: {ssid or 'نامشخص / کابل شبکه (LAN)'}")
    
    is_aut = client.is_aut_wifi()
    print(f"[*] آیا شبکه متعلق به دانشگاه است؟ {'بله' if is_aut else 'خیر'}")
    
    internet_ok = client.is_internet_accessible()
    print(f"[*] وضعیت اینترنت: {'متصل و آزاد ✅' if internet_ok else 'قطع یا پشت کپتیو پورتال ❌'}")
    
    status_info = client.get_status()
    if status_info.get("accessible"):
        print(f"[*] پاسخ درگاه وضعیت: HTTP {status_info.get('status_code')}")
    else:
        print(f"[-] دسترسی به صفحه وضعیت ممکن نشد: {status_info.get('error')}")

def cmd_run(client: AutWifiClient, interval: int):
    print(f"[*] ربات لاگین خودکار فعال شد (بررسی هر {interval} ثانیه)...")
    print("[*] برای توقف کلیدهای Ctrl + C را بفشارید.\n")
    
    already_logged_in_notification = False
    
    while True:
        try:
            ssid = client.get_current_wifi_ssid()
            
            # Check if we are on an AUT network (or LAN)
            if client.is_aut_wifi():
                if client.is_internet_accessible():
                    if not already_logged_in_notification:
                        print(f"[{time.strftime('%H:%M:%S')}] اینترنت آزاد و متصل است. (SSID: {ssid or 'LAN'})")
                        already_logged_in_notification = True
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] اتصال به شبکه دانشگاه تشخیص داده شد، اما اینترنت قطع است. تلاش برای لاگین...")
                    already_logged_in_notification = False
                    success, msg = client.login()
                    if success:
                        print(f"[{time.strftime('%H:%M:%S')}] [+] {msg}")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] [-] {msg}")
            else:
                already_logged_in_notification = False
                # If connected to home/non-AUT wifi, remain silent
                
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[*] برنامه متوقف شد.")
            break
        except Exception as e:
            print(f"[!] خطای غیرمنتظره در حلقه اجرا: {e}")
            time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="AUT Wi-Fi Auto-Login Tool")
    parser.add_argument("command", choices=["run", "login", "logout", "status"], nargs="?", default="run",
                        help="Command to execute (default: run)")
    args = parser.parse_args()

    config = load_config()
    client = AutWifiClient(config)

    if args.command == "login":
        cmd_login(client)
    elif args.command == "logout":
        cmd_logout(client)
    elif args.command == "status":
        cmd_status(client)
    elif args.command == "run":
        interval = int(config.get("check_interval_seconds", 10))
        cmd_run(client, interval)

if __name__ == "__main__":
    main()
