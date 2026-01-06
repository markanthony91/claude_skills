#!/bin/bash

# Script de Diagnóstico e Correção do Bluetooth para Linux
# Compatível com Pop!_OS, Ubuntu, e derivados
# Autor: Claude AI Assistant
# Versão: 2.0 - Inclui correções específicas para Realtek

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Função para verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Este script não deve ser executado como root!"
        print_status "Execute como usuário normal: ./bluetooth_fix.sh"
        exit 1
    fi
}

# Função para diagnóstico inicial
diagnostic() {
    print_header "DIAGNÓSTICO DO BLUETOOTH"
    
    print_status "Verificando informações do sistema..."
    echo "Sistema: $(lsb_release -d | cut -f2)"
    echo "Kernel: $(uname -r)"
    echo "Arquitetura: $(uname -m)"
    
    print_status "Verificando hardware Bluetooth..."
    if lsusb | grep -i bluetooth > /dev/null 2>&1; then
        print_success "Hardware Bluetooth USB detectado:"
        lsusb | grep -i bluetooth
        
        # Verificar se é Realtek problemático
        if lsusb | grep -q "0bda:887b"; then
            print_warning "⚠️  ATENÇÃO: Detectado Realtek RTL8852BE - conhecido por problemas no kernel 6.12+"
            print_status "Use a opção 7 para correção específica deste adaptador"
        fi
        
    elif lspci | grep -i bluetooth > /dev/null 2>&1; then
        print_success "Hardware Bluetooth PCI detectado:"
        lspci | grep -i bluetooth
    else
        print_warning "Hardware Bluetooth não detectado via lsusb/lspci"
        print_status "Verificando via hciconfig..."
        if command -v hciconfig > /dev/null 2>&1; then
            hciconfig -a 2>/dev/null || echo "Nenhum adaptador encontrado"
        fi
    fi
    
    print_status "Verificando módulos do kernel..."
    loaded_modules=$(lsmod | grep -E "(bluetooth|btusb|btintel|btrtl)" | wc -l)
    if [ $loaded_modules -gt 0 ]; then
        print_success "Módulos Bluetooth carregados:"
        lsmod | grep -E "(bluetooth|btusb|btintel|btrtl)"
    else
        print_error "Nenhum módulo Bluetooth carregado!"
    fi
    
    print_status "Verificando status do serviço Bluetooth..."
    if systemctl is-active --quiet bluetooth; then
        print_success "Serviço bluetooth está ativo"
    else
        print_error "Serviço bluetooth está inativo"
    fi
    
    if systemctl is-enabled --quiet bluetooth; then
        print_success "Serviço bluetooth está habilitado"
    else
        print_warning "Serviço bluetooth não está habilitado"
    fi
    
    print_status "Verificando logs recentes do Bluetooth..."
    echo "Últimas 5 entradas do log:"
    journalctl -u bluetooth -n 5 --no-pager 2>/dev/null || echo "Não foi possível acessar os logs"
    
    print_status "Verificando adaptadores Bluetooth..."
    if command -v bluetoothctl > /dev/null 2>&1; then
        echo "Executando 'bluetoothctl list':"
        adapter_output=$(timeout 5 bluetoothctl list 2>/dev/null || echo "")
        if [ -n "$adapter_output" ]; then
            echo "$adapter_output"
        else
            print_error "❌ PROBLEMA: Nenhum adaptador disponível no bluetoothctl"
            print_warning "Isso indica que o hardware não está sendo inicializado corretamente"
        fi
    fi
    
    print_status "Verificando se Bluetooth está bloqueado (rfkill)..."
    if command -v rfkill > /dev/null 2>&1; then
        rfkill list bluetooth
    else
        print_warning "rfkill não disponível"
    fi
}

# Função para soluções básicas
basic_fixes() {
    print_header "APLICANDO CORREÇÕES BÁSICAS"
    
    print_status "1. Desbloqueando Bluetooth via rfkill..."
    if command -v rfkill > /dev/null 2>&1; then
        sudo rfkill unblock bluetooth
        print_success "Bluetooth desbloqueado via rfkill"
    else
        print_warning "rfkill não disponível"
    fi
    
    print_status "2. Reiniciando serviço Bluetooth..."
    sudo systemctl restart bluetooth
    sleep 2
    
    if systemctl is-active --quiet bluetooth; then
        print_success "Serviço Bluetooth reiniciado com sucesso"
    else
        print_error "Falha ao reiniciar serviço Bluetooth"
    fi
    
    print_status "3. Habilitando serviço Bluetooth..."
    sudo systemctl enable bluetooth
    print_success "Serviço Bluetooth habilitado"
    
    print_status "4. Recarregando módulos Bluetooth..."
    
    # Lista de módulos para recarregar
    modules=("btusb" "btintel" "btrtl" "btbcm" "bluetooth")
    
    for module in "${modules[@]}"; do
        if lsmod | grep -q "^$module"; then
            print_status "Removendo módulo $module..."
            sudo modprobe -r $module 2>/dev/null || print_warning "Falha ao remover $module"
        fi
    done
    
    sleep 2
    
    for module in "${modules[@]}"; do
        print_status "Carregando módulo $module..."
        sudo modprobe $module 2>/dev/null && print_success "Módulo $module carregado" || print_warning "Falha ao carregar $module"
    done
    
    sleep 3
}

