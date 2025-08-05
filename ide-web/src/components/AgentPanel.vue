<script setup>
import { ref, watch } from 'vue';
import { store, actions } from '../store.js';
import DiffViewer from './DiffViewer.vue';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

const prompt = ref('');
const thoughtLog = ref([]);
const finalResponse = ref('');
const isLoading = ref(false);

watch(prompt, () => {
  store.error = null;
});

const sendDirective = async () => {
  if (!prompt.value.trim() || !store.activeFile) {
      store.error = "Por favor, selecione um arquivo e forneça uma diretiva.";
      return;
  }

  isLoading.value = true;
  actions.clearProposedDiff();
  thoughtLog.value = [];
  finalResponse.value = '';

  try {
    const fullPrompt = `Considerando o arquivo ativo '${store.activeFile}', minha diretiva é: ${prompt.value}`;
    const response = await axios.post(`${API_URL}/chat`, {
      prompt: fullPrompt,
    });
    
    // Processa os passos intermediários para o log de pensamentos
    if (response.data.intermediate_steps) {
        thoughtLog.value = response.data.intermediate_steps.map(step => {
            return `Pensamento: ${step.log.split('Action:')[0].trim()}\\nFerramenta: ${step.tool}\\nInput: ${step.tool_input}\\nObservação: ${step.observation}`;
        });
    }

    let agentResponse = response.data.response || "O agente não retornou uma resposta.";

    // Tenta parsear a resposta final como JSON para o diff
    try {
      // Limpa a string de quaisquer marcadores de código antes de parsear
      const cleanedResponse = agentResponse.replace(/```json|```/g, '').trim();
      const parsedResponse = JSON.parse(cleanedResponse);
      if (parsedResponse.diff && parsedResponse.new_content) {
        actions.setProposedDiff(parsedResponse.diff, parsedResponse.new_content);
        finalResponse.value = "Proposta de alteração gerada. Revise abaixo.";
      } else {
        finalResponse.value = agentResponse;
      }
    } catch (e) {
      finalResponse.value = agentResponse;
    }

  } catch (e) {
    console.error(e);
    const errorMessage = e.response?.data?.detail || e.message || 'Um erro desconhecido ocorreu.';
    store.error = `Falha na comunicação com o Agente: ${errorMessage}`;
    thoughtLog.value.push('Ocorreu um erro.');
  } finally {
    isLoading.value = false;
    prompt.value = '';
  }
};

const handleApprove = () => {
  actions.applyChange();
};

const handleReject = () => {
  actions.clearProposedDiff();
  finalResponse.value = "Alteração rejeitada pelo usuário.";
};
</script>

<template>
  <div class="flex flex-col h-full p-2">
    <h2 class="text-lg font-bold mb-4 text-gray-300">Agente Gênesis</h2>
    
    <div class="flex-grow bg-gray-900 rounded-lg p-3 mb-4 text-xs overflow-y-auto font-mono">
      <div v-if="!isLoading && thoughtLog.length === 0" class="text-gray-500">
        Aguardando diretiva...
      </div>
      <div v-if="isLoading && thoughtLog.length === 0" class="text-yellow-400">
        Agente Gênesis está pensando...
      </div>

      <div v-for="(log, index) in thoughtLog" :key="index" class="mb-2 p-2 border border-gray-700 rounded">
        <pre class="whitespace-pre-wrap text-gray-400">{{ log }}</pre>
      </div>
      
      <div v-if="finalResponse" class="mt-3 pt-3 border-t border-gray-600 text-green-400">
        <p class="font-bold mb-1">Resposta Final:</p>
        <pre class="whitespace-pre-wrap">{{ finalResponse }}</pre>
      </div>

      <div v-if="store.error" class="mt-3 text-red-400">
        <p class="font-bold">Erro:</p>
        <p>{{ store.error }}</p>
      </div>
    </div>
    
    <DiffViewer
      v-if="store.proposedDiff"
      :diff-text="store.proposedDiff"
      :is-loading="store.isApplyingChange"
      @approve="handleApprove"
      @reject="handleReject"
    />

    <div v-if="store.activeFile" class="mt-auto">
      <textarea
        v-model="prompt"
        @keydown.enter.prevent="sendDirective"
        :disabled="isLoading || !store.activeFile"
        class="bg-gray-700 text-white rounded-lg p-2 w-full h-28 focus:outline-none focus:ring-2 focus:ring-blue-500"
        :placeholder="`Diretiva para '${store.activeFile}'...`"
      ></textarea>
      <button
        @click="sendDirective"
        :disabled="isLoading || !store.activeFile"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg mt-2 disabled:bg-gray-500 disabled:cursor-not-allowed"
      >
        {{ isLoading ? 'Processando...' : 'Enviar Diretiva' }}
      </button>
    </div>
     <div v-else class="mt-auto text-center text-gray-500 p-4 bg-gray-800 rounded-lg">
        Selecione um arquivo no explorador para começar a editar.
    </div>
  </div>
</template>
