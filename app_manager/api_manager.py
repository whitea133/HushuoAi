import webview
import json
'''
这里管理着与vue交互的所有函数，比如创建窗口，子窗口等
'''

class Api():
    def __init__(self, rootPath):
        self.rootPath = rootPath
        # 注意：这里的 Api 初始化不再需要 main_window，因为它只处理 API 逻辑
        # 如果需要访问窗口实例，请在 main.py 中修改创建 Api 实例的方式。


    def say_hello(self):
        print("hello world")

        # 2. 前端会调用这个方法来创建新窗口
    def create_sub_window(self, payload):
        try:
            config = json.loads(payload) # 将发来的json字符串解析为Python 字典
            title = config.get('title', '新窗口')
            # 前端现在只发送路由，例如 '/settings'
            route = config.get('route', '/') 

            # --- 关键修正：构造新窗口的 URL ---
            if 'http' in self.rootPath:
                # 开发环境：http://localhost:5173/settings
                new_window_url = f"{self.rootPath}/#{route}" 
                print("处于开发环境！")
            else:
                # 打包环境：file:///path/to/index.html#/settings (假设 Vue Router 是 Hash 模式)
                # 需检查 self.rootPath 是否已经是 file:// 形式
                new_window_url = f"{self.rootPath}/#/{route}"
                print("处于打包环境！")
            # 3. 创建新窗口的代码
            new_window = webview.create_window(
                title, 
                url=new_window_url,  # 使用构造好的 URL
                width=800, 
                height=600,
                # 注意：这里需要传入新窗口的 rootPath，即新窗口加载的路径
                # 这里的 new_window_url 可能包含路由，需要处理一下
                # 但由于新窗口也要加载同一个 index.html，我们传入相同的 rootPath 即可
                js_api=Api(self.rootPath) 
            )
            print(f"创建了新窗口: {title}，URL: {new_window_url}")
            return "New window created successfully"
        
        except Exception as e:
            print(f"创建窗口失败: {e}")
            return f"Error: {e}"