# Função para correção específica Realtek
fix_realtek() {
    print_header "🔧 CORREÇÃO ESPECÍFICA PARA REALTEK BLUETOOTH"
    
    print_status "Detectado: Realtek Semiconductor Corp. Bluetooth Radio (0bda:887b)"
    print_warning "Problema conhecido: RTL8852BE não inicializa corretamente no kernel 6.12+"
    print_status "Aplicando correções específicas..."
    
    # 1. Reset do dispositivo USB
    print_status "1. Resetando adaptador USB..."
    
    # Encontrar o caminho correto do dispositivo
    usb_device=$(lsusb | grep "0bda:887b" | head -1)
    if [[ -n "$usb_device" ]]; then
        bus=$(echo "$usb_device" | awk '{print $2}')
        device=$(echo "$usb_device" | awk '{print $4}' | tr -d ':')
        
        print_status "Dispositivo encontrado: Bus $bus Device $device"
        
        # Resetar via USB
        if [ -w "/dev/bus/usb/$bus/$device" ] 2>/dev/null; then
            print_status "Tentando reset via usbreset..."
            # Tentar diferentes métodos de reset
            sudo bash -c "echo 0 > /sys/bus/usb/devices/$bus-*/authorized" 2>/dev/null || true
            sleep 1
            sudo bash -c "echo 1 > /sys/bus/usb/devices/$bus-*/authorized" 2>/dev/null || true
        fi
        
        print_success "Reset do dispositivo USB executado"
    fi
    
    # 2. Remover e recarregar módulos na ordem correta
    print_status "2. Removendo módulos existentes..."
    sudo modprobe -r btusb btrtl btintel bluetooth 2>/dev/null || true
    sleep 3
    
    # 3. Criar configuração específica para RTL8852BE
    print_status "3. Criando configuração específica..."
    
    cat << 'EOF' | sudo tee /etc/modprobe.d/rtl8852be-bluetooth.conf > /dev/null
# Configuração específica para RTL8852BE Bluetooth
options btusb enable_autosuspend=0
options btusb reset=1
options bluetooth disable_ertm=1
blacklist btusb
EOF
    
    # 4. Instalar firmware se necessário
    print_status "4. Verificando e instalando firmware..."
    sudo apt update -qq
    sudo apt install -y linux-firmware firmware-realtek 2>/dev/null || true
    
    # Verificar se firmware existe
    if [ -d /lib/firmware/rtl_bt ]; then
        print_success "Firmware Realtek encontrado em /lib/firmware/rtl_bt/"
        ls -la /lib/firmware/rtl_bt/ | grep -E "887b|8852" || echo "Arquivos específicos não encontrados, mas pasta existe"
    fi
    
    # 5. Configuração otimizada do bluetoothd
    print_status "5. Configurando bluetoothd para Realtek..."
    
    if [ -f /etc/bluetooth/main.conf ]; then
        sudo cp /etc/bluetooth/main.conf /etc/bluetooth/main.conf.backup.$(date +%s)
    fi
    
    cat << EOF | sudo tee /etc/bluetooth/main.conf > /dev/null
[General]
Name = $(hostname)
Class = 0x000100
DiscoverableTimeout = 0
PairableTimeout = 0
AutoConnectTimeout = 60
FastConnectable = true
Privacy = device-id
JustWorksRepairing = always
TemporaryTimeout = 30

[Policy]
AutoEnable=true
ReconnectAttempts=7
ReconnectIntervals=1,2,4,8,16,32,64

[LE]
MinConnectionInterval=7
MaxConnectionInterval=9
ConnectionLatency=0
ConnectionSupervisionTimeout=720
EOF
    
    # 6. Remover da blacklist e recarregar módulos
    print_status "6. Recarregando módulos com nova configuração..."
    
    # Remover temporariamente da blacklist
    sudo sed -i '/blacklist btusb/d' /etc/modprobe.d/rtl8852be-bluetooth.conf
    
    # Carregar módulos na ordem correta
    sudo modprobe bluetooth
    sleep 1
    sudo modprobe btrtl  
    sleep 1
    sudo modprobe btintel
    sleep 1
    sudo modprobe btusb reset=1 enable_autosuspend=0
    sleep 3
    
    # 7. Reiniciar serviço
    print_status "7. Reiniciando serviço bluetooth..."
    sudo systemctl restart bluetooth
    sleep 3
    
    print_success "✅ Correção específica Realtek aplicada!"
    print_warning "⚠️  Se ainda não funcionar, reinicie o sistema para garantir que todas as alterações sejam aplicadas"
    
    return 0
}

