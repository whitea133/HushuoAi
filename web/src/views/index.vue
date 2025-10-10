<script setup lang="ts">
import { ref ,onMounted, onUnmounted} from "vue";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from '@/components/ui/input'
import leftBar from "@/views/leftBar.vue";

type Phase = 'checkWin' | 'connectWin' | 'chatWin' // 控制阶段的类型别名
const phase = ref<Phase>('checkWin')

// const ifConnected = ref<boolean>(false);
const connectedObject = ref<string>('');
const messageLog = ref<string[]>([]); // 聊天区的内容
const inputContent = ref<string>('') // 发言的内容
let pollInterval: number | undefined = undefined;

const openToolsWindow = async (config: { title: string; route: string }) => {
  
  // 关键：使用 (window as any) 检测 pywebview 环境
  if ((window as any).pywebview && (window as any).pywebview.api) {
    try {
      // 提取 API 对象，避免重复访问 window
      const pywebviewApi = (window as any).pywebview.api;
      
      // 运行时检查：确保 create_sub_window 方法存在
      if (typeof pywebviewApi.create_sub_window !== 'function') {
        console.error(`[PyWebView] API方法 create_sub_window 未注入或不是函数。`);
        return;
      }
      
      // 1. 将配置对象转换为 JSON 字符串（Python后端需要）
      const payload = JSON.stringify(config);

      // 2. 调用 PyWebView 接口，并等待结果
      // 注意：这里我们直接调用方法
      const result = await pywebviewApi.create_sub_window(payload); 
      
      // 3. 处理成功响应
      if (result) {
        console.log(`[PyWebView] 窗口 "${config.title}" 创建成功。Python 响应:`, result);
      } else {
        console.warn(`[PyWebView] 窗口 "${config.title}" 创建失败，无响应信息。`);
      }

    } catch (error) { // 只有当后端代码是raise异常，而不是return的时候，就会进入这个catch
      // 4. 捕获 Python 端抛出的异常（例如：raise Exception）
      console.error(`create_sub_window()被raise出异常，调用失败。无法创建窗口 ${config.title}:`, error);
      // 可以在这里设置一个状态提示给用户
    }
  } else {
    // 5. 非 PyWebView 环境下的提示
    console.warn(`[DEV MODE] 当前不是 pywebview 环境，无法打开窗口: ${config.title}`);
  }
};

const openTextTools = () => {
  openToolsWindow({
    title: "文本加解密工具",
    route: '/textTool', 
  });
};

const openVideoTools = () => {
  openToolsWindow({
    title: "图片加解密工具",
    route: '/imgTool', 
  });
};

const openVoiceTools = () => {
  openToolsWindow({
    title: "音频加解密工具",
    route: '/voiceTool', 
  });
};

const tryConnect = async () => {
  if (!connectedObject.value.trim()) {
    alert('连接对象不能为空');
    return;
  }
    // 1. 停止任何可能的旧轮询
    if (pollInterval !== undefined) {
        clearInterval(pollInterval);
    }
    
    // TODO: 这里应调用 Python API 启动监听，成功后继续
    const pywebviewApi = (window as any)?.pywebview?.api;
    if (pywebviewApi) {
        try {
            const targetNickname = connectedObject.value.trim();  // 获取监听对象的名字

            // 运行时检查：确保 userMessage.createConnect 方法存在
            if (typeof pywebviewApi.userMessage?.createConnect !== 'function') {
                console.error(`[PyWebView] API方法 userMessage.createConnect 未找到或不是函数。`);
                alert('连接API未准备好，请检查后端暴露的API名称。');
                return;
            }

            // 调用 Python API 启动监听线程
            const result = await pywebviewApi.userMessage.createConnect(targetNickname);  // 开启监听
            
            console.log(`[PyWebView] 连接 API 调用成功。结果: ${result}`);

            // 2. 成功后设置状态为连接成功
            // ifConnected.value = true;
            phase.value = 'chatWin';
            
            // 3. 启动轮询
            pollInterval = setInterval(fetchNewMessages, 500);  // 实时刷新消息队列(在api_manager文件里面)
            console.log("连接成功，轮询已启动。");

        } catch (error) { // 后端代码raise出异常，而不是return时，触发catch
            console.error("[PyWebView] 建立连接失败:", error);
            alert(`createConnect()被raise出异常，调用失败。错误: ${error}`);
            // ifConnected.value = false;
            phase.value = 'connectWin'
        }
    } else {
        // 非 PyWebView 环境下的调试模式
        console.warn("[DEV MODE] 当前不是 pywebview 环境，无法调用 Python API。");
        // ifConnected.value = true;
        phase.value = 'chatWin';
        pollInterval = setInterval(fetchNewMessages, 500);
    }
};

