import webview
import sys
import os
from app_manager.api_manager import Api


# 这下面的if_else是固定操作
if getattr(sys, "frozen", False):
    # 如果是打包后的可执行文件
    base_path = sys._MEIPASS
    # 定义 Vue 构建后的 HTML 文件路径
    html_file_path = os.path.join(base_path, "dist", "index.html")
else:
    # 如果是开发环境
    base_path = os.path.dirname(os.path.abspath(__file__))
    # 定义 Vue 构建后的 HTML 文件路径
    # html_file_path = os.path.join(base_path, "http://localhost:5173")
    html_file_path = "http://localhost:5173"

print("html_file_path：", html_file_path)
js_api = Api(html_file_path)

window = webview.create_window('胡说聊天助手', html_file_path, js_api=js_api, width=1200, height=800)	# 只需要用路径html_file_path即可
webview.start(http_port=51370, debug=True) # 当html_file_path是http://的开发环境时，http_port无效