# Função para soluções avançadas
advanced_fixes() {
    print_header "APLICANDO CORREÇÕES AVANÇADAS"
    
    # Primeiro verificar se é Realtek e sugerir correção específica
    if lsusb | grep -q "0bda:887b"; then
        print_warning "⚠️  Detectado adaptador Realtek RTL8852BE"
        print_status "Recomendo usar a opção 7 (correção específica) ao invés das correções gerais"
        read -p "Deseja continuar com correções gerais mesmo assim? (s/N): " confirm_general
        if [[ ! $confirm_general =~ ^[Ss]$ ]]; then
            return
        fi
    fi
    
    read -p "Deseja aplicar correções avançadas? Isso pode requerer reinicialização. (s/N): " confirm
    if [[ ! $confirm =~ ^[Ss]$ ]]; then
        return
    fi
    
    print_status "1. Reinstalando pacotes Bluetooth..."
    sudo apt update
    sudo apt install --reinstall bluetooth bluez bluez-tools pulseaudio-module-bluetooth -y
    
    print_status "2. Verificando e corrigindo configuração PulseAudio..."
    # Recarregar PulseAudio
    pulseaudio -k
    sleep 2
    pulseaudio --start
    
    # Carregar módulo Bluetooth do PulseAudio
    pactl load-module module-bluetooth-discover 2>/dev/null || print_warning "Módulo Bluetooth já carregado no PulseAudio"
    
    print_status "3. Criando/corrigindo configuração do Bluetooth..."
    
    # Backup da configuração atual
    if [ -f /etc/bluetooth/main.conf ]; then
        sudo cp /etc/bluetooth/main.conf /etc/bluetooth/main.conf.backup
    fi
    
    # Configuração otimizada
    cat << EOF | sudo tee /etc/bluetooth/main.conf > /dev/null
[General]
Name = $(hostname)
Class = 0x000100
DiscoverableTimeout = 0
PairableTimeout = 0
AutoConnectTimeout = 60
FastConnectable = true
Privacy = off

[Policy]
AutoEnable=true
EOF
    
    print_success "Configuração do Bluetooth atualizada"
    
    print_status "4. Verificando blacklist de módulos..."
    if grep -q "btusb\|bluetooth" /etc/modprobe.d/* 2>/dev/null; then
        print_warning "Módulos Bluetooth podem estar na blacklist:"
        grep -r "btusb\|bluetooth" /etc/modprobe.d/ 2>/dev/null
        read -p "Deseja remover da blacklist? (s/N): " remove_blacklist
        if [[ $remove_blacklist =~ ^[Ss]$ ]]; then
            sudo sed -i '/btusb\|bluetooth/d' /etc/modprobe.d/* 2>/dev/null
            print_success "Módulos removidos da blacklist"
        fi
    fi
    
    print_status "5. Atualizando initramfs..."
    sudo update-initramfs -u
    
    print_warning "É recomendado reiniciar o sistema após essas alterações."
    read -p "Deseja reiniciar agora? (s/N): " reboot_now
    if [[ $reboot_now =~ ^[Ss]$ ]]; then
        sudo reboot
    fi
}

# Função para teste final
test_bluetooth() {
    print_header "TESTANDO FUNCIONALIDADE DO BLUETOOTH"
    
    print_status "Aguardando inicialização do Bluetooth..."
    sleep 5
    
    print_status "Status do serviço:"
    systemctl status bluetooth --no-pager -l
    
    print_status "Verificando adaptadores disponíveis..."
    if command -v bluetoothctl > /dev/null 2>&1; then
        adapter_list=$(timeout 10 bluetoothctl list 2>/dev/null)
        if [ -n "$adapter_list" ]; then
            print_success "✅ Adaptadores encontrados:"
            echo "$adapter_list"
            
            print_status "Tentando ativar o Bluetooth..."
            timeout 10 bluetoothctl power on
            
            print_status "Verificando se está detectável..."
            timeout 10 bluetoothctl discoverable on
            
            print_success "✅ Teste básico concluído!"
            print_status "Tente agora conectar através da interface gráfica ou execute:"
            echo "bluetoothctl"
            echo "power on"
            echo "agent on"
            echo "default-agent"
            echo "scan on"
        else
            print_error "❌ FALHA: Nenhum adaptador Bluetooth disponível!"
            print_warning "Possíveis causas:"
            echo "• Hardware não inicializado corretamente"
            echo "• Driver incompatível ou firmware ausente"
            echo "• Problema específico com o chip (ex: Realtek RTL8852BE)"
            echo ""
            
            if lsusb | grep -q "0bda:887b"; then
                print_warning "🔧 SOLUÇÃO: Detectado adaptador Realtek - use a opção 7 (correção específica)"
            else
                print_status "Tente as correções avançadas (opção 3) ou reinicie o sistema"
            fi
        fi
    else
        print_error "bluetoothctl não disponível"
    fi
}

# Função para mostrar informações úteis
show_help() {
    print_header "INFORMAÇÕES ÚTEIS"
    
    echo "Comandos úteis para Bluetooth:"
    echo "1. Verificar status: systemctl status bluetooth"
    echo "2. Ver logs: journalctl -u bluetooth -f"
    echo "3. Controle interativo: bluetoothctl"
    echo "4. Verificar hardware: lsusb | grep -i bluetooth"
    echo "5. Verificar rfkill: rfkill list bluetooth"
    echo "6. Reiniciar Bluetooth: sudo systemctl restart bluetooth"
    echo ""
    echo "Arquivos importantes:"
    echo "- Configuração: /etc/bluetooth/main.conf"
    echo "- Logs: /var/log/bluetooth/"
    echo "- Módulos: /etc/modprobe.d/"
    echo ""
    echo "Para problemas específicos:"
    echo "🔧 Realtek RTL8852BE: Use opção 7 deste script"
    echo "• Intel AX200/210: Pode precisar de firmware atualizado"
    echo "• Broadcom: Pode precisar do pacote bcmwl-kernel-source"
    echo ""
    echo "Para problemas persistentes:"
    echo "1. Verifique se o hardware é compatível"
    echo "2. Atualize drivers: sudo ubuntu-drivers autoinstall"
    echo "3. Verifique BIOS/UEFI para configurações de Bluetooth"
    echo "4. Considere usar um adaptador USB Bluetooth externo"
}

# Menu principal
main_menu() {
    print_header "SCRIPT DE CORREÇÃO DO BLUETOOTH v2.0"
    
    # Detectar se é Realtek e mostrar aviso especial
    if lsusb | grep -q "0bda:887b"; then
        print_warning "🚨 ADAPTADOR REALTEK RTL8852BE DETECTADO!"
        print_status "Este adaptador tem problemas conhecidos no kernel 6.12+"
        print_success "✅ Correção específica disponível na opção 7"
        echo ""
    fi
    
    echo "Escolha uma opção:"
    echo "1. Diagnóstico completo"
    echo "2. Aplicar correções básicas"
    echo "3. Aplicar correções avançadas"
    echo "4. Testar funcionalidade"
    echo "5. Mostrar ajuda"
    echo "6. Executar tudo (diagnóstico + correções básicas + teste)"
    if lsusb | grep -q "0bda:887b"; then
        echo "7. 🔧 [REALTEK] Correção específica para RTL8852BE"
    fi
    echo "0. Sair"
    echo ""
    
    if lsusb | grep -q "0bda:887b"; then
        read -p "Digite sua opção (0-7): " option
    else
        read -p "Digite sua opção (0-6): " option
    fi
    
    case $option in
        1)
            diagnostic
            ;;
        2)
            basic_fixes
            ;;
        3)
            advanced_fixes
            ;;
        4)
            test_bluetooth
            ;;
        5)
            show_help
            ;;
        6)
            diagnostic
            echo ""
            basic_fixes
            echo ""
            test_bluetooth
            ;;
        7)
            if lsusb | grep -q "0bda:887b"; then
                fix_realtek
                echo ""
                print_status "Testando após correção específica..."
                test_bluetooth
            else
                print_error "Opção 7 disponível apenas para adaptadores Realtek (0bda:887b)"
                print_status "Seu adaptador: $(lsusb | grep -i bluetooth || echo 'Não detectado')"
            fi
            ;;
        0)
            print_success "Saindo..."
            exit 0
            ;;
        *)
            print_error "Opção inválida!"
            main_menu
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para voltar ao menu..."
    main_menu
}

# Função principal
main() {
    check_root
    
    print_header "INICIALIZANDO SCRIPT DE CORREÇÃO DO BLUETOOTH v2.0"
    print_status "Sistema detectado: $(lsb_release -d | cut -f2) $(uname -m)"
    print_status "Este script irá diagnosticar e tentar corrigir problemas de Bluetooth"
    
    # Verificação inicial para Realtek
    if lsusb | grep -q "0bda:887b"; then
        echo ""
        print_warning "⚠️  ATENÇÃO: Detectado adaptador Realtek RTL8852BE problemático!"
        print_status "Recomendação: Use diretamente a opção 7 para correção específica"
    fi
    
    echo ""
    main_menu
}

# Tratamento de sinais para saída limpa
trap 'print_error "Script interrompido pelo usuário"; exit 1' SIGINT SIGTERM

# Executar função principal
main "$@"
