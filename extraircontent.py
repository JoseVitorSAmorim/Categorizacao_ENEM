import os
import time
import cv2
import pytesseract
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# ---------------- CONFIGURAÇÃO ----------------
INPUT_DIR = "questoes"
OUTPUT_DIR = "textos_extraidos"
MODEL_NAME = "gemini-2.5-flash"  # O modelo multimodal gratuito estável

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

def load_env():
    if ENV_FILE.exists():
        for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")
    return os.getenv("GEMINI_API_KEY")

def executar_pipeline_gemini_seguro():
    if not load_env():
        print("ERRO: Chave 'GEMINI_API_KEY' não encontrada no arquivo .env.")
        return
    if genai is None:
        print("ERRO: O pacote 'google-genai' não está instalado. Execute: pip install google-genai")
        return

    client = genai.Client()
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    extensoes = (".png", ".jpg", ".jpeg")
    arquivos = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(extensoes)]

    print(f"=== Iniciando Pipeline Seguro Gemini para {len(arquivos)} imagens ===")

    for idx, filename in enumerate(arquivos, 1):
        image_path = os.path.join(INPUT_DIR, filename)
        nome_puro, ext = os.path.splitext(filename)
        output_path = os.path.join(OUTPUT_DIR, f"{nome_puro}.txt")

        # Evita reprocessar arquivos que já deram certo em tentativas anteriores
        if os.path.exists(output_path):
            print(f"[{idx}/{len(arquivos)}] Pulando (já processado): {filename}")
            continue

        print(f"\n[{idx}/{len(arquivos)}] Processando via Gemini: {filename}")

        try:
            # 1. OCR Local com Tesseract
            img = cv2.imread(image_path)
            if img is None:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            texto_bruto_tesseract = pytesseract.image_to_string(gray, lang='por')

            # 2. Carrega Imagem para a API
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            mime_type = "image/png" if ext.lower() == ".png" else "image/jpeg"
            imagem_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            # 3. Prompt Corretor Híbrido
            prompt_revisao = f"""
            Você é um revisor de texto especializado em exames educacionais.
            Sua tarefa é corrigir o 'Texto Bruto' fornecido abaixo, usando a imagem anexada apenas como referência para solucionar erros de OCR.

            Regras estritas:
            1. **Ignore Completamente as Imagens/Figuras:** Se houver fotos, charges, gráficos ou tabelas ilustradas, NÃO descreva-as e ignore qualquer texto confuso que o OCR tenha tentado ler de dentro delas.
            2. **Recupere as Alternativas (A, B, C, D, E):** A imagem contém letras dentro de círculos. Garanta que cada uma das 5 alternativas comece exatamente com a letra correspondente correta (A, B, C, D, E) seguida do respectivo texto.
            3. **Limpeza Geral:** Remova caracteres especiais perdidos, quebras de linha incoerentes e resíduos visuais do OCR.
            4. **Saída Limpa:** Retorne APENAS o texto final formatado da questão (Enunciado + Alternativas). Não adicione saudações, introduções ou comentários extras.

            Texto Bruto do Tesseract:
            ---
            {texto_bruto_tesseract}
            ---
            """

            # 4. Requisição
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt_revisao, imagem_part]
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response.text.strip())
            
            print(f"   -> SUCESSO: Salvo em {output_path}")

            # 5. O Segredo do Controle de Fluxo: 
            # Pausa de 5 segundos garante no máximo 12 requisições por minuto. 
            # Como o limite gratuito é 15 RPM
            time.sleep(5)

        except Exception as e:
            print(f"   [FALHA] Erro ao processar {filename}: {e}")
            print("   Aguardando 20 segundos para reestabelecer a API e tentando a próxima...")
            time.sleep(20)

if __name__ == "__main__":
    executar_pipeline_gemini_seguro()