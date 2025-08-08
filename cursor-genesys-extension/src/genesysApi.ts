import axios, { AxiosResponse } from 'axios';
import * as vscode from 'vscode';

export interface GenesysResponse {
    response: string;
    intermediate_steps?: any[];
}

export class GenesysApi {
    private serverUrl: string = '';
    private timeout: number = 30000;

    constructor() {
        this.updateConfiguration();
        
        // Atualizar configuração quando as settings mudarem
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('genesys')) {
                this.updateConfiguration();
            }
        });
    }

    private updateConfiguration() {
        const config = vscode.workspace.getConfiguration('genesys');
        this.serverUrl = config.get('serverUrl', 'https://genesys.webcreations.com.br');
        this.timeout = config.get('timeout', 30) * 1000; // converter para ms
    }

    /**
     * Testa a conexão com o servidor Genesys
     */
    async testConnection(): Promise<boolean> {
        try {
            const response = await axios.get(this.serverUrl, {
                timeout: 5000
            });
            
            return response.status === 200 && 
                   response.data.message && 
                   response.data.message.includes('Genesys');
        } catch (error) {
            console.error('Erro ao testar conexão com Genesys:', error);
            return false;
        }
    }

    /**
     * Envia uma mensagem para o Genesys e retorna a resposta
     */
    async sendMessage(prompt: string, includeContext: boolean = true): Promise<string> {
        try {
            // Incluir contexto do arquivo atual se solicitado
            let enhancedPrompt = prompt;
            
            if (includeContext) {
                const context = this.getCurrentContext();
                if (context) {
                    enhancedPrompt = `${context}\n\n${prompt}`;
                }
            }

            const response: AxiosResponse<GenesysResponse> = await axios.post(
                `${this.serverUrl}/chat`,
                {
                    prompt: enhancedPrompt
                },
                {
                    timeout: this.timeout,
                    headers: {
                        'Content-Type': 'application/json',
                        'User-Agent': 'Cursor-Genesys-Extension/1.0'
                    }
                }
            );

            if (response.data && response.data.response) {
                return response.data.response;
            } else {
                throw new Error('Resposta inválida do servidor Genesys');
            }

        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 503) {
                    return 'ℹ️ O modelo Genesys não está carregado no momento. O servidor está em modo de desenvolvimento.';
                } else if (error.code === 'ECONNABORTED') {
                    throw new Error('Timeout: O Genesys está demorando para responder');
                } else if (error.response) {
                    throw new Error(`Erro do servidor: ${error.response.status} - ${error.response.statusText}`);
                } else if (error.request) {
                    throw new Error('Não foi possível conectar ao servidor Genesys. Verifique se está rodando.');
                }
            }
            
            throw new Error(`Erro inesperado: ${error}`);
        }
    }

    /**
     * Envia uma imagem junto com texto para análise multimodal
     */
    async sendMessageWithImage(prompt: string, imageBase64: string): Promise<string> {
        try {
            const response: AxiosResponse<GenesysResponse> = await axios.post(
                `${this.serverUrl}/chat`,
                {
                    prompt: prompt,
                    image: imageBase64
                },
                {
                    timeout: this.timeout * 2, // Timeout maior para multimodal
                    headers: {
                        'Content-Type': 'application/json',
                        'User-Agent': 'Cursor-Genesys-Extension/1.0'
                    }
                }
            );

            if (response.data && response.data.response) {
                return response.data.response;
            } else {
                throw new Error('Resposta inválida do servidor Genesys');
            }

        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 503) {
                    return 'ℹ️ A funcionalidade multimodal não está disponível no momento.';
                }
            }
            throw error;
        }
    }

    /**
     * Obtém informações de status do servidor
     */
    async getServerStatus(): Promise<any> {
        try {
            const response = await axios.get(this.serverUrl, {
                timeout: 5000
            });
            return response.data;
        } catch (error) {
            throw new Error('Não foi possível obter status do servidor');
        }
    }

    /**
     * Obtém o contexto atual do editor (arquivo, linguagem, seleção)
     */
    private getCurrentContext(): string | null {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return null;

        const config = vscode.workspace.getConfiguration('genesys');
        const includeContext = config.get('includeContext', true);
        
        if (!includeContext) return null;

        const document = editor.document;
        const fileName = document.fileName.split('/').pop() || 'arquivo';
        const language = document.languageId;
        
        // Incluir algumas linhas de contexto ao redor da seleção/cursor
        const selection = editor.selection;
        const startLine = Math.max(0, selection.start.line - 5);
        const endLine = Math.min(document.lineCount - 1, selection.end.line + 5);
        
        const contextRange = new vscode.Range(startLine, 0, endLine, document.lineAt(endLine).text.length);
        const contextCode = document.getText(contextRange);

        return `Contexto do arquivo atual:
Arquivo: ${fileName}
Linguagem: ${language}
Trecho de código (linhas ${startLine + 1}-${endLine + 1}):
\`\`\`${language}
${contextCode}
\`\`\``;
    }

    /**
     * Verifica se o servidor suporta uma funcionalidade específica
     */
    async checkFeatureSupport(feature: 'multimodal' | 'tools' | 'memory'): Promise<boolean> {
        try {
            const status = await this.getServerStatus();
            
            switch (feature) {
                case 'multimodal':
                    return status.message && !status.message.includes('não carregado');
                case 'tools':
                    return true; // API sempre suporta tools
                case 'memory':
                    return true; // API sempre suporta memory
                default:
                    return false;
            }
        } catch (error) {
            return false;
        }
    }

    /**
     * Configurações personalizáveis
     */
    getConfiguration() {
        return {
            serverUrl: this.serverUrl,
            timeout: this.timeout / 1000, // retornar em segundos
        };
    }
}
