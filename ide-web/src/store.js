// ide-web/src/store.js
import { reactive } from 'vue';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// O estado reativo da nossa IDE
export const store = reactive({
  files: [],
  activeFile: null,
  activeFileContent: '',
  isLoadingFiles: false,
  isLoadingFileContent: false,
  isUploadingFile: false, // Novo estado para o feedback de upload
  error: null,
  // Estado para o fluxo de Diff & Approve
  proposedDiff: null,
  newContentForApply: null,
  isApplyingChange: false,
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