const tryDisConnect = async () => {
    // 1. 清除前端定时器
    if (pollInterval !== undefined) {
        clearInterval(pollInterval);
        pollInterval = undefined;
        console.log("前端轮询已停止。");
    }
    
    const pywebviewApi = (window as any)?.pywebview?.api;
    if (pywebviewApi) {
        try {
            // 2. 调用 Python API 停止监听线程
            if (typeof pywebviewApi.userMessage?.stopConnect === 'function') {
                 // 修正后的代码现在在 async 函数中
                 await pywebviewApi.userMessage.stopConnect(); 
            }

            // 3. 调用 Python API 清空消息缓存
            if (typeof pywebviewApi.clear_all_caches === 'function') {
                 // 修正后的代码现在在 async 函数中
                 const clearResult = await pywebviewApi.clear_all_caches();
                 console.log(`[PyWebView] 清理缓存结果: ${clearResult}`);
            } else {
                 console.warn(`[PyWebView] API方法 clear_all_caches 未找到。`);
            }
            
        } catch (error) { // 后端代码raise出异常，而不是return时，触发catch
            console.error("clear_all_caches被raise出异常，执行操作失败:", error);
        }
    }
    
    // 4. 更新前端状态和清理日志
    // ifConnected.value = false;
    phase.value = 'connectWin';
    messageLog.value = []; // 清空聊天日志
    connectedObject.value = ''; // 清空连接对象
};

const checkLogin = async () => {
  const pywebviewApi = (window as any)?.pywebview?.api;
  if (pywebviewApi) {
    try {
          // 运行时检查：确保 userMessage.createConnect 方法存在
          if (typeof pywebviewApi.userMessage?.init_wechat !== 'function') {
              console.error(`[PyWebView] API方法 userMessage.init_wechat 未找到或不是函数。`);
              alert('连接API未准备好，请检查后端暴露的API名称。');
              return;
          }

          // 调用 Python API 启动监听线程
          const result = await pywebviewApi.userMessage.init_wechat(); // 仅返回 true/false
          
          if (!result) {              // ← 新增：利用返回值做业务失败分支
              alert('连接失败：请检查微信是否已经登录或版本不符。');
              phase.value = 'checkWin';
              return;
            }

          // 2. 进入连接界面
          phase.value = 'connectWin';
          console.log("检测微信环境已正常启动");
    } catch (error) { // 后端代码raise出异常，而不是return时，触发catch
          console.error("[PyWebView] 建立连接失败:", error);
          alert(`init_wechat()被raise出异常，调用失败：${error}`);
          phase.value = 'checkWin'
      }
    }
    else // 与最上面的if对应
    {  
        // 非 PyWebView 环境下的调试模式
        console.warn("[DEV MODE] 当前不是 pywebview 环境，无法调用 Python API。");
        phase.value = 'connectWin';
    }
}

const sendMessages = async () => {
  const pywebviewApi = (window as any)?.pywebview?.api;
  if (pywebviewApi) {
    try {
          // 运行时检查：确保 userMessage.createConnect 方法存在
          if (typeof pywebviewApi.userMessage?.sendMessages !== 'function') {
              console.error(`[PyWebView] API方法 userMessage.sendMessages 未找到或不是函数。`);
              alert('连接API未准备好，请检查后端暴露的API名称。');
              return;
          }

          // 调用 Python API 启动监听线程
          const result = await pywebviewApi.userMessage.sendMessages(inputContent.value); // 仅返回 true/false
          
          if (!result) {              // ← 新增：利用返回值做业务失败分支
              alert('发送失败，请检查网络');
              return;
            }
          console.log("消息发送成功");
          inputContent.value = '';   // 清空输入框
    } catch (error) {
          console.error("[PyWebView] 建立连接失败:", error);
          alert(`sendMessages()被raise出异常，调用失败。错误: ${error}`);
      }
    }
    else // 与最上面的if对应
    {  
        // 非 PyWebView 环境下的调试模式
        console.warn("[DEV MODE] 当前不是 pywebview 环境，无法调用 Python API。");
    }

}

