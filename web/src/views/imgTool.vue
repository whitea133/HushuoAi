<script setup lang="ts">
import { ref } from "vue";
import axios from 'axios';
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

const API_BASE_URL = 'http://10.154.24.21:8010';

const buttonStr1 = ref<string>("图片隐写")    // 隐藏信息按钮的文本，响应式变量
const buttonStr2 = ref<string>("图片提取隐藏信息")

const originalImg = ref<File | null>(null); // 原始的待加密图片
const return_encryptedImg = ref<Blob | null>(null);    // 服务器返回加密后的图片
const return_encryptedImgName = ref<string>('');
const return_attackParameter  = ref<Blob | null>(null); // 服务器返回的攻击参数.pkl文件
const return_attackParameterName = ref<string>('');

const input_encryptedImg = ref<File | null>(null); // 输入加密后的图片
const input_attackParameter = ref<File | null>(null); // 输入攻击次数.pkl文件
const return_decryptedImg = ref<Blob | null>(null); // 破译后的图片
const return_decryptedImgName = ref<string>('');

// 辅助函数：将 Base64 字符串转换为 Blob 对象
const b64toBlob = (b64Data: string, contentType = '', sliceSize = 512): Blob => {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);

        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }

    return new Blob(byteArrays, { type: contentType });
};

// 辅助函数：下载 Blob 对象
const downloadFile = (blob: Blob, fileName: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
};

async function imgEncode(): Promise<void>
{
    // 重置结果和状态
    return_encryptedImg.value = null;
    return_attackParameter.value = null;
    return_encryptedImgName.value = '';
    return_attackParameterName.value = '';

    if (!originalImg.value) {
        alert("请先选择要隐藏的 PNG 图片！");
        return;
    }
    
    buttonStr1.value = "处理中... 请等待";

    const formData = new FormData();
    // API参数名：SECRET_IMAGE_PATH 
    formData.append('SECRET_IMAGE_PATH', originalImg.value, originalImg.value.name); 

    try {
        // **修改为配置对象写法**：/hide 接口返回 JSON，因此不设置 responseType: 'blob'
        const response = await axios({
            url: `${API_BASE_URL}/hide`, 
            method: 'POST',
            data: formData,
        });

        // Axios 自动处理非 2xx 状态码为异常，因此只需处理成功的响应数据
        const data = response.data; 

        const stegoImageB64 = data?.results?.stego_image_b64;
        const dataFileB64 = data?.results?.data_file_b64;

        if (!stegoImageB64 || !dataFileB64) {
             throw new Error("API 响应格式不正确，缺少 Base64 数据。");
        }

        // 1. 转换隐写图片 Base64 -> Blob
        const stegoBlob = b64toBlob(stegoImageB64, 'image/png');
        return_encryptedImg.value = stegoBlob;
        return_encryptedImgName.value = 'stego_' + originalImg.value.name;
        
        // 2. 转换数据文件 Base64 -> Blob
        const parameterFileName = 'data_' + originalImg.value.name.replace('.png', '.pkl');
        const dataBlob = b64toBlob(dataFileB64, 'application/octet-stream');
        return_attackParameter.value = dataBlob;
        return_attackParameterName.value = parameterFileName;
        
        console.log("隐写成功！");
        alert("隐写成功！请下载载秘图片和参数文件。");

    } catch (error) {
        console.error("图片隐写失败:", error);
        // 捕获 Axios 错误，如果存在响应，则显示响应中的错误信息
        if (axios.isAxiosError(error) && error.response) {
            alert(`隐写失败: ${error.response.status} - ${error.response.data || error.message}`);
        } else {
            alert(`隐写失败: ${(error as Error).message}`);
        }
    } finally {
        buttonStr1.value = "图片隐写";
    }
}

async function imgDeocde(): Promise<void>
{
    // 重置结果
    return_decryptedImg.value = null;
    return_decryptedImgName.value = '';
    
    if (!input_encryptedImg.value || !input_attackParameter.value) {
        alert("请同时选择载秘图片（PNG）和对应的参数文件（PKL）！");
        return;
    }
    
    buttonStr2.value = "处理中... 请等待";

    const formData = new FormData();
    // API参数名：STEGO_IMAGE_PATH, DATA_FILE_PATH
    formData.append('STEGO_IMAGE_PATH', input_encryptedImg.value, input_encryptedImg.value.name);
    formData.append('DATA_FILE_PATH', input_attackParameter.value, input_attackParameter.value.name); 

    try {
        // **修改为配置对象写法**：/reveal 接口返回原始图片数据，responseType 必须是 'blob'
        const response = await axios({
            url: `${API_BASE_URL}/reveal`, 
            method: 'POST',
            data: formData,
            responseType: 'blob', // 确保接收到的是二进制 Blob 数据
        });

        // 响应内容是原始二进制数据，Axios 将其放在 response.data 中
        const imageBlob = response.data;
        
        // 检查返回的数据是否确实是图片类型
        if (imageBlob && imageBlob.type.startsWith('image/')) {
            return_decryptedImg.value = imageBlob;
            return_decryptedImgName.value = 'revealed_' + input_encryptedImg.value.name;
            console.log("提取成功！");
            alert("提取成功！请下载恢复后的秘密图片。");
        } else {
             // 如果返回的 Blob 类型不对，通常意味着服务器返回了错误消息（但状态码仍是 200）
             throw new Error(`服务器返回非图片数据，可能是错误信息。返回类型: ${imageBlob?.type || '未知'}`);
        }

    } catch (error) {
        console.error("图片提取失败:", error);
        if (axios.isAxiosError(error) && error.response) {
            // 如果后端返回了错误状态码，但响应体是 Blob，我们无法直接读取文本，所以只能依赖状态码和通用消息。
            alert(`提取失败: ${error.response.status} - ${error.message}`);
        } else {
            alert(`提取失败: ${(error as Error).message}`);
        }
    } finally {
        buttonStr2.value = "图片提取隐藏信息";
    }
}

