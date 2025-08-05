<script setup>
import { onMounted, ref } from 'vue';
import { store, actions } from '../store.js';

const fileInput = ref(null);

// Chama a função para buscar os arquivos quando o componente é montado
onMounted(() => {
  actions.fetchFiles();
});

const handleFileClick = (filePath) => {
  actions.setActiveFile(filePath);
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    actions.uploadFile(file);
  }
  // Reseta o input para permitir o upload do mesmo arquivo novamente
  e.target.value = '';
};
</script>

<template>
  <div class="p-2">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-bold text-gray-300">Explorador</h2>
      <div class="flex items-center space-x-2">
        <input type="file" ref="fileInput" @change="onFileChange" class="hidden" />
        <button @click="triggerFileInput" title="Fazer upload de arquivo" class="text-gray-400 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </button>
        <button @click="actions.fetchFiles" title="Recarregar arquivos" class="text-gray-400 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M20 4h-5v5M4 20h5v-5M12 4V2M12 22v-2M2 12H4M22 12h-2M12 16a4 4 0 100-8 4 4 0 000 8z" />
          </svg>
        </button>
      </div>
    </div>
    
    <div v-if="store.isLoadingFiles" class="text-gray-400">Carregando arquivos...</div>
    <div v-if="store.isUploadingFile" class="text-blue-400">Enviando arquivo...</div>
    <div v-if="store.error" class="text-red-500 text-sm">{{ store.error }}</div>
    
    <ul v-if="!store.isLoadingFiles && !store.error" class="space-y-1">
      <li 
        v-for="file in store.files" 
        :key="file"
        @click="handleFileClick(file)"
        :class="{
          'bg-gray-700 text-white': store.activeFile === file,
          'text-gray-400 hover:bg-gray-700': store.activeFile !== file
        }"
        class="rounded p-1 cursor-pointer text-sm truncate"
      >
        <span>{{ file }}</span>
      </li>
    </ul>

  </div>
</template>
