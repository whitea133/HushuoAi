<script setup lang="ts">
import {ref} from 'vue';
import axios from 'axios';
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

const API_BASE_URL_ENCODE = 'http://10.154.24.21:8000';
const API_BASE_URL_DECODE = 'http://10.154.24.21:8001'
const API_KEY = '88888888';
const buttonStr1 = ref<string>("隐藏信息到音频")    // 隐藏信息按钮的文本，响应式变量
const buttonStr2 = ref<string>("提取音频中的信息")

const encryptedBlob = ref<Blob | null>(null);
const encryptedFileName = ref<string>('');

const inputFile = ref<File | null>(null); // 输入的wav音频
const secretText = ref<string>('');  // 秘密信息
const decryptedText = ref<string>('');; // 提取后的秘密信息

// 输入文件。将按钮传入的文件，保存为ref变量inputFile
const handleFileChange = (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
        const selectedFile = input.files[0];
        
        // 检查文件后缀名是否为 .wav
        const fileName = selectedFile.name;
        const isWav = fileName.toLowerCase().endsWith('.wav');

        if (isWav) 
        {
            // 存储文件对象
            inputFile.value = selectedFile;
            console.log("已选择文件:", fileName);
        } 
        else 
        {
            // 格式不正确时发出警告
            alert(`错误：请选择 WAV 格式的音频文件。您选择了 ${fileName}`);   
            // 清空 input 字段，防止用户误以为已选择正确文件
            input.value = ''; 
            inputFile.value = null;
        }
    } 
    else 
    {
        inputFile.value = null;
    }
};

// 音频信息隐藏
async function voiceEncode(): Promise<void>
{
    // 每次加密前清空状态
    encryptedBlob.value = null; 
    encryptedFileName.value = '';

    const file = inputFile.value;
    const text = secretText.value.trim();
    // 1. 输入验证
    if (!file) {
        alert("请选择要隐藏信息的音频文件！");
        return;
    }
    if (!text) {
        alert("请输入要隐藏的秘密文本！");
        return;
    }
    // 2. 强制执行 API 文档的限制：最多 2 个 ASCII 字符
    if (text.length > 2) {
        alert(`错误：秘密文本不能超过 2 个 ASCII 字符。当前长度为 ${text.length}。`);
        return;
    }

     // 3. 构造 FormData
    const formData = new FormData();
    formData.append('api_key', API_KEY);
    formData.append('secret_text', text);
    // 关键：上传文件对象，第三个参数是文件名
    formData.append('audio_file', file, file.name); 

    try {
        // 4. 发送请求，设置响应类型为 blob
        buttonStr1.value = "隐藏信息中，请等待。。。"
        const response = await axios({
            url: `${API_BASE_URL_ENCODE}/api/Voice_Encrypt`, 
            method: 'POST',
            data: formData,
            responseType: 'blob', 
        });
        // 5. 检查响应并存储 Blob
        if (response.data instanceof Blob) 
        {
            
            // 提取文件名
            const contentDisposition = response.headers['content-disposition'];
            let fileName = 'encrypted_audio.wav'; 
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?(.+)"?$/);
                if (match && match[1]) {
                    fileName = match[1];
                }
            }
            
            // 存储 Blob 和文件名，触发下载按钮显示
            encryptedBlob.value = response.data;
            encryptedFileName.value = fileName;
            alert(`音频隐藏信息成功！请点击下载按钮保存文件。`);
        } 
        else 
        {
            alert("隐藏信息失败：服务器未返回音频文件。");
        }
        buttonStr1.value = "隐藏信息到音频" // 恢复按钮状态
    } catch (error) {
        buttonStr1.value = "隐藏信息到音频"
        console.error("音频隐藏信息失败:", error);
        // 可以尝试解析 JSON 错误信息，如果服务器返回的是 JSON 错误
        // if (error.response && error.response.data instanceof Blob) { ... }
        alert('音频隐藏信息失败，请检查API地址和网络连接。');
    }
}

async function voiceDecode(): Promise<void>
{
    const file = inputFile.value; // 使用用户选择的当前文件

    // 每次解密前清空状态
    decryptedText.value = ''; 

    if (!file) {
        alert("请选择要解密的音频文件！");
        return;
    }

    // 1. 构造 FormData (仅需 api_key 和 audio_file)
    const formData = new FormData();
    formData.append('api_key', API_KEY);
    formData.append('audio_file', file); 

    try {
        buttonStr2.value = "解密中，请等待。。。"; // 更新按钮状态

        const response = await axios({
            url: `${API_BASE_URL_DECODE}/api/Voice_Decrypt`, 
            method: 'POST',
            data: formData,
            // 响应类型为 JSON
            responseType: 'json', 
        });

        // 2. 检查响应并更新状态
        if (response.data && response.data.secret_text !== undefined) {
            const recoveredText = response.data.secret_text as string;
            decryptedText.value = recoveredText;
            alert(`解密成功！还原信息: ${recoveredText}`);
        } else {
            console.error("API 返回格式错误:", response.data);
            alert("解密失败：API未返回还原信息。");
        }
        buttonStr2.value = "解密音频"; // 恢复按钮状态

    } catch (error) {
        buttonStr2.value = "解密音频"; // 恢复按钮状态
        console.error("音频解密失败:", error);
        alert('音频解密失败，请检查API地址和网络连接。');
    }
}

const handleEncryptClick = () => {
    voiceEncode();
}

// 执行下载操作
const downloadEncryptedAudio = () => {
    const blob = encryptedBlob.value;
    const fileName = encryptedFileName.value;
    
    if (!blob) {
        alert("没有可下载的文件！请先执行加密操作。");
        return;
    }
    
    // 核心下载逻辑
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = fileName; // 设置下载文件名
    document.body.appendChild(a);
    a.click(); // 触发下载，浏览器会弹出保存对话框（如果设置了）
    
    // 清理和重置状态
    window.URL.revokeObjectURL(url); 
    document.body.removeChild(a);
    
    // 清空状态，防止重复下载或下载旧文件
    encryptedBlob.value = null;
    encryptedFileName.value = '';
};

const handleDecryptClick = () => {
    voiceDecode();
}

</script>

<template>
<div class="grid bg-white items-center gap-2 mx-1">
    <!-- 加密区域 -->
    <Label for="picture">输入wav格式音频</Label>
    <div>
        <Input id="picture" type="file" class="cursor-pointer rounded-sm border-3 border-indigo-500 border-solid" @change="handleFileChange" />
    </div>
        <Input type="email" class="rounded-sm border-3 border-indigo-500 border-solid" placeholder="输入加密信息（解密则无需输入信息）" v-model="secretText" />
    <Button class="cursor-pointer" @click="handleEncryptClick"> {{ buttonStr1 }} </Button>
    <Button class="cursor-pointer bg-green-500" v-if="encryptedBlob"  @click="downloadEncryptedAudio">下载加密后的文件</Button>
    
    <!-- 解密区域 -->
    <Button variant="destructive" class="cursor-pointer" @click="handleDecryptClick"> {{ buttonStr2 }} </Button>
       <Input type="email" class="rounded-sm border-3 border-red-500 border-solid my-3" placeholder="提取到的信息" v-model="decryptedText" />
</div>
    
</template>



<style scoped>

</style>