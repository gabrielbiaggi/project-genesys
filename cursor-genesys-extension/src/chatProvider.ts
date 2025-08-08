import * as vscode from 'vscode';
import { GenesysApi } from './genesysApi';

export class GenesysChatProvider implements vscode.TreeDataProvider<ChatItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ChatItem | undefined | null | void> = new vscode.EventEmitter<ChatItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ChatItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private chatHistory: ChatMessage[] = [];

    constructor(private genesysApi: GenesysApi) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ChatItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ChatItem): Thenable<ChatItem[]> {
        if (!element) {
            // Itens do nível raiz
            return Promise.resolve([
                new ChatItem('💬 Iniciar Chat', vscode.TreeItemCollapsibleState.None, {
                    command: 'genesys.openChat',
                    title: 'Abrir Chat',
                }),
                new ChatItem('🔍 Status do Servidor', vscode.TreeItemCollapsibleState.Collapsed),
                new ChatItem('⚙️ Configurações', vscode.TreeItemCollapsibleState.Collapsed),
                new ChatItem('📝 Histórico Recente', vscode.TreeItemCollapsibleState.Collapsed),
            ]);
        } else {
            // Itens filhos
            switch (element.label) {
                case '🔍 Status do Servidor':
                    return this.getServerStatusItems();
                case '⚙️ Configurações':
                    return this.getConfigurationItems();
                case '📝 Histórico Recente':
                    return this.getHistoryItems();
                default:
                    return Promise.resolve([]);
            }
        }
    }

    private async getServerStatusItems(): Promise<ChatItem[]> {
        try {
            const isConnected = await this.genesysApi.testConnection();
            const config = this.genesysApi.getConfiguration();
            
            const items = [
                new ChatItem(
                    isConnected ? '✅ Conectado' : '❌ Desconectado', 
                    vscode.TreeItemCollapsibleState.None
                ),
                new ChatItem(
                    `🌐 ${config.serverUrl}`, 
                    vscode.TreeItemCollapsibleState.None
                ),
                new ChatItem(
                    `⏱️ Timeout: ${config.timeout}s`, 
                    vscode.TreeItemCollapsibleState.None
                ),
            ];

            if (isConnected) {
                try {
                    const status = await this.genesysApi.getServerStatus();
                    if (status.message) {
                        const agentStatus = status.message.includes('não carregado') ? 
                            '🟡 Modo Desenvolvimento' : '🟢 Agente Ativo';
                        items.push(new ChatItem(agentStatus, vscode.TreeItemCollapsibleState.None));
                    }
                } catch (error) {
                    items.push(new ChatItem('⚠️ Erro ao obter status', vscode.TreeItemCollapsibleState.None));
                }
            }

            return items;
        } catch (error) {
            return [new ChatItem('❌ Erro ao verificar status', vscode.TreeItemCollapsibleState.None)];
        }
    }

    private getConfigurationItems(): Promise<ChatItem[]> {
        const items = [
            new ChatItem('🔧 Abrir Configurações', vscode.TreeItemCollapsibleState.None, {
                command: 'workbench.action.openSettings',
                title: 'Abrir Configurações',
                arguments: ['genesys']
            }),
            new ChatItem('🔄 Recarregar Extensão', vscode.TreeItemCollapsibleState.None, {
                command: 'workbench.action.reloadWindow',
                title: 'Recarregar'
            }),
            new ChatItem('🧪 Testar Conexão', vscode.TreeItemCollapsibleState.None, {
                command: 'genesys.testConnection',
                title: 'Testar Conexão'
            }),
        ];

        return Promise.resolve(items);
    }

    private getHistoryItems(): Promise<ChatItem[]> {
        const recentMessages = this.chatHistory.slice(-5).reverse();
        
        if (recentMessages.length === 0) {
            return Promise.resolve([
                new ChatItem('💭 Nenhuma conversa recente', vscode.TreeItemCollapsibleState.None)
            ]);
        }

        const items = recentMessages.map((msg, index) => {
            const preview = msg.content.length > 50 ? 
                msg.content.substring(0, 50) + '...' : 
                msg.content;
            
            const icon = msg.sender === 'user' ? '👤' : '🤖';
            
            return new ChatItem(
                `${icon} ${preview}`,
                vscode.TreeItemCollapsibleState.None,
                undefined,
                msg.content // tooltip com conteúdo completo
            );
        });

        return Promise.resolve(items);
    }

    // Métodos para gerenciar histórico de chat
    addMessage(sender: 'user' | 'genesys', content: string) {
        this.chatHistory.push({
            sender,
            content,
            timestamp: new Date()
        });

        // Manter apenas as últimas 50 mensagens
        if (this.chatHistory.length > 50) {
            this.chatHistory = this.chatHistory.slice(-50);
        }

        this.refresh();
    }

    clearHistory() {
        this.chatHistory = [];
        this.refresh();
    }

    getHistory(): ChatMessage[] {
        return [...this.chatHistory];
    }
}

class ChatItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly command?: vscode.Command,
        public readonly tooltip?: string
    ) {
        super(label, collapsibleState);
        
        if (tooltip) {
            this.tooltip = tooltip;
        }

        if (command) {
            this.command = command;
        }

        // Definir contexto para itens específicos
        this.contextValue = this.getContextValue();
    }

    private getContextValue(): string {
        if (this.label.includes('Chat')) return 'chat';
        if (this.label.includes('Configurações')) return 'config';
        if (this.label.includes('Status')) return 'status';
        if (this.label.includes('Histórico')) return 'history';
        return 'item';
    }
}

interface ChatMessage {
    sender: 'user' | 'genesys';
    content: string;
    timestamp: Date;
}
