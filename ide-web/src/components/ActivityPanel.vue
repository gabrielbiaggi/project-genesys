<script setup>
import { store, actions } from '../store.js';
import DiffViewer from './DiffViewer.vue';

// Funções para lidar com a aprovação ou rejeição vinda do DiffViewer
const handleApprove = () => {
  actions.applyChange();
  // Após aprovar, podemos querer voltar para a visão do editor
  // actions.resetView();
};

const handleReject = () => {
  actions.clearProposedDiff();
  // Após rejeitar, voltamos para a visão do editor/terminal
  actions.resetView(); 
};
</script>

<template>
  <div class="h-full flex flex-col p-4 bg-gray-900 overflow-y-auto">
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-gray-200">Atividade do Agente Gênesis</h2>
        <button @click="actions.resetView" class="text-gray-400 hover:text-white">&times; Fechar</button>
    </div>
    
    <!-- Log de Pensamentos e Resposta Final -->
    <div class="flex-grow bg-gray-800 rounded-lg p-3 mb-4 text-sm font-mono overflow-y-auto">
      <div v-if="store.isLoading && !store.thoughtLog?.length" class="text-yellow-300">
        Agente Gênesis está pensando...
      </div>

      <div v-for="(log, index) in store.thoughtLog" :key="index" class="mb-3 p-2 border-l-2 border-gray-600">
        <pre class="whitespace-pre-wrap text-gray-300">{{ log }}</pre>
      </div>
      
      <div v-if="store.finalResponse" class="mt-4 pt-3 border-t border-gray-700 text-green-300">
        <p class="font-bold mb-1">Resposta Final:</p>
        <pre class="whitespace-pre-wrap">{{ store.finalResponse }}</pre>
      </div>

      <div v-if="store.error" class="mt-4 text-red-400">
        <p class="font-bold">Erro:</p>
        <p>{{ store.error }}</p>
      </div>
    </div>

    <!-- Visualizador de Diff -->
    <DiffViewer
      v-if="store.proposedDiff"
      :diff-text="store.proposedDiff"
      :is-loading="store.isApplyingChange"
      @approve="handleApprove"
      @reject="handleReject"
    />
  </div>
</template>
