<script setup>
import { store } from './store.js';
import FileExplorer from './components/FileExplorer.vue'
import CodeEditor from './components/CodeEditor.vue'
import AgentPanel from './components/AgentPanel.vue'
import Terminal from './components/Terminal.vue'
import ActivityPanel from './components/ActivityPanel.vue' // Importar o novo painel
</script>

<template>
  <div id="app" class="flex h-screen bg-gray-900 text-white font-sans">
    <!-- Coluna da Esquerda: Explorador de Arquivos -->
    <div class="w-1/5 bg-gray-800 p-4 overflow-y-auto flex-shrink-0">
      <FileExplorer />
    </div>

    <!-- Área Central Dinâmica -->
    <div class="w-3/5 flex flex-col flex-grow">
      <!-- Visão Padrão: Editor e Terminal -->
      <template v-if="!store.isAgentActive">
        <div class="h-3/5">
          <CodeEditor />
        </div>
        <div class="h-2/5 border-t-2 border-gray-700">
          <Terminal />
        </div>
      </template>
      <!-- Visão de Atividade: Painel de Atividade do Agente -->
      <template v-else>
        <ActivityPanel />
      </template>
    </div>

    <!-- Coluna da Direita: Painel do Agente -->
    <div class="w-1/5 bg-gray-800 p-4 flex flex-col flex-shrink-0">
      <AgentPanel />
    </div>
  </div>
</template>

<style>
/* Estilos globais para a IDE */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden; /* Previne barras de rolagem no nível da página */
}
</style>
