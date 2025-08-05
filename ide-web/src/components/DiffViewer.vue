<script setup>
import { defineProps, defineEmits } from 'vue';
import VueDiff, { DiffMode } from 'vue-diff';

const props = defineProps({
  diffText: {
    type: String,
    required: true,
  },
  isLoading: {
    type: Boolean,
    default: false,
  }
});

const emits = defineEmits(['approve', 'reject']);
</script>

<template>
  <div class="diff-viewer-container p-2 border-t border-gray-700">
    <h3 class="text-md font-bold mb-2 text-gray-300">Proposta de Alteração</h3>
    <div class="max-h-96 overflow-y-auto rounded bg-gray-800 p-2 text-xs">
      <VueDiff :mode="DiffMode.UNIFIED" theme="dark" :old-string="''" :new-string="diffText" />
    </div>
    <div class="flex justify-end space-x-2 mt-3">
      <button 
        @click="$emit('reject')"
        :disabled="isLoading"
        class="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm disabled:opacity-50"
      >
        Rejeitar
      </button>
      <button 
        @click="$emit('approve')"
        :disabled="isLoading"
        class="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-sm disabled:opacity-50"
      >
        {{ isLoading ? 'Aplicando...' : 'Aprovar e Aplicar' }}
      </button>
    </div>
  </div>
</template>

<style>
/* Estilos para o componente vue-diff */
.vue-diff-theme-dark {
  background-color: #1f2937; /* bg-gray-800 */
}
.vue-diff-hunk-header {
  background-color: #374151; /* bg-gray-700 */
}
</style>
