// ide-web/src/store.js
import { reactive } from 'vue';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';

// O estado reativo da nossa IDE
export const store = reactive({
  files: [],
  activeFile: null,
  activeFileContent: '',
  isLoadingFiles: false,
  isLoadingFileContent: false,
  isUploadingFile: false,
  isLoading: false, // Estado de carregamento genérico para o agente
  error: null,
  // Estado para o fluxo de Diff & Approve
  proposedDiff: null,
  newContentForApply: null,
  isApplyingChange: false,
  isAgentActive: false, // Novo estado para controlar a visão central
  // Estados para o ActivityPanel
  thoughtLog: [],
  finalResponse: '',
});

// Ações para modificar o estado
export const actions = {
  async fetchFiles() {
    store.isLoadingFiles = true;
    store.error = null;
    try {
      const response = await axios.get(`${API_URL}/files/list`);
      store.files = response.data.files || [];
    } catch (e) {
      console.error(e);
      store.error = `Não foi possível carregar os arquivos: ${e.response?.data?.detail || e.message}`;
      store.files = [];
    } finally {
      store.isLoadingFiles = false;
    }
  },

  async setActiveFile(filePath) {
    if (!filePath) {
      store.activeFile = null;
      store.activeFileContent = '';
      return;
    }
    
    store.isLoadingFileContent = true;
    store.error = null;
    store.activeFile = filePath;

    try {
      const response = await axios.get(`${API_URL}/files/read?path=${filePath}`);
      store.activeFileContent = response.data.content || '';
    } catch (e) {
      console.error(e);
      store.error = `Não foi possível carregar o conteúdo do arquivo: ${e.response?.data?.detail || e.message}`;
      store.activeFileContent = `Erro ao carregar ${filePath}.`;
    } finally {
      store.isLoadingFileContent = false;
    }
  },

  setProposedDiff(diff, newContent) {
    store.proposedDiff = diff;
    store.newContentForApply = newContent;
  },

  clearProposedDiff() {
    store.proposedDiff = null;
    store.newContentForApply = null;
  },

  async applyChange() {
    if (!store.activeFile || store.newContentForApply === null) {
      store.error = "Nenhuma alteração para aplicar.";
      return;
    }
    store.isApplyingChange = true;
    store.error = null;
    try {
      await axios.post(`${API_URL}/files/write`, {
        path: store.activeFile,
        content: store.newContentForApply,
      });
      // Após aplicar, atualiza o conteúdo do editor e limpa o diff
      store.activeFileContent = store.newContentForApply;
      actions.clearProposedDiff();
      // Opcional: recarregar a lista de arquivos se a alteração puder ter criado/removido um.
      // await actions.fetchFiles(); 
    } catch (e) {
       console.error(e);
      store.error = `Falha ao aplicar alteração: ${e.response?.data?.detail || e.message}`;
    } finally {
      store.isApplyingChange = false;
    }
  },

  // Ação centralizada para enviar diretivas ao agente
  async sendDirective(payload) {
    store.isLoading = true;
    store.isAgentActive = true; // Ativa a visão de atividade
    store.error = null;
    this.clearProposedDiff();

    try {
      const response = await axios.post(`${API_URL}/chat`, payload);
      return response.data; // Retorna os dados para o componente lidar
    } catch (e) {
      console.error(e);
      const errorMessage = e.response?.data?.error || e.response?.data?.detail || e.message || 'Um erro desconhecido ocorreu.';
      store.error = `Falha na comunicação com o Agente: ${errorMessage}`;
      throw e; // Lança o erro para o componente saber que falhou
    } finally {
      store.isLoading = false;
      // Não desativamos o isAgentActive aqui, a UI pode querer manter a visão
    }
  },

  // Nova ação para resetar a visão
  resetView() {
    store.isAgentActive = false;
    this.clearProposedDiff();
    store.thoughtLog = [];
    store.finalResponse = '';
  },

  // Nova ação para fazer upload de arquivos
  async uploadFile(file) {
    store.isUploadingFile = true;
    store.error = null;
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_URL}/files/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      // Após o upload, recarrega a lista de arquivos para exibir o novo item
      await this.fetchFiles();
    } catch (e) {
      console.error(e);
      store.error = `Falha ao enviar o arquivo: ${e.response?.data?.detail || e.message}`;
    } finally {
      store.isUploadingFile = false;
    }
  }
};
