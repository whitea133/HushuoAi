<script setup lang="ts">
import { Button } from "@/components/ui/button"
</script>


<template>
    <div class="grid bg-white grid-rows-10 gap-2 mx-2 my-3 justify-center items-center rounded-sm">
    <Button variant="outline" size="icon" title="主页" class="cursor-pointer">
        <img src="@/components/icons/主页.png" alt="主页" />
    </Button>
            <Button variant="outline" size="icon" title="设置" class="cursor-pointer">
        <img src="@/components/icons/设置.png" alt="设置"  />
    </Button>
            <!-- <Button variant="outline" size="icon" title="文本加解密" class="cursor-pointer">
        <img src="@/components/icons/加密文本.png" alt="文本加解密" class="w-5 h-5" />
    </Button> -->
    </div>
</template>


<style scoped>

</style>