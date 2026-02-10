# Playbook de Treinamento — Detecção de Fraudes em Documentos (Fases)

Este documento descreve um caminho **faseado e detalhado** para construir um sistema de detecção de fraudes (documentoscopia) no Ultrathink, com foco em:

- Escalabilidade (milhões de páginas)
- Explicabilidade (sinais + evidências, não só “fraude/não fraude”)
- Baixa taxa de falsos positivos (impacto operacional)
- Governança e privacidade (zero-retention por padrão; opt-in para dados de treino)
- Portabilidade cloud e on-prem

Fraude é um alvo “moving target”: padrões mudam, rótulos são raros e o custo de erro é assimétrico. Por isso, o caminho recomendado é **camadas**: regras/forense → score de risco → ML supervisionado quando houver labels.

---

## 0) Definições e escopo (antes de treinar qualquer coisa)

### 0.1 Tipos de fraude (defina o que entra no modelo)

Liste explicitamente quais fraudes você quer detectar (exemplos):

- **Adulteração de valores**: total/parcelas/juros alterados.
- **Substituição de páginas**: páginas de outro documento inseridas.
- **Colagem/recorte**: campos montados por edição (copy/paste).
- **Assinatura falsa**: assinatura desenhada/colada; ausência de assinatura válida onde deveria existir.
- **Reimpressão/scan fraudulento**: documento digital reimpresso e escaneado para “perder rastros”.
- **Metadados suspeitos**: inconsistências de datas/produtor/estrutura PDF.

> Importante: “fraude” não é um rótulo único. Use uma taxonomia: `fraud_type` e `signals[]`.

### 0.2 Saída do sistema (contrato)

Evite resposta binária. Retorne:

- `risk_score` (0–1)
- `risk_level` (ex.: `low/medium/high`)
- `signals[]`: lista de sinais acionados (ex.: `PDF_METADATA_INCONSISTENT`, `ELA_HIGH`, `FONT_ANOMALY`)
- `evidence[]`: ponteiros para evidências **não sensíveis** (ex.: bbox/coords, hashes de páginas, estatísticas, IDs)
- `recommended_action`: `accept`, `review`, `reject` (ou apenas `review`/`ok`)

Isso é fundamental para operação: times de fraude/compliance precisam de justificativa.

### 0.3 Métrica de sucesso (SLO e custo)

Você precisa de metas operacionais, não só “acurácia”:

- **FPR (false positive rate)**: % de docs bons enviados para revisão (custo humano).
- **TPR/Recall**: % de fraudes capturadas (risco).
- **Precision**: fraudes que você sinaliza, quantas realmente são fraude.
- **Tempo adicional**: overhead de processamento (ms/página).
- **Impacto por tenant**: falsos positivos concentrados em 1 cliente quebram contrato.

Defina pelo menos dois thresholds:

- `T_review`: acima disso vai para revisão humana.
- `T_block` (opcional): acima disso bloqueia automaticamente (normalmente só depois de maturidade).

---

## 1) Fundamentos: coleta de sinais forenses (sem ML, sem treino)

### Objetivo

Construir um “motor de sinais” determinístico que:

- detecta anomalias óbvias
- produz evidência explicável
- gera features para ML no futuro

### 1.1 Sinais em PDF (estrutura/forense)

Extraia features e sinais do PDF sem olhar conteúdo semântico:

- **Metadados**: `Creator`, `Producer`, `CreationDate`, `ModDate`
  - sinais: datas impossíveis/ausentes; `ModDate` muito posterior; produtor incomum.
- **Estrutura**:
  - número de objetos, streams, xref, compressões
  - fontes embutidas e suas variações
  - imagens por página (qtd, dimensões)
  - presença de camadas/overlays (XObjects)
- **Assinatura digital** (quando houver):
  - presença de assinatura PAdES
  - validação da cadeia e integridade (válida/expirada/revogada)
  - sinais: assinatura inválida, conteúdo alterado após assinatura

> Resultado: um vetor de features por documento + sinais acionados.

### 1.2 Sinais em imagem (página renderizada)

Renderize a página (com DPI consistente) e compute:

- **Qualidade**: blur, contraste, ruído, skew/rotation estimada
- **Compressão**: artefatos JPEG e inconsistência local
- **ELA (Error Level Analysis)** (heurística útil):
  - sinal: regiões com erro alto relativo ao resto
- **Inconsistência local**:
  - variação de blur/ruído por região (indicativo de colagem)
  - bordas duras em regiões “de texto”
- **Duplicação**:
  - padrões repetidos (copy/paste), templates suspeitos

