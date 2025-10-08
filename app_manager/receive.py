# 8-30日新加的监听消息模块
import os
import time
import threading
import pythoncom
from hushuoGUI.shared import global_wx as wx


import hushuoGUI.shared as shared

SAVE_DIR = "received_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------- 微信监听 ----------
def listener():
    pythoncom.CoInitialize()
    wx.ChatWith(shared.target_man)
    # 
    def on_message(msg, chat):
        now = time.time()
        with shared.buffer_lock:
            if msg.type == 'text':
                shared.buffer_msgs.append({"type": "text", "content": msg.content, "ts": now})
                shared.realtime_q.put(f"[实时文字] {msg.content}")

            elif msg.type == 'image':
                path = msg.download(dir_path=SAVE_DIR)
                if path:
                    shared.buffer_msgs.append({"type": "image", "content": path, "ts": now})
                    shared.realtime_q.put(f"[实时图片] {path}")

            elif msg.type == 'video':
                path = msg.download(dir_path=SAVE_DIR)
                if path:
                    shared.buffer_msgs.append({"type": "video", "content": path, "ts": now})
                    shared.realtime_q.put(f"[实时视频] {path}")

    wx.AddListenChat(nickname=shared.target_man, callback=on_message)
    try:
        while True:
            time.sleep(1)
    finally:
        wx.RemoveListenChat(shared.target_man)
        pythoncom.CoUninitialize()

# ---------- 启动后台 ----------
def start_listen():
    threading.Thread(target=listener, daemon=True).start()