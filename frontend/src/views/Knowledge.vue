<template>
  <div class="knowledge-container">
    <h2 v-if="!config.dify.useFullChatInterface">知识库问答</h2>
    <div class="chatbot-container" :class="{ 'full-interface': config.dify.useFullChatInterface }">
      <!-- 使用iframe方式嵌入Dify对话界面 -->
      <iframe
        :src="difyUrl"
        frameborder="0"
        allow="microphone"
        class="chatbot-iframe">
      </iframe>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import config from '@/config';

// 构建 Dify URL
const difyUrl = computed(() => {
  if (config.dify.useFullChatInterface) {
    return `${config.dify.baseUrl}/chat/${config.dify.token}`;
  } else {
    return `${config.dify.baseUrl}/chatbot/${config.dify.token}`;
  }
});
</script>

<style scoped>
/* 保证页面全高，外层容器需配合设置 height: 100% */
html, body, #app {
  height: 100%;
  margin: 0;
}

.knowledge-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
}

/* 全屏模式下的样式调整 */
.full-interface {
  margin-top: 0 !important;
  height: 100% !important;
  border-radius: 0 !important;
}

.chatbot-container {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  height: 100%;
  margin-top: 20px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.chatbot-iframe {
  width: 100%;
  height: 100%;
  border: none;
  position: relative; /* 替代 absolute，防止破坏布局 */
  display: block;
}

h2 {
  margin-top: 0;
  margin-bottom: 0;
  color: #303133;
}
</style>
