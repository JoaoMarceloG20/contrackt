import cv2
import fitz
import numpy as np
from paddleocr import PaddleOCR

print("Carregando modelos de IA na memória...")

ocr_engine = PaddleOCR(use_angle_cls=True, lang="pt", show_log=False)

print("Modelos de IA carregados com sucesso!")

def extract_pdf(content_file: bytes) -> list[dict]:
    """ Recebe um arquivo PDF e retorna o texto extraído.

    Args:
        content_file (bytes): Conteúdo do arquivo PDF.

    Returns:
        str: Texto extraído do PDF.
    """
    # O stream representa o conteúdo binário do arquivo PDF que está sendo passado para o PyMuPDF (fitz)
    # A lista final_result será usada para armazenar os resultados do OCR de todas as páginas do PDF
    file = fitz.open(stream=content_file, filetype="pdf")
    final_result = []

    #Loop por cada página do pdf
    for i, page in enumerate(file):  # i representa o índice da página atual no loop (começando de 0)
    # i+1 é usado para mostrar o número da página ao usuário (começando de 1)
    # Este print mostra qual página está sendo processada no momento
        print(f"Processando página {i+1}...")

        #1. Converte página PDF -> Imagem (Pixmap)
        # zoom=2 aumenta a resolução para o OCR ler melhor
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        #2. Converte Pixmap (objeto de imagem do PyMuPDF que contém pixels e metadados) em formato que o OpenCV/Paddle entendem (numpy array)
        image_bytes = np.frombuffer(pix.samples, dtype=np.uint8)
        # pix.n representa o número de canais de cor na imagem:
        # 3 para RGB (Vermelho, Verde, Azul)
        # 4 para RGBA (Vermelho, Verde, Azul, Transparência)
        image = image_bytes.reshape(pix.h, pix.w, pix.n)

        #Se a imagem for RGB, converte para BGR (padrão do OpenCV)
        if pix.n ==3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif pix.n == 4: #Se tiver transparência
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

        #3. Realiza OCR na imagem
        # result é a lista de caixas de texto detectadas
        # cls=True ativa a classificação de orientação de texto (0, 90, 180, 270 graus)
        # Isso ajuda o OCR a detectar automaticamente a orientação correta do texto na imagem
        result = ocr_engine.ocr(image, cls=True)

        page_data = {
            'page_number': i+1,
            'text': [],
            'low_confidence_alert': False
        }

        # Explicação do trecho:
        # result é a saída do OCR, que é uma lista onde o primeiro elemento (result[0]) contém
        # todas as detecções de texto da página atual
        # Cada detecção (line) é uma lista onde:
        # - line[1][0] contém o texto reconhecido
        # - line[1][1] contém o nível de confiança (0.0 a 1.0) do reconhecimento

        if result and result[0]:
            for line in result[0]:
                # Extrai o texto e a confiança da detecção atual
                text = line[1][0]
                confidence = line[1][1]

                # Adiciona o texto e sua confiança à lista de textos da página
                # O append adiciona um novo dicionário à lista page_data["text"]
                page_data["text"].append({
                    'content': text,
                    'confidence': round(confidence, 4)  # Arredonda para 4 casas decimais
                })

                # Verifica se a confiança é baixa (<85%)
                # Se encontrar qualquer texto com confiança baixa, marca a página
                if confidence < 0.85:
                    page_data['low_confidence_alert'] = True

            # Adiciona os dados da página atual à lista final de resultados
            final_result.append(page_data)

    return final_result
