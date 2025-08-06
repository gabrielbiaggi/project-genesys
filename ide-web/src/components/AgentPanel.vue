<script setup>
import { ref } from 'vue';
import { store, actions } from '../store.js';

const prompt = ref('');
const attachedImage = ref(null);
const imagePreview = ref(null);

const handleImageAttach = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      attachedImage.value = e.target.result.split(',')[1];
      imagePreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const sendDirective = async () => {
  if (!prompt.value.trim()) {
      store.error = "Por favor, forneça uma diretiva.";
      return;
  }

  // Limpa os logs antigos da store
  store.thoughtLog = [];
  store.finalResponse = '';

  try {
    const payload = {
      prompt: prompt.value,
      image: attachedImage.value
    };
    
    if (!payload.image && store.activeFile) {
        payload.prompt = `Considerando o arquivo ativo '${store.activeFile}', minha diretiva é: ${prompt.value}`;
    }

    const data = await actions.sendDirective(payload);
    
    if (data.intermediate_steps) {
        store.thoughtLog = data.intermediate_steps.map(step => {
            return `Pensamento: ${step.log.split('Action:')[0].trim()}\\nFerramenta: ${step.tool}\\nInput: ${step.tool_input}\\nObservação: ${step.observation}`;
        });
    }

    let agentResponse = data.response || "O agente não retornou uma resposta.";

    try {
      const cleanedResponse = agentResponse.replace(/```json|```/g, '').trim();
      const parsedResponse = JSON.parse(cleanedResponse);
      if (parsedResponse.diff && parsedResponse.new_content) {
        actions.setProposedDiff(parsedResponse.diff, parsedResponse.new_content);
        store.finalResponse = "Proposta de alteração gerada. Revise no painel central.";
      } else {
        store.finalResponse = agentResponse;
      }
    } catch (e) {
      store.finalResponse = agentResponse;
    }

  } catch (e) {
    store.thoughtLog.push('Ocorreu um erro ao processar a diretiva.');
  } finally {
    prompt.value = '';
    attachedImage.value = null;
    imagePreview.value = null;
  }
};

const handleApprove = () => {
  actions.applyChange();
};

const handleReject = () => {
  actions.clearProposedDiff();
  store.finalResponse = "Alteração rejeitada pelo usuário.";
};
</script>

<template>
  <div class="flex flex-col h-full p-2">
    <h2 class="text-lg font-bold mb-4 text-gray-300">Agente Gênesis</h2>
    
    <div class="flex-grow bg-gray-900 rounded-lg p-3 mb-4 text-xs overflow-y-auto font-mono">
        <div v-if="store.isAgentActive" class="text-yellow-400">
            Processando diretiva no painel central...
        </div>
         <div v-else class="text-gray-500">
            Aguardando diretiva...
        </div>
    </div>
    
    <!-- O DiffViewer foi removido daqui -->

    <div v-if="store.activeFile || attachedImage" class="mt-auto">
      <div v-if="imagePreview" class="mb-2 relative w-full">
        <img :src="imagePreview" alt="Preview da imagem" class="max-h-32 rounded-lg" />
        <button @click="imagePreview = null; attachedImage = null" class="absolute top-1 right-1 bg-red-600 text-white rounded-full h-5 w-5 flex items-center justify-center text-xs">&times;</button>
      </div>

      <div class="flex items-center">
        <textarea
          v-model="prompt"
          @keydown.enter.prevent="sendDirective"
          :disabled="store.isLoading"
          class="bg-gray-700 text-white rounded-l-lg p-2 w-full h-28 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :placeholder="attachedImage ? 'Descreva a imagem ou dê uma diretiva...' : `Diretiva para '${store.activeFile}'...`"
        ></textarea>
        <label for="image-upload" class="bg-gray-700 hover:bg-gray-600 h-28 px-3 flex items-center justify-center cursor-pointer rounded-r-lg">
           <input id="image-upload" type="file" @change="handleImageAttach" accept="image/*" class="hidden" />
           <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
        </label>
      </div>

      <button
        @click="sendDirective"
        :disabled="store.isLoading"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg mt-2 disabled:bg-gray-500 disabled:cursor-not-allowed"
      >
        {{ store.isLoading ? 'Processando...' : 'Enviar Diretiva' }}
      </button>
    </div>
     <div v-else class="mt-auto text-center text-gray-500 p-4 bg-gray-800 rounded-lg">
        Selecione um arquivo ou anexe uma imagem para começar.
    </div>
  </div>
</template>
