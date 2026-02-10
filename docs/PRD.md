# Ultrathink Document Extraction Platform
## Product Requirements Document (PRD)

**Versão:** 1.0  
**Data:** Janeiro 2026  
**Autor:** Joao / Ultrathink  
**Status:** Draft

---

## Sumário Executivo

Ultrathink é uma plataforma de extração inteligente de dados de documentos, posicionada como alternativa brasileira ao Instabase. O produto é API-first, especializado no mercado brasileiro, e oferece arquitetura LGPD-native com zero data retention.

### Visão do Produto

Criar um "cinto do batman" de ferramentas internas para empresas brasileiras, começando com extração de documentos e expandindo gradualmente — sempre priorizando qualidade extrema antes de quantidade.

### Proposta de Valor

| Para | Ultrathink oferece |
|------|-------------------|
| **Bancos e Fintechs** | Extração estruturada de contratos bancários com compliance LGPD nativo |
| **Hospitais e Clínicas** | OCR de alta precisão para laudos médicos manuscritos |
| **Empresas em geral** | Processamento de documentos brasileiros (NF-e, CNH, CPF, contratos) |

---

## 1. Contexto e Problema

### 1.1 Dores do Mercado

**Bancos e Instituições Financeiras:**
- Contratos legados em papel/PDF sem dados estruturados
- Entrada manual de dados (erros, lentidão, custo alto)
- Recuperação de informações requer abrir PDFs manualmente
- Verificação de compliance/auditoria é manual
- Integração com core banking requer redigitação

**Hospitais e Clínicas:**
- Laudos médicos manuscritos de difícil digitalização
- OCR tradicional falha com caligrafia médica
- Necessidade de 85%+ de acurácia para dados críticos
- Volume massivo (até 3 milhões de páginas/mês)

**Mercado Brasileiro em Geral:**
- Documentos específicos (NF-e, CNH, CPF) mal suportados por soluções globais
- Soluções internacionais caras e complexas
- Preocupações com LGPD e soberania de dados

### 1.2 Competidores

| Competidor | Pontos Fortes | Pontos Fracos |
|------------|---------------|---------------|
| **Instabase** | Enterprise completo, IA avançada | Caro, complexo, não especializado em BR |
| **Google Document AI** | Escala, precisão | Genérico, sem foco Brasil |
| **AWS Textract** | Integração AWS | Sem especialização em docs brasileiros |
| **Infosimples** | Foco Brasil, consultas | Menos foco em extração inteligente |

### 1.3 Oportunidade

- Mercado brasileiro com menor competição
- Alto volume de documentos (burocracia)
- Profissionais dispostos a pagar premium por qualidade
- LGPD criou demanda por soluções locais

---

## 2. Público-Alvo e Casos de Uso

### 2.1 Segmentos Prioritários

```
FASE 1: Hospitais/Clínicas
├── Laudos médicos manuscritos
├── Prescrições
└── Prontuários

FASE 2: Bancos/Fintechs
├── Contratos de empréstimo
├── Financiamentos
├── Cartões de crédito
└── Documentoscopia (anti-fraude)

FASE 3: Empresas em Geral
├── Notas Fiscais (NF-e, NFS-e)
├── Documentos de identidade
├── Contratos comerciais
└── RH e folha de pagamento
```

### 2.2 Personas

**Persona 1: Gerente de TI de Banco**
- Precisa integrar extração com core banking legacy
- Preocupado com compliance e LGPD
- Quer API robusta e SLA garantido
- Budget: R$ 10.000-50.000/mês

**Persona 2: Diretor de Operações de Hospital**
- Volume massivo de laudos manuscritos
- Precisa de alta acurácia (erro = risco clínico)
- Quer reduzir equipe de digitação
- Budget: R$ 5.000-20.000/mês

**Persona 3: Analista de Compliance de Fintech**
- Precisa validar documentos de onboarding
- Preocupado com fraudes documentais
- Quer detecção automática de adulterações
- Budget: R$ 3.000-15.000/mês

---

## 3. Tipos de Documentos Suportados

### 3.1 Contratos Bancários (Prioridade Alta)

#### Pessoa Física (PF)

| Tipo | Prioridade | Complexidade |
|------|------------|--------------|
| Empréstimo Pessoal | P0 | Média |
| Consignado | P0 | Média |
| CDC (Crédito Direto ao Consumidor) | P1 | Média |
| Financiamento de Veículos | P1 | Alta |
| Financiamento Imobiliário (SFH/SFI) | P2 | Muito Alta |
| Cartão de Crédito | P1 | Média |
| Cheque Especial | P2 | Baixa |

#### Pessoa Jurídica (PJ)

| Tipo | Prioridade | Complexidade |
|------|------------|--------------|
| Capital de Giro | P1 | Alta |
| Antecipação de Recebíveis | P2 | Alta |
| Linhas BNDES | P2 | Muito Alta |
| Finame | P3 | Alta |
| ACC/ACE (financiamento exportação) | P3 | Alta |

### 3.2 Documentos Médicos (Prioridade Alta)

| Tipo | Prioridade | Desafio Principal |
|------|------------|-------------------|
| Laudos Manuscritos | P0 | Caligrafia médica |
| Prescrições | P1 | Abreviações médicas |
| Prontuários | P2 | Formato variado |
| Atestados | P1 | Validação de autenticidade |

### 3.3 Documentos Brasileiros (Prioridade Média)

