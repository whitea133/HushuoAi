<script setup lang="ts">
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
</script>

<template>
<div class="grid bg-white items-center gap-2 mx-1">
    <Label for="picture">输入视频</Label>
    <div>
        <Input id="picture" type="file" class="cursor-pointer rounded-sm border-3 border-indigo-500 border-solid"/>
    </div>
        <Input type="email" class="rounded-sm border-3 border-indigo-500 border-solid" placeholder="输入加密信息（解密则无需输入信息）" />
    <Button>加密视频</Button>
    <Button variant="destructive">解密视频</Button>
       <Input type="email" class="rounded-sm border-3 border-red-500 border-solid my-3" placeholder="解密信息" />
</div>
</template>



<style scoped>

</style>