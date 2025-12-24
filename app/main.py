import time

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.services.ocr import extract_pdf

app = FastAPI(title="Contrackt OCR API")


@app.get("/")
def health_check():
    return {"status": "online", "motor": "PaddleOCR v5"}


@app.post("/extract")
async def process_pdf(file: UploadFile = File(...)):
    # Verificação básica de segurança
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Por favor envie apenas arquivos PDF válidos"
        )

    start = time.time()

    print(f"Recebendo arquivo: {file.filename}")

    # Lendo o arquivo da mémoria RAM
    content = await file.read()

    try:
        # Chamamos nosso motor de OCR criado acima
        result = extract_pdf(content)

        total_time = time.time() - start

        return {
            "file": file.filename,
            "time_process_seconds": round(total_time, 2),
            "process_pages": len(result),
            "data": result,
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