const inputOrginial = (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
        const selectedFile = input.files[0];
        
        // 检查文件后缀名是否为 .png
        const fileName = selectedFile.name;
        const isWav = fileName.toLowerCase().endsWith('.png');

        if (isWav) 
        {
            // 存储文件对象
            originalImg.value = selectedFile;
            console.log("已选择文件:", fileName);
        } 
        else 
        {
            // 格式不正确时发出警告
            alert(`错误：请选择 png 格式的图片。您选择了 ${fileName}`);   
            // 清空 input 字段，防止用户误以为已选择正确文件
            input.value = ''; 
            originalImg.value = null;
        }
    } 
    else 
    {
        originalImg.value = null;
    }
}

const inputEncrypt = (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
        const selectedFile = input.files[0];
        
        // 检查文件后缀名是否为 .png
        const fileName = selectedFile.name;
        const isWav = fileName.toLowerCase().endsWith('.png');

        if (isWav) 
        {
            // 存储文件对象
            input_encryptedImg.value = selectedFile;
            console.log("已选择文件:", fileName);
        } 
        else 
        {
            // 格式不正确时发出警告
            alert(`错误：请选择 png 格式的图片。您选择了 ${fileName}`);   
            // 清空 input 字段，防止用户误以为已选择正确文件
            input.value = ''; 
            input_encryptedImg.value = null;
        }
    } 
    else 
    {
        input_encryptedImg.value = null;
    }
}

const inputParameter = (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
        const selectedFile = input.files[0];
        
        // 检查文件后缀名是否为 .png
        const fileName = selectedFile.name;
        const isWav = fileName.toLowerCase().endsWith('.pkl');

        if (isWav) 
        {
            // 存储文件对象
            input_attackParameter.value = selectedFile;
            console.log("已选择文件:", fileName);
        } 
        else 
        {
            // 格式不正确时发出警告
            alert(`错误：请选择 pkl参数文件。您选择了 ${fileName}`);   
            // 清空 input 字段，防止用户误以为已选择正确文件
            input.value = ''; 
            input_attackParameter.value = null;
        }
    } 
    else 
    {
        input_attackParameter.value = null;
    }
}

// --- 下载函数绑定，方便在模板中调用 ---

const handleDownloadEncryptedImage = () => {
    if (return_encryptedImg.value) {
        downloadFile(return_encryptedImg.value, return_encryptedImgName.value || 'stego_image.png');
    }
}

const handleDownloadParameter = () => {
    if (return_attackParameter.value) {
        downloadFile(return_attackParameter.value, return_attackParameterName.value || 'data_file.pkl');
    }
}

const handleDownloadDecryptedImage = () => {
    if (return_decryptedImg.value) {
        downloadFile(return_decryptedImg.value, return_decryptedImgName.value || 'revealed_image.png');
    }
}

</script>

<template>
<div class="grid bg-white items-center gap-2 mx-1">
    <Label for="picture">图片加密</Label>
    <div class="grid grid-cols-10 items-center gap-1">
        <div class="col-span-2 bg-amber-200">输入要隐藏的图片:</div>
        <Input id="picture" type="file" class="col-span-8 cursor-pointer rounded-sm border-3 border-indigo-500 border-solid" @change="inputOrginial"/>
    </div>
        <!-- <Input type="email" class="rounded-sm border-3 border-indigo-500 border-solid" placeholder="输入加密信息（解密则无需输入信息）" /> -->
    <Button class="cursor-pointer" @click="imgEncode"> {{ buttonStr1 }} </Button>
    <Button class="cursor-pointer bg-green-600" v-if="return_encryptedImg" @click="handleDownloadEncryptedImage"> 隐写成功，点击下载信息图片 </Button>
    <Button class="cursor-pointer bg-green-600" v-if="return_attackParameter" @click="handleDownloadParameter"> 隐写成功，点击参数文件 </Button>
    
    <Label for="picture">图片解密</Label>
    <div class="grid grid-cols-10 items-center gap-1">
        <div class="col-span-2 bg-amber-200">输入要破解的图片:</div>
        <Input id="picture" type="file" class="col-span-8 cursor-pointer rounded-sm border-3 border-red-500 border-solid" @change="inputEncrypt"/>
    </div>
      <div class="grid grid-cols-10 items-center gap-1">
        <div class="col-span-2 bg-amber-200">输入破解参数文件:</div>
        <Input id="picture" type="file" class="col-span-8 cursor-pointer rounded-sm border-3 border-red-500 border-solid" @chang="inputParameter"/>
    </div>
    <Button variant="destructive" class="cursor-pointer" @click="imgDeocde"> {{ buttonStr2 }} </Button>
       <!-- <Input type="email" class="rounded-sm border-3 border-red-500 border-solid my-3" placeholder="解密信息" /> -->
    <Button class="cursor-pointer bg-green-600" v-if="return_decryptedImg" @click="handleDownloadDecryptedImage"> 破解成功，点击下载信息图片 </Button>
</div>
</template>



<style scoped>

</style>