| Tipo | Prioridade | Notas |
|------|------------|-------|
| NF-e (Nota Fiscal Eletrônica) | P1 | XML estruturado disponível |
| NFS-e (Nota Fiscal de Serviço) | P2 | Varia por município |
| CT-e (Conhecimento de Transporte) | P2 | Logística |
| CNH | P1 | OCR + validação |
| CPF/CNPJ (comprovantes) | P1 | Extração básica |
| RG | P2 | Muitos formatos estaduais |
| Comprovante de Residência | P2 | Contas de luz, água, etc. |

---

## 4. Schema de Extração

### 4.1 Contratos Bancários - Schema Completo

```json
{
  "contract_extraction_schema": {
    "version": "1.0",
    "document_type": "banking_contract",

    "identificacao_contrato": {
      "numero_contrato": "string",
      "tipo_contrato": "enum[emprestimo_pessoal, consignado, cdc, financiamento_veiculo, financiamento_imobiliario, cartao_credito, cheque_especial, capital_giro, antecipacao_recebiveis]",
      "modalidade": "string",
      "data_contrato": "date",
      "data_primeiro_vencimento": "date",
      "data_ultimo_vencimento": "date",
      "agencia": "string",
      "canal_contratacao": "enum[agencia, digital, correspondente]"
    },

    "dados_cliente": {
      "tipo_pessoa": "enum[PF, PJ]",
      "nome_razao_social": "string",
      "cpf_cnpj": "string",
      "data_nascimento_fundacao": "date",
      "endereco": {
        "logradouro": "string",
        "numero": "string",
        "complemento": "string",
        "bairro": "string",
        "cidade": "string",
        "uf": "string",
        "cep": "string"
      },
      "telefone": "string",
      "email": "string"
    },

    "dados_operacao": {
      "valor_credito": "decimal",
      "valor_iof": "decimal",
      "valor_tarifa_cadastro": "decimal",
      "valor_outras_tarifas": "decimal",
      "valor_seguro": "decimal",
      "valor_total_financiado": "decimal",
      "finalidade": "string"
    },

    "condicoes_financeiras": {
      "taxa_juros_mensal": "decimal",
      "taxa_juros_anual": "decimal",
      "cet_mensal": "decimal",
      "cet_anual": "decimal",
      "sistema_amortizacao": "enum[PRICE, SAC, SAM, AMERICANO]",
      "indexador": "string",
      "spread": "decimal"
    },

    "parcelas": {
      "quantidade_parcelas": "integer",
      "valor_parcela": "decimal",
      "periodicidade": "enum[mensal, quinzenal, semanal]",
      "datas_vencimento": ["date"],
      "valor_total_a_pagar": "decimal"
    },

    "encargos_inadimplencia": {
      "juros_mora_mensal": "decimal",
      "multa_atraso": "decimal",
      "comissao_permanencia": "decimal"
    },

    "garantias": [
      {
        "tipo": "enum[alienacao_fiduciaria, hipoteca, penhor, aval, fianca, sem_garantia]",
        "descricao": "string",
        "valor_avaliacao": "decimal",
        "bem_garantia": {
          "tipo": "string",
          "identificacao": "string",
          "marca_modelo": "string",
          "ano": "integer"
        }
      }
    ],

    "seguro": {
      "tipo": "enum[prestamista, MIP, DFI, residencial, veicular]",
      "seguradora": "string",
      "numero_apolice": "string",
      "premio_total": "decimal",
      "premio_mensal": "decimal",
      "coberturas": ["string"]
    },

    "consignacao": {
      "orgao_pagador": "string",
      "codigo_convenio": "string",
      "matricula": "string",
      "margem_disponivel": "decimal",
      "margem_utilizada": "decimal"
    },

    "assinaturas": [
      {
        "tipo": "enum[contratante, avalista, testemunha, representante_banco]",
        "nome": "string",
        "cpf": "string",
        "data": "date",
        "assinatura_detectada": "boolean"
      }
    ],

    "extraction_metadata": {
      "overall_confidence": "decimal",
      "low_confidence_fields": ["string"],
      "fields_not_found": ["string"],
      "pages_processed": "integer",
      "processing_time_ms": "integer"
    }
  }
}
```

### 4.2 Campos Regulatórios Críticos

| Campo | Obrigatoriedade | Regulação |
|-------|-----------------|-----------|
| CET (Custo Efetivo Total) | Obrigatório | Resolução 3.517/2007 CMN |
| Taxa de Juros Nominal | Obrigatório | Código de Defesa do Consumidor |
| IOF | Obrigatório | Decreto 6.306/2007 |
| Valor Total a Pagar | Obrigatório | CDC |
| Sistema de Amortização | Obrigatório | Transparência |

---

## 5. Arquitetura Técnica

### 5.1 Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENTE (BANCO)                               │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    ULTRATHINK SDK                                │  │
│   │   ┌───────────┐   ┌───────────┐   ┌───────────┐                 │  │
│   │   │  Upload   │──▶│  Process  │──▶│   Store   │                 │  │
│   │   │   Doc     │   │   API     │   │  Local    │                 │  │
│   │   └───────────┘   └───────────┘   └───────────┘                 │  │
│   │                                          │                       │  │
│   │                                          ▼                       │  │
│   │                          ┌───────────────────────────┐          │  │
│   │                          │   SQLite Criptografado    │          │  │
│   │                          │   • Dados extraídos       │          │  │
│   │                          │   • Embeddings/Chunks     │          │  │
│   │                          │   • Histórico de chat     │          │  │
│   │                          └───────────────────────────┘          │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Apenas:
                                    │ • Hashes (SHA-256)
                                    │ • Logs de processamento
                                    │ • Métricas agregadas
                                    │ • Billing info
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ULTRATHINK CLOUD                                │
│                                                                         │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌───────────┐  │
│   │  Processing │   │   OCR/ML    │   │   Billing   │   │ Training  │  │
│   │    API      │   │   Models    │   │   Engine    │   │   Data    │  │
│   │  (Stateless)│   │             │   │             │   │ (Opt-in)  │  │
│   └─────────────┘   └─────────────┘   └─────────────┘   └───────────┘  │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    AUDIT TRAIL (Compliance)                      │  │
│   │   • Document hashes    • Processing logs    • Access logs       │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Arquitetura de Zero Data Retention

