'''
python后端全局数据管理
'''
import toml
import queue
import threading
import pathlib
from wxauto4 import WeChat  # 假设你使用的是 wxauto4

# 1. 单例对象 (全局使用一次)
# -----------------------------------------------------
global_wx = WeChat()# 用于全局的微信对象，避免多次调用
target_man = "" # 目标联系人，全局共享

# 共享队列 (跨线程通信)
realtime_q = queue.Queue() # 实时消息（监听到的原始消息）
send_q = queue.Queue() # 发送区的文本（最终要发送的消息

# 4. 共享缓存和锁 (跨线程同步)
# 当前缓存（待生成）
buffer_msgs = []# [{"type": "text|image|video", "content": str, "ts": float}]
buffer_lock = threading.Lock()

# 项目根目录下的 config.toml
config_path = 'E:\CodeProject\hushuoChat\config.toml'

class AppConfig():
    def __init__(self, configFile_path=config_path):
        self.config = toml.load(configFile_path)
    
    def test(self):
        from pprint import pp
        pp(self.config)

    def get_save_dir(self):
        return self.config["paths"]["received_files_dir"]
