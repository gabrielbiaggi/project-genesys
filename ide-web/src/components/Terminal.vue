<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

// Constrói a URL do WebSocket a partir da URL base da API
const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';
const wsUrl = baseUrl.replace(/^http/, 'ws');
const API_WS_URL = `${wsUrl}/ws/terminal`;

const terminalRef = ref(null);
let term;
let fitAddon;
let socket;

const connectWebSocket = () => {
  socket = new WebSocket(API_WS_URL);

  socket.onopen = () => {
    term.writeln('\\n>>> Conectado ao shell do servidor Gênesis <<<');
  };

  socket.onmessage = (event) => {
    // Escreve os dados recebidos do servidor diretamente no terminal
    term.write(event.data);
  };

  socket.onerror = (error) => {
    console.error('Erro no WebSocket:', error);
    term.writeln('\\n>>> Erro de conexão com o servidor. Tente recarregar. <<<');
  };

  socket.onclose = () => {
    term.writeln('\\n>>> Conexão com o servidor encerrada. <<<');
  };
};

onMounted(() => {
  if (terminalRef.value) {
    term = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'monospace',
      theme: {
        background: '#18181B',
        foreground: '#D4D4D4',
        cursor: '#D4D4D4',
      },
    });

    fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    
    term.open(terminalRef.value);
    fitAddon.fit();
    
    // Conecta ao backend via WebSocket
    connectWebSocket();

    // Envia os dados do terminal para o backend quando o usuário digita
    term.onData(data => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(data);
      }
    });
    
    window.addEventListener('resize', () => fitAddon.fit());
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', () => fitAddon.fit());
  if (socket) {
    socket.close();
  }
  if (term) {
    term.dispose();
  }
});

</script>

<template>
  <div ref="terminalRef" class="w-full h-full p-2 bg-[#18181B]"></div>
</template>
