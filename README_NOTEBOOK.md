# 📱 Genesys Notebook - Guia de Teste Remoto

Este guia é especificamente para **testar o servidor Genesys remotamente através do seu notebook**, conectando-se ao servidor principal via túnel Cloudflare.

## 🎯 Objetivo

Permitir que você teste e valide todas as funcionalidades do servidor Genesys a partir de qualquer lugar, usando apenas seu notebook, sem necessidade de instalar o modelo de IA de 70B localmente.

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conexão com a internet
- Servidor Genesys rodando no servidor principal
- Túnel Cloudflare configurado e ativo

## 🚀 Configuração Rápida (Primeira Vez)

### Passo 1: Clone o Repositório (se necessário)
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd myproject
```

### Passo 2: Instale Dependências de Teste
```bash
pip install requests tqdm
```

Este comando instala apenas as dependências essenciais para testar o servidor remotamente.

## 🔧 Configuração da URL do Servidor

### Opção A: Descoberta Automática (Recomendado)
```bash
python scripts/cloudflare_tunnel_helper.py discover
```

### Opção B: URL Padrão (Já Configurada)
A URL do seu túnel já está configurada como padrão:
```env
SERVER_URL=https://genesys.webcreations.com.br
```

## 🧪 Executando os Testes

### Teste Completo (Recomendado)
```bash
python scripts/test_server_notebook.py
```

### Teste Rápido
```bash
python scripts/test_server_notebook.py --quick
```

### Teste com URL Específica (Opcional)
```bash
python scripts/test_server_notebook.py --server-url https://genesys.webcreations.com.br
```

## 📊 O Que os Testes Validam

| Teste | Descrição | Resultado Esperado |
|-------|-----------|-------------------|
| **Conectividade** | Testa se o servidor responde | ✅ Status 200 + mensagem do Gênesis |
| **Chat Básico** | Envia um prompt simples | ✅ Resposta do agente OU modo desenvolvimento |
| **Download de Modelo** | Testa endpoint de download | ✅ Confirmação de verificação |
| **Execução de Script** | Testa capacidade de execução | ✅ Script executado com sucesso |
| **Multimodal** | Testa processamento de imagem | ✅ Resposta multimodal OU não disponível |
| **Performance** | Mede latência da conexão | 📊 Latência em millisegundos |

## 🔍 Monitoramento Contínuo

### Monitorar Túnel em Tempo Real
```bash
python scripts/cloudflare_tunnel_helper.py monitor
```

### Teste de Conectividade Periódico
```bash
python scripts/cloudflare_tunnel_helper.py test
```

## ⚙️ Comandos Úteis

### Verificar Status do Ambiente
```bash
# No ambiente ativado
python -c "import fastapi, uvicorn, requests; print('✅ Ambiente OK')"
```

### Listar Dependências Instaladas
```bash
pip list
```

### Atualizar Dependências
```bash
pip install --upgrade fastapi uvicorn requests
```

### Recriar Ambiente (se necessário)
```bash
python scripts/setup_notebook_environment.py --force-reinstall
```

## 🐛 Solução de Problemas

### Problema: "Túnel não encontrado"
**Soluções:**
1. Verifique se o túnel está rodando no servidor principal
2. Execute: `python scripts/cloudflare_tunnel_helper.py discover`
3. Configure manualmente no arquivo `.env`

### Problema: "Timeout na conexão"
**Soluções:**
1. Verifique sua conexão com a internet
2. Teste com timeout maior: `--timeout 60`
3. Verifique se o firewall não está bloqueando

### Problema: "Agente não carregado (503)"
**Explicação:** Este é o comportamento esperado quando o servidor está em "modo de desenvolvimento" (sem o modelo de IA carregado). Os testes básicos ainda funcionarão.

### Problema: "Módulo não encontrado"
**Soluções:**
1. Certifique-se de que o ambiente está ativado
2. Reinstale: `python scripts/setup_notebook_environment.py --force-reinstall`
3. Instale manualmente: `pip install fastapi uvicorn requests`

## 📈 Interpretando os Resultados

### ✅ Todos os Testes Passaram
Servidor funcionando perfeitamente. Todas as funcionalidades estão operacionais.

### ⚠️ Maioria dos Testes Passou
Servidor operacional com algumas limitações (ex: modelo não carregado). Funcionalidades básicas funcionam.

### ❌ Muitos Testes Falharam
Problema na conectividade ou configuração do servidor. Verifique:
- Túnel Cloudflare está ativo?
- Servidor principal está rodando?
- URL está correta no `.env`?

## 🔄 Fluxo de Trabalho Típico

1. **Manhã:** Verificar se o túnel está ativo
   ```bash
   python scripts/cloudflare_tunnel_helper.py test
   ```

2. **Trabalho:** Executar testes conforme necessário
   ```bash
   python scripts/test_server_notebook.py --quick
   ```

3. **Validação:** Teste completo após mudanças
   ```bash
   python scripts/test_server_notebook.py
   ```

4. **Monitoramento:** Deixar monitor rodando se necessário
   ```bash
   python scripts/cloudflare_tunnel_helper.py monitor
   ```

## 💡 Dicas Avançadas

### Automatizar Testes com Agendamento
**Windows (Task Scheduler):**
```cmd
schtasks /create /tn "Genesis Test" /tr "C:\path\to\python scripts\test_server_notebook.py --quick" /sc hourly
```

**Linux/Mac (Cron):**
```bash
0 * * * * cd /path/to/project && python scripts/test_server_notebook.py --quick
```

### Integração com CI/CD
Os scripts podem ser integrados em pipelines de CI/CD para validação automática:
```yaml
# GitHub Actions exemplo
- name: Test Genesis Server
  run: python scripts/test_server_notebook.py --server-url ${{ secrets.GENESIS_TUNNEL_URL }}
```

### Logs Personalizados
Os scripts salvam logs automáticos. Para acessar:
```bash
# Ver logs de teste (se configurado)
tail -f test_results.log
```

## 🎯 Próximos Passos

Após validar que o servidor está funcionando através dos testes:

1. **Desenvolvimento:** Use a API remotamente para desenvolvimento
2. **Integração:** Conecte outras ferramentas ao servidor via túnel
3. **Monitoramento:** Configure alertas automáticos
4. **Scaling:** Considere múltiplos túneis para redundância

---

## 📞 Suporte

Se encontrar problemas:

1. Execute o teste de diagnóstico: `python scripts/test_server_notebook.py --quick`
2. Verifique os logs do túnel: `python scripts/cloudflare_tunnel_helper.py discover`
3. Consulte a seção de "Solução de Problemas" acima
4. Recrie o ambiente se necessário: `--force-reinstall`

**🎉 Aproveite seu ambiente de teste remoto do Gênesis!**
