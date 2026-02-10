# Playbook de Treinamento (Fases) — Ultrathink

Este documento descreve **como executar cada fase de treinamento** recomendada para o produto, com foco em: alta escala, qualidade, rastreabilidade (MLflow), e compatibilidade com **zero-retention** (por padrão) + **opt-in** quando for necessário coletar dados.

O objetivo é melhorar o sistema em etapas de ROI crescente, evitando treinar “modelos grandes” cedo demais e sem dados/labels.

---

## Premissas e princípios

1. **Não treine com dados reais sem opt-in** e base legal/contratual (DPA + anexos). Por padrão: **telemetria sem conteúdo**.
2. **Dados de treino são produtos de segurança**: bucket separado, controles de acesso, retenção definida, auditoria, e segregação por tenant.
3. **Não guarde PDF inteiro se não precisar**: prefira **artefatos mínimos** (crops, bbox, textos curtos, labels) e manifests.
4. **Treino ≠ inferência**: inferência precisa de latência e robustez; treino precisa de rastreabilidade e qualidade de dataset.
5. **Comece com um tipo de documento** (ou um “vertical”) para reduzir entropia: schema, métricas, pipeline, UI de correção, etc.

---

## Infra mínima (válida para cloud e on-prem)

### Armazenamento

- **Object Storage**:
  - Cloud: S3
  - On-prem: MinIO (S3 compatível)
- Buckets recomendados (nomes ilustrativos):
  - `ultrathink-temp` (retenção técnica, TTL curto)
  - `ultrathink-training` (opt-in, dataset de treino)
  - `ultrathink-artifacts` (modelos, relatórios, evals)

### Banco (metadados)

- **PostgreSQL**: tabelas de consentimento, amostras de treino, versões de dataset, versões de modelo, métricas agregadas.

### Rastreamento de experimentos

- **MLflow**:
  - Backend store: Postgres
  - Artifact store: S3/MinIO

### Observabilidade

- OpenTelemetry (recomendado) → Datadog (cloud) e/ou Prometheus/Grafana (on-prem).

---

## Esquema de dados (recomendação prática)

### 1) Manifests (versionamento de dataset)

Em vez de “um dataset = uma pasta solta”, padronize um arquivo `manifest.jsonl` (ou Parquet) com uma linha por amostra:

- `sample_id`
- `tenant_id`
- `document_type`
- `source` (`opt_in_customer`, `synthetic`, `public_dataset`, etc.)
- `created_at`
- `consent_id` (quando aplicável)
- `artifacts` (lista de URIs S3/MinIO para crops, jsons, etc.)
- `labels` (ou URI para labels)
- `features` (opcional)
- `hashes` (`document_hash`, `page_hash`, `crop_hash`)
- `expires_at` (retention)

Esse manifest é o “contrato” do dataset e vira input de treino/reprodutibilidade.

### 2) Artefatos mínimos por fase

- Router: features + rótulos (sem texto sensível)
- NER/extração: tokens OCR + bbox + labels por entidade/campo (ou spans)
- Calibração: features + label de “erro/ok”
- Manuscrito: crops de linhas/palavras + transcrição corrigida

---

## Governança (opt-in e segregação)

### Opt-in (recomendado)

Para qualquer retenção de conteúdo (mesmo crop):

1. **Consentimento contratual**: addendum no DPA ou termo de opt-in com:
   - finalidade (treino e melhoria)
   - quais dados (crops, bbox, texto)
   - retenção (ex.: 30/90/180 dias)
   - medidas de segurança
   - sub-processadores (se houver)
2. **Separação física/lógica**:
   - bucket de treino separado
   - prefixo por `tenant_id`
3. **Retenção**:
   - lifecycle rules por prefixo e por classe de dados
4. **Auditoria**:
   - logs de acesso a objetos
   - trilha de “quem exportou/rotulou/usou no treino”

### “Zero-retention” (default)

Sem opt-in, colete apenas:

- tempos (p50/p95), falhas, tamanhos, contagem de páginas
- estatísticas de confiança (médias, histogramas)
- qualidade da imagem (blur/contraste/rotação) como números
- tipo de documento (se não for PII), ou “classe” genérica

---

# Fase 1 — Router de páginas/documentos (alto ROI)

## Objetivo

Decidir automaticamente **qual pipeline aplicar** por documento/página, reduzindo custo e aumentando robustez:

- `pdf_has_text_layer` (pular OCR e extrair texto do PDF)
- `digital_vs_scan`
- `printed_vs_handwritten`
- `needs_deskew` / `rotation`
- `document_type` (mínimo viável)

## Saídas esperadas

Um “roteador” que recebe metadados e/ou uma imagem e retorna:

- `route`: `PDF_TEXT`, `OCR_PRINTED`, `OCR_HANDWRITTEN`, `MIXED`
- `confidence` do roteamento
- `hints`: `rotation=90`, `dpi_estimate`, `quality_score`, etc.

## Dados necessários

### Coleta (sem conteúdo sensível)

Para muitas decisões, dá para treinar com:

