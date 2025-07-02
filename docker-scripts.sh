#!/bin/bash

# Scripts úteis para gerenciar o projeto DGU com Docker
# Torne este arquivo executável: chmod +x docker-scripts.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para verificar se Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker não está rodando. Inicie o Docker primeiro."
        exit 1
    fi
}

# Função para verificar credenciais
check_credentials() {
    if [ ! -f "credentials/bigquery-credentials.json" ]; then
        print_error "Credenciais do BigQuery não encontradas!"
        print_info "Copie suas credenciais para: credentials/bigquery-credentials.json"
        exit 1
    fi
    
    if [ ! -f "DGU/profiles.yml" ]; then
        print_error "Arquivo profiles.yml não encontrado!"
        print_info "Copie e configure: cp DGU/profiles.yml.example DGU/profiles.yml"
        exit 1
    fi
}

# Função principal de setup
setup() {
    print_info "Configurando ambiente DGU..."
    
    # Criar diretórios necessários
    mkdir -p credentials
    mkdir -p logs
    
    # Verificar se profiles.yml existe
    if [ ! -f "DGU/profiles.yml" ]; then
        if [ -f "DGU/profiles.yml.example" ]; then
            cp DGU/profiles.yml.example DGU/profiles.yml
            print_warning "Arquivo profiles.yml criado. Configure suas credenciais!"
        fi
    fi
    
    print_success "Setup concluído!"
    print_info "Próximos passos:"
    echo "1. Copie suas credenciais BigQuery para: credentials/bigquery-credentials.json"
    echo "2. Configure DGU/profiles.yml com seus dados"
    echo "3. Execute: ./docker-scripts.sh run"
}

# Função para executar pipeline completo
run() {
    print_info "Executando pipeline completo..."
    check_docker
    check_credentials
    
    docker-compose up --build
}

# Função para executar em background
run_detached() {
    print_info "Executando pipeline em background..."
    check_docker
    check_credentials
    
    docker-compose up -d --build
    print_success "Pipeline iniciado em background!"
    print_info "Use './docker-scripts.sh logs' para ver o progresso"
}

# Função para ver logs
logs() {
    print_info "Mostrando logs do pipeline..."
    docker-compose logs -f dgu-futebol
}

# Função para executar comandos dbt específicos
dbt_command() {
    local cmd="$1"
    if [ -z "$cmd" ]; then
        print_error "Especifique um comando dbt!"
        print_info "Exemplo: ./docker-scripts.sh dbt 'seed'"
        exit 1
    fi
    
    print_info "Executando: dbt $cmd"
    check_docker
    check_credentials
    
    docker-compose run --rm dgu-futebol bash -c "cd DGU && dbt $cmd --profiles-dir ."
}

# Função para acessar shell do container
shell() {
    print_info "Acessando shell do container..."
    check_docker
    
    docker-compose run --rm dgu-futebol bash
}

# Função para limpar ambiente
clean() {
    print_warning "Limpando ambiente Docker..."
    
    # Parar containers
    docker-compose down
    
    # Remover imagens do projeto
    docker-compose down --rmi all
    
    # Limpar volumes (opcional)
    read -p "Remover volumes também? (logs serão perdidos) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
    fi
    
    print_success "Ambiente limpo!"
}

# Função para mostrar status
status() {
    print_info "Status dos containers:"
    docker-compose ps
    
    print_info "Uso de recursos:"
    docker stats --no-stream
}

# Função para inicializar Airflow
init_airflow() {
    print_info "Inicializando Apache Airflow 3.0..."
    check_docker
    check_credentials

    # Definir AIRFLOW_UID
    export AIRFLOW_UID=$(id -u)

    # Executar script de inicialização do Airflow
    ./airflow/init_airflow.sh
}

# Função para executar com Airflow
run_airflow() {
    print_info "Executando pipeline via Airflow..."
    check_docker
    check_credentials

    export AIRFLOW_UID=$(id -u)

    # Iniciar Airflow se não estiver rodando
    if ! docker-compose -f docker-compose-integrated.yml ps | grep -q "airflow-webserver"; then
        print_info "Iniciando Airflow..."
        docker-compose -f docker-compose-integrated.yml up -d
        sleep 30
    fi

    print_success "Airflow disponível em: http://localhost:8080"
    print_info "Usuário: airflow | Senha: airflow"
}

# Função para parar Airflow
stop_airflow() {
    print_info "Parando serviços do Airflow..."
    docker-compose -f docker-compose-integrated.yml down
    print_success "Airflow parado!"
}

# Função para ver logs do Airflow
logs_airflow() {
    print_info "Mostrando logs do Airflow..."
    docker-compose -f docker-compose-integrated.yml logs -f
}

# Função para mostrar ajuda
help() {
    echo "🏆 Scripts DGU - Pipeline de Dados de Futebol"
    echo ""
    echo "Uso: ./docker-scripts.sh [comando]"
    echo ""
    echo "📋 Comandos Pipeline Tradicional:"
    echo "  setup          - Configurar ambiente inicial"
    echo "  run            - Executar pipeline completo"
    echo "  run-bg         - Executar em background"
    echo "  logs           - Ver logs em tempo real"
    echo "  dbt [cmd]      - Executar comando dbt específico"
    echo "  shell          - Acessar shell do container"
    echo ""
    echo "🚀 Comandos Airflow:"
    echo "  init-airflow   - Inicializar Apache Airflow 3.0"
    echo "  run-airflow    - Executar pipeline via Airflow"
    echo "  stop-airflow   - Parar serviços do Airflow"
    echo "  logs-airflow   - Ver logs do Airflow"
    echo ""
    echo "🛠️ Comandos Gerais:"
    echo "  status         - Ver status dos containers"
    echo "  clean          - Limpar ambiente Docker"
    echo "  help           - Mostrar esta ajuda"
    echo ""
    echo "📊 Exemplos:"
    echo "  ./docker-scripts.sh setup"
    echo "  ./docker-scripts.sh init-airflow"
    echo "  ./docker-scripts.sh run-airflow"
    echo "  ./docker-scripts.sh dbt 'seed'"
    echo ""
    echo "🌐 URLs importantes:"
    echo "  • Airflow Web UI: http://localhost:8080"
    echo "  • Usuário/Senha: airflow/airflow"
}

# Processar argumentos
case "${1:-help}" in
    setup)
        setup
        ;;
    run)
        run
        ;;
    run-bg)
        run_detached
        ;;
    logs)
        logs
        ;;
    dbt)
        dbt_command "$2"
        ;;
    shell)
        shell
        ;;
    init-airflow)
        init_airflow
        ;;
    run-airflow)
        run_airflow
        ;;
    stop-airflow)
        stop_airflow
        ;;
    logs-airflow)
        logs_airflow
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    help|*)
        help
        ;;
esac