**Princípio:** Dados sensíveis nunca são armazenados no Ultrathink Cloud.

```
FLUXO DE PROCESSAMENTO SEGURO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RECEBIMENTO
   └── Documento entra via API
   └── Hash SHA-256 calculado imediatamente
   └── Documento processado em memória

2. PROCESSAMENTO
   └── OCR e extração executados
   └── Resultado gerado em memória
   └── Hash do resultado calculado

3. RESPOSTA
   └── Resultado retornado ao cliente
   └── Hashes salvos para auditoria
   └── Log de processamento salvo (sem PII)

4. LIMPEZA
   └── Documento deletado com overwrite 3x
   └── Memória liberada
   └── GC forçado

DADOS RETIDOS NO ULTRATHINK:
✓ document_hash (SHA-256)
✓ result_hash (SHA-256)
✓ processing_log (sem PII)
✓ billing_metadata
✓ aggregate_statistics

DADOS NÃO RETIDOS:
✗ Documento original
✗ Dados extraídos
✗ Informações pessoais
✗ Conteúdo de texto
```

### 5.3 Storage Local no Cliente (SQLite)

```sql
-- Schema do SQLite Local (no ambiente do cliente)

-- Documentos processados
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    external_id TEXT,
    filename TEXT,
    document_hash TEXT NOT NULL,
    document_type TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence REAL,
    pages INTEGER,
    extracted_data_encrypted BLOB,  -- AES-256
    metadata JSON
);

-- Chunks para RAG/Chat
CREATE TABLE document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id),
    chunk_index INTEGER,
    content_encrypted BLOB,
    embedding BLOB,
    page_number INTEGER,
    bbox JSON
);

-- Histórico de chat
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES chat_sessions(id),
    role TEXT,
    content_encrypted BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logs de processamento
CREATE TABLE processing_logs (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id),
    document_hash TEXT,
    status TEXT,
    processing_time_ms INTEGER,
    synced_to_cloud BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice FTS para busca
CREATE VIRTUAL TABLE chunks_fts USING fts5(
    content,
    content='document_chunks',
    content_rowid='rowid'
);
```

### 5.4 Deleção Segura

```python
import os
import gc
import hashlib
from pathlib import Path

async def process_document_secure(file_content: bytes) -> dict:
    """Processa documento com deleção segura garantida"""
    temp_path = None
    content = None

    try:
        # 1. Calcular hash imediatamente
        document_hash = hashlib.sha256(file_content).hexdigest()

        # 2. Processar extração
        result = await extract_data(file_content)
        result_hash = hashlib.sha256(
            json.dumps(result, sort_keys=True).encode()
        ).hexdigest()

        # 3. Salvar log (sem PII)
        await save_processing_log(
            document_hash=document_hash,
            result_hash=result_hash,
            processing_time_ms=elapsed,
            document_type=result.get('document_type'),
            confidence=result.get('confidence'),
            pages=result.get('pages')
        )

        # 4. Retornar resultado com hashes
        return {
            "data": result,
            "document_hash": document_hash,
            "result_hash": result_hash,
            "chat_package": {
                "chunks": result.get('chunks', []),
                "embeddings": result.get('embeddings', [])
            },
            "certificate": generate_processing_certificate(
                document_hash, result_hash
            )
        }

    finally:
        # 5. SEMPRE deletar com segurança
        if temp_path and Path(temp_path).exists():
            secure_delete(temp_path)

        # Limpar da memória
        if content:
            del content
        del file_content
        gc.collect()


def secure_delete(file_path: str, passes: int = 3):
    """Deleção segura com overwrite múltiplo"""
    path = Path(file_path)
    if not path.exists():
        return

    file_size = path.stat().st_size

    with open(path, 'r+b') as f:
        for pass_num in range(passes):
            f.seek(0)
            if pass_num == 0:
                # Pass 1: zeros
                f.write(b'\x00' * file_size)
            elif pass_num == 1:
                # Pass 2: ones
                f.write(b'\xFF' * file_size)
            else:
                # Pass 3: random
                f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())

    # Deletar arquivo
    path.unlink()
```

---

## 6. API Design

### 6.1 Endpoints Principais

