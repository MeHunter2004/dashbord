# داشبورد پایش درخواست‌ها — MVP

یک داشبورد وب فارسی و راست‌به‌چپ برای پایش و تحلیل درخواست‌های پشتیبانی و توسعه.

## وضعیت و اجزای پروژه

- **بک‌اند:** FastAPI، Pandas و Pydantic
- **فرانت‌اند:** React، TypeScript، Vite، ECharts و TanStack Table
- **منبع داده در نسخه MVP:** فایل Excel و برگه `ریز اطلاعات`
- **منبع داده در آینده:** PostgreSQL، از طریق همان قرارداد Repository

```text
request-dashboard-mvp/
├── backend/                 # API و خواندن داده Excel
│   ├── app/
│   ├── data/
│   └── requirements.txt
└── frontend/                # رابط کاربری داشبورد
    ├── src/
    └── package.json
```

## پیش‌نیازها

روی ویندوز این موارد باید نصب باشند:

- Python 3.11 یا جدیدتر: `python --version`
- Node.js 18 یا جدیدتر: `node --version`
- npm (همراه Node.js نصب می‌شود): `npm.cmd --version`

دستورها را از پوشه ریشه پروژه اجرا نکنید؛ برای بک‌اند وارد `backend` و برای فرانت‌اند وارد `frontend` شوید.

> مثال‌های اصلی این راهنما برای **Command Prompt (CMD)** هستند. اگر از PowerShell استفاده می‌کنید، بخش مخصوص PowerShell را ببینید.

## داده Excel

فایل زیر باید موجود باشد:

```text
backend/data/پایش کل درخواست ها MASTER.xlsx
```

بک‌اند فقط برگه `ریز اطلاعات` را می‌خواند و برگه `ریز اطلاعات 2` را، چون تکراری است، ترکیب نمی‌کند.

اگر فایل Excel جای دیگری قرار دارد، فایل `backend/.env.example` را با نام `backend/.env` کپی کنید و مقدار `EXCEL_FILE_PATH` را به مسیر فایل خود تغییر دهید. در صورت تغییر نام برگه نیز `EXCEL_SHEET_NAME` را تغییر دهید.

## اجرای پروژه در ویندوز (CMD)

### 1. اجرای بک‌اند

یک پنجره CMD باز کنید و دستورهای زیر را اجرا کنید. به‌جای مسیر نمونه، مسیر واقعی پوشه پروژه خودتان را وارد کنید.

```bat
cd /d H:\work\Projects\EDR_Dashboard\request-dashboard-mvp\backend
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

پس از دیدن پیام آماده‌بودن سرور، این پنجره را باز نگه دارید. سپس این نشانی‌ها را بررسی کنید:

- سلامت سرویس: <http://127.0.0.1:8000/health>
- مستندات تعاملی API: <http://127.0.0.1:8000/docs>

### 2. اجرای فرانت‌اند

یک پنجره CMD **جدید** باز کنید و اجرا کنید:

```bat
cd /d H:\work\Projects\EDR_Dashboard\request-dashboard-mvp\frontend
npm.cmd install
npm.cmd run dev
```

آدرس نمایش‌داده‌شده توسط Vite را در مرورگر باز کنید؛ معمولاً این آدرس است:

```text
http://127.0.0.1:5173
```

فرانت‌اند به API بک‌اند در `http://127.0.0.1:8000/api` متصل می‌شود؛ بنابراین بک‌اند باید قبل از باز کردن داشبورد در حال اجرا باشد.

## اجرای پروژه در PowerShell

برای بک‌اند:

```powershell
cd H:\work\Projects\EDR_Dashboard\request-dashboard-mvp\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

برای فرانت‌اند، در یک پنجره PowerShell جدید:

```powershell
cd H:\work\Projects\EDR_Dashboard\request-dashboard-mvp\frontend
npm.cmd install
npm.cmd run dev
```

اگر اجرای `Activate.ps1` به دلیل Execution Policy مسدود شد، از CMD استفاده کنید یا برای همان پنجره PowerShell اجرا کنید:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

سپس دوباره دستور `Activate.ps1` را اجرا کنید.

## توقف سرویس‌ها

در پنجره‌ای که هر سرویس را اجرا کرده‌اید، کلیدهای `Ctrl + C` را بزنید.

اگر پنجره اجرای سرویس را بسته‌اید، ابتدا شناسه پردازش (PID) را پیدا کنید:

```bat
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

شماره انتهای خطی که `LISTENING` دارد همان PID است. سپس آن پردازش را متوقف کنید:

```bat
taskkill /PID شماره_PID /F
```

پورت `8000` برای بک‌اند و پورت `5173` برای فرانت‌اند است.

## خطاهای رایج

### `uvicorn is not recognized`

محیط مجازی فعال نشده یا وابستگی‌ها نصب نشده‌اند. در پوشه `backend` این دستورها را اجرا کنید:

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

استفاده از `python -m uvicorn` تضمین می‌کند نسخه نصب‌شده در همان محیط مجازی اجرا شود.

### خطای `WinError 10013` یا اشغال بودن پورت `8000`

احتمالاً یک بک‌اند دیگر روی پورت `8000` اجرا شده است. یا همان سرویس در حال اجرا را استفاده کنید، یا مطابق بخش «توقف سرویس‌ها» پردازش آن پورت را متوقف کرده و دوباره بک‌اند را اجرا کنید.

### Vite به‌جای `5173` از `5174` استفاده می‌کند

پورت `5173` اشغال است. سرویس فعلی را متوقف کنید یا در `backend/.env` مقدار `CORS_ORIGINS` را برای پورت جدید نیز اضافه کنید، سپس بک‌اند را یک‌بار راه‌اندازی مجدد کنید:

```text
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

### خطای پیدا نشدن فایل Excel یا برگه

نام فایل، مسیر `backend/data/` و نام برگه `ریز اطلاعات` را بررسی کنید. در صورت نگهداری فایل در محل دیگر، `EXCEL_FILE_PATH` و `EXCEL_SHEET_NAME` را در `backend/.env` تنظیم کنید.

## ساخت نسخه Production فرانت‌اند

برای اطمینان از صحت build فرانت‌اند:

```bat
cd /d H:\work\Projects\EDR_Dashboard\request-dashboard-mvp\frontend
npm.cmd run build
```

خروجی در پوشه `frontend/dist/` تولید می‌شود. این پروژه در وضعیت فعلی برای سرویس‌دهی production به تنظیم وب‌سرور یا reverse proxy و روش استقرار بک‌اند نیاز دارد.

## نگاشت وضعیت‌ها

داشبورد وضعیت‌های جزئی را به وضعیت‌های سطح‌بالا تبدیل می‌کند:

- `رسیدگی‌شده`: `حل شده`، `خاتمه يافته`
- `ردشده`: `رد شده`
- `باز / در جریان`: سایر وضعیت‌ها

برای تغییر این قواعد، فایل `backend/app/core/statuses.py` را ویرایش کنید.
