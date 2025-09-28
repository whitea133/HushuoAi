<script setup lang="ts">
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
</script>

<template>
 <div class="grid grid-cols-1 grid-rows-10 gap-4 m-3"> 
<!-- 下面是信息窗口，以及发送窗口 -->
    <Textarea class="bg-white row-span-6" placeholder="这里是信息窗口" disabled />

    <div class="row-span-4 grid bg-white grid-rows-12 p-1 gap-1">

        <div class="row-span-2 flex items-center space-x-3 px-2">
        <!-- 功能栏 -->
        <Button variant="outline" size="icon" title="文本加解密" class="cursor-pointer">
            <img src="@/components/icons/加密文本.png" alt="文本加解密" class="w-5 h-5" />
        </Button>
        <Button variant="outline" size="icon" title="视频加解密" class="cursor-pointer">
            <img src="@/components/icons/加密视频.png" alt="视频加解密" class="w-5 h-5" />
        </Button>
        <Button variant="outline" size="icon" title="音频加解密" class="cursor-pointer">
            <img src="@/components/icons/加密音频.png" alt="音频加解密" class="w-5 h-5" />
        </Button>
        </div>

        <Textarea class="row-span-8 bg-white" placeholder="这里是对话窗口" />
        
        <div class="row-span-2 flex items-center justify-end px-2">
            <Button class="w-24">发送</Button>
        </div>
        
    </div>

 </div>
</template>


<style scoped>

</style>