```yaml
openapi: 3.0.0
info:
  title: Ultrathink Document Extraction API
  version: 1.0.0

paths:
  /v1/extract:
    post:
      summary: Extrair dados de documento único
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                document_type:
                  type: string
                  enum: [auto, emprestimo_pessoal, consignado, nfe, cnh, laudo_medico]
                include_chat_package:
                  type: boolean
                  default: false
      responses:
        200:
          description: Extração bem-sucedida
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExtractionResult'

  /v1/extract/batch:
    post:
      summary: Processar lote de documentos
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                files:
                  type: array
                  items:
                    type: string
                    format: binary
                document_type:
                  type: string
                webhook_url:
                  type: string
                  format: uri
      responses:
        202:
          description: Lote aceito para processamento
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchResponse'

  /v1/chat:
    post:
      summary: Chat sobre documento (requer contexto do cliente)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                context:
                  type: object
                  properties:
                    chunks:
                      type: array
                    embeddings:
                      type: array
      responses:
        200:
          description: Resposta do chat

  /v1/verify/{processing_id}:
    get:
      summary: Verificar certificado de processamento
      responses:
        200:
          description: Certificado válido

components:
  schemas:
    ExtractionResult:
      type: object
      properties:
        data:
          type: object
          description: Dados extraídos conforme schema
        document_hash:
          type: string
        result_hash:
          type: string
        confidence:
          type: number
        processing_time_ms:
          type: integer
        chat_package:
          type: object
          properties:
            chunks:
              type: array
            embeddings:
              type: array
        certificate:
          $ref: '#/components/schemas/ProcessingCertificate'

    BatchResponse:
      type: object
      properties:
        batch_id:
          type: string
        total_documents:
          type: integer
        status:
          type: string
          enum: [processing, completed, failed]
        estimated_completion:
          type: string
          format: date-time

    ProcessingCertificate:
      type: object
      properties:
        id:
          type: string
        timestamp:
          type: string
          format: date-time
        document_hash:
          type: string
        result_hash:
          type: string
        retention_statement:
          type: string
        verification_url:
          type: string
          format: uri
```

### 6.2 Batch Processing com Webhooks

```json
// POST /v1/extract/batch
{
  "files": ["contrato_001.pdf", "contrato_002.pdf", ...],
  "document_type": "emprestimo_pessoal",
  "webhook_url": "https://banco.com.br/api/ultrathink/webhook",
  "webhook_secret": "whsec_xxxxx"
}

// Response
{
  "batch_id": "batch_abc123",
  "total_documents": 150,
  "status": "processing",
  "estimated_completion": "2026-01-17T15:30:00Z"
}

// Webhook per document
{
  "event": "document.processed",
  "batch_id": "batch_abc123",
  "document_id": "doc_xyz789",
  "status": "completed",
  "data": {
    "identificacao_contrato": {...},
    "dados_cliente": {...},
    ...
  },
  "document_hash": "sha256:a1b2c3d4...",
  "result_hash": "sha256:9f8e7d6c...",
  "confidence": 0.94
}

// Webhook batch complete
{
  "event": "batch.completed",
  "batch_id": "batch_abc123",
  "total_processed": 150,
  "successful": 147,
  "failed": 3,
  "average_confidence": 0.92
}
```

### 6.3 Formatos de Exportação

| Formato | Uso Principal | Encoding |
|---------|---------------|----------|
| JSON | APIs modernas, integrações | UTF-8 |
| CSV | Análise de dados, Excel | UTF-8 BOM |
| XML | Core banking legacy | UTF-8 |
| TXT Posicional | Mainframes | ISO-8859-1 |
| Parquet | Data lakes | N/A |

```python
# Exemplo de export para diferentes formatos
class ExportService:

    def to_json(self, data: dict) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2)

    def to_csv(self, data: dict) -> str:
        # Flatten nested structure
        flat = self.flatten_dict(data)
        return self.dict_to_csv(flat)

    def to_xml(self, data: dict, root: str = "contrato") -> str:
        return dicttoxml(data, custom_root=root, attr_type=False)

    def to_positional(self, data: dict, layout: dict) -> str:
        """Formato posicional para mainframes"""
        line = ""
        for field, config in layout.items():
            value = str(data.get(field, ""))
            if config['align'] == 'right':
                value = value.zfill(config['size'])
            else:
                value = value.ljust(config['size'])
            line += value[:config['size']]
        return line
```

---

## 7. Funcionalidade de Chat

### 7.1 Arquitetura Client-Side

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUXO DE CHAT (CLIENT-SIDE STORAGE)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   1. PROCESSAMENTO INICIAL                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│   │  Documento  │────▶│  Ultrathink │────▶│  Resposta   │              │
│   │             │     │    API      │     │  + chunks   │              │
│   └─────────────┘     └─────────────┘     │  + embeds   │              │
│                                           └──────┬──────┘              │
│                                                  │                      │
│   2. STORAGE LOCAL                               │                      │
│                                                  ▼                      │
│                              ┌─────────────────────────────┐           │
│                              │      SQLite + Qdrant        │           │
│                              │      (no cliente)           │           │
│                              └──────────────┬──────────────┘           │
│                                             │                           │
│   3. CHAT                                   │                           │
│   ┌─────────────┐                           │                           │
│   │  Usuário    │     ┌─────────────┐       │                           │
│   │  pergunta   │────▶│  Busca      │◀──────┘                           │
│   └─────────────┘     │  vetorial   │                                   │
│                       │  local      │                                   │
│                       └──────┬──────┘                                   │
│                              │                                          │
│                              ▼                                          │
│                       ┌─────────────┐     ┌─────────────┐              │
│                       │  Contexto   │────▶│  Ultrathink │              │
│                       │  relevante  │     │  Chat API   │              │
│                       └─────────────┘     └──────┬──────┘              │
│                                                  │                      │
│                                                  ▼                      │
│                                           ┌─────────────┐              │
│                                           │  Resposta   │              │
│                                           │  + citações │              │
│                                           └─────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Chat Package Response

