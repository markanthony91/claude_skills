#!/bin/bash
################################################################################
# Iniciar Dashboard Web de Monitoramento de Câmeras
################################################################################

DASHBOARD_DIR="/home/marcelo/sistemas"
PORT=8080

echo "═══════════════════════════════════════════════════════════════════════════"
echo "           DASHBOARD DE MONITORAMENTO DE CÂMERAS"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 detectado"
    echo ""
    echo "Iniciando servidor web em http://localhost:$PORT"
    echo ""
    echo "📊 Acesse o dashboard em:"
    echo "   → http://localhost:$PORT/dashboard_cameras.html"
    echo ""
    echo "Pressione Ctrl+C para parar o servidor"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""

    cd "$DASHBOARD_DIR"
    python3 -m http.server $PORT

elif command -v php &> /dev/null; then
    echo "✓ PHP detectado"
    echo ""
    echo "Iniciando servidor web em http://localhost:$PORT"
    echo ""
    echo "📊 Acesse o dashboard em:"
    echo "   → http://localhost:$PORT/dashboard_cameras.html"
    echo ""
    echo "Pressione Ctrl+C para parar o servidor"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""

    cd "$DASHBOARD_DIR"
    php -S localhost:$PORT

else
    echo "❌ Erro: Python 3 ou PHP não encontrado"
    echo ""
    echo "Instale Python 3:"
    echo "  sudo apt-get install python3"
    echo ""
    echo "Ou simplesmente abra o arquivo diretamente no navegador:"
    echo "  file://$DASHBOARD_DIR/dashboard_cameras.html"
    exit 1
fi
