# Ultrathink — Stack Tecnológica

**Versão:** 1.0  
**Última atualização:** Janeiro 2026  
**Escopo:** Fase 1 (Medical MVP) com extensões para Fases 2–6

---

## 1. Visão Geral

A stack do Ultrathink é **API-first**, com backend em Python, pipeline de OCR/ML em Python, e frontend para demo e interfaces de uso. A escolha prioriza: desempenho para documentos, integração com ecossistema ML, e facilidade de deploy em ambiente do cliente (Docker, on-premise futuro).

---

## 2. Backend

### 2.1 Runtime e Framework

| Camada | Tecnologia | Versão mínima | Notas |
|--------|------------|---------------|-------|
| **Linguagem** | Python | 3.12 | Tipagem moderna, performance, suporte a `uv` |
| **Framework HTTP** | FastAPI | 0.115+ | Async, OpenAPI, validação Pydantic |
| **Servidor ASGI** | Uvicorn | 0.30+ | Produção com workers; `--reload` em dev |

### 2.2 Gerenciamento de Dependências

| Ferramenta | Uso |
|------------|-----|
| **uv** | Instalação de pacotes, lockfile (`uv.lock`), venv; substitui pip/poetry para o projeto |
| **pyproject.toml** | Metadados, dependências, scripts, grupos (ex.: `semgrep`, `dev`) |

### 2.3 Estrutura de Código (Backend)

```
app/
├── main.py              # FastAPI app, rotas /v1/extract, /v1/health
├── api/
│   └── v1/
│       ├── extract.py   # (Fase 2: separar em módulos)
│       └── health.py
├── services/
│   ├── ocr.py           # PaddleOCR + (opcional) TrOCR
│   ├── hashing.py
│   └── (Fase 2: batch, webhooks, certificate)
├── schemas/             # Pydantic: ExtractionResult, BatchResponse, etc.
└── config.py            # Settings (pydantic-settings): env, feature flags
```

### 2.4 Dependências Principais (Backend)

| Pacote | Uso |
|--------|-----|
| `fastapi` | API REST, OpenAPI |
| `uvicorn` | ASGI server |
| `python-multipart` | Upload de arquivos |
| `pydantic`, `pydantic-settings` | Schemas e config |
| `pymupdf` (fitz) | PDF → imagem (páginas) |
| `opencv-python` | Manipulação de imagem para OCR |
| `paddlepaddle`, `paddleocr` | OCR impresso |
| `transformers`, `torch` | (Opcional Fase 1) TrOCR para manuscritos |
| `httpx` | (Fase 2) Cliente HTTP para webhooks |

---

## 3. OCR e ML

### 3.1 Pipeline de OCR

| Componente | Tecnologia | Papel |
|------------|------------|-------|
| **PDF → imagem** | PyMuPDF (`fitz`) | `page.get_pixmap()` por página; matriz 2x2 para resolução |
| **Impresso** | PaddleOCR | `use_angle_cls=True`, `lang="pt"`; retorno com bbox, texto, confidence |
| **Manuscrito (opcional)** | TrOCR (`microsoft/trocr-base-handwritten` ou `-large`) | Refinamento de regiões com confidence &lt; limiar (ex.: 0.85) |

### 3.2 Fluxo (Resumido)

```
PDF (bytes) → fitz (páginas) → por página:
  → OpenCV (BGR) → PaddleOCR → {text, confidence, bbox}
  → [opcional] se confidence < 0.85: crop → TrOCR → substituir texto/confidence
→ Agregação: list[page_data], full_text, mean_confidence, low_confidence_pages
```

### 3.3 Ambientes de Execução (OCR/ML)

- **CPU:** PaddleOCR e TrOCR (base) rodam em CPU; adequado para Fase 1 e volumes moderados.
- **GPU (Fase 2+):** Opcional para TrOCR-large e batch alto; CUDA via `paddlepaddle-gpu` e `torch` com CUDA. Deploy em modal, RunPod ou VM com GPU.

---

## 4. Frontend (Demo e Futuras UIs)

### 4.1 Stack Recomendada (Fase 1)

