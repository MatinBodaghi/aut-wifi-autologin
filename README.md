# 📶 aut-wifi-autologin

ابزار اتصال و لاگین خودکار به سامانه اینترنت دانشگاه صنعتی امیرکبیر (پلی‌تکنیک تهران).

بدون نیاز به باز کردن مکرر مرورگر، به محض اتصال به وای‌فای دانشگاه یا خوابگاه (`AUT-Student`، `AUT-Staff`، `AUT-Dorm` یا کابل شبکه LAN)، وضعیت دسترسی به اینترنت بررسی شده و در صورت نیاز لاگین خودکار انجام می‌شود.

---

## 🚀 ویژگی‌ها

- **تشخیص خودکار شبکه (SSID Detection):** فقط زمانی فعال می‌شود که به شبکه‌های دانشگاه امیرکبیر متصل باشید و روی اینترنت خانگی یا غیردانشگاهی کاری انجام نمی‌دهد.
- **پروب پورتال کپتیو (Captive Portal Probe):** با بررسی استاندارد بدون مزاحمت (مشابه سیستم‌عامل اندروید و ویندوز)، قطعی یا قفل بودن اینترنت را در کسری از ثانیه تشخیص می‌دهد.
- **پشتیبانی از درگاه‌های رسمی:** ارتباط مستقیم با `https://login.aut.ac.ir/login` و `https://internet.aut.ac.ir/login`.
- **حالت Daemon (پس‌زمینه):** قابلیت اجرا به عنوان یک سرویس پس‌زمینه برای پایش مداوم اتصال.
- **دستورات دستی:** لاگین (`login`)، لاگ‌اوت (`logout`) و بررسی وضعیت شبکه (`status`).

---

## 🛠️ راه‌اندازی سریع

### ۱. نصب وابستگی‌ها

```bash
cd aut-wifi-autologin
pip install -r requirements.txt
```

### ۲. تنظیم مشخصات کاربری

فایل نمونه `config.example.json` را به `config.json` کپی کنید:

```bash
cp config.example.json config.json
```

سپس نام کاربری و رمز عبور اینترنت دانشگاه را داخل `config.json` قرار دهید:

```json
{
  "username": "your_student_id",
  "password": "your_password",
  "gateway_url": "https://login.aut.ac.ir/login",
  "status_url": "https://login.aut.ac.ir/status",
  "logout_url": "https://login.aut.ac.ir/logout",
  "check_interval_seconds": 10,
  "wifi_ssids": [
    "AUT",
    "AUT-Student",
    "AUT-Staff",
    "AUT-Dorm",
    "Amirkabir"
  ]
}
```

> **نکته:** فایل `config.json` در `.gitignore` قرار دارد و کامیت نخواهد شد.

---

## 💻 نحوه استفاده

### اجرای خودکار در پس‌زمینه (Daemon):
```bash
python main.py run
```
این دستور اتصال شبکه را هر ۱۰ ثانیه چک می‌کند و در صورت قطعی اینترنت در شبکه دانشگاه، به صورت خودکار لاگین می‌کند.

### دستورات دستی:
```bash
# یک‌بار لاگین فوری
python main.py login

# قطع نشست اینترنت فعلی (خروج)
python main.py logout

# بررسی وضعیت اتصال و نام وای‌فای
python main.py status
```