```json
{
  "extraction_result": {
    "data": {...},
    "confidence": 0.94
  },

  "chat_package": {
    "document_id": "doc_xyz789",

    "chunks": [
      {
        "id": "chunk_001",
        "content": "O valor total financiado é de R$ 50.000,00...",
        "page": 1,
        "bbox": [100, 200, 500, 250],
        "metadata": {
          "section": "quadro_resumo",
          "field_types": ["valor_financiado", "parcelas"]
        }
      },
      {
        "id": "chunk_002",
        "content": "Taxa de juros de 1,89% ao mês, equivalente a...",
        "page": 1,
        "bbox": [100, 260, 500, 310],
        "metadata": {
          "section": "condicoes_financeiras",
          "field_types": ["taxa_juros", "cet"]
        }
      }
    ],

    "embeddings": [
      {
        "chunk_id": "chunk_001",
        "vector": [0.123, -0.456, 0.789, ...]
      },
      {
        "chunk_id": "chunk_002",
        "vector": [0.234, -0.567, 0.890, ...]
      }
    ],

    "metadata": {
      "total_chunks": 24,
      "embedding_model": "text-embedding-3-small",
      "embedding_dimensions": 1536
    }
  }
}
```

### 7.3 Casos de Uso do Chat

| Caso de Uso | Exemplo de Pergunta | Usuário |
|-------------|---------------------|---------|
| Atendimento ao cliente | "Qual a taxa de juros deste contrato?" | Atendente |
| Cobrança | "Qual o valor da parcela em atraso?" | Cobrador |
| Jurídico | "Quais as cláusulas de rescisão?" | Advogado |
| Compliance | "O CET está correto conforme regulação?" | Auditor |
| Busca por contrato | "Encontre contratos com taxa acima de 2%" | Analista |

---

## 8. Dados para Treinamento de Modelos

### 8.1 Estratégia de Coleta

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NÍVEIS DE COLETA DE DADOS                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  NÍVEL 1: SEMPRE COLETADO (Não sensível)                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                               │
│  • Métricas de processamento (tempo, páginas)                          │
│  • Tipos de documento detectados (agregado)                            │
│  • Distribuição de confiança por campo                                 │
│  • Templates/layouts identificados (estrutura)                         │
│  • Metadados de PDF (software, versão)                                 │
│                                                                         │
│  NÍVEL 2: OPT-IN ANONIMIZADO                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                       │
│  • Imagens de trechos com dados substituídos                           │
│  • Bounding boxes de campos (posição, não conteúdo)                    │
│  • Correções de usuário (campo X errado → correto)                     │
│  • Scores de anomalia (sem dados originais)                           │
│                                                                         │
│  NÍVEL 3: ACORDO ESPECIAL                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                          │
│  • Documentos fraudulentos confirmados                                 │
│  • Amostras para validação de novos modelos                           │
│  • Benchmark datasets                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Anonimização de Documentos

```python
class DocumentAnonymizer:
    """Anonimiza documento para uso em treinamento"""

    def anonymize_for_training(
        self,
        image: np.ndarray,
        extracted_data: dict
    ) -> dict:
        anonymized = image.copy()

        # 1. Substituir números por valores fake
        for field in extracted_data["fields"]:
            if field["type"] in ["cpf", "cnpj", "valor", "taxa", "telefone"]:
                bbox = field["bbox"]
                fake_value = self.generate_fake_value(
                    field["type"],
                    field["value"]
                )
                anonymized = self.render_text_in_bbox(
                    anonymized, bbox, fake_value
                )

        # 2. Borrar nomes e assinaturas
        for field in extracted_data["fields"]:
            if field["type"] in ["nome", "assinatura"]:
                bbox = field["bbox"]
                anonymized = self.blur_region(anonymized, bbox)

        return {
            "image": anonymized,
            "layout": self.extract_layout_only(extracted_data),
            "field_types": [f["type"] for f in extracted_data["fields"]],
            "template_signature": self.compute_template_signature(extracted_data)
        }

    def generate_fake_value(self, field_type: str, original: str) -> str:
        """Gera valor fake mantendo formato"""
        from faker import Faker
        fake = Faker('pt_BR')

        if field_type == "cpf":
            return fake.cpf()
        elif field_type == "cnpj":
            return fake.cnpj()
        elif field_type == "valor":
            magnitude = len(original.replace(".", "").replace(",", ""))
            return f"R$ {random.randint(1000, 100000):,.2f}"
        elif field_type == "taxa":
            return f"{random.uniform(0.5, 3.0):.2f}%"
        elif field_type == "telefone":
            return fake.phone_number()

        return "***ANONIMIZADO***"
```

### 8.3 Active Learning

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       ACTIVE LEARNING LOOP                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Documento com baixa confiança (< 85%)                                │
│                     │                                                   │
│                     ▼                                                   │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                                                                 │  │
│   │   Campo: "Taxa de Juros Mensal"                                │  │
│   │                                                                 │  │
│   │   Valor extraído: [1,89%]  Confiança: 67%                      │  │
│   │                                                                 │  │
│   │   ┌─────────────────────────────────────────┐                  │  │
│   │   │  [imagem do trecho do documento]        │                  │  │
│   │   └─────────────────────────────────────────┘                  │  │
│   │                                                                 │  │
│   │   O valor está correto?                                        │  │
│   │   ( ) Sim, está correto                                        │  │
│   │   ( ) Não, o correto é: [___________]                          │  │
│   │   ( ) Campo não existe no documento                            │  │
│   │                                                                 │  │
│   │   [ ] Permitir uso para melhorar o modelo                      │  │
│   │                                                                 │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.4 Dados Úteis por Tipo de Modelo

