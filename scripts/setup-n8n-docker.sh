#!/bin/bash
# Instalador do N8N em Docker
# Autor: Autotic
# Versao: 0.236.3

clear
echo "INICIANDO SETUP DO N8N 0.236.3 ..."
sleep 5
clear
sudo apt -y update
sudo apt -y upgrade
sudo apt install -y docker.io
sudo timedatectl set-timezone America/Sao_Paulo
sudo docker run -d --restart unless-stopped --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n:0.236.3
host=$(sudo hostname -I | head -n1 | cut -d " " -f1)
clear
echo "N8N INSTALADO COM SUCESSO!"
echo "Acesse a URL: http://${host}:5678"
echo ""
echo "#################################################################################################"
echo "1. Faça parte do grupo N8N Brasil no Telegram: https://t.me/n8nbr"
echo "2. Faça parte do grupo N8N Brasil no WhatsApp: https://chat.whatsapp.com/EST1hV8aITs33IdS0BoNOY"
echo "3. Configure seu n8n de forma escalável: https://autotic.com.br/n8n-curso-completo-de-setup"
echo "4. Desenvolva qualquer automação no seu n8n: https://autotic.com.br/curso-intensivo-de-n8n"
echo "#################################################################################################"