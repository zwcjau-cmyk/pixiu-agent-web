"""终端交互式聊天脚本"""
import urllib.request
import json
import uuid

API_URL = "http://localhost:8000/api/script/chat"
USER_ID = "default_user"
SESSION_ID = str(uuid.uuid4())

print("🐾 貔貅学长剧情模式 | 输入 quit 退出")
print("-" * 40)

while True:
    try:
        msg = input("\n你: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n再见！")
        break
    if not msg or msg.lower() == "quit":
        print("再见！")
        break
    try:
        payload = json.dumps({"message": msg, "user_id": USER_ID, "session_id": SESSION_ID}).encode("utf-8")
        req = urllib.request.Request(API_URL, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(f"\n貔貅: {data['reply']}")
        if data.get("image_url"):
            print(f"🎨 剧情海报: {data['image_url']}")
    except Exception as e:
        print(f"请求失败: {e}")