| Camada | Tecnologia | Versão | Notas |
|--------|------------|--------|-------|
| **Runtime e package manager** | Bun | 1.1+ | Instalação, scripts, execução; mais rápido que npm/pnpm |
| **Framework** | Next.js | 15 | App Router, file-based routing, SSR/SSG, build |
| **UI** | React | 18 | Componentes (incluído no Next.js); reuso para Chat na Fase 3 |
| **Linguagem** | TypeScript | 5 | Tipagem, contratos com API |
| **HTTP** | fetch ou `ky` | — | Chamadas a `POST /v1/extract`; `ky` opcional para retry e timeout |
| **Formulário / estado** | React (useState) ou React Hook Form | — | Fase 1: estado local suficiente |
| **Estilos** | CSS (tokens do Design System) | — | Variáveis em `tokens.css`; `app/globals.css`; Tailwind opcional se alinhado aos tokens |
| **Ícones** | lucide-react | — | Consistente com o Design System |

### 4.2 Alternativas Documentadas

| Cenário | Stack alternativa | Prós | Contras |
|---------|-------------------|------|---------|
| Menor complexidade | HTML + Alpine.js + CSS | Sem build, deploy estático | Menos reuso para Chat |
| Equipe Vue | Vue 3 + Vite + TypeScript | Ecossistema Vue, SFC | Reuso do Design System; Chat exigiria componentes Vue |
| Máxima simplicidade | HTML + HTMX + CSS | Servidor renderiza; pouco JS | Menos interatividade rica |

A implementação de referência assume **Next.js + Bun + TypeScript**; as alternativas podem ser adotadas mantendo o mesmo Design System e contratos de API.

### 4.3 Estrutura de Pastas (Frontend — Next.js App Router)

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx            # Demo em /
│   └── globals.css
├── components/
│   ├── UploadZone.tsx
│   ├── ExtractResult.tsx
│   ├── HashBlock.tsx
│   ├── ConfidenceBadge.tsx
│   └── (Fase 3: Chat, etc.)
├── lib/
│   └── extract.ts         # postExtract, POST /v1/extract
├── types/
│   └── extract.ts
├── styles/
│   └── tokens.css
├── public/
├── next.config.ts
├── package.json
└── bun.lockb
```

---

## 5. Infraestrutura e Deploy

### 5.1 Containerização

| Artefato | Uso |
|----------|-----|
| **Dockerfile** | Multi-stage: (1) build do frontend com Bun (`bun run build`; Next com `output: 'export'` → `out/`); (2) Python + deps + `app/` + `frontend/out`; CMD uvicorn. Ou Next como serviço separado (`bun run start`). |
| **docker-compose.yml** | Serviço `api` (FastAPI); serviço `frontend` (Next com `bun run start`) ou um único serviço (FastAPI servindo `frontend/out` em static export) |
| **.dockerignore** | `node_modules`, `__pycache__`, `.git`, `frontend/node_modules`, `frontend/.next`, `frontend/out`, etc. |

### 5.2 Execução Local (Dev)

| Comando | Descrição |
|---------|-----------|
| `uv run uvicorn app.main:app --reload` | API em `http://localhost:8000` |
| `cd frontend && bun run dev` | Frontend em `http://localhost:3000` (Next.js); rewrites para API em `/v1` |
| `docker compose up` | API + demo (produção-like) |

### 5.3 Produção (Fase 1 e 2)

- **API:** Uvicorn com 2–4 workers; atrás de reverse proxy (nginx, Caddy) para TLS e rate limiting.
- **Demo:** Arquivos estáticos servidos pelo mesmo proxy ou pelo FastAPI (`StaticFiles` em `/` ou `/demo`).
- **Futuro:** Kubernetes, ECS, ou on-premise conforme PRD (Fase 5).

---

## 6. Persistência e Dados

### 6.1 Fase 1 (API)

- **Nenhuma persistência no servidor.** Documentos e resultados processados em memória; hashes e `extraction_metadata` retornados na resposta. (Opcional: log de auditoria apenas `document_hash`, `result_hash`, `processing_time_ms`, `document_type`, `pages` em arquivo ou DB; ver plano.)

### 6.2 Fase 2+ (Ultrathink Cloud)

- **Audit trail:** SQLite ou Postgres: `document_hash`, `result_hash`, `timestamp`, `document_type`, `processing_time_ms`, etc. Sem PII.
- **Billing e métricas:** Agregados por `api_key` ou tenant; armazenamento a definir (Postgres, BigQuery, etc.).

