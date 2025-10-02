<script setup lang="ts">
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import leftBar from "@/views/leftBar.vue";


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

    } catch (error) {
      // 4. 捕获 Python 端抛出的异常（例如：raise Exception）
      console.error(`[PyWebView] 调用 Python API 失败，无法创建窗口 ${config.title}:`, error);
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
</script>

<template>
<div class="grid grid-cols-12 h-screen bg-gray-100">

  <leftBar class="col-span-1"/>
  <!-- <RouterView class="col-span-9"/> -->
   <div class="col-span-11 grid grid-cols-1 grid-rows-10 gap-4 m-3"> 
    
    <!-- 下面是信息窗口，以及发送窗口 -->
    <Textarea class="bg-white row-span-6" placeholder="这里是信息窗口" disabled />

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
        </div>

        <Textarea class="row-span-8 bg-white" placeholder="这里是对话窗口" />
        
        <div class="row-span-2 flex items-center justify-end px-2">
            <Button class="w-24">发送</Button>
        </div>
        
    </div>

 </div>
</div>
 
</template>


<style scoped>

</style>