- features do PDF (se tem text layer, número de páginas, dimensões)
- estatísticas de OCR barato (rodar um OCR “rápido” em 1ª página e usar scores)
- métricas de qualidade de imagem (blur/contraste/ruído)

### Rotulagem

Crie uma UI interna simples (ou CSV) para rotular amostras:

- `pdf_has_text_layer`: boolean
- `page_is_handwritten`: boolean (ou `ratio_handwritten` por doc)
- `page_rotation`: {0,90,180,270}
- `document_type`: enum curto (comece pequeno)

## Modelo (recomendação)

Comece simples e rápido:

- Para `pdf_has_text_layer`: regra determinística (parse do PDF) antes de ML.
- Para `digital_vs_scan` / `printed_vs_handwritten` / `rotation`:
  - baseline: heurísticas + thresholds
  - depois: um classificador leve (CNN pequena ou ViT tiny) ou até modelo tabular se features forem boas.

## Treino (passo a passo)

1. **Definir classes** e o que é “misto”.
2. **Montar dataset** com `manifest` + splits (train/val/test).
3. **Treinar baseline** (heurísticas) e registrar métricas.
4. **Treinar modelo leve** e comparar com baseline.
5. **Avaliar por segmento**:
   - digital vs scan
   - documento com 1–2 páginas vs 30+ páginas
6. **Definir thresholds operacionais** (ex.: quando “não sei”, cair para pipeline mais seguro).
7. **Deploy**:
   - versionar `router_version`
   - logar `router_decision` + `confidence` (sem conteúdo)

## Métricas

- `accuracy`, `precision/recall` por classe
- `confusion matrix`
- impacto no custo: % docs que pulam OCR
- impacto na latência: p95 antes/depois

---

# Fase 2 — Extração estruturada (NER / schema) para 1 tipo de documento

## Objetivo

Dado o texto OCR (ou texto do PDF), extrair um **schema** consistente (campos críticos) com alta precisão.

Exemplos (bancário): CET, taxa juros, IOF, valor total, número de parcelas, datas, etc.
Exemplos (medical): CRM, data, achados, etc. (se aplicável).

## Decisão importante: o que treinar primeiro

Evite começar com “LLM gigante” sem dados rotulados.

Ordem prática:

1. Baseline determinístico: regex + regras por layout (rápido, boa referência).
2. Modelo de NER/Token Classification com bbox (melhora generalização).
3. Pós-processamento e validações (ex.: normalização monetária, datas).

## Dados necessários

### O que guardar (opt-in)

Para treinar NER de verdade você precisa de exemplos rotulados. Recomendação de artefatos mínimos:

- tokens OCR por página: `[{text, bbox, confidence}]`
- texto linearizado (opcional)
- labels por token (BIO) ou spans por campo
- metadados: `document_type`, `language=pt-BR`, `ocr_engine_version`, `router_version`

Evite guardar PDF inteiro se o token/bbox já resolve.

### Como rotular

Você precisa de um fluxo de correção:

- UI interna de anotação (pode ser simples no começo):
  - mostra o OCR com bbox
  - permite marcar campos do schema
  - exporta para JSONL

### Active learning (muito recomendado)

Não rotule aleatoriamente “milhares” de docs.
Priorize:

- docs com `low_confidence_alert`
- campos ausentes (`campos_nao_encontrados`)
- divergência entre baseline (regex) e modelo

## Modelo (recomendação)

Escolha 1 abordagem inicial:

1. **Layout-aware** (melhor com bbox): modelos do tipo LayoutLM/Donut-like (mais complexos).
2. **NER em texto + features** (mais simples): transformer PT-BR + heurísticas de posição/linha.

Se a prioridade é velocidade de entrega: comece com NER clássico + pós-processamento, e só migre para layout-aware se o layout for decisivo.

## Treino (passo a passo)

1. **Definir schema mínimo** (campos P0).
2. **Definir o formato de label**:
   - BIO por token (ex.: `B-CET`, `I-CET`) ou
   - spans por campo (mais fácil de rotular, mais trabalho no treino).
3. **Criar dataset v1** (100–500 docs bem escolhidos).
4. **Treinar baseline** (regras/regex) e medir.
5. **Treinar modelo v1** e medir no mesmo split.
6. **Avaliar por campo**:
   - F1 por campo
   - taxa de “não encontrado”
   - taxa de “extraído errado com alta confiança” (pior caso)
7. **Adicionar validações**:
   - formatos (data, moeda, percentuais)
   - coerência (ex.: parcelas * valor ≈ total, quando aplicável)
8. **Criar ciclo de feedback**:
   - UI do cliente corrige campos
   - as correções geram samples opt-in
9. **Deploy com versionamento**:
   - `extractor_version`
   - canary por tenant ou % de tráfego

## Métricas

- por campo: `precision/recall/F1`
- exatidão de valores numéricos (tolerância)
- taxa de campos obrigatórios ausentes
- taxa de revisões humanas (quantas exigem correção)

---

# Fase 3 — Calibração de confiança (qualidade operacional)

## Objetivo

