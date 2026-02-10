# Ultrathink — TODOs Passo a Passo

**Versão:** 1.0  
**Data:** Janeiro 2026  
**Objetivo:** Listar todos os TODOs do projeto em passos detalhados e acionáveis.

---

## Índice

1. [MVP — API v1 e hashes](#1-mvp--api-v1-e-hashes)
2. [MVP — Ajustes no OCR](#2-mvp--ajustes-no-ocr)
3. [MVP — Demo UI](#3-mvp--demo-ui)
4. [MVP — Docker e documentação](#4-mvp--docker-e-documentação)
5. [MVP — Piloto](#5-mvp--piloto)
6. [Design System — Estilo Harvey](#6-design-system--estilo-harvey)
7. [Roadmap 2026 — Manutenção do doc](#7-roadmap-2026--manutenção-do-doc)
8. [Fase 2 — Banking MVP (pós-MVP)](#8-fase-2--banking-mvp-pós-mvp)
9. [Fases 3 a 7 — Visão geral](#9-fases-3-a-7--visão-geral)

---

## 1. MVP — API v1 e hashes

### 1.1 Rotas e contrato

- [ ] **1.1.1** Criar ou ajustar `app/main.py` para registrar rotas sob o prefixo `/v1/`.
- [ ] **1.1.2** Criar rota `POST /v1/extract` que aceite `multipart/form-data`.
- [ ] **1.1.3** Adicionar parâmetro `file: UploadFile = File(...)` e validar `file.content_type == "application/pdf"`; se não for, retornar `HTTPException(400, "Por favor envie apenas arquivos PDF válidos")`.
- [ ] **1.1.4** Adicionar parâmetro opcional `document_type: str = Form("auto")` com valores aceitos: `auto`, `laudo_medico` (e depois `prescricao` se necessário). Rejeitar outros com 422.
- [ ] **1.1.5** Adicionar parâmetro opcional `include_chat_package: bool = Form(False)`.
- [ ] **1.1.6** Ler o conteúdo do arquivo com `content = await file.read()` e manter apenas em memória (não gravar em disco).
- [ ] **1.1.7** Chamar `extract_pdf(content)` de `app.services.ocr` e obter `list[dict]` por página.
- [ ] **1.1.8** Em bloco `try/except`, em caso de exceção: retornar `HTTPException(500, detail=str(e))`; em `finally`: garantir `del content` e `gc.collect()` após o `return` (ou ao sair do handler) para não reter o PDF na memória.

### 1.2 Serviço de hash e metadata

- [ ] **1.2.1** Criar arquivo `app/services/hash_and_metadata.py`.
- [ ] **1.2.2** Implementar `compute_document_hash(content: bytes) -> str`: usar `hashlib.sha256(content).hexdigest()` e retornar string hex (ex. `"a1b2c3d4..."`).
- [ ] **1.2.3** Implementar `compute_result_hash(data: dict) -> str`: `json.dumps(data, sort_keys=True)` em UTF-8, depois `hashlib.sha256(...).hexdigest()`.
- [ ] **1.2.4** Implementar `build_metadata_extracao(pages: list, processing_time_ms: int) -> dict` com: `confianca_geral` (média dos `mean_confidence` ou dos scores por página, ou 0 se vazio), `campos_baixa_confianca` (lista de `"page_N"` onde `mean_confidence < 0.85` ou `low_confidence_alert`), `campos_nao_encontrados` (lista vazia na Fase 1), `paginas_processadas` (len(pages)), `tempo_processamento_ms` (valor passado).
- [ ] **1.2.5** Exportar as três funções no `__init__` ou importá-las diretamente em `main.py`.

### 1.3 Montagem da resposta ExtractionResult

- [ ] **1.3.1** Antes de chamar `extract_pdf`, calcular `document_hash = compute_document_hash(content)`.
- [ ] **1.3.2** Após `extract_pdf`, montar `data = {"pages": result, "full_text": " ".join(...)}` (full_text opcional: concatenação do texto de todas as páginas).
- [ ] **1.3.3** Calcular `result_hash = compute_result_hash(data)`.
- [ ] **1.3.4** Calcular `processing_time_ms = int((time.time() - start) * 1000)` (usar `start = time.time()` no início do handler).
- [ ] **1.3.5** Chamar `metadata_extracao = build_metadata_extracao(result, processing_time_ms)`.
- [ ] **1.3.6** Calcular `confidence` como a média dos `mean_confidence` de cada página (ou dos `rec_scores` se `mean_confidence` não existir ainda); se não houver, usar `metadata_extracao["confianca_geral"]`.
- [ ] **1.3.7** Definir `chat_package = None` (sempre na Fase 1, independente de `include_chat_package`).
- [ ] **1.3.8** Retornar JSON: `{"data": data, "document_hash": document_hash, "result_hash": result_hash, "confidence": confidence, "processing_time_ms": processing_time_ms, "metadata_extracao": metadata_extracao, "chat_package": chat_package}`.

### 1.4 Rota /v1/health e /extract legado

- [ ] **1.4.1** Criar rota `GET /v1/health` que retorne `{"status": "online", "motor": "PaddleOCR"}` (ou `"PaddleOCR+TrOCR"` quando TrOCR estiver integrado).
- [ ] **1.4.2** Decidir e implementar: (a) redirecionar `POST /extract` para `POST /v1/extract` com 308, ou (b) manter `POST /extract` funcionando e adicionar header `Deprecation` ou comentário no código. Documentar no README.

---

## 2. MVP — Ajustes no OCR

- [ ] **2.1 Em `app/services/ocr.py`**, para cada página em `result[0]` (ou estrutura equivalente do PaddleOCR), calcular a média dos `rec_scores` (ou `current_score` no loop existente) e adicionar ao `page_data` a chave `"mean_confidence"` com esse valor.
- [ ] **2.2** Garantir que `build_metadata_extracao` em `hash_and_metadata.py` use `mean_confidence` por página quando disponível; caso contrário, inferir a partir de `low_confidence_alert` ou dos itens em `text` com `confidence`.
- [ ] **2.3 (Opcional — pode ficar para pós-MVP)** Integrar TrOCR: em `ocr.py`, para cada região/linha com `confidence < 0.85`, extrair o bbox, fazer crop da imagem, rodar TrOCR (`microsoft/trocr-base-handwritten`) no crop e substituir o texto e a confidence no resultado. Isolar em função `refine_with_trocr(image, paddle_result) -> refined_result` ou similar.

---

## 3. MVP — Demo UI

### 3.1 Setup do frontend

- [ ] **3.1.1** Criar pasta `frontend/` na raiz do projeto.
- [ ] **3.1.2** Executar `bunx create-next-app@latest frontend` com TypeScript, ESLint, `src/` opcional (ou sem `src/` e usar `app/` na raiz); escolher App Router. Ou criar manualmente com `app/`, `next.config.ts`, `package.json`, `tsconfig.json`.
- [ ] **3.1.3** Instalar dependências com Bun: `bun add lucide-react`; dev: `bun add -d @testing-library/react @testing-library/jest-dom vitest` (ou `jest`), `prettier` (conforme [FRONTEND](FRONTEND.md)). Next já traz `typescript`, `eslint`, `eslint-config-next`.
- [ ] **3.1.4** Em `next.config.ts`, configurar `rewrites: async () => [{ source: "/v1/:path*", destination: "http://localhost:8000/v1/:path*" }]` para proxy da API em dev.
- [ ] **3.1.5** Criar `frontend/.env.example` com `NEXT_PUBLIC_API_URL=` (vazio para usar rewrites em dev).

### 3.2 Estilos e tokens

- [ ] **3.2.1** Criar `frontend/styles/tokens.css` com as variáveis do [DESIGN_SYSTEM](DESIGN_SYSTEM.md) (ou Harvey-inspired quando aplicado): `--font-display`, `--font-body`, `--font-mono`; `--color-primary`, `--color-surface`, `--color-background`, `--color-border`, `--color-text`, `--color-text-muted`, `--color-success`, `--color-warning`, `--color-error`, `--color-info` e respectivos `-bg`; `--space-*`, `--radius-*`, `--text-*`.
- [ ] **3.2.2** Criar `frontend/app/globals.css` com reset mínimo, `box-sizing: border-box`, `body { font-family: var(--font-body); }` e `@import` de `../styles/tokens.css` (ou `@/styles/tokens.css`).
- [ ] **3.2.3** Em `frontend/app/layout.tsx`, importar `../styles/tokens.css` (ou `@/styles/tokens.css`) e `./globals.css`; em `app/globals.css` fazer `@import` de `tokens.css` ou importar ambos em `layout.tsx`.
- [ ] **3.2.4** Em `app/layout.tsx`, carregar fontes com `next/font/google` (ex.: `IBM_Plex_Sans`, `JetBrains_Mono`) ou `<link>` no `<head>` para Google Fonts (Instrument Sans, Source Serif 4 / Fraunces se Harvey — ver [FRONTEND](FRONTEND.md) 8.3).

### 3.3 Tipos e API client

- [ ] **3.3.1** Criar `frontend/types/extract.ts` com interfaces: `PageData` (`page_number`, `text: Array<{content, confidence}>`, `low_confidence_alert` ou equivalente); `MetadataExtracao` (`confianca_geral`, `campos_baixa_confianca`, `campos_nao_encontrados`, `paginas_processadas`, `tempo_processamento_ms`); `ExtractionResult` (`data`, `document_hash`, `result_hash`, `confidence`, `processing_time_ms`, `metadata_extracao`, `chat_package`).
- [ ] **3.3.2** Criar `frontend/lib/extract.ts` com função `postExtract(file: File, options?: { document_type?: string; include_chat_package?: boolean }): Promise<ExtractionResult>`.
- [ ] **3.3.3** Em `postExtract`: criar `FormData`, anexar `file` com chave `"file"`; se `options?.document_type` existir, anexar com chave `"document_type"`; se `options?.include_chat_package` não for `undefined`, anexar `"include_chat_package"` como string `"true"` ou `"false"`.
- [ ] **3.3.4** Fazer `fetch(\`${process.env.NEXT_PUBLIC_API_URL || ""}/v1/extract\`, { method: "POST", body: formData })`; se `!res.ok`, ler `res.json().catch(() => ({}))` e lançar `new Error(err.detail || \`Erro ${res.status}\`)`; senão `return res.json()`.

### 3.4 Componentes

- [ ] **3.4.1** Criar `frontend/components/UploadZone.tsx`: área com borda 2px dashed `var(--color-border)`, `border-radius: var(--radius-lg)`, padding `var(--space-8)`; texto "Arraste o PDF ou clique para selecionar" em `--color-text-muted`; `<input type="file" accept="application/pdf" />` oculto, acionado pelo clique na área ou por drag-and-drop; estado `file: File | null`; ao selecionar, exibir nome e tamanho do arquivo e botão "Remover"; em `onDragOver`/`onDrop`, prevenir default e atualizar estado (opcional: borda `--color-primary` e fundo `--color-primary-muted` no hover/drag). Expor `file` e `onFileChange` ou `onClear` via props.
- [ ] **3.4.2** Criar `frontend/components/ExtractResult.tsx`: recebe `result: ExtractionResult`; exibe `result.data.pages` em lista ou abas; para cada página: `page_number`, lista de `text` com `content` e, se `confidence < 0.85`, fundo `var(--color-warning-bg)` ou sublinhado; exibir `metadata_extracao.paginas_processadas` e `metadata_extracao.tempo_processamento_ms`.
- [ ] **3.4.3** Criar `frontend/components/HashBlock.tsx`: recebe `document_hash` e `result_hash`; exibe cada hash em `font-family: var(--font-mono)`, `font-size: var(--text-sm)`; truncar com `text-overflow: ellipsis` ou em uma linha; botão "Copiar" ao lado de cada hash que chama `navigator.clipboard.writeText(document_hash)` ou `result_hash`; `aria-label` descritivo no botão.
- [ ] **3.4.4** Criar `frontend/components/ConfidenceBadge.tsx`: recebe `confidence: number`; se `>= 0.9` usa `--color-success-bg` e `--color-success`; se `>= 0.7` e `< 0.9` usa `--color-warning-bg` e `--color-warning`; se `< 0.7` usa `--color-error-bg` e `--color-error`; exibe texto tipo "Alta", "Média", "Baixa" ou o valor em percentual; `border-radius: var(--radius-sm)`, `padding: 4px 10px`, `font-size: var(--text-sm)`, `font-weight: 500`.
- [ ] **3.4.5** Criar `frontend/components/MetadataExtracao.tsx` (opcional): recebe `metadata_extracao` e exibe em formato resumido (confiança geral, páginas processadas, tempo, lista de `campos_baixa_confianca`).

### 3.5 App e fluxo

- [ ] **3.5.1** Em `app/page.tsx` (ou em um client component `components/DemoPage.tsx` com `"use client"`), criar estado: `file: File | null`, `result: ExtractionResult | null`, `loading: boolean`, `error: string | null`.
- [ ] **3.5.2** Adicionar `<UploadZone file={file} onFileChange={setFile} onClear={() => setFile(null)} />`.
- [ ] **3.5.3** Adicionar `<select>` para `document_type` com opções `auto`, `laudo_medico`; e `<input type="checkbox">` para `include_chat_package`; estado local para os dois.
- [ ] **3.5.4** Adicionar botão "Processar" (ou "Enviar"): ao clicar, se `!file` mostrar erro; senão `setLoading(true)`, `setError(null)`, chamar `postExtract(file, { document_type, include_chat_package })`, em `then` `setResult(res)`, em `catch` `setError(e.message)`, em `finally` `setLoading(false)`.
- [ ] **3.5.5** Se `loading`, exibir spinner (Loader2 do lucide-react) ou skeleton na área de resultado.
- [ ] **3.5.6** Se `error`, exibir mensagem em `--color-error` ou card com `--color-error-bg`.
- [ ] **3.5.7** Se `result`, exibir `<ExtractResult result={result} />`, `<HashBlock document_hash={result.document_hash} result_hash={result.result_hash} />`, `<ConfidenceBadge confidence={result.confidence} />` e, se existir, `<MetadataExtracao metadata_extracao={result.metadata_extracao} />`.
- [ ] **3.5.8** Garantir que a UI seja responsiva (coluna única em mobile; em desktop, upload à esquerda ou no topo e resultado à direita/abaixo).

---

## 4. MVP — Docker e documentação

### 4.1 Dockerfile

- [ ] **4.1.1** Criar `Dockerfile` na raiz do projeto.
- [ ] **4.1.2** Stage 1 (frontend): `FROM oven/bun:1-alpine AS frontend`; `WORKDIR /app/frontend`; `COPY frontend/package.json frontend/bun.lockb* ./`; `RUN bun install --frozen-lockfile` (ou `bun install` se não houver lock); `COPY frontend/ .`; em `next.config.ts` usar `output: 'export'` para gerar `out/`; `RUN bun run build`; copiar `out/` para o stage da API (ex.: `/app/static`). Se não usar static export, o frontend roda como serviço com `bun run start` e o Dockerfile ou docker-compose precisa de um serviço separado.
- [ ] **4.1.3** Stage 2 (API): `FROM python:3.12-slim` (ou imagem com deps de sistema para PaddleOCR/OpenCV se necessário); `WORKDIR /app`; copiar `pyproject.toml`, `uv.lock` (ou `requirements.txt`); instalar deps com `uv` ou `pip`; copiar `app/`; `COPY --from=frontend /app/frontend/out ./static` (Next com `output: 'export'` gera `out/`).
- [ ] **4.1.4** No `main.py` (ou em configuração), montar `StaticFiles(directory="static", html=True)` em `"/"` ou `"/demo"` para servir `index.html` e os assets do `out/`; ou servir apenas a API e documentar que o frontend (Next com `bun run start`) pode ser servido como serviço separado.
- [ ] **4.1.5** `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` (ou `uv run uvicorn` conforme setup).

### 4.2 docker-compose e .dockerignore

- [ ] **4.2.1** Criar `docker-compose.yml` com serviço `app` (ou `api`): `build: .`, `ports: ["8000:8000"]`, `environment` se necessário (ex. `NEXT_PUBLIC_API_URL` não é necessário em produção se o frontend for static export servido pelo mesmo host ou se rewrites/ mesmo-origin forem usados).
- [ ] **4.2.2** Criar `.dockerignore` com: `node_modules`, `__pycache__`, `.git`, `frontend/node_modules`, `frontend/.next`, `frontend/out`, `docs`, `.env`, `.DS_Store`, `*.pyc`, etc.

### 4.3 README

- [ ] **4.3.1** Atualizar `README.md` com: título e descrição do Ultrathink (ou Contrackt conforme o projeto).
- [ ] **4.3.2** Seção "Requisitos": Python 3.12, Bun, uv.
- [ ] **4.3.3** Seção "Instalação": `uv sync` (ou `pip install -e .`) na raiz; `cd frontend && bun install`.
- [ ] **4.3.4** Seção "Executar": `uv run uvicorn app.main:app --reload` para API em `http://localhost:8000`; `cd frontend && bun run dev` para frontend em `http://localhost:3000` (rewrites para /v1 em dev).
- [ ] **4.3.5** Seção "Docker": `docker compose up --build`; acessar `http://localhost:8000` (ou a URL que servir o frontend).
- [ ] **4.3.6** Seção "Exemplo de uso": `curl -X POST http://localhost:8000/v1/extract -F "file=@/caminho/arquivo.pdf" -F "document_type=laudo_medico"` e exemplo de resposta (resumido).
- [ ] **4.3.7** Link para `docs/` (PRD, STACK, FRONTEND, DESIGN_SYSTEM, ROADMAP_2026, TODOS).

---

## 5. MVP — Piloto

- [ ] **5.1** Criar `docs/CRITERIOS_PILOTO.md` (ou seção em README) com: critérios de sucesso para o teste com hospital (ex. acurácia mínima em N laudos, tempo médio de processamento < X segundos, ausência de vazamento de dados); como medir (amostra de documentos, comparação com extração manual ou baseline).
- [ ] **5.2** Redigir one-pager ou 1–2 slides: proposta de valor (extração de laudos, zero-retention, hashes para auditoria); como funciona (upload → API → resultado + hashes); próximos passos (piloto, feedback, Fase 2).

---

## 6. Design System — Estilo Harvey

### 6.1 Cores

- [ ] **6.1.1** Em [DESIGN_SYSTEM](DESIGN_SYSTEM.md) seção 3.1, substituir `--color-primary` por `#002764` e `--color-primary-hover` por `#001d4a` ou `#003580`; `--color-primary-muted` por `#e8eef5` ou `#f0f4f9`.
- [ ] **6.1.2** Substituir `--color-text` por `#0a0a0a` ou `#111111`; `--color-text-muted` por `#525252` ou `#6b6b6b`; `--color-text-faint` por `#737373` ou `#8c8c8c`; `--color-background` por `#fafafa` ou `#f8f9fa`; `--color-border` por `#e5e5e5` ou `#ebebeb`.
- [ ] **6.1.3** Ajustar cores semânticas (success, warning, error, info) para combinar com o navy; atualizar tabela 3.2 e o bloco 3.4.
- [ ] **6.1.4** Ajustar seção 3.3 (Tema escuro): `--color-primary-dark`, `--color-background-dark`, etc., para tons que não puxem para marrom.
- [ ] **6.1.5** Atualizar o bloco "Tokens CSS consolidados" (seção 10) com os novos valores.

### 6.2 Tipografia

- [ ] **6.2.1** Em DESIGN_SYSTEM seção 2.1, trocar `--font-display` de "Instrument Sans" para "Source Serif 4" ou "Fraunces"; manter "IBM Plex Sans" para `--font-body` ou trocar para "General Sans" se definido.
- [ ] **6.2.2** Atualizar tabela 2.1, bloco 2.4 e seção 10 com as novas famílias.
- [ ] **6.2.3** Em [FRONTEND](FRONTEND.md) seção 8.3, atualizar o `link` do Google Fonts para incluir Source Serif 4 (ou Fraunces) e IBM Plex Sans, JetBrains Mono.

### 6.3 Tom e princípios

- [ ] **6.3.1** Em DESIGN_SYSTEM seção 1.2, reescrever a "Direção estética" para: "Precisão, gravitas, sofisticação" (bordas definidas, grid estável, paleta contida, serif em títulos).
- [ ] **6.3.2** Na seção 1.3, adicionar princípio "Semantics over appearance" (tokens por função/uso quando possível).
- [ ] **6.3.3** Adicionar subseção 3.5 "Mapa semântico": descrever a função de cada token (ex. `--color-text` = foreground-base) e, opcionalmente, aliases `--color-foreground: var(--color-text)`.
- [ ] **6.3.4** Na seção 11 (Referências), adicionar: Harvey AI (https://www.harvey.ai/), Press Kit (https://www.harvey.ai/brand/press), post "Rebuilding Harvey's Design System From the Ground Up" (https://www.harvey.ai/blog/rebuilding-harveys-design-system-from-the-ground-up); nota de que a estética Ultrathink é inspirada no Harvey, adaptada ao contexto brasileiro.

### 6.4 Correções

- [ ] **6.4.1** Corrigir typo na tabela 3.2 (Cores semânticas): remover `|` extra em `--color-warning` (a célula com `#c17a0b` não deve ter `|` no meio do hex).

---

## 7. Roadmap 2026 — Manutenção do doc

- [ ] **7.1** Garantir que [ROADMAP_2026](ROADMAP_2026.md) exista com: cabeçalho (MVP 13/fev, referência 17/jan); seção 1 (Tecnologias e Serviços) com tabelas Backend, OCR/ML, Frontend, Infra, Persistência, Segurança, Observabilidade, RAG/embeddings, Ferramentas, Design, Serviços externos; seção 2 (Roadmap) com visão geral, MVP por semana, Fases 2–7; diagrama Gantt (mermaid); dependências entre fases; referências para PRD, STACK, FRONTEND, DESIGN_SYSTEM, TODOS.
- [ ] **7.2** À medida que fases forem concluídas, marcar no ROADMAP_2026 e ajustar datas se necessário.
- [ ] **7.3** Quando novas tecnologias forem adotadas, adicioná-las à seção 1 com a Fase correspondente.

---

## 8. Fase 2 — Banking MVP (pós-MVP)

### 8.1 Templates e schema

- [ ] **8.1.1** Definir schema de extração (subset do PRD) para Empréstimo Pessoal e Consignado: `identificacao_contrato`, `dados_cliente`, `dados_operacao`, `condicoes_financeiras`, `parcelas`, etc.
- [ ] **8.1.2** Implementar ou adaptar pipeline de extração (OCR + pós-processamento ou modelo de NER/LLM) para preencher o schema a partir do texto extraído.
- [ ] **8.1.3** Mapear `document_type` para os novos tipos: `emprestimo_pessoal`, `consignado`; retornar `data` no formato do schema.

### 8.2 Batch e webhooks

- [ ] **8.2.1** Criar rota `POST /v1/extract/batch` que aceite `files: list[UploadFile]`, `document_type`, `webhook_url`, `webhook_secret` (opcional).
- [ ] **8.2.2** Retornar `202` com `batch_id`, `total_documents`, `status: "processing"`, `estimated_completion`.
- [ ] **8.2.3** Processar documentos em background (asyncio, Celery, ou worker); para cada documento concluído, enviar POST para `webhook_url` com payload `{ "event": "document.processed", "batch_id", "document_id", "status", "data", "document_hash", "result_hash", "confidence" }`; assinatura ou `webhook_secret` no header conforme PRD.
- [ ] **8.2.4** Ao finalizar o lote, enviar `{ "event": "batch.completed", "batch_id", "total_processed", "successful", "failed", "average_confidence" }`.
- [ ] **8.2.5** Usar `httpx` para as chamadas ao webhook; retry com backoff; logar falhas.

### 8.3 Zero-retention e certificado

- [ ] **8.3.1** Implementar `secure_delete(file_path: str, passes: int = 3)` em `app/services` ou `app/utils`: overwrite com zeros, uns e random; `os.fsync`; `path.unlink()`. Usar quando houver `temp_path` (ex. batch com arquivos grandes gravados em disco).
- [ ] **8.3.2** Garantir que, em fluxos que gravam em disco, o `secure_delete` seja chamado em `finally`.
- [ ] **8.3.3** Gerar certificado de processamento (estrutura conforme PRD 9.1): `id`, `timestamp`, `document_hash`, `result_hash`, `retention_statement`, `verification_url`; incluir no retorno de `POST /v1/extract` (e no webhook de batch) em `certificate`.
- [ ] **8.3.4** Persistir em audit trail (SQLite ou Postgres) apenas: `id` (processing_id), `document_hash`, `result_hash`, `timestamp`, `document_type`, `pages`, `processing_time_ms` — sem conteúdo, sem PII.
- [ ] **8.3.5** Criar rota `GET /v1/verify/{processing_id}` que consulte o audit trail e retorne `{ "valid", "certificate", "signature", "signature_valid" }` conforme PRD 9.2.

### 8.4 Autenticação e admin

- [ ] **8.4.1** Implementar autenticação por API Key: middleware ou dependência que leia `Authorization: Bearer uk_xxx` ou `X-API-Key`; validar contra armazenamento (arquivo, DB ou config); retornar 401 se inválido.
- [ ] **8.4.2** Admin interface (básica): listar batches, status, logs de processamento; autenticação (login ou uso da mesma API Key). Pode ser uma rota no mesmo frontend (React Router) ou app separado.

---

## 9. Fases 3 a 7 — Visão geral

*(Estes itens são de alto nível; serão detalhados em TODOs futuros quando as fases forem iniciadas.)*

### Fase 3 — Chat

- [ ] Implementar geração de `chat_package` na API: chunks (texto por bloco), embeddings (OpenAI `text-embedding-3-small` ou modelo local); incluir em `POST /v1/extract` quando `include_chat_package=true`.
- [ ] Criar rota `POST /v1/chat` que receba `message` e `context` (chunks, embeddings); buscar chunks relevantes (similaridade ou busca vetorial); montar prompt com contexto; chamar LLM e retornar resposta com citações.
- [ ] UI de Chat: input, lista de mensagens, exibição de citações; busca por número de contrato; histórico (SQLite local no cliente ou backend se persistência for necessária).
- [ ] SDK ou guia para armazenar `chat_package` no cliente (SQLite, Qdrant opcional) e enviar `context` para `/v1/chat`.

### Fase 4 — Expansão de contratos

- [ ] Templates: Financiamento de Veículos, Cartão de Crédito, Capital de Giro (PJ).
- [ ] Templates específicos por banco (Itaú, BB, Bradesco): mapeamento de campos e layouts.
- [ ] Ajustes de schema e pipeline de extração.

### Fase 5 — Integrações

- [ ] Conectores Core Banking: export em XML, TXT posicional; SFTP, MQ (conforme PRD 10.1).
- [ ] Webhooks avançados (retry, dead-letter, assinatura).
- [ ] SSO/SAML para admin e interfaces.
- [ ] Opção on-premise: pacote de deploy (Docker, K8s), documentação.
- [ ] nginx/Caddy, TLS, deploys em produção.

### Fase 6 — Documentoscopia

- [ ] Detecção de adulterações em imagens/PDF (inconsistências, recompressão, etc.).
- [ ] Validação de assinaturas (análise de padrões; integração com certificados digitais se aplicável).
- [ ] Análise de metadados PDF (autor, software, datas).
- [ ] Score de risco de fraude; dashboard de alertas.
- [ ] Modelos e heurísticas específicas; treinamento com dados de clientes (acordo).

### Fase 7 — Training e modelos (contínuo)

- [ ] Pipeline de active learning: identificar documentos com baixa confiança; coletar correções (UI ou integração); anonimizar e usar para fine-tune ou treino.
- [ ] Opt-in de coleta: métricas anônimas, feedback de correções anonimizado; configuração na interface do cliente (conforme PRD 16).
- [ ] Federated learning (pesquisa): definir protocolo e agregador; experimentos com clientes-piloto.
- [ ] Benchmark datasets: construir e publicar (anonimizados) para comparar modelos.

---

## Referências

- [README](README.md) — Índice de `docs/`
- [PRD](PRD.md)
- [STACK](STACK.md)
- [COMPLIANCE](COMPLIANCE.md) — Regulamentação e compliance
- [FRONTEND](FRONTEND.md)
- [DESIGN_SYSTEM](DESIGN_SYSTEM.md)
- [ROADMAP_2026](ROADMAP_2026.md)