| Modelo | Dado Útil | Como Coletar | Privacidade |
|--------|-----------|--------------|-------------|
| **OCR Manuscrito** | Imagens de texto | Crops anonimizados | Borrar dados |
| **OCR Manuscrito** | Correções de OCR | Feedback de usuário | Só texto corrigido |
| **Extração** | Posição dos campos | Automático | Não sensível |
| **Extração** | Tipos de campo | Labels anotados | Não sensível |
| **Extração** | Correções | Feedback humano | Anonimizar valores |
| **Fraude** | Docs fraudulentos | Cliente reporta | Muito sensível |
| **Fraude** | Docs legítimos | Cliente confirma | Muito sensível |
| **Fraude** | Metadados PDF | Automático | Não sensível |

### 8.5 Federated Learning (Futuro)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FEDERATED LEARNING (FASE 2)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   CLIENTE A              CLIENTE B              CLIENTE C               │
│   ┌─────────┐           ┌─────────┐           ┌─────────┐              │
│   │ Dados   │           │ Dados   │           │ Dados   │              │
│   │ Locais  │           │ Locais  │           │ Locais  │              │
│   └────┬────┘           └────┬────┘           └────┬────┘              │
│        │                     │                     │                    │
│        ▼                     ▼                     ▼                    │
│   ┌─────────┐           ┌─────────┐           ┌─────────┐              │
│   │ Treino  │           │ Treino  │           │ Treino  │              │
│   │ Local   │           │ Local   │           │ Local   │              │
│   └────┬────┘           └────┬────┘           └────┬────┘              │
│        │                     │                     │                    │
│        │    Gradientes       │     Gradientes      │                    │
│        │    (não dados)      │     (não dados)     │                    │
│        └─────────────────────┼─────────────────────┘                    │
│                              ▼                                          │
│                    ┌──────────────────┐                                │
│                    │   ULTRATHINK     │                                │
│                    │   Agregador      │                                │
│                    │                  │                                │
│                    │ Combina updates  │                                │
│                    │ sem ver dados    │                                │
│                    └────────┬─────────┘                                │
│                             │                                           │
│                             ▼                                           │
│                    ┌──────────────────┐                                │
│                    │  Modelo Global   │                                │
│                    │  Atualizado      │                                │
│                    └──────────────────┘                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Certificado de Processamento

### 9.1 Estrutura do Certificado

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│               CERTIFICADO DE PROCESSAMENTO SEGURO                       │
│                         ULTRATHINK                                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ID: proc_abc123def456                                                │
│   Data: 2026-01-17T14:32:15Z                                           │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                         │
│   DOCUMENTO PROCESSADO                                                 │
│   Hash (SHA-256): a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2        │
│                                                                         │
│   RESULTADO DA EXTRAÇÃO                                                │
│   Hash (SHA-256): 9f8e7d6c5b4a3z2y1x0w9v8u7t6s5r4q3p2o1n0m9l8k7        │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                         │
│   DECLARAÇÃO DE NÃO-RETENÇÃO                                           │
│                                                                         │
│   Declaramos que:                                                       │
│   ✓ O documento original foi deletado imediatamente após               │
│     processamento, com overwrite seguro de 3 passes                    │
│   ✓ Os dados extraídos não foram armazenados em nossos                │
│     servidores                                                          │
│   ✓ Apenas os hashes criptográficos e logs de processamento           │
│     (sem dados pessoais) foram retidos para fins de auditoria         │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                         │
│   VERIFICAÇÃO                                                           │
│   Este certificado pode ser verificado em:                             │
│   https://api.ultrathink.com.br/v1/verify/proc_abc123def456            │
│                                                                         │
│   Assinatura Digital: sig_xyz789...                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 API de Verificação

```json
// GET /v1/verify/proc_abc123def456
{
  "valid": true,
  "certificate": {
    "id": "proc_abc123def456",
    "timestamp": "2026-01-17T14:32:15Z",
    "document_hash": "sha256:a1b2c3d4...",
    "result_hash": "sha256:9f8e7d6c...",
    "retention_status": {
      "document_retained": false,
      "data_retained": false,
      "deletion_confirmed": true,
      "deletion_method": "secure_overwrite_3_pass"
    },
    "processing_metadata": {
      "document_type": "emprestimo_pessoal",
      "pages_processed": 4,
      "processing_time_ms": 2341,
      "confidence": 0.94
    }
  },
  "signature": "sig_xyz789...",
  "signature_valid": true
}
```

---

## 10. Integrações Empresariais

### 10.1 Matriz de Integrações

```
SISTEMAS BANCÁRIOS
━━━━━━━━━━━━━━━━━━

┌─────────────────┬──────────────┬───────────────┬─────────────────┐
│    Sistema      │   Formato    │   Protocolo   │   Prioridade    │
├─────────────────┼──────────────┼───────────────┼─────────────────┤
│ Core Banking    │ XML, TXT     │ SFTP, MQ      │ P0              │
│ (legacy)        │ posicional   │               │                 │
├─────────────────┼──────────────┼───────────────┼─────────────────┤
│ CRM             │ JSON         │ REST API      │ P1              │
│ (Salesforce)    │              │               │                 │
├─────────────────┼──────────────┼───────────────┼─────────────────┤
│ Data Lake       │ Parquet,     │ S3, Kafka     │ P1              │
│                 │ JSON         │               │                 │
├─────────────────┼──────────────┼───────────────┼─────────────────┤
│ GED/ECM         │ JSON +       │ REST API      │ P2              │
│ (OnBase)        │ metadata     │               │                 │
├─────────────────┼──────────────┼───────────────┼─────────────────┤
│ RPA             │ JSON, CSV    │ REST API      │ P2              │
│ (UiPath)        │              │               │                 │
├─────────────────┼──────────────┼───────────────┼─────────────────┤
│ Mainframe       │ TXT          │ SFTP, MQ      │ P3              │
│                 │ posicional   │               │                 │
└─────────────────┴──────────────┴───────────────┴─────────────────┘
```