### 6.3 Cliente (SDK, Fase 2+)

- **SQLite local (no ambiente do cliente):** `documents`, `document_chunks`, `chat_sessions`, `chat_messages`, `processing_logs` — conforme PRD Seção 5.3. Criptografia AES-256 no cliente; Ultrathink não acessa.

---

## 7. Segurança e Compliance

| Aspecto | Tecnologia / Prática |
|---------|-----------------------|
| **TLS** | 1.3 em produção (reverse proxy) |
| **Autenticação API** | API Key no header `Authorization: Bearer uk_xxx` ou `X-API-Key` (Fase 2) |
| **Hash** | SHA-256 para `document_hash` e `result_hash` (lib `hashlib`) |
| **Deleção segura** | Overwrite 3-pass em arquivos temporários (Fase 2, quando houver `temp_path`) |
| **Secrets** | Variáveis de ambiente; não commitar `.env` |
| **CORS** | Restringir origens em produção; em dev, permitir `localhost` do frontend |

---

## 8. Observabilidade (Fase 2+)

| Camada | Ferramenta | Uso |
|--------|------------|-----|
| **Logs** | Estruturados (JSON) via `structlog` ou `logging` | stdout; coleta por Fluentd, Loki, CloudWatch, etc. |
| **Métricas** | Prometheus + `prometheus-client` | `latency_seconds`, `requests_total`, `extract_errors_total` |
| **Health** | `GET /v1/health` | `motor`, `version`; (Fase 2) checagem de dependências |
| **Tracing** | (Opcional) OpenTelemetry | Traces de `POST /v1/extract` e chamadas a OCR |

---

## 9. Testes

| Tipo | Ferramenta | Escopo |
|------|------------|--------|
| **Backend unit** | pytest | `hashing`, funções puras de `ocr` (mocks de PaddleOCR) |
| **Backend API** | pytest + `httpx.ASGITransport` + `TestClient` | `POST /v1/extract` com PDF fixture; validação de schema |
| **Frontend unit** | Vitest | Componentes e funções de `api/extract` (mock de fetch) |
| **E2E (opcional)** | Playwright | Upload → resultado → hashes na UI |
| **OCR (integração)** | pytest com 1–2 PDFs de teste (anonimizados) | Acurácia e formato de saída; rodar em CI ou manual |

---

## 10. Ferramentas de Desenvolvimento

| Ferramenta | Uso |
|------------|-----|
| **uv** | Instalar deps, rodar `uv run pytest`, `uv run uvicorn ...` |
| **ruff** | Lint e format (substitui flake8, black, isort) |
| **mypy** | Checagem de tipos no backend (opcional, strict em novos módulos) |
| **pre-commit** | Hooks: ruff, mypy, pytest (opcional) |
| **npm / pnpm** | Frontend: deps, `npm run build`, `npm run dev` |

---

## 11. Resumo por Fase

| Fase | Backend | OCR | Frontend | Infra | Persistência |
|------|---------|-----|----------|-------|--------------|
| **1** | FastAPI, uvicorn, Python 3.12 | PaddleOCR (+ TrOCR opcional) | Next.js 15 + Bun + TS, tokens do Design System | Docker, docker-compose | Nenhuma (ou só log de hashes) |
| **2** | + batch, webhooks, `/v1/verify` | — | — | — | Audit trail (hashes, logs); certificados |
| **3** | + `/v1/chat`, chat_package | — | + UI de Chat, RAG | — | Cliente: SQLite local (chunks, embeddings) |
| **4–6** | Novos endpoints, modelos | TrOCR, documentoscopia | Novos fluxos | On-prem, K8s | Conforme PRD |

---

## 12. Referências

- [FastAPI](https://fastapi.tiangolo.com/)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [TrOCR (Hugging Face)](https://huggingface.co/microsoft/trocr-base-handwritten)
- [Next.js](https://nextjs.org/), [Bun](https://bun.sh/)
- [Design System (DESIGN_SYSTEM.md)](DESIGN_SYSTEM.md)
- [PRD — Ultrathink](../../) (raiz do repositório ou link interno)
