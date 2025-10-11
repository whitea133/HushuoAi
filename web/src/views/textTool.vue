<script setup lang="ts">
import { ref } from 'vue'; // 1. 导入 ref
import axios from 'axios';
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"


const buttonStr1 = ref<string>('嵌入秘密');
const buttonStr2 = ref<string>('提取秘密');

const API_BASE_URL = 'http://10.154.24.21:8002';
const API_KEY = 'jnu@fenglab';
const plainText = ref<string>('');
const cryptText = ref<string>('');
const DEFAULT_CONTEXT = 'hello'; // 假设的 context

async function textEncode(): Promise<string>
{
    const message = plainText.value.trim();

    if (!message) {
        alert("请输入要嵌入的明文信息！");
        return '';
    }

    try {
        buttonStr1.value = "嵌入秘密中，请稍候。。。"
        const response = await axios({
            url: `${API_BASE_URL}/encode`,
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json',
            },
            data: {
                message: message, // 必填的明文信息
                context: DEFAULT_CONTEXT
                // context（选填，str）引导语言模型的上下文，未提供时使用默认段落。
                // settings（选填，object）覆盖部分生成参数，键可包含 algo/temp/top_p/length/seed。
            },
            timeout: 10000,
        });

        // 检查 API 响应是否成功
        if (response.data && response.data.stego_text) 
        {
            const stegoText = response.data.stego_text as string;
            
            cryptText.value = stegoText; // 将密文详细修改为stegoText

           buttonStr1.value = "嵌入秘密" // 恢复”嵌入秘密“按钮的状态
            return stegoText;

        } 
        else 
        {
            buttonStr1.value = "嵌入秘密" // 恢复”嵌入秘密“按钮的状态
            console.error("API 返回格式错误:", response.data);
            cryptText.value = "嵌入失败：API返回数据结构异常。";
            return ""; 
        }

    } catch (error) {
        let errorMessage = '嵌入失败：网络或服务器错误。';
        if (axios.isAxiosError(error) && error.response) {
            // 捕捉 HTTP 错误（如 401 Unauthorized, 500 Internal Server Error）
            const status = error.response.status;
            const detail = error.response.data?.detail || '服务器未返回详细信息';
            errorMessage = `嵌入失败: HTTP ${status} - ${detail}`;
        }
        
        console.error("嵌入秘密失败:", error);
        cryptText.value = errorMessage;

        buttonStr1.value = "嵌入秘密" // 恢复”嵌入秘密“按钮的状态
        return "";
    }
}

async function textDecode(): Promise<void>
{
    const stegoText = cryptText.value.trim();

    if (!stegoText) {
        alert("请输入要提取信息的密文！");
        return;
    }

    try {
        buttonStr2.value = "提取秘密中，请稍候。。。" // 恢复”嵌入秘密“按钮的状态

        const response = await axios({
            url: `${API_BASE_URL}/decode`,
            method: 'POST',
            
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json',
            },

            data: { 
                stego_text: stegoText,          // 必填：待解析的密文
                context: DEFAULT_CONTEXT,       // 必填：编码时使用的上下文 (必须匹配)
                // settings: {},                 // 选填：如果编码时有 settings，需在这里传入
            },
            timeout: 10000, 
        });

        // 检查 API 响应是否成功
        if (response.data && response.data.recovered_text !== undefined) {
            const recoveredText = response.data.recovered_text as string;
            
            // 成功后将还原出的明文赋值给明文输入框
            plainText.value = recoveredText; 

            alert(`提取成功！提取的秘密已显示。\n实际解析比特数: ${response.data.used_bits}`);
            
        } else {
            console.error("API 返回格式错误或未找到 recovered_text:", response.data);
            alert("提取失败：API返回数据结构异常或无法还原明文。");
        }
        buttonStr2.value = "提取秘密" // 恢复”提取秘密“按钮的状态

    } catch (error) {
        let errorMessage = '提取失败：网络或服务器错误。';
        if (axios.isAxiosError(error) && error.response) {
            const status = error.response.status;
            const detail = error.response.data?.detail || '服务器未返回详细信息';
            errorMessage = `提取失败: HTTP ${status} - ${detail}`;
        }
        
        buttonStr2.value = "提取秘密" // 恢复”提取秘密“按钮的状态
        console.error("文本提取失败:", error);
        alert(errorMessage);
    }
}

const handleEncryptClick = () => {
    // 调用异步函数
    textEncode();
}

const handleDecryptClick = () => {
    textDecode();
}

</script>

<template>
<div class="grid grid-rows-2 h-screen gap-2 mx-1">
    <div class="row-span-1 grid bg-white grid-rows-8 gap-2">
        <Label for="message" class="row-span-1">嵌入秘密</Label>
        <Textarea class="row-span-5" placeholder="输入要嵌入的信息" v-model="plainText"/>
        <Button class="row-span-1 cursor-pointer" @click="handleEncryptClick"> {{ buttonStr1  }} </Button>
    </div>
    <div class="row-span-1 grid bg-white grid-rows-8 gap-2">
        <Label for="message" class="row-span-1">提取秘密</Label>
        <Textarea class="row-span-5" placeholder="提取秘密信息"  v-model="cryptText"/>
        <Button variant="destructive" class="row-span-1 cursor-pointer" @click="handleDecryptClick">  {{ buttonStr2  }} </Button>
    </div>
</div>

</template>



<style scoped>

</style>