<script setup lang="ts">
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
</script>

<template>
<div class="grid grid-rows-2 h-screen gap-4 mx-1">
    <div class="row-span-1 grid bg-white grid-rows-8 gap-2">
        <Label for="message" class="row-span-1">加密文本</Label>
        <Textarea class="row-span-5" placeholder="输入要加密的信息" />
        <Button class="row-span-1 cursor-pointer">加密原文</Button>
    </div>
    <div class="row-span-1 grid bg-white grid-rows-8 gap-2">
        <Label for="message" class="row-span-1">解密文本</Label>
        <Textarea class="row-span-5" placeholder="解密密文信息" />
        <Button variant="destructive" class="row-span-1 cursor-pointer">解密密文</Button>
    </div>
</div>

</template>



<style scoped>

</style>