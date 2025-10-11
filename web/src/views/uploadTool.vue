<script setup lang="ts">
import { ref } from "vue";
import { Button } from "@/components/ui/button"
import { Input } from '@/components/ui/input'

const uploadButton = ref<string>('上传文件');
const filePath = ref<string>('');

async function sendFile(): Promise<void>
{
    const pywebviewApi = (window as any)?.pywebview?.api;
    if (pywebviewApi) {
    try {
          // 运行时检查：确保 userMessage.createConnect 方法存在
          if (typeof pywebviewApi.userMessage?.sendFile !== 'function') {
              console.error(`[PyWebView] API方法 userMessage.sendFile 未找到或不是函数。`);
              alert('连接API未准备好，请检查后端暴露的API名称。');
              return;
          }
          
          uploadButton.value = '上传文件中。。。';
          // 调用 Python API 启动监听线程
          const result = await pywebviewApi.userMessage.sendFile(filePath.value); // 仅返回 true/false
          
          if (!result) {              // ← 新增：利用返回值做业务失败分支
              alert('发送文件失败');;
              uploadButton.value = '上传文件';
              return;
            }

          uploadButton.value = '上传文件';
          console.log("发送文件成功");

    } catch (error) { // 后端代码raise出异常，而不是return时，触发catch
            uploadButton.value = '上传文件';
            console.error("[PyWebView] 建立连接失败:", error);
            alert(`sendFile()被raise出异常，调用失败：${error}`);
      }
    }
    else // 与最上面的if对应
    {  
        // 非 PyWebView 环境下的调试模式
        console.warn("[DEV MODE] 当前不是 pywebview 环境，无法调用 Python API。");
    }
}

function getFilePath(): void
{
    
   const pywebviewApi = (window as any)?.pywebview?.api;
    if (pywebviewApi) 
    {
        try
        {
            if (typeof pywebviewApi.openFileDialog !== 'function') 
            {
                console.error(`[PyWebView] API方法 openFileDialog 未找到或不是函数。`);
                alert('连接API未准备好，请检查后端暴露的API名称。');
                filePath.value = '';
                return;
            }
            
            // 调用 Python API 启动监听线程
            const path = pywebviewApi.openFileDialog(); 
            
            if (!path || typeof path !== 'string') 
            {
                // 用户取消或后端返回空串
                filePath.value = '';        // 用户取消
            }
            else 
            {
                filePath.value = path;      // 保存绝对路径
                console.log('已选择文件:', path);
            }
        } 
        catch (error) 
        { // 后端代码raise出异常，而不是return时，触发catch
            console.error("[PyWebView] 建立连接失败:", error);
            filePath.value = '';
            alert(`getFilePath()被raise出异常，调用失败：${error}`);
        }
    }
    else // 与最上面的if对应
    {  
        // 非 PyWebView 环境下的调试模式
        console.warn("[DEV MODE] 当前不是 pywebview 环境，无法调用 Python API。");
    }
}

</script>


<template>
    <div class="grid bg-white items-center gap-2 mx-1">
        <div class="grid items-center gap-1">
            <div class="flex">
            <Button class="cursor-pointer bg-amber-500 hover:bg-amber-600" @click="getFilePath"> 选择要上传的文件 </Button>
              <Input disabled id="text" type="text" placeholder="文件路径" class="bg-white mx-2 border-1 border-blue-500 rounded-md" v-model="filePath" />
            </div>
        </div>
         <Button class="cursor-pointer" @click="sendFile"> {{ uploadButton }} </Button>
    </div>
</template>


<style scoped>

</style>