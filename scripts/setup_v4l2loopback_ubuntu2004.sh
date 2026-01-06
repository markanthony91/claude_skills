#!/bin/bash

# Script para configurar v4l2loopback no WSL Ubuntu 20.04
# Otimizado especificamente para Ubuntu 20.04 LTS
# Execute com: sudo ./setup_v4l2loopback_ubuntu2004.sh

set -e  # Sair imediatamente se qualquer comando falhar

DELAY=2
ACTIVE_KERNEL=$(uname -r)
V4L2LOOPBACK_VIDEO_NR=10
V4L2LOOPBACK_CARD_LABEL="WSL Virtual Cam (Ubuntu 20.04)"
MODULE_NAME="v4l2loopback"

# Verificar se está sendo executado com sudo
if [[ $EUID -ne 0 ]]; then
    echo "ERRO: Este script deve ser executado com sudo"
    echo "Uso: sudo $0"
    exit 1
fi

# Verificar se é Ubuntu 20.04
if ! grep -q "Ubuntu 20.04" /etc/os-release 2>/dev/null; then
    echo "AVISO: Este script foi otimizado para Ubuntu 20.04. Sua distribuição pode funcionar, mas pode haver diferenças."
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar dependências necessárias (específico para Ubuntu 20.04)
check_dependencies() {
    local deps=("modprobe" "dpkg-reconfigure" "dkms" "lsmod" "depmod" "apt-get")
    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            echo "ERRO: Comando '$cmd' não encontrado."
            exit 1
        fi
    done
}

# Função para imprimir mensagem e adicionar delay
echo_and_sleep() {
    echo "$1"
    sleep $DELAY
}

# Função melhorada para executar comandos (compatível com bash Ubuntu 20.04)
execute_and_sleep() {
    echo "--------------------------------------------------------------------"
    echo "Executando: $*"
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "ATENÇÃO: Comando '$*' falhou com status $status." >&2
    else
        echo "Comando '$*' executado com sucesso."
    fi
    echo "--------------------------------------------------------------------"
    sleep $DELAY
    return $status
}

# Função para buscar arquivo .ko alternativo (otimizada para Ubuntu 20.04)
find_alternative_ko() {
    echo "Procurando por ${MODULE_NAME}.ko alternativo..."
    
    # Primeiro: padrão conhecido com '+'
    local source_ko="/lib/modules/${ACTIVE_KERNEL}+/updates/dkms/${MODULE_NAME}.ko"
    if [ -f "$source_ko" ]; then
        echo "Encontrado: $source_ko"
        echo "$source_ko"
        return 0
    fi
    
    # Segundo: busca mais ampla (compatível com find do Ubuntu 20.04)
    local kernel_base=$(echo "$ACTIVE_KERNEL" | cut -d'-' -f1-3)  # Ex: 5.15.167
    echo "Buscando módulos compatíveis com base do kernel: $kernel_base"
    
    # Busca mais conservadora para Ubuntu 20.04
    local found_ko
    found_ko=$(find /lib/modules/ -name "${MODULE_NAME}.ko" -path "*${kernel_base}*" 2>/dev/null | grep -v "/${ACTIVE_KERNEL}/" | head -1)
    
    if [ -n "$found_ko" ] && [ -f "$found_ko" ]; then
        echo "Encontrado: $found_ko"
        echo "$found_ko"
        return 0
    fi
    
    echo "Nenhum módulo alternativo encontrado."
    return 1
}

# Limpeza em caso de falha
cleanup_on_failure() {
    echo "Executando limpeza devido a falha..."
    modprobe -r ${MODULE_NAME} 2>/dev/null || true
}

# Trap para cleanup (funciona bem no Ubuntu 20.04)
trap cleanup_on_failure ERR

echo_and_sleep "--- Iniciando configuração do ${MODULE_NAME} para Ubuntu 20.04 ---"
echo_and_sleep "Kernel ativo: ${ACTIVE_KERNEL}"

echo_and_sleep "Verificando dependências..."
check_dependencies

echo_and_sleep "Passo 1: Atualizando lista de pacotes..."
execute_and_sleep apt-get update

# Specific para Ubuntu 20.04 - problema comum com mudanças de label
echo_and_sleep "Passo 1b: Resolvendo possíveis problemas de repositório (comum no Ubuntu 20.04)..."
execute_and_sleep apt-get --allow-releaseinfo-change update

echo_and_sleep "Passo 2: Instalando ${MODULE_NAME}-dkms..."
execute_and_sleep apt-get install -y ${MODULE_NAME}-dkms

echo_and_sleep "Passo 3: Tentando instalar headers para ${ACTIVE_KERNEL}..."
if ! apt-get install -y "linux-headers-${ACTIVE_KERNEL}" 2>/dev/null; then
    echo_and_sleep "Headers específicos não encontrados - isso é normal para kernels WSL customizados."
fi

echo_and_sleep "Passo 4: Reconfigurando ${MODULE_NAME}-dkms..."
execute_and_sleep dpkg-reconfigure -f noninteractive ${MODULE_NAME}-dkms

