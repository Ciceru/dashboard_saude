#!/bin/bash

# ============================================================
# Script para subir o projeto dashboard_saude para o Git
# ============================================================

PASTA_PROJETO="/home/cicero/Documentos/Logica de Programação/Projeto/dashboard_saude"

echo "=============================="
echo " Subindo projeto para o Git"
echo "=============================="

# --- Navegar para a pasta do projeto ---
cd "$PASTA_PROJETO" || { echo "Erro: Pasta do projeto não encontrada."; exit 1; }

# --- Criar .gitignore se não existir ---
if [ ! -f ".gitignore" ]; then
    echo "Criando .gitignore..."
    cat > .gitignore << 'EOF'
# Ambiente virtual Python
venv/
env/
.env/
.venv/

# Cache do Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Arquivos de configuração de IDEs
.vscode/
.idea/
*.swp
*.swo

# Arquivos de sistema
.DS_Store
Thumbs.db

# Logs
*.log

# Arquivos temporários
*.tmp
*.bak

# Dash e Plotly cache
.cache/
EOF
    echo ".gitignore criado com sucesso."
else
    echo ".gitignore já existe. Pulando criação."
fi

# --- Verificar se o Git já foi inicializado ---
if [ ! -d ".git" ]; then
    echo "Inicializando repositório Git..."
    git init
    echo "Repositório Git inicializado."
else
    echo "Repositório Git já existe. Pulando inicialização."
fi

# --- Verificar se o usuário do Git está configurado ---
GIT_USER=$(git config --global user.name)
GIT_EMAIL=$(git config --global user.email)

if [ -z "$GIT_USER" ]; then
    echo ""
    echo "Nome do usuário Git não configurado."
    read -p "Digite seu nome para o Git (ex: Cicero Santos): " NOME_GIT
    git config --global user.name "$NOME_GIT"
fi

if [ -z "$GIT_EMAIL" ]; then
    echo ""
    echo "E-mail do usuário Git não configurado."
    read -p "Digite seu e-mail para o Git (ex: cicero@email.com): " EMAIL_GIT
    git config --global user.email "$EMAIL_GIT"
fi

# --- Verificar se o repositório remoto já está configurado ---
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if [ -z "$REMOTE_URL" ]; then
    echo ""
    echo "Repositório remoto (origin) não configurado."
    echo "Crie um repositório vazio no GitHub (https://github.com/new) e cole a URL abaixo."
    echo "Exemplo: https://github.com/seu-usuario/dashboard_saude.git"
    read -p "Digite a URL do repositório remoto: " REMOTE_URL_INPUT
    git remote add origin "$REMOTE_URL_INPUT"
    echo "Repositório remoto configurado: $REMOTE_URL_INPUT"
else
    echo "Repositório remoto já configurado: $REMOTE_URL"
fi

# --- Adicionar todos os arquivos ao staging ---
echo ""
echo "Adicionando arquivos ao staging..."
git add .

# --- Mostrar o status dos arquivos ---
echo ""
echo "Arquivos que serão enviados:"
echo "------------------------------"
git status --short
echo "------------------------------"

# --- Solicitar mensagem do commit ---
echo ""
read -p "Digite a mensagem do commit (ou pressione Enter para usar a padrão): " MSG_COMMIT

if [ -z "$MSG_COMMIT" ]; then
    DATA_HORA=$(date "+%d/%m/%Y %H:%M")
    MSG_COMMIT="Atualização do projeto - $DATA_HORA"
fi

# --- Criar o commit ---
echo ""
echo "Criando commit: '$MSG_COMMIT'..."
git commit -m "$MSG_COMMIT"

# --- Verificar a branch atual ---
BRANCH_ATUAL=$(git branch --show-current)

if [ -z "$BRANCH_ATUAL" ]; then
    BRANCH_ATUAL="main"
    git checkout -b main
fi

echo ""
echo "Branch atual: $BRANCH_ATUAL"

# --- Enviar para o repositório remoto ---
echo ""
echo "Enviando para o repositório remoto..."
git push -u origin "$BRANCH_ATUAL"

# --- Verificar se o push foi bem-sucedido ---
if [ $? -eq 0 ]; then
    echo ""
    echo "=============================="
    echo " Projeto enviado com sucesso!"
    echo "=============================="
else
    echo ""
    echo "=============================="
    echo " Erro ao enviar o projeto."
    echo " Verifique sua conexão e as"
    echo " credenciais do GitHub."
    echo "=============================="
    exit 1
fi
