# Revisão Sênior (Top 10) — Próximas mudanças no MVP

Este documento transforma a documentação existente (`docs/PRD.md`, `docs/TODOS.md`, `docs/STACK.md`, `docs/COMPLIANCE.md`) em uma lista curta e executável de mudanças **na ordem certa**, com foco em entregar o **MVP** de forma consistente, segura e verificável.

---

## 1) Alinhar a narrativa do projeto (produto/escopo)

- Ajustar `README.md` (raiz) para refletir o que o projeto é hoje: **API-first de extração (OCR/ML) com zero-retention + hashes** (não “gerenciamento de contratos”).
- Deixar explícito: público-alvo inicial (Fase 1 medical vs banking) e o que entra no MVP.
- Resultado esperado: qualquer pessoa entende “o que é”, “para quem é”, “o que está pronto” em 30s.

## 2) Fixar o contrato da API v1 e manter legado de forma explícita

- Implementar `POST /v1/extract` e `GET /v1/health` conforme `docs/TODOS.md` e `docs/PRD.md` (payload `ExtractionResult`).
- Decidir destino de `POST /extract`:
  - Opção A: redirecionar (308) para `/v1/extract`, ou
  - Opção B: manter como legado com indicação clara de depreciação.
- Resultado esperado: “API v1” é a única referência para integrações e demo.

## 3) Instrumentar hashes e metadata como base de auditoria

- Implementar funções puras:
  - `compute_document_hash(content: bytes) -> str` (SHA-256)
  - `compute_result_hash(data: dict) -> str` (JSON canônico + SHA-256)
  - `build_extraction_metadata(...) -> dict` (confiança, páginas, tempo etc.)
- Padronizar formato (ex.: `sha256:<hex>` ou apenas `<hex>`) e documentar.
- Resultado esperado: reprocessar o mesmo documento gera hashes previsíveis (ou explica quando não).

## 4) Corrigir logging para ser compatível com “logs sem PII”

- Remover/evitar:
  - `print(file.filename)` e logs de conteúdo/trechos OCR
  - `print(e)` com stacktrace em produção sem redaction
- Introduzir logging estruturado mínimo (mesmo que seja `logging` stdlib) com campos:
  - `request_id`, `document_hash`, `pages`, `processing_time_ms`, `confidence`, `document_type`, `status`
- Resultado esperado: logs úteis para operação sem vazar PII acidentalmente.

## 5) Tratar segurança de upload além de `content_type`

- Impor limites:
  - tamanho máximo do PDF (bytes)
  - páginas máximas (ou timeout por página)
- Validar “PDF de verdade” (assinatura/abertura com erro controlado) e retornar erros previsíveis (400/422).
- Resultado esperado: resiliência a PDFs corrompidos e mitigação de DoS trivial.

## 6) Separar trabalho CPU-bound do event loop (concorrência)

- O OCR é CPU-bound. Evitar degradar o servidor sob carga:
  - usar `run_in_threadpool`/executor para OCR
  - limitar concorrência (ex.: semáforo) para não saturar CPU/memória
- Resultado esperado: o servidor mantém latência aceitável quando chegam múltiplas requisições.

## 7) Ajustar o OCR para produzir confiança agregada por página

- Em `app/services/ocr.py`:
  - garantir estrutura de saída consistente (lista por página)
  - calcular `mean_confidence` por página (média de `rec_scores`) e sinalizar baixa confiança
- Resultado esperado: `extraction_metadata` e `confidence` deixam de ser "chute" e passam a ser consistentes.

## 8) Definir “zero-retention” com precisão técnica e jurídica

- No MVP: **não gravar em disco** (processamento em memória) + garantir liberação de referências.
- Evitar prometer “overwrite 3-pass” como garantia universal (SSD/COW/journaling podem invalidar).
- Resultado esperado: a promessa de privacidade é verdadeira e defensável em auditoria/contrato.

## 9) Criar um pequeno pacote de validação (testes mínimos)

- Backend:
  - 1–2 testes de unidade para hashes/metadata (determinismo)
  - 1 teste de API para `POST /v1/extract` validando o schema do response (mesmo que OCR seja mockado)
- Resultado esperado: alterações futuras não quebram o contrato do MVP sem perceber.

## 10) “Caminho feliz” completo: demo + docker + documentação de execução

- Entregar um fluxo único que qualquer pessoa rode:
  - `uv run uvicorn ...` + um `curl` de exemplo para `/v1/extract`
  - `GET /v1/health`
  - (se/quando existir frontend) upload → resultado → hashes
  - `docker compose up` como modo produção-like
- Resultado esperado: reduz atrito de piloto e acelera feedback.

---

## Sugestão de ordem de entrega (1 semana de foco)

1. API v1 + contrato de response
2. hashes + metadata
3. logging sem PII
4. limites de upload + validações
5. concorrência/CPU-bound
6. mean_confidence no OCR
7. testes mínimos
8. docker + README com comandos
