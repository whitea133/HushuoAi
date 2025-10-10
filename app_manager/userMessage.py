'''
# self.py  共享数据容器（tiny 模块）
import queue
import threading
from wxauto import WeChat

global_wx = WeChat()    # 用于全局的微信对象，避免多次调用wx = WeChat() 
target_man = ""
realtime_q = queue.Queue()   # 实时消息
reply_q    = queue.Queue()   # AI 回答
send_q    = queue.Queue()   # 发送区的文本
# 当前缓存（待生成）
buffer_msgs = []          # {"type": "text|image|video", "content": str, "ts": float}
buffer_lock = threading.Lock()
'''
import os
import sys
import time
import threading
import pythoncom
from .shared_data import (
    global_wx,
    target_man, 
    realtime_q, 
    buffer_msgs, 
    buffer_lock, 
    AppConfig
)       # 使用全局实时消息队列
from wxauto import WeChat  # 使用的是 wxauto

# SAVE_DIR = "received_images"
# os.makedirs(SAVE_DIR, exist_ok=True)


class userMessage():
    
    def __init__(self, config_service: AppConfig):
        # 将配置服务实例保存为属性
        self.config = config_service 
        # 关键：使用配置服务获取 SAVE_DIR
        self.save_dir = self.config.get_save_dir() 
        os.makedirs(self.save_dir, exist_ok=True) # 创建目录

        # 线程停止事件
        self.stop_event = threading.Event()

    def init_wechat(self) -> bool: # 初始化微信
        global global_wx
        if global_wx is not None:          # 已经初始化过
            return True

        try:
            global_wx = WeChat()
            return True
        except Exception as e:             # 任何原因导致失败
            print(f"[ERROR] 无法启动微信自动化：{e}")
            return False
        
    # ----------------------------------------------------
    # 1. 提升：将回调逻辑作为私有方法
    # ----------------------------------------------------
    def _on_message(self, msg, chat):
        """
        处理微信接收到的消息的回调函数。
        """
        now = time.time()
        # 使用全局锁
        with buffer_lock:
            if msg.type == 'text':
                buffer_msgs.append({"type": "text", "content": msg.content, "ts": now})
                realtime_q.put(f"[实时文字] {msg.content}")

            elif msg.type == 'image':
                print(f"Attempting to download image to {self.save_dir}")
                path = msg.download(dir_path=self.save_dir)
                if path:
                    buffer_msgs.append({"type": "image", "content": path, "ts": now})
                    realtime_q.put(f"[实时图片] {path}")

            elif msg.type == 'video':
                print(f"Attempting to download bideo to {self.save_dir}")
                path = msg.download(dir_path=self.save_dir)
                if path:
                    buffer_msgs.append({"type": "video", "content": path, "ts": now})
                    realtime_q.put(f"[实时视频] {path}")

    # ----------------------------------------------------
    # 2. 线程入口：将连接和监听逻辑独立成一个方法
    # ----------------------------------------------------
    def _connection_logic(self):
        """
        在新线程中运行的连接和监听核心逻辑。
        """
        # 注意：pythoncom.CoInitialize() 必须在 COM 相关的调用前
        pythoncom.CoInitialize() 

        try:
            global_wx.ChatWith(target_man)
            
            # 关键：传入类方法作为回调
            global_wx.AddListenChat(nickname=target_man, callback=self._on_message)
            
            # 保持线程存活，同时检查停止事件
            while not self.stop_event.is_set():
                time.sleep(1)
        finally:
            global_wx.RemoveListenChat(target_man)
            print(f"Listener for {target_man} has been removed.")
            pythoncom.CoUninitialize()

    # ----------------------------------------------------
    # 3. 外部接口：只负责设置并启动线程
    # ----------------------------------------------------
    def createConnect(self, target_nickname: str):
        """
        建立对话连接并启动监听线程。
        """

        # 清除任何旧的停止信号，准备开始新的监听
        self.stop_event.clear()

        # 1. 设置全局目标
        global target_man   # 这里设置全局目标的原因，是为了下面能够主动给target_man赋值成其他对象
        target_man = target_nickname

        # 2. 启动线程，目标是 _connection_logic 方法
        threading.Thread(target=self._connection_logic, daemon=True).start()
        
        return f"Listening thread started for {target_man}"
    
    # ----------------------------------------------------
    # 接口：停止监听
    # ----------------------------------------------------
    def stopConnect(self):
        """
        设置停止事件，通知后台监听线程退出。
        """
        if not self.stop_event.is_set():
            # 发送停止信号
            self.stop_event.set()
            return f"Stop signal sent for listener: {target_man}"
        
        return "Listener is already stopped or stopping."
    
    # 发送消息函数
    def sendMessages(self, input):    # input是输入的内容
        try:
            global_wx.SendMsg(input, who=target_man)
            return True
        except Exception as e:             # 任何原因导致失败
            print(f"[ERROR] 发送消息失败：{e}")
            return False
        # # 清空消息缓冲区
        # shared.buffer_msgs.clear()