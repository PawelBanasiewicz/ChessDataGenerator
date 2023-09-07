import subprocess
import time

while True:
    try:
        print("start new subprocess")
        subprocess.run(["python", "generate_games.py"])
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
