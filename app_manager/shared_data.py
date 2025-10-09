'''
python后端全局数据管理
'''
import toml
import queue
import threading
import sys
import os
import pathlib
from wxauto import WeChat  # 使用的是 wxauto4

# 1. 单例对象 (全局使用一次)
# -----------------------------------------------------
_global_wx = None

def init_wechat():
    global _global_wx
    if _global_wx is None:
        try:
            _global_wx = WeChat()
        except Exception as e:          # wxauto 版本不对、微信版本过高都会进这里
            # 友好退出，或者抛自定义异常给上层处理
            print(f"[ERROR] 无法启动微信自动化：{e}")
            sys.exit(1)
    return _global_wx    # 用于全局的微信对象，避免多次调用

target_man = "" # 目标联系人，全局共享

# 共享队列 (跨线程通信)
realtime_q = queue.Queue() # 实时消息（监听到的原始消息）
send_q = queue.Queue() # 发送区的文本（最终要发送的消息

# 4. 共享缓存和锁 (跨线程同步)
# 当前缓存（待生成）
buffer_msgs = []# [{"type": "text|image|video", "content": str, "ts": float}]
buffer_lock = threading.Lock()

# 项目根目录下的 config.toml
# 这下面的if_else是固定操作
if getattr(sys, 'frozen', False):   # 被打包后的 EXE
    BASE_DIR = pathlib.Path(sys._MEIPASS)  # 打包后解压目录
else:                           
    # 当前文件 .../项目根/app_manager/shared_data.py
    BASE_DIR = pathlib.Path(__file__).resolve().parent.parent   # 跳一级到项目根

# BASE_DIR = pathlib.Path(start_path).resolve().parent
# config_path = os.path.join(BASE_DIR, 'config.toml')

class AppConfig():
    def __init__(self):
        config_path = os.path.join(BASE_DIR, 'config.toml')
        self.config = toml.load(config_path)
    
    def test(self):
        from pprint import pp
        pp(self.config)

    def get_save_dir(self):
        # _internal目录的上一级
        middle_path = BASE_DIR.parent
        save_dir = os.path.join(middle_path, self.config["paths"]["received_files_dir"])
        return save_dir
    
if __name__ == "__main__":
    print("路径是:", BASE_DIR)
    appConfig = AppConfig()
    print(appConfig.get_save_dir())