> Não salve imagens por padrão (zero-retention). Salve apenas estatísticas e, se opt-in, crops mínimos.

### 1.3 Sinais semânticos leves (consistência de campos)

Mesmo sem “modelo de fraude”, a extração pode gerar verificações:

- coerência: parcelas × valor ≈ total (quando aplicável)
- ranges plausíveis: CET/juros dentro de limites
- presença de campos obrigatórios
- consistência entre valores repetidos em diferentes seções

Isso produz sinais muito fortes com custo baixo.

### 1.4 Produto desta fase

- Uma biblioteca `fraud_signals` que:
  - calcula features (numéricas/categóricas)
  - levanta `signals[]`
  - retorna um `risk_score` básico (regras/ponderações)
- Um “schema de sinais” versionado (`signals_version`)

---

## 2) Score de risco explicável (modelo simples, supervisionado fraco ou sem labels)

### Objetivo

Transformar sinais/features em um `risk_score` calibrado, mantendo explicabilidade.

### 2.1 Se você NÃO tem labels (situação comum)

Use uma abordagem de **anomaly detection**:

- Entradas: apenas features numéricas/categóricas (sem conteúdo).
- Modelos iniciais:
  - Isolation Forest
  - One-Class SVM (menos escalável)
  - Autoencoder tabular (mais complexo; geralmente depois)

Treino:

1. Construir dataset com um grande volume de “documentos típicos” por tipo/tenant.
2. Treinar por segmento (por `document_type` e/ou por tenant) para reduzir falsos positivos.
3. Definir um threshold de outlier para `review`.

Validação:

- Revisão humana em amostra dos outliers para estimar “fraude provável”.
- Ajuste de features e thresholds até ficar operacional.

### 2.2 Se você tem labels parciais (fraudes confirmadas são poucas)

Use modelo supervisionado clássico em features:

- Logistic Regression / XGBoost / LightGBM

Cuidados:

- Classes desbalanceadas: use `class_weight`, downsample de negativos, ou focal loss (se DL).
- Métrica principal: **Precision@K** (top suspeitos), **PR-AUC** (melhor que ROC-AUC em desbalanceamento).

Saída:

- score + lista de top features/sinais que contribuíram (SHAP ajuda, mas comece simples).

### 2.3 Produto desta fase

- `risk_model_v1` (tabular) ou `anomaly_model_v1`
- thresholds por tipo de documento
- dashboards: taxa de revisão, taxa de bloqueio (se houver), drift de features

---

## 3) Dataset e rotulagem (como conseguir labels sem “guardar tudo”)

### Objetivo

Criar um pipeline de geração de dataset de fraude **com governança**.

### 3.1 Fontes de rótulo (do mais confiável ao menos)

1. **Fraude confirmada** por investigação do cliente (gold label).
2. **Chargeback / contestação** (quase-gold, depende do processo).
3. **Revisão interna** com playbook e dupla checagem.
4. **Sinais fortes** (assinatura inválida + inconsistências) como “silver label”.

Regra: nunca misture “silver” com “gold” sem marcar `label_quality`.

### 3.2 Coleta com opt-in e minimização

Por padrão (zero-retention):

- armazene apenas features + sinais + hashes + metadados de processamento

Com opt-in:

- armazene **somente evidências mínimas** para rotulagem e treino:
  - crops de regiões suspeitas (com bbox)
  - página renderizada com baixa resolução (se necessário) *ou* embeddings visuais
  - nunca armazene “pacotes” sem TTL

### 3.3 UI/fluxo de rotulagem

Mesmo que seja simples no começo:

- fila de revisão por risco (top-K)
- checklist por tipo de fraude (taxonomia)
- campos:
  - `fraud_type` (multi-label)
  - `fraud_confirmed` (sim/não/incerto)
  - `notes` (opcional)
  - `labeler_id`, `review_time_sec`, `confidence`

### 3.4 Active learning (essencial)

Selecione amostras para revisão/rotulagem por:

- maior risco + alta incerteza do modelo
- divergência entre dois modelos (tabular vs visão)
- novos produtores/metadados não vistos
- drift de distribuição de features por tenant

---

## 4) Modelo visual de adulteração (quando valer a pena)

### Objetivo

Detectar padrões visuais de edição que regras simples não capturam bem.

### 4.1 Antes de treinar: baselines e dados sintéticos

Você pode acelerar muito com **fraude sintética**:

1. Pegue documentos legítimos (opt-in ou datasets públicos).
2. Aplique transformações:
   - recorte/colagem de campos
   - alteração de números com fontes similares
   - mudança de contraste local
   - inserção de ruído seletivo
