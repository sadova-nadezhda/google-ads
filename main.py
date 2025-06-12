import subprocess
import time
import sys
from token_utils import is_token_valid, update_refresh_token_from_file

if is_token_valid():
    print("✅ Refresh token действителен. Запуск приложения...")
    subprocess.run([sys.executable, "app.py"])
else:
    print("⚠️ Refresh token недействителен. Запуск генератора токена...")
    generator_proc = subprocess.Popen([sys.executable, "refresh_token_generator.py"])

    print("👉 Откройте браузер, авторизуйтесь и получите токен.")
    input("Нажмите Enter после завершения генерации токена...")

    if update_refresh_token_from_file():
        print("🔁 Завершение генератора токена...")
        generator_proc.terminate()
        generator_proc.wait()
        print("🔁 Повторный запуск приложения...")
        subprocess.run([sys.executable, "app.py"])
    else:
        print("❌ Не удалось обновить refresh token.")