// ---------------------------------------------
// 关键：定时从 Python 队列中获取数据
// ---------------------------------------------
async function fetchNewMessages() {
    if (!(window as any).pywebview || !(window as any).pywebview.api) {
        // 开发环境或 API 未就绪时跳过
        return; 
    }
    
    try {
        // 调用 Python API
        const newMessages = await (window as any).pywebview.api.get_realtime_messages();
        
        if (newMessages && newMessages.length > 0) {
            // 将新消息添加到日志列表
            messageLog.value.push(...newMessages);
            // 可以滚动到底部等操作
        }
    } catch (error) {
        console.error("get_realtime_messages()被raise出异常，调用失败:", error);
    }
}

onUnmounted(() => {
    // 这是一个安全网，确保当组件被路由切换或 v-if 移除时，定时器不会在后台运行。
    if (pollInterval !== undefined) {
        clearInterval(pollInterval);
        pollInterval = undefined;
        console.log("组件销毁，安全停止轮询。");
    }
});

</script>

<template>
<div class="grid grid-cols-12 h-screen bg-gray-100">

  <leftBar class="col-span-1"/>

  <div v-if="phase==='checkWin'" class="col-span-11 grid place-content-center">
    <Button class="h-10 cursor-pointer bg-green-600 hover:bg-green-700" @click="checkLogin"> 检测微信是否登录 </Button>
  </div>

    <div v-else-if="phase==='connectWin'" class="col-span-11 grid place-content-center">
    <div class="flex">
     <Input id="email" type="email" placeholder=" 请填入对话对象" v-model="connectedObject" class="bg-white mx-2 w-60 h-8 border-1 border-blue-500 rounded-md"/>
     <Button class="h-8 cursor-pointer" @click="tryConnect">连接</Button>
    </div>

  </div>
<!-- 右侧界面代码开始 -->
  <div class="col-span-11 grid grid-cols-1 grid-rows-10 gap-4 m-3" v-else-if="phase==='chatWin'"> 
    <!-- 下面是信息窗口，以及发送窗口 -->
    <Textarea class="bg-white row-span-6" placeholder="这里是信息窗口" disabled :value="messageLog.join('\n')"/>

    <div class="row-span-4 grid bg-white grid-rows-12 p-1 gap-1 rounded-sm">

        <div class="row-span-2 flex items-center space-x-3 px-2">
        <!-- 功能栏 -->
        <Button variant="outline" size="icon" title="文本加解密" class="cursor-pointer" @click="openTextTools">
            <img src="@/components/icons/加密文本.png" alt="文本加解密" class="w-5 h-5" />
        </Button>
        <Button variant="outline" size="icon" title="视频加解密" class="cursor-pointer" @click="openVideoTools">
            <img src="@/components/icons/加密视频.png" alt="视频加解密" class="w-5 h-5" />
        </Button>
        <Button variant="outline" size="icon" title="音频加解密" class="cursor-pointer" @click="openVoiceTools">
            <img src="@/components/icons/加密音频.png" alt="音频加解密" class="w-5 h-5" />
        </Button>
        
        <Button class="h-8 cursor-pointer ml-auto bg-orange-400 hover:bg-orange-500" @click="tryDisConnect">断开连接</Button>
      </div>

        <Textarea class="row-span-8 bg-white" placeholder="这里是对话窗口" v-model="inputContent" />
        
        <div class="row-span-2 flex items-center justify-end px-2">
            <Button class="w-24 cursor-pointer" @click="sendMessages">发送</Button>
        </div>
        
    </div>
    
<!-- 右侧界面代码结束 -->  
  </div>

</div>
 
</template>


<style scoped>

</style>