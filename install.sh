#!/bin/bash

echo "============================================================"
echo " Instalador de Dependências"
echo "============================================================"

# 1. Detecta o Sistema Operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     machine=Linux;;
    CYGWIN*)    machine=Windows;;
    MINGW*)     machine=Windows;;
    MSYS*)      machine=Windows;;
    *)          machine="Desconhecido"
esac

echo "-> Sistema operacional detectado: $machine"

# 2. Atualizar e verificar o PIP
echo "-> Verificando e atualizando o PIP..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERRO] Python não encontrado! Instale o Python antes de continuar."
    exit 1
fi

$PYTHON_CMD -m pip install --upgrade pip

# 3. Instalar Tesseract OCR (Motor do Sistema)
echo "-> Verificando o motor do Tesseract OCR..."
if ! command -v tesseract &>/dev/null; then
    if [ "$machine" == "Linux" ]; then
        echo "-> Instalando Tesseract via APT (Requer senha sudo)..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-por
    elif [ "$machine" == "Windows" ]; then
        echo "-> Tentando instalar Tesseract no Windows via Winget..."
        if command -v winget &>/dev/null; then
            winget install -e --id UB-Mannheim.TesseractOCR
            echo "------------------------------------------------------------"
            echo "[ATENÇÃO] O Tesseract foi instalado no Windows."
            echo "Lembre-se de verificar se a pasta de instalação (geralmente"
            echo "C:\Program Files\Tesseract-OCR) está no PATH do Windows."
            echo "------------------------------------------------------------"
        else
            echo "[AVISO] Gerenciador 'winget' não encontrado."
            echo "No Windows, por favor, baixe o instalador do Tesseract manualmente:"
            echo "Link: https://github.com/UB-Mannheim/tesseract/wiki"
        fi
    else
        echo "[AVISO] Sistema não suportado para instalação automática do Tesseract. Instale manualmente."
    fi
else
    echo "-> Tesseract OCR já está instalado no sistema!"
fi

# 4. Instalar Dependências Python (Bibliotecas)
echo "-> Instalando pacotes Python..."
# Adicionei o opencv-python pois os scripts anteriores utilizam o cv2
$PYTHON_CMD -m pip install pytesseract google-genai opencv-python

echo "============================================================"
echo " Processo finalizado!"
echo "============================================================"