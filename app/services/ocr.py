import time

import cv2
import fitz
import numpy as np
from paddleocr import PaddleOCR

print("Carregando modelos de IA na memória...")
ocr_engine = PaddleOCR(
    use_angle_cls=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="latin_PP-OCRv5_mobile_rec",
    lang="pt",
)
print("Modelos OCR carregados com sucesso!")


def extract_pdf(content_file: bytes) -> list[dict]:
    """Recebe um arquivo PDF e retorna o texto extraído.

    Args:
        content_file (bytes): Conteúdo do arquivo PDF.

    Returns:
        str: Texto extraído do PDF.
    """
    # Abre o PDF em memória e prepara a lista de resultados por página
    doc = fitz.open(stream=content_file, filetype="pdf")
    final_result = []

    # Itera por cada página do PDF
    for i in range(len(doc)):
        page = doc.load_page(i)
        print(f"Processando página {i + 1}...")

        page_start = time.perf_counter()

        # 1) PDF -> imagem (Pixmap); zoom=2 melhora a leitura do OCR
        raster_start = time.perf_counter()
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        # 2) Pixmap -> numpy array (formato esperado pelo OpenCV/Paddle)
        image_bytes = np.frombuffer(pix.samples, dtype=np.uint8)
        image = image_bytes.reshape(pix.h, pix.w, pix.n)
        raster_time = time.perf_counter() - raster_start

        # Ajusta o espaço de cores para o padrão do OpenCV (BGR)
        if pix.n == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif pix.n == 4:  # Se tiver transparência (RGBA)
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        ocr_start = time.perf_counter()

        # 3) OCR na imagem (inclui classificação de orientação)
        result = ocr_engine.ocr(image)

        ocr_time = time.perf_counter() - ocr_start

        total_page_time = time.perf_counter() - page_start

        page_data = {"page_number": i + 1, "text": [], "low_confidence_alert": False}

        page_data["processing_time_ms"] = round(total_page_time * 1000, 2)
        page_data["raster_time_ms"] = round(raster_time * 1000, 2)
        page_data["ocr_time_ms"] = round(ocr_time * 1000, 2)

        # result[0] contém as detecções; cada linha traz (texto, confiança)
        if result and result[0]:
            data = result[0]  # Pega o resultado bruto

            if isinstance(data, dict):  # Verifica se 'data' é um dicionário
                text_list = data.get("rec_texts", [])
                score_list = data.get("rec_scores", [])

                for current_text, current_score in zip(text_list, score_list):
                    page_data["text"].append(
                        {"content": current_text, "confidence": round(current_score, 4)}
                    )

                    if current_score < 0.85:
                        page_data["low_confidence_alert"] = True

            elif isinstance(data, list):
                print("Formato antigo detectado (lista)")

        # Adiciona os dados da página atual ao resultado final
        final_result.append(page_data)

    return final_result