echo_and_sleep "Passo 5: Verificando status do DKMS..."
echo "Status atual do DKMS:"
dkms status | grep -i v4l2loopback || echo "Nenhum status v4l2loopback encontrado"
sleep $DELAY

# Verificar se módulo já está carregado
echo_and_sleep "Verificando se ${MODULE_NAME} já está carregado..."
if lsmod | grep -q "^${MODULE_NAME} "; then
    echo_and_sleep "Módulo já carregado. Removendo para recarregar com novos parâmetros..."
    execute_and_sleep modprobe -r ${MODULE_NAME}
fi

echo_and_sleep "Passo 6: Tentando carregar o módulo ${MODULE_NAME}..."
if modprobe ${MODULE_NAME} video_nr=${V4L2LOOPBACK_VIDEO_NR} card_label="${V4L2LOOPBACK_CARD_LABEL}" exclusive_caps=1; then
    echo_and_sleep "SUCESSO! Módulo ${MODULE_NAME} carregado diretamente."
else
    echo_and_sleep "Falha ao carregar diretamente. Iniciando workaround..."
    
    # Buscar arquivo .ko alternativo
    SOURCE_KO_PATH=$(find_alternative_ko)
    if [ $? -eq 0 ] && [ -n "$SOURCE_KO_PATH" ]; then
        TARGET_KO_DIR="/lib/modules/${ACTIVE_KERNEL}/updates/dkms"
        TARGET_KO_PATH="${TARGET_KO_DIR}/${MODULE_NAME}.ko"
        
        echo_and_sleep "Criando diretório de destino..."
        execute_and_sleep mkdir -p "${TARGET_KO_DIR}"
        
        echo_and_sleep "Copiando módulo..."
        execute_and_sleep cp "${SOURCE_KO_PATH}" "${TARGET_KO_PATH}"
        
        echo_and_sleep "Atualizando dependências dos módulos..."
        execute_and_sleep depmod -a
        
        echo_and_sleep "Tentando carregar módulo após workaround..."
        if modprobe ${MODULE_NAME} video_nr=${V4L2LOOPBACK_VIDEO_NR} card_label="${V4L2LOOPBACK_CARD_LABEL}" exclusive_caps=1; then
            echo_and_sleep "SUCESSO COM WORKAROUND! Módulo carregado após cópia manual."
        else
            echo_and_sleep "FALHA CRÍTICA: Workaround não funcionou."
            echo_and_sleep "Possíveis soluções:"
            echo_and_sleep "1. Compilar headers manualmente para ${ACTIVE_KERNEL}"
            echo_and_sleep "2. Atualizar WSL para kernel mais recente"
            echo_and_sleep "3. Usar kernel Linux genérico ao invés do WSL"
            exit 1
        fi
    else
        echo_and_sleep "ERRO: Nenhum módulo alternativo encontrado."
        echo_and_sleep "Execute 'find /lib/modules/ -name \"${MODULE_NAME}.ko\"' para debug manual."
        exit 1
    fi
fi

echo_and_sleep "Passo 7: Verificando configuração final..."

# Verificar módulo carregado (regex compatível com Ubuntu 20.04)
if lsmod | grep -q "^${MODULE_NAME} "; then
    echo_and_sleep "✓ Módulo ${MODULE_NAME} está carregado."
else
    echo_and_sleep "✗ ERRO: Módulo não está carregado!"
    exit 1
fi

# Verificar dispositivo criado
DEVICE_PATH="/dev/video${V4L2LOOPBACK_VIDEO_NR}"
if [ -e "${DEVICE_PATH}" ]; then
    echo_and_sleep "✓ Dispositivo ${DEVICE_PATH} criado com sucesso."
else
    echo_and_sleep "✗ ERRO: Dispositivo ${DEVICE_PATH} não foi criado!"
    exit 1
fi

echo_and_sleep "--- CONFIGURAÇÃO CONCLUÍDA COM SUCESSO! ---"
echo ""
echo "==================================================================="
echo "         PRÓXIMOS PASSOS PARA UBUNTU 20.04"
echo "==================================================================="
echo ""
echo "1. Encontre o IP do Windows no WSL:"
echo "   cat /etc/resolv.conf | grep nameserver | awk '{print \$2}'"
echo ""
echo "2. Inicie o cam2web no Windows (porta padrão 8000)"
echo ""
echo "3. Instale ferramentas de teste (se necessário):"
echo "   sudo apt install zbar-tools ffmpeg -y"
echo ""
echo "4. Stream da webcam para o dispositivo virtual:"
echo "   ffmpeg -i http://IP_DO_WINDOWS:8000/camera/mjpeg -vf format=yuv420p -f v4l2 ${DEVICE_PATH}"
echo ""
echo "5. Teste com zbarcam:"
echo "   zbarcam ${DEVICE_PATH}"
echo ""
echo "==================================================================="
echo "Dispositivo virtual criado: ${DEVICE_PATH}"
echo "Nome do dispositivo: ${V4L2LOOPBACK_CARD_LABEL}"
echo "==================================================================="

exit 0
