import sys
from app_manager import shared_data
import os

# print(sys.path)
appConfig = shared_data.AppConfig()
path = appConfig.get_save_dir()

os.makedirs(path, exist_ok=True) # 创建目录。创建的根目录是根据你命令行的执行路径为根目录的。