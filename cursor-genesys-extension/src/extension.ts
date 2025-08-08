import * as vscode from 'vscode';
import { GenesysApi } from './genesysApi';
import { GenesysChatProvider } from './chatProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('🤖 Genesys AI Assistant ativado!');

    // Inicializar API
    const genesysApi = new GenesysApi();
    
    // Inicializar Chat Provider
    const chatProvider = new GenesysChatProvider(genesysApi);
    
    // Registrar o provider do chat
    vscode.window.registerTreeDataProvider('genesysChat', chatProvider);

    // Comando: Abrir Chat
    const openChatCommand = vscode.commands.registerCommand('genesys.openChat', async () => {
        const panel = vscode.window.createWebviewPanel(
            'genesysChat',
            '💬 Chat com Genesys',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = getChatWebviewContent();

        // Lidar com mensagens do webview
        panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'sendMessage':
                    try {
                        vscode.window.withProgress({
                            location: vscode.ProgressLocation.Notification,
                            title: '🤖 Genesys pensando...',
                            cancellable: false
                        }, async (progress) => {
                            const response = await genesysApi.sendMessage(message.text);
                            panel.webview.postMessage({
                                command: 'receiveMessage',
                                text: response
                            });
                        });
                    } catch (error) {
                        vscode.window.showErrorMessage(`Erro ao comunicar com Genesys: ${error}`);
                    }
                    break;
            }
        });
    });

    // Comando: Explicar Código
    const explainCodeCommand = vscode.commands.registerCommand('genesys.explainCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('Nenhum editor ativo!');
            return;
        }

        const selection = editor.document.getText(editor.selection);
        if (!selection) {
            vscode.window.showWarningMessage('Selecione um trecho de código primeiro!');
            return;
        }

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: '🧠 Analisando código...',
                cancellable: false
            }, async (progress) => {
                const language = editor.document.languageId;
                const prompt = `Explique o seguinte código ${language}:\n\n\`\`\`${language}\n${selection}\n\`\`\``;
                
                const explanation = await genesysApi.sendMessage(prompt);
                
                // Mostrar resultado em um painel
                const panel = vscode.window.createWebviewPanel(
                    'genesysExplanation',
                    '🧠 Explicação do Código',
                    vscode.ViewColumn.Beside,
                    { enableScripts: true }
                );

                panel.webview.html = getExplanationWebviewContent(selection, explanation, language);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Erro ao explicar código: ${error}`);
        }
    });

    // Comando: Revisar Código
    const reviewCodeCommand = vscode.commands.registerCommand('genesys.reviewCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        const selection = editor.document.getText(editor.selection);
        if (!selection) return;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: '🔍 Revisando código...',
                cancellable: false
            }, async (progress) => {
                const language = editor.document.languageId;
                const prompt = `Faça uma revisão detalhada do seguinte código ${language}, destacando problemas de performance, segurança, boas práticas e sugestões de melhoria:\n\n\`\`\`${language}\n${selection}\n\`\`\``;
                
                const review = await genesysApi.sendMessage(prompt);
                
                const panel = vscode.window.createWebviewPanel(
                    'genesysReview',
                    '🔍 Revisão de Código',
                    vscode.ViewColumn.Beside,
                    { enableScripts: true }
                );

                panel.webview.html = getReviewWebviewContent(selection, review, language);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Erro ao revisar código: ${error}`);
        }
    });

    // Comando: Gerar Código
    const generateCodeCommand = vscode.commands.registerCommand('genesys.generateCode', async () => {
        const prompt = await vscode.window.showInputBox({
            prompt: '💡 Descreva o código que você quer gerar:',
            placeHolder: 'Ex: função para ordenar array por data em JavaScript'
        });

        if (!prompt) return;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: '⚡ Gerando código...',
                cancellable: false
            }, async (progress) => {
                const editor = vscode.window.activeTextEditor;
                const language = editor?.document.languageId || 'javascript';
                
                const codePrompt = `Gere código ${language} para: ${prompt}\n\nRetorne apenas o código, bem comentado e seguindo boas práticas.`;
                const generatedCode = await genesysApi.sendMessage(codePrompt);

                // Inserir no editor atual ou criar novo arquivo
                if (editor) {
                    const position = editor.selection.active;
                    editor.edit(editBuilder => {
                        editBuilder.insert(position, `\n// Gerado por Genesys AI\n${generatedCode}\n`);
                    });
                } else {
                    const document = await vscode.workspace.openTextDocument({
                        content: generatedCode,
                        language: language
                    });
                    vscode.window.showTextDocument(document);
                }
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Erro ao gerar código: ${error}`);
        }
    });

    // Comando: Otimizar Código
    const optimizeCodeCommand = vscode.commands.registerCommand('genesys.optimizeCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        const selection = editor.document.getText(editor.selection);
        if (!selection) return;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: '🚀 Otimizando código...',
                cancellable: false
            }, async (progress) => {
                const language = editor.document.languageId;
                const prompt = `Otimize o seguinte código ${language} para melhor performance, legibilidade e manutenibilidade:\n\n\`\`\`${language}\n${selection}\n\`\`\`\n\nRetorne apenas o código otimizado com comentários explicando as melhorias.`;
                
                const optimizedCode = await genesysApi.sendMessage(prompt);
                
                const panel = vscode.window.createWebviewPanel(
                    'genesysOptimization',
                    '🚀 Código Otimizado',
                    vscode.ViewColumn.Beside,
                    { enableScripts: true }
                );

                panel.webview.html = getOptimizationWebviewContent(selection, optimizedCode, language);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Erro ao otimizar código: ${error}`);
        }
    });

    // Registrar comandos
    context.subscriptions.push(
        openChatCommand,
        explainCodeCommand,
        reviewCodeCommand,
        generateCodeCommand,
        optimizeCodeCommand
    );

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '🤖 Genesys';
    statusBarItem.tooltip = 'Clique para conversar com Genesys';
    statusBarItem.command = 'genesys.openChat';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Verificar conexão com o servidor
    checkServerConnection(genesysApi, statusBarItem);
}

async function checkServerConnection(api: GenesysApi, statusBar: vscode.StatusBarItem) {
    try {
        const isConnected = await api.testConnection();
        if (isConnected) {
            statusBar.text = '🤖 Genesys ✅';
            statusBar.tooltip = 'Genesys conectado e funcionando';
            vscode.window.showInformationMessage('🎉 Genesys AI conectado com sucesso!');
        } else {
            statusBar.text = '🤖 Genesys ❌';
            statusBar.tooltip = 'Genesys desconectado';
        }
    } catch (error) {
        statusBar.text = '🤖 Genesys ⚠️';
        statusBar.tooltip = 'Erro de conexão com Genesys';
        vscode.window.showWarningMessage('⚠️ Não foi possível conectar ao Genesys. Verifique se o servidor está rodando.');
    }
}

function getChatWebviewContent(): string {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat Genesys</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0; padding: 20px; height: 100vh; display: flex; flex-direction: column;
                background: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
            }
            .chat-container { flex: 1; overflow-y: auto; margin-bottom: 20px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
            .user-message { 
                background: var(--vscode-button-background); 
                color: var(--vscode-button-foreground);
                margin-left: 20%;
            }
            .ai-message { 
                background: var(--vscode-textCodeBlock-background);
                margin-right: 20%;
            }
            .input-container { display: flex; gap: 10px; }
            input { 
                flex: 1; padding: 10px; border: 1px solid var(--vscode-input-border);
                background: var(--vscode-input-background); color: var(--vscode-input-foreground);
                border-radius: 4px;
            }
            button { 
                padding: 10px 20px; background: var(--vscode-button-background);
                color: var(--vscode-button-foreground); border: none; border-radius: 4px;
                cursor: pointer;
            }
            button:hover { background: var(--vscode-button-hoverBackground); }
            .typing { opacity: 0.7; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="chat-container" id="chatContainer">
            <div class="message ai-message">
                🤖 <strong>Genesys:</strong> Olá! Como posso ajudar você hoje?
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Digite sua mensagem..." />
            <button onclick="sendMessage()">Enviar</button>
        </div>
        
        <script>
            const vscode = acquireVsCodeApi();
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, 'user');
                input.value = '';
                
                addTypingIndicator();
                vscode.postMessage({ command: 'sendMessage', text: message });
            }
            
            function addMessage(text, sender) {
                const container = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = \`message \${sender}-message\`;
                messageDiv.innerHTML = \`<strong>\${sender === 'user' ? '👤 Você' : '🤖 Genesys'}:</strong> \${text}\`;
                container.appendChild(messageDiv);
                container.scrollTop = container.scrollHeight;
            }
            
            function addTypingIndicator() {
                const container = document.getElementById('chatContainer');
                const typingDiv = document.createElement('div');
                typingDiv.className = 'message ai-message typing';
                typingDiv.id = 'typing';
                typingDiv.innerHTML = '🤖 <strong>Genesys:</strong> digitando...';
                container.appendChild(typingDiv);
                container.scrollTop = container.scrollHeight;
            }
            
            function removeTypingIndicator() {
                const typing = document.getElementById('typing');
                if (typing) typing.remove();
            }
            
            // Receber mensagens do Genesys
            window.addEventListener('message', event => {
                const message = event.data;
                if (message.command === 'receiveMessage') {
                    removeTypingIndicator();
                    addMessage(message.text, 'ai');
                }
            });
            
            // Enter para enviar
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>`;
}

