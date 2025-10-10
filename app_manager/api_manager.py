import webview
import json
import queue
from .shared_data import realtime_q, AppConfig,  buffer_lock,  buffer_msgs
from .userMessage import userMessage
'''
这里管理着与vue交互的所有函数，比如创建窗口，子窗口等
'''

class Api():
    def __init__(self, rootPath):
        self.rootPath = rootPath
        # 注意：这里的 Api 初始化不再需要 main_window，因为它只处理 API 逻辑
        # 如果需要访问窗口实例，请在 main.py 中修改创建 Api 实例的方式。
        self.cfg = AppConfig() # 这里是因为userMessage要传入AppConfig类才这样写的，不知道是好不好。后面修改
        self.userMessage = userMessage(self.cfg) #


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
                '''
                开发环境：http://localhost:5173/#/settings
                开发环境下，会自动寻找根路径index.html
                '''
                new_window_url = f"{self.rootPath}/#{route}" 
                print("处于开发环境！")
            else:
                '''
                程序启动时默认会启动本地服务器，使用配置文件设定的端口关联子窗口
                注意hash静态服务器，必须写出index.html的位置，因为静态服务器不会自动寻找index.html
                路由访问格式必须是：http://localhost:51370/index.html#/yourrouter
                访问之后浏览器会自动变更为http://localhost:51370/#/yourrouter
                '''
                new_window_url = f"http://localhost:51370/index.html#{route}"
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
        
    # 新增方法：让 Vue 轮询这个方法来获取新消息
    def get_realtime_messages(self):    # 处理的是realtime_q数据
        """
        从实时队列中取出所有当前可用的消息，并返回列表。
        """
        messages = []
        # 安全地从队列中取出所有项
        while not realtime_q.empty():
            try:
                # 设置非阻塞获取，确保不会卡住
                messages.append(realtime_q.get_nowait())
            except queue.Empty:
                # 队列为空时退出循环
                break
        
        return messages
    
    # 清空消息队列和缓存
    def clear_all_caches(self):
        """
        清空实时消息队列 (realtime_q) 和待生成消息缓存 (buffer_msgs)。
        通常在断开连接时调用。
        """
        # 1. 清空实时队列
        while not realtime_q.empty():
            try:
                realtime_q.get_nowait()
            except queue.Empty:
                break
        
        # 2. 清空待生成消息缓存（需要加锁）
        with buffer_lock:
            buffer_msgs.clear()
            
        return "All message queues and caches cleared."
    
