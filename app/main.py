import time
import gc

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.services.ocr import extract_pdf

app = FastAPI(title="Contrackt OCR API")


@app.get("/")
def health_check():
    return {"status": "online", "motor": "PaddleOCR v5"}


@app.post("/v1/extract")
async def process_pdf(
    file: UploadFile = File(...),
    document_type: str = Form("auto"),
    include_chat_package: bool = Form(False)):

    # Verificação básica de segurança
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Por favor envie apenas arquivos PDF válidos"
        )

    #Valores aceitos para document_type
    accepted_document_types = ["auto"]
    if document_type not in accepted_document_types:
        raise HTTPException(
            status_code=422, detail=f"document_type inválido"
        )

    start = time.time()

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
        print(f"Error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Liberando memória
        del content
        gc.collect()