Transformar “confidence do OCR/modelo” em um score que represente melhor a **probabilidade de erro**, para:

- triagem (“revisar” vs “ok”)
- SLO (qualidade por tenant/tipo)
- otimizar custo (evitar retrabalho)

## Dados necessários

Você precisa de uma definição de “erro”.

Fontes de label (da mais forte para a mais fraca):

1. **Correção humana**: usuário corrigiu campo → antes estava errado.
2. **Validações falharam**: regras de consistência detectaram erro provável.
3. **Discrepância entre dois extratores** (baseline vs modelo).

## Features recomendadas (sem conteúdo)

- `mean_confidence` por página e por campo
- `low_confidence_alert` boolean
- tamanho do doc, nº páginas
- métricas de qualidade da imagem: blur/contraste, rotação
- tipo de pipeline (digital/scan/manuscrito)
- versões: `ocr_engine_version`, `extractor_version`

## Modelo (recomendação)

Comece com modelos simples e interpretáveis:

- Logistic Regression / Gradient Boosted Trees

Eles são rápidos, robustos e fáceis de calibrar (Platt scaling/isotonic).

## Treino (passo a passo)

1. Definir label: `error=1/0` por campo e/ou por documento.
2. Construir dataset com features + label.
3. Treinar modelo e calibrar probabilidades.
4. Escolher thresholds:
   - ex.: `risk_score >= 0.7` → revisão obrigatória
5. Validar impacto:
   - reduzir falsos negativos (erro que passou como ok)
   - controlar custo de revisões (falsos positivos)
6. Deploy:
   - score exibido na UI (com explicação simples)
   - logar apenas score e features agregadas (sem conteúdo)

## Métricas

- AUROC / AUPRC
- curva de calibração (reliability)
- trade-off custo vs risco (revisões vs erros escapados)

---

# Fase 4 — Manuscrito (fine-tune) quando houver dados suficientes

## Objetivo

Melhorar a leitura de manuscritos em PT-BR (principalmente “casos difíceis”), reduzindo erro onde OCR padrão falha.

## Pré-requisito (não pule isso)

Você precisa de:

- crops de linhas/palavras (imagens)
- transcrição corrigida (ground truth)
- diversidade de caligrafias/escaneamentos

Sem isso, fine-tune tende a overfit e piorar em produção.

## Coleta (opt-in, mínimo necessário)

Recomendação: coletar **apenas crops** das regiões com baixa confiança.

Pipeline:

1. OCR primário (Paddle) gera bbox + score.
2. Selecionar regiões com `score < threshold` e que pareçam manuscritas.
3. Gerar crops normalizados (tamanho, contraste).
4. Enviar para rotulagem (transcrição).

## Rotulagem (estratégia prática)

- Primeiro: “transcrever texto do crop”.
- Depois: se necessário, normalizar (acentos, abreviações) em uma segunda etapa.

Evite começar rotulando PDFs inteiros.

## Modelo (recomendação)

- TrOCR fine-tune (base) ou modelo equivalente, treinando em cima dos crops.
- Se for muito caro, comece com:
  - melhorar pré-processamento (deskew, binarização, contraste)
  - usar ensemble de OCRs (somente para casos low-confidence)

## Treino (passo a passo)

1. Criar dataset de crops + texto (train/val/test por “writer” quando possível).
2. Definir métricas:
   - CER (Character Error Rate)
   - WER (Word Error Rate)
3. Treinar com early stopping e avaliar generalização.
4. Testar em produção como fallback:
   - só acionar fine-tuned model em regiões low-confidence
5. Monitorar drift:
   - se novos padrões de escrita surgirem, alimentar active learning.

## Deploy e custo

- Sempre como **fallback seletivo**, senão o custo explode.
- Logar apenas CER/WER agregados por versão (nunca texto bruto).

---

## MLflow — como registrar corretamente (todas as fases)

Para cada run:

- `params`:
  - `dataset_version`, `manifest_hash`
  - `model_arch`, `hyperparams`
  - `preprocess_version`, `ocr_engine_version`
  - `document_type`
- `metrics`:
  - router: accuracy/F1 por classe
  - extração: F1 por campo + taxa de ausentes
  - calibração: AUROC/AUPRC + calibração
  - manuscrito: CER/WER
- `artifacts`:
  - relatório (HTML/JSON) com tabelas e gráficos agregados
  - confusion matrix / per-field report
  - pacote do modelo (pesos)
  - (opcional) lista de “casos difíceis” como IDs/hash, sem conteúdo

Use o **Model Registry**:

- `staging`: validação e canary
- `production`: tráfego principal
- sempre com `model_version` explícita na resposta/telemetria

---

## Checklist de produção (antes de “ligar” uma fase)

1. Existe opt-in e retenção definida (se coletar conteúdo)?
2. Dataset tem manifesto versionado + splits reprodutíveis?
3. Métricas por segmento (tipo, qualidade, manuscrito vs impresso)?
4. Canary e rollback estão prontos?
5. Telemetria não contém conteúdo/PII?
6. A UI expõe “revisar/baixa confiança” de forma clara?