3. Gere “máscaras” (ground truth) das regiões adulteradas.

Isso cria dataset supervisionado com labels fortes (para tamper localization), sem depender de fraudes reais no início.

### 4.2 Modelos recomendados (incremental)

Comece com classificação por página:

- CNN leve / EfficientNet / ViT pequeno

Depois, se precisar localizar:

- segmentação/heatmap (U-Net/DeepLab) para indicar regiões suspeitas

### 4.3 Treino (passo a passo)

1. Dataset:
   - `legit` vs `tampered`
   - se localizar: máscara por pixel
2. Splits:
   - por template/tenant (evitar vazamento)
3. Métricas:
   - classificação: PR-AUC, Precision@K
   - localização: IoU/Dice das máscaras (quando houver)
4. Deploy:
   - como “sinal” adicional (não decisão final)
   - roda apenas em páginas candidatas (para custo)

---

## 5) Integração com assinatura digital e verificações “fortes”

### Objetivo

Usar verificações criptográficas e validações estruturais como sinais de altíssima confiabilidade.

Checklist:

- Verificar assinatura PAdES quando existir:
  - integridade
  - certificado, cadeia e validade
  - alteração pós-assinatura
- Se documento “deveria” ser assinado e não é:
  - sinal `MISSING_SIGNATURE_EXPECTED`

> Em muitos cenários bancários, isso sozinho reduz fraudes e falsos positivos.

---

## 6) Calibração, thresholds e política de decisão

### Objetivo

Transformar scores em ações operacionais, com controle de custo/risco.

Passos:

1. Definir `T_review` por `document_type` (e possivelmente por tenant).
2. Medir:
   - % docs revisados
   - fraudes capturadas
3. Ajustar para restrição de custo:
   - ex.: “revisar no máximo 1% dos docs”
4. Calibrar probabilidades (Platt / isotonic) se supervisionado.

Saída:

- `risk_score_calibrated`
- `policy_version` (versione a regra de decisão)

---

## 7) MLflow: rastreabilidade e promoção de modelos

Para cada run (tabular/visual):

- `params`:
  - `dataset_version`, `manifest_hash`
  - `feature_schema_version`, `signals_version`
  - `document_type`
  - `label_quality` (gold/silver/synthetic)
- `metrics`:
  - PR-AUC, Precision@K, Recall@K
  - FPR @ threshold
  - calibração
- `artifacts`:
  - relatório agregado (sem conteúdo)
  - matriz de confusão, curvas PR
  - lista de “top signals” (IDs/hashes, sem PDF)

Model Registry:

- `staging`: canary por tenant / 1–5% tráfego
- `production`: promoção após SLOs atingidos

---

## 8) Deploy seguro (e compatível com cloud + on-prem)

### 8.1 Arquitetura de inferência

Recomendação:

- `fraud_signals` roda junto do pipeline (worker).
- `risk_model` roda no worker (tabular) e opcionalmente no GPU worker (visual).

### 8.2 Versionamento na resposta e telemetria

Sempre incluir:

- `signals_version`
- `risk_model_version`
- `policy_version`

E logar por documento:

- score + sinais + tempos (sem conteúdo).

### 8.3 Drift e monitoramento

Monitorar:

- distribuição de features por tenant (drift)
- taxa de revisão (subiu = modelo degradou ou ataque novo)
- taxa de fraude confirmada por bucket de score

---

## 9) Checklist por fase (o que “pronto” significa)

### Fase 1 pronta quando:

- sinais explicáveis estão implementados e versionados
- não há retenção de conteúdo por padrão
- dashboard mínimo de taxa de revisão e sinais mais comuns

### Fase 2 pronta quando:

- risk score (anomaly ou supervisionado) reduz falsos positivos vs regras puras
- thresholds por tipo e política versionada

### Fase 3 pronta quando:

- pipeline de labels (gold/silver) existe
- active learning seleciona amostras com melhor ROI

### Fase 4 pronta quando:

- modelo visual adiciona sinal útil (PR-AUC/Precision@K) em produção
- custo é controlado (rodar só em candidatos)

---

## 10) Nota de privacidade/compliance (resumo)

Mesmo com “zero-retention”, detecção de fraude pode envolver dados pessoais.

Regras:

- por padrão: guardar apenas hashes, métricas e features numéricas
- com opt-in: guardar evidências mínimas (crops) com TTL e segregação por tenant
- auditoria: logs de acesso ao bucket de treino e ao MLflow/artifacts
