<script setup lang="ts">
import { computed } from 'vue'
import { Button } from "@/components/ui/button"
import textTool from '@/views/textTool.vue';
import imgTool from '@/views/imgTool.vue'
import voiceTool from '@/views/voiceTool.vue'
import uploadTool from './uploadTool.vue';

const props = withDefaults(defineProps<{
    toolType:  'text' | 'img' | 'voice' | 'upload'}   // toolType必传入
    >(), {
        toolType: 'text'    // 默认值
    })

const toolMap = {
  text: textTool,   // 定义一个映射对象，key默认是字符串，不需要加引号，value是对应的组件。ts会自动识别导入的组件
  img: imgTool,
  voice: voiceTool,
  upload: uploadTool
}

// 计算当前要渲染的组件。
// 必须要用computed动态计算currentTool的值。否则只在第一次打开改vue文件的时候赋值一次currentTool
// 无法做到 props.toolType 的响应式引用
const currentTool = computed(() => toolMap[props.toolType])

</script>


<template>
    <!-- <div class="grid bg-white grid-rows-10 gap-2 mx-2 my-3 justify-center items-center rounded-sm">
    <Button variant="outline" size="icon" title="主页" class="cursor-pointer">
        <img src="@/components/icons/主页.png" alt="主页" />
    </Button>
            <Button variant="outline" size="icon" title="设置" class="cursor-pointer">
        <img src="@/components/icons/设置.png" alt="设置"  />
    </Button>
    </div> -->

  <!-- 动态渲染 -->
  <component :is="currentTool" />

</template>


<style scoped>

</style>