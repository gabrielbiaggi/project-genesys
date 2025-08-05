<script setup>
import MonacoEditor from 'monaco-editor-vue3';
import { store } from '../store.js';
import { watch } from 'vue';

// Observa mudanças no conteúdo do arquivo ativo no store
// e atualiza o conteúdo local do editor.
watch(() => store.activeFileContent, (newContent) => {
  if (store.activeFileContent !== newContent) {
      store.activeFileContent = newContent;
  }
});
</script>

<template>
  <div class="w-full h-full bg-gray-900 relative">
    <div v-if="store.isLoadingFileContent" class="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-10">
      <span class="text-white">Carregando arquivo...</span>
    </div>
    <MonacoEditor
      v-else
      class="w-full h-full"
      v-model="store.activeFileContent"
      :options="{
        automaticLayout: true,
        minimap: { enabled: false }
      }"
      theme="vs-dark"
      :language="store.activeFile?.split('.').pop() || 'plaintext'"
    />
  </div>
</template>