### 10.2 SDK e Bibliotecas

```python
# Python SDK
from ultrathink import UltrathinkClient, LocalStorage

client = UltrathinkClient(
    api_key="uk_xxxxx",
    storage=LocalStorage(
        path="/data/ultrathink/documents.db",
        encryption_key=os.environ["ENCRYPTION_KEY"]
    )
)

# Processar documento
result = client.extract(
    file="contrato.pdf",
    document_type="emprestimo_pessoal",
    include_chat_package=True
)

# Chat local
chat = client.chat(document_id=result.id)
response = chat.ask("Qual a taxa de juros?")
print(response.answer)
print(response.citations)
```

```javascript
// Node.js SDK
const { UltrathinkClient } = require('@ultrathink/sdk');

const client = new UltrathinkClient({
  apiKey: 'uk_xxxxx',
  storage: {
    type: 'sqlite',
    path: './data/documents.db',
    encryptionKey: process.env.ENCRYPTION_KEY
  }
});

// Processar documento
const result = await client.extract({
  file: fs.readFileSync('contrato.pdf'),
  documentType: 'emprestimo_pessoal',
  includeChatPackage: true
});

// Chat
const answer = await client.chat(result.id, "Qual o CET?");
```

---

## 11. Modelo de Preços

### 11.1 Planos para Bancos

| Plano | Volume/mês | Extração | Chat | Preço |
|-------|------------|----------|------|-------|
| **Starter** | 1.000 contratos | ✅ | 50 sessões | R$ 2.990/mês |
| **Professional** | 5.000 contratos | ✅ | 200 sessões | R$ 9.990/mês |
| **Enterprise** | 20.000+ contratos | ✅ | Ilimitado | Sob consulta |

### 11.2 Add-ons

| Add-on | Preço |
|--------|-------|
| Integração Core Banking | R$ 5.000 setup + R$ 500/mês |
| SLA 99.9% | +30% do plano |
| On-premise deployment | Sob consulta |
| Documentoscopia (anti-fraude) | +R$ 0,50/documento |
| Treinamento customizado | R$ 15.000 |

### 11.3 Planos para Hospitais

| Plano | Volume/mês | Preço |
|-------|------------|-------|
| **Básico** | 10.000 laudos | R$ 4.990/mês |
| **Profissional** | 50.000 laudos | R$ 14.990/mês |
| **Enterprise** | 200.000+ laudos | Sob consulta |

---

## 12. Requisitos Não-Funcionais

### 12.1 Performance

| Métrica | Target | Crítico |
|---------|--------|---------|
| Latência (documento único) | < 3s | < 5s |
| Latência (batch, por doc) | < 1s | < 2s |
| Throughput | 100 docs/min | 50 docs/min |
| Disponibilidade | 99.9% | 99.5% |

### 12.2 Segurança

| Requisito | Implementação |
|-----------|----------------|
| Criptografia em trânsito | TLS 1.3 |
| Criptografia em repouso | AES-256 |
| Autenticação | API Keys + OAuth 2.0 |
| Auditoria | Logs imutáveis 5 anos |
| Compliance | LGPD, SOC 2 (roadmap) |

### 12.3 Acurácia

| Tipo de Documento | Target Acurácia | Mínimo |
|-------------------|-----------------|--------|
| Contratos impressos | 98% | 95% |
| Contratos manuscritos | 90% | 85% |
| Laudos manuscritos | 88% | 85% |
| NF-e | 99% | 98% |
| CNH/RG | 97% | 95% |

---

## 13. Roadmap

### Fase 1: Medical Reports MVP (8-10 semanas)
- [x] OCR de laudos manuscritos
- [x] Pipeline TrOCR + PaddleOCR
- [ ] API v1 básica
- [ ] Interface de demonstração
- [ ] Cliente piloto (hospital)

### Fase 2: Banking Contracts MVP (8-10 semanas)
- [ ] Templates: Empréstimo Pessoal, Consignado
- [ ] Schema completo de extração
- [ ] Batch API com webhooks
- [ ] Zero-retention architecture
- [ ] Certificado de processamento
- [ ] Admin interface

### Fase 3: Chat on Contracts (4-6 semanas)
- [ ] RAG com client-side storage
- [ ] Chat package na API
- [ ] Interface web para funcionários do banco
- [ ] Busca por número de contrato
- [ ] Histórico de conversas

### Fase 4: Contract Type Expansion (6-8 semanas)
- [ ] Financiamento de Veículos
- [ ] Cartões de Crédito
- [ ] Capital de Giro (PJ)
- [ ] Templates específicos por banco (Itaú, BB, Bradesco)

### Fase 5: Enterprise Integrations (4-6 semanas)
- [ ] Conectores Core Banking
- [ ] Export multi-formato (XML, TXT posicional)
- [ ] Webhooks avançados
- [ ] SSO/SAML
- [ ] On-premise deployment option

