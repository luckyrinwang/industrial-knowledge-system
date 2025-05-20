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
import { onMounted, onBeforeUnmount, ref, computed } from 'vue';
import config from '@/config';

// 构建Dify URL
const difyUrl = computed(() => {
  if (config.dify.useFullChatInterface) {
    return `${config.dify.baseUrl}/chat/${config.dify.token}`;
  } else {
    return `${config.dify.baseUrl}/chatbot/${config.dify.token}`;
  }
});

// 调整iframe高度的函数
const resizeIframe = () => {
  const iframe = document.querySelector('.chatbot-iframe');
  if (iframe) {
    const container = document.querySelector('.chatbot-container');
    if (container) {
      iframe.style.height = `${container.clientHeight}px`;
      iframe.style.width = `${container.clientWidth}px`;
    }
  }
};

onMounted(() => {
  // 初始调整
  resizeIframe();
  // 添加窗口大小变化的监听器
  window.addEventListener('resize', resizeIframe);
});

onBeforeUnmount(() => {
  // 清理监听器
  window.removeEventListener('resize', resizeIframe);
});
</script>

<style scoped>
.knowledge-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

/* 全屏模式下的样式调整 */
.full-interface {
  margin-top: 0 !important;
  height: 100% !important;
  border-radius: 0 !important;
}

.chatbot-container {
  flex: 1;
  margin-top: 20px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  min-height: v-bind('config.dify.iframe.minHeight');
  /* 增加z-index确保iframe内容能够正确显示 */
  z-index: 1;
}

.chatbot-iframe {
  width: 100%;
  height: 100%;
  border: none;
  position: absolute;
  top: 0;
  left: 0;
}

h2 {
  margin-top: 0;
  margin-bottom: 0;
  color: #303133;
}
</style>
