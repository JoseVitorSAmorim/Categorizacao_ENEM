# Categorizacao_ENEM
Extração do conteúdo das questões da segunda prova ENEM de 2012, caderno 5 por OCR
## Requisitos
- Python3
- Pdf2image
- pytesseract
- tesseract
- API Gemini 2.5 Flash

## Ativando ambiente virtual
### Linux
```
python3 -m venv venv  
source venv/bin/activate  
```
### Windows
```
python -m venv venv
venv\Scripts\activate.ps1
```
## Instalar dependências
### Linux
Dê permissão
```
chmod +x install.sh
```
Para executar
```
./install.sh
```
### Windows
- Precisará rodar isso através do Git Bash (que costuma vir instalado junto com o Git)
- Clique com o botão direito na pasta do projeto e selecione "Open Git Bash here"
- Para executar
```
bash install.sh
```
## API
### Chave da API
Obter API key no Google AI Studio  
https://aistudio.google.com/app/api-keys

Adicione nas variável de ambiente com:
```
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
```