### Fase 6: Documentoscopia (6-8 semanas)
- [ ] Detecção de adulterações
- [ ] Validação de assinaturas
- [ ] Análise de metadados PDF
- [ ] Score de risco de fraude
- [ ] Dashboard de alertas

### Fase 7: Training Data & Model Improvement (Contínuo)
- [ ] Active learning pipeline
- [ ] Opt-in data collection
- [ ] Federated learning (pesquisa)
- [ ] Benchmark datasets

---

## 14. Métricas de Sucesso

### 14.1 KPIs de Produto

| Métrica | Target 6 meses | Target 12 meses |
|---------|----------------|-----------------|
| Clientes pagantes | 5 | 20 |
| MRR | R$ 50.000 | R$ 200.000 |
| Documentos processados/mês | 50.000 | 500.000 |
| NPS | > 50 | > 60 |
| Churn mensal | < 5% | < 3% |

### 14.2 KPIs Técnicos

| Métrica | Target |
|---------|--------|
| Uptime | 99.9% |
| Latência P95 | < 3s |
| Taxa de erro | < 0.1% |
| Acurácia média | > 95% |

### 14.3 KPIs de Compliance

| Métrica | Target |
|---------|--------|
| Incidentes de dados | 0 |
| Certificados verificados | 100% disponíveis |
| Tempo de resposta LGPD | < 72h |

---

## 15. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Acurácia insuficiente para manuscritos | Média | Alto | Ensemble de modelos, active learning |
| Concorrência de big techs | Alta | Médio | Especialização Brasil, preço, suporte |
| Mudanças regulatórias LGPD | Baixa | Alto | Arquitetura zero-retention nativa |
| Dificuldade de integração com legados | Alta | Médio | SDKs multi-formato, consultoria |
| Custo de GPU | Média | Médio | Modal serverless, otimização de batch |

---

## 16. Configurações de Privacidade (Interface do Cliente)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│              CONFIGURAÇÕES DE PRIVACIDADE E TREINAMENTO                 │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ARMAZENAMENTO DE DADOS                                                │
│  ───────────────────────                                               │
│                                                                         │
│  (•) Apenas local (recomendado para compliance)                        │
│      Todos os documentos e dados extraídos ficam apenas                │
│      no seu ambiente. Ultrathink não armazena nenhum dado.             │
│                                                                         │
│  ( ) Local + cache temporário (24h)                                    │
│      Permite reprocessamento sem re-upload por 24 horas.               │
│                                                                         │
│                                                                         │
│  CONTRIBUIÇÃO PARA MELHORIA DOS MODELOS                                │
│  ───────────────────────────────────────                               │
│                                                                         │
│  [ ] Contribuir com métricas anônimas                                  │
│      Tempo de processamento, tipos de documento, taxas de              │
│      confiança. Nenhum dado pessoal ou conteúdo é enviado.             │
│                                                                         │
│  [ ] Contribuir com feedback de correções                              │
│      Quando você corrige um campo extraído incorretamente,            │
│      a correção (anonimizada) ajuda a melhorar o modelo.               │
│                                                                         │
│  [ ] Participar do programa de melhoria de anti-fraude                 │
│      Compartilhar padrões de documentos fraudulentos                   │
│      detectados para melhorar a detecção global.                       │
│      * Requer acordo adicional de compartilhamento de dados            │
│                                                                         │
│                                          [Salvar Configurações]        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 17. Glossário

| Termo | Definição |
|-------|-----------|
| **CET** | Custo Efetivo Total - taxa que representa o custo total do crédito |
| **CDC** | Crédito Direto ao Consumidor |
| **Consignado** | Empréstimo com desconto em folha de pagamento |
| **Core Banking** | Sistema central de processamento bancário |
| **LGPD** | Lei Geral de Proteção de Dados |
| **NF-e** | Nota Fiscal Eletrônica |
| **OCR** | Optical Character Recognition |
| **RAG** | Retrieval-Augmented Generation |
| **SFH/SFI** | Sistema Financeiro de Habitação / Imobiliário |
| **Zero Retention** | Política de não armazenar dados do cliente |

---

## 18. Anexos

### A. Diferencial Competitivo

| Aspecto | Ultrathink | Instabase | Google Doc AI |
|---------|------------|-----------|-------------|
| Especialização Brasil | ✅ Nativo | ❌ Genérico | ❌ Genérico |
| LGPD Native | ✅ Zero retention | ⚠️ Configurável | ⚠️ Configurável |
| Preço | R$ 2.990+ | USD 10.000+ | Pay-per-use |
| Complexidade | Baixa | Alta | Média |
| Suporte local | ✅ Português | ❌ Inglês | ⚠️ Limitado |
| On-premise | ✅ Disponível | ✅ Enterprise | ❌ Cloud only |

### B. Próximos Passos

1. **Para Cliente Bancário:**
   - Entender volume mensal de contratos
   - Identificar tipos prioritários (Consignado? CDC? PJ?)
   - Mapear sistemas de destino (Core banking? CRM? Data lake?)
   - Obter amostras anonimizadas para mapeamento de campos
   - Preparar proposta comercial

2. **Desenvolvimento:**
   - Implementar secure deletion com overwrite
   - Construir audit trail baseado em hashes
   - Desenvolver batch processing com webhooks
   - Criar formato de chat package
   - Testar SDKs Python e Node.js

3. **Compliance:**
   - Documentar políticas de retenção
   - Preparar DPA (Data Processing Agreement)
   - Iniciar processo SOC 2

---

**Documento preparado por:** Ultrathink Team  
**Última atualização:** Janeiro 2026  
**Versão:** 1.0
