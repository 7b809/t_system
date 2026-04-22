import subprocess
import re
import time
import os


def start_full_system(port=8080):
    """
    Starts Django + Cloudflare tunnel automatically.
    """

    # ============================================
    # 1️⃣ Ensure cloudflared exists
    # ============================================
    if not os.path.exists("cloudflared.exe"):
        print("⏳ Installing cloudflared...\n")

        subprocess.run([
            "powershell",
            "-Command",
            "Invoke-WebRequest -Uri https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -OutFile cloudflared.exe"
        ], check=True)

        print("✅ cloudflared installed.\n")
    else:
        print("✅ cloudflared already exists.\n")

    # ============================================
    # 2️⃣ Start Django in NEW CMD window
    # ============================================
    print(f"🚀 Starting Django on port {port}...\n")

    subprocess.Popen(
        f'start cmd /k python manage.py runserver 0.0.0.0:{port}',
        shell=True
    )

    # wait for Django to boot
    time.sleep(5)

    # ============================================
    # 3️⃣ Start Cloudflare tunnel
    # ============================================
    print(f"🌐 Starting tunnel for http://localhost:{port}...\n")

    cf_proc = subprocess.Popen(
        ["cloudflared.exe", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    public_url = None

    for line in iter(cf_proc.stdout.readline, ""):
        if line:
            print(f"[Cloudflare] {line.strip()}")

            if "trycloudflare.com" in line:
                match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
                if match:
                    public_url = match.group(0)
                    break

    if not public_url:
        print("❌ Failed to get URL")
        return None

    webhook_url = f"{public_url}/webhook/tradingview/13/"

    print("\n✅ PUBLIC URL:", public_url)
    print("🎯 WEBHOOK URL:", webhook_url)

    print("\n🟢 System running... Keep this window open\n")

    return webhook_url




start_full_system(8080)