function getExplanationWebviewContent(code: string, explanation: string, language: string): string {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 20px; background: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground); line-height: 1.6;
            }
            .code-block { 
                background: var(--vscode-textCodeBlock-background);
                padding: 15px; border-radius: 8px; margin: 15px 0;
                border-left: 4px solid var(--vscode-button-background);
                overflow-x: auto;
            }
            h2 { color: var(--vscode-button-background); }
            .explanation { background: var(--vscode-textCodeBlock-background); padding: 15px; border-radius: 8px; }
        </style>
    </head>
    <body>
        <h2>🧠 Explicação do Código (${language})</h2>
        <div class="code-block">
            <pre><code>${code}</code></pre>
        </div>
        <h2>📝 Explicação</h2>
        <div class="explanation">
            ${explanation.replace(/\n/g, '<br>')}
        </div>
    </body>
    </html>`;
}

function getReviewWebviewContent(code: string, review: string, language: string): string {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 20px; background: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground); line-height: 1.6;
            }
            .code-block { 
                background: var(--vscode-textCodeBlock-background);
                padding: 15px; border-radius: 8px; margin: 15px 0;
                border-left: 4px solid #ff6b6b; overflow-x: auto;
            }
            h2 { color: var(--vscode-button-background); }
            .review { background: var(--vscode-textCodeBlock-background); padding: 15px; border-radius: 8px; }
        </style>
    </head>
    <body>
        <h2>🔍 Revisão de Código (${language})</h2>
        <div class="code-block">
            <pre><code>${code}</code></pre>
        </div>
        <h2>📋 Análise e Sugestões</h2>
        <div class="review">
            ${review.replace(/\n/g, '<br>')}
        </div>
    </body>
    </html>`;
}

function getOptimizationWebviewContent(original: string, optimized: string, language: string): string {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 20px; background: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground); line-height: 1.6;
            }
            .code-block { 
                background: var(--vscode-textCodeBlock-background);
                padding: 15px; border-radius: 8px; margin: 15px 0;
                overflow-x: auto;
            }
            .original { border-left: 4px solid #ff6b6b; }
            .optimized { border-left: 4px solid #51cf66; }
            h2 { color: var(--vscode-button-background); }
        </style>
    </head>
    <body>
        <h2>🚀 Otimização de Código (${language})</h2>
        
        <h3>📋 Código Original</h3>
        <div class="code-block original">
            <pre><code>${original}</code></pre>
        </div>
        
        <h3>⚡ Código Otimizado</h3>
        <div class="code-block optimized">
            <pre><code>${optimized}</code></pre>
        </div>
    </body>
    </html>`;
}

export function deactivate() {
    console.log('🤖 Genesys AI Assistant desativado');
}
