# Contrackt — Relatório de Arquitetura para Produção

**Versão:** 1.0
**Data:** Julho 2025
**Autor:** Revisão de Arquitetura Sênior
**Escopo:** POC → Produção com milhões de execuções, multi-tenant, compliance LGPD

---

## Índice

1. [Decisões de Storage: Filesystem vs S3](#1-decisões-de-storage-filesystem-vs-s3)
2. [Decisões de Fila: Redis Streams vs Celery vs Kafka](#2-decisões-de-fila-redis-streams-vs-celery-vs-kafka)
3. [Arquitetura Multi-Tenant e Isolamento de Dados](#3-arquitetura-multi-tenant-e-isolamento-de-dados)
4. [Kubernetes: Orquestração e Escalabilidade](#4-kubernetes-orquestração-e-escalabilidade)
5. [Segurança e Compliance em Produção](#5-segurança-e-compliance-em-produção)
6. [Arquitetura Final Consolidada](#6-arquitetura-final-consolidada)
7. [Estimativa de Custos](#7-estimativa-de-custos)
8. [Roadmap de Implementação](#8-roadmap-de-implementação)

---

## 1. Decisões de Storage: Filesystem vs S3

### Por que NÃO usar filesystem em produção

O filesystem local falha em produção com Kubernetes por razões fundamentais:

| Problema | Impacto |
|----------|---------|
| Pods são efêmeros | Pod morre → PDF desaparece → job perdido |
| Workers em nós diferentes | Worker no nó B não acessa arquivo do nó A |
| Escalabilidade horizontal | Impossível distribuir trabalho sem storage compartilhado |
| Sem lifecycle policies | Precisa de cron manual para limpar arquivos antigos |
| Sem audit trail de acesso | Não sabe quem acessou o quê |
| Sem replicação | Disco falha → dados perdidos |

### Por que S3/MinIO é a escolha correta

| Vantagem | Detalhe |
|----------|---------|
| **Acesso entre nós** | Qualquer worker em qualquer nó acessa o PDF |
| **Lifecycle policies** | TTL nativo — S3 deleta automaticamente após N minutos |
| **Server-Side Encryption** | SSE-S3 (AES-256) ou SSE-KMS (chave gerenciada) — sem código extra |
| **Versionamento** | Audit trail de todas as operações no objeto |
| **Durabilidade** | 99.999999999% (11 noves) no S3 |
| **Pre-signed URLs** | Worker gera URL temporária para acessar o PDF — sem expor credenciais |
| **Per-tenant prefixes** | `s3://contrackt/{tenant_id}/{job_id}.enc` — isolamento natural |
| **MinIO para on-premise** | 100% compatível com S3, roda em Docker/K8s |

### Fluxo com S3

```
Upload PDF → API calcula SHA-256 → Cifra com Fernet
  → PUT s3://contrackt-tmp/{tenant_id}/{job_id}.enc
  → Lifecycle rule: delete after 10 minutes
  → Publica mensagem na fila com { job_id, tenant_id, s3_key }

Worker recebe mensagem
  → GET s3://contrackt-tmp/{tenant_id}/{job_id}.enc (pre-signed URL)
  → Decifra em memória → OCR → Resultado
  → DELETE s3://contrackt-tmp/{tenant_id}/{job_id}.enc
  → gc.collect()
```

### POC vs Produção

| Fase | Storage | Por quê |
|------|---------|---------|
| POC (local) | MinIO em Docker | Mesmo código do S3, roda local |
| Produção AWS | S3 com SSE-KMS | Gerenciado, durável, lifecycle |
| Produção on-premise | MinIO em K8s | S3-compatível, controle total |

**Decisão: MinIO (POC) → S3 (produção). Código idêntico via boto3/aioboto3.**

---

## 2. Decisões de Fila: Redis Streams vs Celery vs Kafka

### Análise comparativa

| Critério | Celery + Redis | Redis Streams | Kafka | NATS JetStream |
|----------|---------------|---------------|-------|----------------|
| **Complexidade** | Alta (15+ deps) | Baixa (0 deps extras) | Média-Alta | Média |
| **Durabilidade** | Redis = volátil | Redis = volátil | Disco = durável | Disco = durável |
| **Throughput** | ~50K msg/s | ~100K msg/s | ~1M msg/s | ~500K msg/s |
| **Particionamento** | Não nativo | Não nativo | Nativo por key | Nativo |
| **Replay de mensagens** | Não | Limitado (XRANGE) | Sim (offset replay) | Sim |
| **Dead letter queue** | Manual | Manual (XCLAIM) | Nativo | Nativo |
| **Consumer groups** | Via routing | Nativo | Nativo | Nativo |
| **Ordenação por tenant** | Não garantida | Não garantida | Garantida por partition | Garantida |
| **Observabilidade** | Flower (frágil) | XINFO, XPENDING | Kafka UI, métricas JMX | NATS dashboard |
| **Operação** | Complexa | Simples | Complexa (ou managed) | Simples |
| **Memory leaks** | Conhecidos com libs pesadas | Não aplicável | Não aplicável | Não aplicável |

### Por que NÃO usar Celery

Celery é overengineering para esse projeto:

- **Pesado**: traz consigo Kombu, Billiard, Vine, Amqp — um ecossistema inteiro de ~15 dependências transitivas
- **Memory leaks conhecidos** com bibliotecas pesadas como PaddleOCR
- **Configuração complexa**: serializers, result backends, prefork vs gevent, signals
- **Debug difícil**: quando dá erro no Celery, logs em 3 lugares diferentes, stacktraces truncados
- **Já temos Redis** no stack — Redis Streams faz o mesmo trabalho com zero dependência extra

### Recomendação por fase

#### POC: Redis Streams

- Já temos Redis no stack
- Zero dependências extras
- Consumer groups nativos para distribuir trabalho
- XPENDING para monitorar mensagens não processadas
- XCLAIM para recuperar mensagens de workers mortos
- Suficiente para ~500K jobs/dia

```
XADD contrackt:jobs * tenant_id abc job_id 123 s3_key tenant/abc/123.enc
XREADGROUP GROUP workers consumer-1 COUNT 1 BLOCK 5000 STREAMS contrackt:jobs >
XACK contrackt:jobs workers <message-id>
```

#### Produção (milhões/dia): Kafka

Kafka é a escolha certa para produção com milhões de execuções por três razões que nenhuma alternativa resolve tão bem:

**1. Particionamento por tenant_id = isolamento na fila**

```
Topic: contrackt.jobs (12 partições)

Mensagem { tenant_id: "banco-x", job_id: "123", ... }
  → Kafka roteia para partição = hash("banco-x") % 12
  → Todas as mensagens do banco-x vão para a MESMA partição
  → Garantia de ordenação por cliente
  → Consumer group processa em paralelo entre partições
```

Isso significa que o Banco X nunca tem seus jobs misturados com o Hospital Y na mesma fila de processamento.

**2. Replay e auditoria**

```
Se um worker processou errado um lote às 14h:
  → kafka-consumer-groups --reset-offsets --to-datetime 2026-01-15T14:00:00
  → Reprocessa tudo a partir daquele momento
  → Sem perder nenhuma mensagem
```

Redis Streams não consegue fazer isso de forma confiável em escala.

**3. Dead Letter Topic nativo**

```
Topic: contrackt.jobs          (jobs normais)
Topic: contrackt.jobs.dlq      (jobs que falharam 3x)
Topic: contrackt.jobs.audit    (log de todas as transições)

Fluxo: jobs → worker tenta 3x → falha → vai para DLQ
       → alerta no Slack/PagerDuty → engenheiro investiga
       → corrige → republica no topic original
```

#### Migração Redis Streams → Kafka

O código do worker é quase idêntico. A abstração é:

```python
# POC (Redis Streams):
consumer = RedisStreamConsumer(stream="contrackt:jobs", group="workers")
async for message in consumer:
    await process(message)
    await consumer.ack(message)

# Produção (Kafka):
consumer = KafkaConsumer(topic="contrackt.jobs", group="workers")
async for message in consumer:
    await process(message)
    await consumer.commit(message)
```

Se o worker depender de uma interface `MessageConsumer`, a troca é uma linha de configuração.

**Decisão: Redis Streams (POC) → Kafka managed/MSK (produção). Interface abstraída para troca transparente.**

---

## 3. Arquitetura Multi-Tenant e Isolamento de Dados

### Por que NÃO uma instância por cliente

| Problema | Impacto |
|----------|---------|
| Custo | 20 clientes × infra completa = 20× o custo |
| Operação | 20 deploys, 20 monitoramentos, 20 upgrades |
| Ociosidade | A maioria dos clientes usa 5% da capacidade 95% do tempo |
| Escalabilidade | Não escala — cada novo cliente é um projeto de infra |

Uma instância por cliente só faz sentido para **on-premise dedicado** (ex: banco Tier 1 que exige tudo dentro do datacenter dele). Mesmo assim, é uma exceção, não a regra.

### Modelo correto: Multi-tenant com isolamento lógico em 7 camadas

#### Camada 1 — API (autenticação e roteamento)

```
Request → Header: X-API-Key: uk_abc123
  → Middleware valida API Key
  → Resolve tenant_id a partir da key
  → Injeta tenant_id no contexto do request
  → TODAS as operações downstream recebem tenant_id
  → Se API Key inválida → 401 (sem revelar se a key existe)
```

Cada API Key é vinculada a exatamente um tenant. O tenant_id é um UUID que nunca é exposto ao cliente — ele só conhece sua API Key.

#### Camada 2 — Fila (Kafka particionado)

```
Topic: contrackt.jobs
  Partition key: tenant_id

Resultado:
  - Tenant A → partições 0, 3, 7 (determinístico por hash)
  - Tenant B → partições 1, 4, 8
  - Mensagens de A NUNCA são lidas por consumer de B
  - Kafka ACLs restringem acesso por consumer group
```

#### Camada 3 — Storage (S3 com prefixos isolados)

```
Bucket: contrackt-documents
  ├── tenant-a/
  │   ├── job-001.enc
  │   └── job-002.enc
  ├── tenant-b/
  │   ├── job-003.enc
  │   └── job-004.enc

IAM Policy por tenant:
  {
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
    "Resource": "arn:aws:s3:::contrackt-documents/tenant-a/*"
  }

Worker do tenant-a NÃO CONSEGUE acessar tenant-b/ mesmo com bug no código.
```

#### Camada 4 — Banco de dados (Row-Level Security)

```sql
-- Ativar RLS no PostgreSQL
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Política: cada query só vê dados do seu tenant
CREATE POLICY tenant_isolation_jobs ON jobs
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

CREATE POLICY tenant_isolation_audit ON audit_logs
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Na aplicação, antes de cada query:
SET app.current_tenant = '<tenant-uuid>';

-- Agora: SELECT * FROM jobs; ← retorna APENAS jobs do tenant atual
-- Mesmo que o código tenha bug e não filtre, RLS bloqueia.
```

Row-Level Security é a última linha de defesa. Mesmo que a aplicação tenha um bug que esqueça de filtrar por tenant, o PostgreSQL bloqueia o acesso cruzado no nível do engine.

#### Camada 5 — Criptografia (chaves por tenant)

```
Envelope Encryption com AWS KMS (ou Vault):

  Master Key (KMS)
    └── Tenant A Data Key (gerada por KMS, armazenada cifrada)
    │     └── Cifra PDFs do Tenant A
    └── Tenant B Data Key (gerada por KMS, armazenada cifrada)
          └── Cifra PDFs do Tenant B

Se por algum motivo impossível o PDF do Tenant A chegar ao Tenant B:
  → Tenant B não tem a Data Key do Tenant A
  → PDF é lixo binário indecifrável
  → Zero risco de vazamento de conteúdo
```

#### Camada 6 — Rede (Kubernetes Network Policies)

```yaml
# Workers só podem acessar: S3, Kafka, PostgreSQL, Redis
# Workers NÃO podem acessar: API pods, internet, outros namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: worker-network-policy
spec:
  podSelector:
    matchLabels:
      app: contrackt-worker
  policyTypes:
    - Ingress
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: contrackt-data
      ports:
        - port: 5432    # PostgreSQL
        - port: 6379    # Redis
        - port: 9092    # Kafka
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0  # S3 endpoint
      ports:
        - port: 443
  ingress: []  # Workers não recebem tráfego de ninguém
```

#### Camada 7 — Observabilidade (logs segregados)

```json
{
  "timestamp": "2026-07-15T14:30:00Z",
  "level": "info",
  "event": "ocr.page.completed",
  "tenant_id": "tenant-a-uuid",
  "job_id": "job-001-uuid",
  "request_id": "req-xyz-uuid",
  "page": 3,
  "confidence": 0.92,
  "processing_ms": 1200
}
```

Todo log carrega `tenant_id`. Dashboards filtrados por tenant. Alertas configurados por tenant. Um tenant com problemas não polui os logs de outro.

### Resumo: as 7 camadas de isolamento

```
┌─────────────────────────────────────────────────────────┐
│  Camada 7: Observabilidade (logs segregados por tenant) │
├─────────────────────────────────────────────────────────┤
│  Camada 6: Rede (NetworkPolicy — pods isolados)         │
├─────────────────────────────────────────────────────────┤
│  Camada 5: Criptografia (chave por tenant — envelope)   │
├─────────────────────────────────────────────────────────┤
│  Camada 4: Banco de dados (RLS — PostgreSQL)            │
├─────────────────────────────────────────────────────────┤
│  Camada 3: Storage (S3 prefixos + IAM policies)         │
├─────────────────────────────────────────────────────────┤
│  Camada 2: Fila (Kafka particionado por tenant_id)      │
├─────────────────────────────────────────────────────────┤
│  Camada 1: API (API Key → tenant_id, middleware)        │
└─────────────────────────────────────────────────────────┘

Para um dado do Tenant A chegar ao Tenant B, seria necessário
falhar TODAS as 7 camadas simultaneamente. Isso é, na prática,
impossível.
```

---

## 4. Kubernetes: Orquestração e Escalabilidade

### Topologia do cluster

```
K8s Cluster
├── Namespace: contrackt-api
│   ├── Deployment: api (FastAPI)
│   │   ├── HPA: 2-20 réplicas (baseado em requests/s)
│   │   ├── Resources: 1 vCPU, 2GB RAM por pod
│   │   └── Anti-affinity: spread entre nós
│   ├── Service: api-svc (ClusterIP)
│   └── Ingress: api-ingress (TLS termination, rate limiting)
│
├── Namespace: contrackt-workers
│   ├── Deployment: worker-cpu
│   │   ├── HPA: 2-50 réplicas (baseado em queue depth via KEDA)
│   │   ├── Resources: 4 vCPU, 8GB RAM por pod
│   │   ├── PaddleOCR model loaded on startup
│   │   └── Graceful shutdown: 60s termination grace
│   ├── Deployment: worker-gpu (quando necessário)
│   │   ├── HPA: 1-10 réplicas
│   │   ├── Resources: 4 vCPU, 16GB RAM, 1 GPU por pod
│   │   ├── Node selector: gpu=true
│   │   └── Tolerations: nvidia.com/gpu
│   └── NetworkPolicy: egress-only (S3, Kafka, Postgres, Redis)
│
├── Namespace: contrackt-data
│   ├── StatefulSet: redis (ou ElastiCache managed)
│   ├── StatefulSet: postgresql (ou RDS managed)
│   ├── StatefulSet: kafka (ou MSK managed)
│   └── StatefulSet: minio (se on-premise, senão usa S3)
│
└── Namespace: contrackt-monitoring
    ├── Deployment: prometheus
    ├── Deployment: grafana
    ├── Deployment: loki (logs)
    └── DaemonSet: promtail (coleta de logs)
```

### Autoscaling com KEDA

```
                    ┌──────────────┐
                    │ KEDA Scaler  │
                    │              │
                    │ Monitora:    │
                    │ • Queue depth│  ← Kafka consumer lag
                    │ • CPU usage  │  ← Prometheus metrics
                    │ • Memory     │
                    └──────┬───────┘
                           │
              Escala workers conforme demanda:
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
     │  Worker 1   │ │  Worker 2   │ │  Worker N   │
     │  (always on)│ │ (scaled up) │ │ (scaled up) │
     └─────────────┘ └─────────────┘ └─────────────┘

Regras:
  - Lag < 10 mensagens  → mínimo 2 workers (baseline)
  - Lag 10-100          → escala para 5-10 workers
  - Lag > 100           → escala para 20-50 workers
  - Lag = 0 por 5 min   → volta para 2 workers
  - Sempre manter mínimo 2 (redundância)
```

### Por que KEDA e não HPA nativo

O HPA nativo do Kubernetes só escala baseado em CPU/memória dos pods. Mas para OCR workers, o indicador correto é **profundidade da fila** (quantos jobs estão esperando). KEDA (Kubernetes Event-Driven Autoscaling) consegue escalar baseado em:

- Kafka consumer lag (mensagens não processadas)
- Redis stream length
- Métricas customizadas do Prometheus

### Estratégia de deploy

```yaml
# Rolling update: zero downtime
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Cria 1 pod novo antes de matar o antigo
    maxUnavailable: 0  # Nunca fica com menos pods que o mínimo

# Pod Disruption Budget: proteção contra maintenance
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: worker-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: contrackt-worker
```

### Node pools separados

```
Node Pool: api-nodes
  - Tipo: c5.large (2 vCPU, 4GB)
  - Tamanho: 2-5 nós
  - Uso: API pods apenas
  - Custo: ~$0.085/hr por nó

Node Pool: worker-cpu-nodes
  - Tipo: c5.2xlarge (8 vCPU, 16GB)
  - Tamanho: 2-20 nós (autoscale)
  - Uso: OCR workers (CPU)
  - Custo: ~$0.34/hr por nó

Node Pool: worker-gpu-nodes (quando necessário)
  - Tipo: g5.xlarge (4 vCPU, 16GB, 1x A10G)
  - Tamanho: 0-10 nós (autoscale, pode ir a zero)
  - Uso: OCR workers (GPU)
  - Custo: ~$1.006/hr por nó
```

---

## 5. Segurança e Compliance em Produção

### Criptografia fim-a-fim

```
Cliente → [TLS 1.3] → API Gateway/Ingress
  → [mTLS] → API Pod
    → [Fernet + per-tenant key] → S3 (SSE-KMS)
    → [TLS] → Kafka (in-transit encryption)
    → [SSL verify-full] → PostgreSQL
    → [TLS + AUTH] → Redis

Nenhum dado trafega em texto claro em nenhum ponto.
```

### Ciclo de vida de um PDF (compliance LGPD)

```
T+0s     PDF chega via HTTPS
T+0.01s  SHA-256 calculado (document_hash)
T+0.02s  PDF cifrado com Fernet (per-tenant key)
T+0.03s  PDF cifrado enviado ao S3 (SSE-KMS = dupla criptografia)
T+0.04s  audit_log: RECEIVED (document_hash, tenant_id, timestamp)
T+0.05s  Job publicado no Kafka (sem o PDF, apenas referência S3)
T+0.1s   del content; gc.collect() — PDF raw removido da RAM da API

T+1-4s   Worker baixa PDF do S3, decifra, processa OCR
T+4s     Resultado gerado, result_hash calculado
T+4.01s  audit_log: COMPLETED (document_hash, result_hash, confidence)
T+4.02s  PDF deletado do S3 (DELETE + lifecycle policy como backup)
T+4.03s  audit_log: PURGED (document_hash, deletion_confirmed=true)
T+4.04s  del content; gc.collect() — PDF removido da RAM do worker

T+4-14m  Cliente busca resultado (SSE ou polling)
T+14.01m audit_log: DELIVERED (result_hash, delivered_to=api_key_hash)
T+15m    Resultado expira do Redis (TTL automático)

Retenção permanente (PostgreSQL, 5 anos):
  ✓ document_hash (SHA-256)
  ✓ result_hash (SHA-256)
  ✓ audit_logs (sem PII)
  ✓ métricas de processamento

Retenção zero:
  ✗ PDF original
  ✗ Texto extraído
  ✗ Dados pessoais
  ✗ Conteúdo de qualquer natureza
```

### Secrets management

```
Produção: AWS Secrets Manager ou HashiCorp Vault
  - Encryption keys por tenant
  - Database credentials
  - API keys (hashed no banco, plain no Vault)
  - Kafka credentials
  - S3 credentials
  - Rotação automática a cada 90 dias

Kubernetes:
  - ExternalSecrets Operator sincroniza Vault → K8s Secrets
  - Pods montam secrets como volumes (não env vars — env vars
    aparecem em `kubectl describe pod`)
  - Secrets encrypted at rest no etcd (EncryptionConfiguration)
```

### Rate limiting e proteção contra abuso

```
3 camadas de rate limiting:

1. Ingress (nginx/Caddy):
   - 100 requests/min por IP
   - Proteção contra DDoS básico

2. API middleware:
   - 30 requests/min por API Key (extração)
   - 300 requests/min por API Key (consulta de status)
   - Resposta: 429 com Retry-After header

3. Kafka (backpressure):
   - Se consumer lag > 1000 → API retorna 503
   - "Sistema ocupado, tente em N segundos"
   - Protege os workers de sobrecarga
```

### Schema do PostgreSQL (audit trail + jobs)

```sql
-- Jobs: estado atual (mutável)
CREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    document_hash   VARCHAR(64) NOT NULL,
    result_hash     VARCHAR(64),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','processing','completed','failed')),
    filename        VARCHAR(255),
    file_size_bytes INTEGER,
    pages_total     SMALLINT,
    confidence_avg  REAL,
    processing_ms   INTEGER,
    error_message   TEXT,
    api_key_hash    VARCHAR(64) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);

-- Audit trail: histórico imutável (INSERT-only, sem UPDATE/DELETE)
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    job_id          UUID NOT NULL REFERENCES jobs(id),
    action          VARCHAR(20) NOT NULL
                    CHECK (action IN ('RECEIVED','PROCESSING','COMPLETED','FAILED','DELIVERED','PURGED')),
    document_hash   VARCHAR(64) NOT NULL,
    result_hash     VARCHAR(64),
    metadata        JSONB DEFAULT '{}',
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Row-Level Security
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_jobs ON jobs
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

CREATE POLICY tenant_isolation_audit ON audit_logs
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Índices essenciais
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_tenant ON jobs(tenant_id);
CREATE INDEX idx_jobs_doc_hash ON jobs(document_hash);
CREATE INDEX idx_audit_job ON audit_logs(job_id);
CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

---

## 6. Arquitetura Final Consolidada

### Diagrama completo (produção)

```
                    Internet
                       │
                       ▼
              ┌─────────────────┐
              │  AWS WAF / CDN  │  DDoS protection, geo-blocking
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Ingress      │  TLS termination, rate limit L1
              │  (nginx/Caddy)  │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼                         ▼
┌───────────────────┐    ┌───────────────────┐
│   API Pod (1..N)  │    │   API Pod (1..N)  │
│                   │    │                   │
│ • Auth middleware │    │ • Auth middleware │
│ • Tenant resolve │    │ • Tenant resolve │
│ • SHA-256 hash   │    │ • SHA-256 hash   │
│ • Encrypt + S3   │    │ • Encrypt + S3   │
│ • Publish Kafka  │    │ • Publish Kafka  │
│ • SSE streaming  │    │ • SSE streaming  │
│ • Audit log      │    │ • Audit log      │
└──────┬──────┬─────┘    └──────┬──────┬─────┘
       │      │                 │      │
       │      │    ┌────────────┘      │
       ▼      ▼    ▼                   ▼
┌────────┐ ┌──────────┐ ┌───────────┐ ┌─────────────┐
│   S3   │ │  Kafka   │ │ PostgreSQL│ │    Redis    │
│ MinIO  │ │  (MSK)   │ │  (RDS)   │ │(ElastiCache)│
│        │ │          │ │          │ │             │
│PDF enc │ │Jobs topic│ │jobs table│ │Job status   │
│per-    │ │DLQ topic │ │audit_logs│ │Result cache │
│tenant  │ │Audit     │ │RLS on   │ │TTL 15min    │
│prefix  │ │topic     │ │          │ │             │
└───┬────┘ └────┬─────┘ └──────────┘ └─────────────┘
    │           │
    │      ┌────┘
    ▼      ▼
┌────────────────────────────────┐
│       Worker Pod (1..N)        │
│                                │
│  1. Consume from Kafka         │
│  2. Download PDF from S3       │
│  3. Decrypt (per-tenant key)   │
│  4. OCR (PaddleOCR adaptive)   │
│  5. Hash result (SHA-256)      │
│  6. Cache result in Redis      │
│  7. Update job in PostgreSQL   │
│  8. Insert audit_log           │
│  9. Delete PDF from S3         │
│ 10. Ack Kafka message          │
│ 11. gc.collect()               │
└────────────────────────────────┘
```

### Componentes e responsabilidades

| Componente | Responsabilidade | O que NÃO faz |
|------------|-----------------|---------------|
| **Ingress** | TLS, rate limit, routing | Não processa dados |
| **API Pods** | Autenticação, upload, hash, enqueue, SSE | Não faz OCR |
| **S3/MinIO** | PDF cifrado temporário, lifecycle delete | Não persiste permanente |
| **Kafka** | Fila durável, particionamento por tenant | Não armazena PDF |
| **PostgreSQL** | Jobs state, audit trail (5 anos, RLS) | Não guarda documento |
| **Redis** | Status do job, cache do resultado (TTL) | Não armazena PDF |
| **Workers** | OCR, cleanup, ack | Não expõem porta |
| **KEDA** | Autoscaling de workers por queue depth | — |

### Estrutura de pastas do projeto

```
contrackt/
├── app/
│   ├── main.py                     # FastAPI bootstrap + lifespan
│   ├── config.py                   # pydantic-settings (1 fonte de verdade)
│   ├── api/
│   │   └── v1/
│   │       ├── extract.py          # POST /v1/extract
│   │       ├── jobs.py             # GET  /v1/jobs/{id} + SSE stream
│   │       └── health.py           # GET  /v1/health (real checks)
│   ├── security/
│   │   ├── encryption.py           # Fernet encrypt/decrypt (per-tenant keys)
│   │   ├── hashing.py              # SHA-256 (document + result)
│   │   └── auth.py                 # API Key middleware → tenant_id
│   ├── models/
│   │   └── tables.py               # SQLAlchemy: jobs + audit_logs (com RLS)
│   ├── schemas/
│   │   └── responses.py            # Pydantic: JobCreated, JobStatus, etc
│   ├── services/
│   │   ├── ocr.py                  # PaddleOCR + zoom adaptativo (1.5x → 2x)
│   │   ├── storage.py              # S3/MinIO upload/download/delete
│   │   ├── queue.py                # Interface abstrata (Redis Streams / Kafka)
│   │   └── audit.py                # structlog → PostgreSQL
│   ├── worker.py                   # Consumer loop (Redis Streams ou Kafka)
│   └── db.py                       # SQLAlchemy async engine + session
├── migrations/                     # Alembic
├── k8s/                            # Kubernetes manifests
│   ├── api-deployment.yaml
│   ├── worker-deployment.yaml
│   ├── network-policies.yaml
│   ├── keda-scaledobject.yaml
│   └── ingress.yaml
├── Dockerfile                      # UM só, dois entrypoints (api / worker)
├── docker-compose.yml              # POC local (API + Worker + Redis + PG + MinIO)
├── .env.example
├── ARCHITECTURE.md                 # Este documento
└── pyproject.toml
```

---

## 7. Estimativa de Custos

### POC (desenvolvimento e testes)

| Componente | Recurso | Custo estimado/mês |
|------------|---------|-------------------|
| API + Workers | 1× c5.xlarge (4 vCPU, 8GB) | ~$125 |
| Redis | ElastiCache t3.micro | ~$15 |
| PostgreSQL | RDS t3.micro | ~$15 |
| MinIO | Roda na mesma instância | $0 |
| S3 | Poucos GB | ~$5 |
| **Total POC** | | **~$160/mês** |

### Produção — 100K jobs/dia (~1.2 jobs/s)

| Componente | Recurso | Custo estimado/mês |
|------------|---------|-------------------|
| API | 2× c5.large (HPA 2-5) | ~$125 |
| Workers CPU | 3× c5.2xlarge (HPA 3-10) | ~$750 |
| Kafka | MSK (3 brokers, m5.large) | ~$600 |
| PostgreSQL | RDS db.r5.large (multi-AZ) | ~$350 |
| Redis | ElastiCache r5.large | ~$200 |
| S3 | ~500GB throughput/mês | ~$50 |
| Monitoring | Prometheus + Grafana + Loki | ~$100 |
| **Total 100K/dia** | | **~$2,175/mês** |

### Produção — 1M jobs/dia (~12 jobs/s)

| Componente | Recurso | Custo estimado/mês |
|------------|---------|-------------------|
| API | 5× c5.xlarge (HPA 5-20) | ~$625 |
| Workers GPU | 5× g5.xlarge (HPA 5-15) | ~$3,650 |
| Kafka | MSK (6 brokers, m5.xlarge) | ~$1,800 |
| PostgreSQL | RDS db.r5.xlarge (multi-AZ) | ~$700 |
| Redis | ElastiCache r5.xlarge cluster | ~$500 |
| S3 | ~5TB throughput/mês | ~$150 |
| EKS | Cluster fee + node management | ~$200 |
| Monitoring | Stack completa | ~$300 |
| **Total 1M/dia** | | **~$7,925/mês** |

### Otimizações de custo

| Estratégia | Economia estimada |
|------------|-------------------|
| Spot Instances para workers | -60% nos workers |
| Reserved Instances para baseline | -30% nos managed services |
| Scale-to-zero em horários ociosos | -40% fora do horário comercial |
| GPU só quando backlog > threshold | -50% em GPU (usa CPU como baseline) |
| **Combinadas** | **~50-60% de economia total** |

---

## 8. Roadmap de Implementação

### Fase 0 — POC (2-3 semanas)

```
Semana 1: Fundação
├── config.py (pydantic-settings)
├── security/ (hashing, encryption, auth)
├── db.py + models/ + migrations (Alembic)
├── services/audit.py (structlog → PostgreSQL)
└── docker-compose.yml (API + Redis + PostgreSQL + MinIO)

Semana 2: Core
├── services/storage.py (MinIO/S3 upload/download/delete)
├── services/queue.py (interface abstrata + Redis Streams impl)
├── api/v1/extract.py (upload → hash → encrypt → S3 → queue)
├── worker.py (Redis Streams consumer → OCR → result)
├── services/ocr.py (zoom adaptativo 1.5x → 2x)
└── api/v1/jobs.py (polling + SSE)

Semana 3: Hardening
├── api/v1/health.py (real checks: Redis, PG, OCR engine)
├── Validação de PDF (magic bytes, size limit, page limit)
├── Rate limiting middleware
├── Graceful shutdown no worker
├── Testes (pytest: hashing, encryption, API contract)
└── Dockerfile + docker-compose completo
```

### Fase 1 — Produção early (2-4 semanas)

```
├── Migrar Redis Streams → Kafka (ou manter Redis se volume < 500K/dia)
├── Migrar MinIO → S3 (ou manter MinIO se on-premise)
├── Implementar Row-Level Security no PostgreSQL
├── Implementar per-tenant encryption keys (KMS/Vault)
├── Kubernetes manifests (Deployments, Services, Ingress, NetworkPolicies)
├── KEDA para autoscaling por queue depth
├── Prometheus + Grafana + Loki stack
├── CI/CD pipeline (build → test → push image → deploy)
└── Load testing (k6 ou locust)
```

### Fase 2 — Produção scale (contínuo)

```
├── GPU workers (PaddleOCR com paddlepaddle-gpu)
├── Spot Instance handling (graceful preemption)
├── Multi-region (se necessário para latência)
├── Kafka Schema Registry (validação de contratos de mensagem)
├── Dead Letter Queue processing automation
├── Chaos engineering (kill pods, test recovery)
├── SOC 2 audit preparation
├── Penetration testing
└── Performance tuning (profiling OCR, batch page processing)
```

---

## Anexo A — Decisões arquiteturais (ADR resumido)

| # | Decisão | Alternativas descartadas | Razão |
|---|---------|--------------------------|-------|
| 1 | S3/MinIO para PDFs temporários | Filesystem, Redis | Escala horizontal, lifecycle, encryption nativa, K8s-ready |
| 2 | Redis Streams (POC) → Kafka (prod) | Celery, RabbitMQ, SQS | Celery pesado/leaky; Kafka durável e particionável por tenant |
| 3 | Multi-tenant com RLS | Instância por cliente | Custo 10-20× menor, operação unificada, RLS impede cross-tenant |
| 4 | Per-tenant encryption keys | Chave única global | Limita blast radius; vazamento de uma key não compromete outros |
| 5 | KEDA para autoscaling | HPA nativo | HPA não escala por queue depth; KEDA sim |
| 6 | Structlog desde dia 1 | print() / logging | LGPD exige logs sem PII; structlog garante por design |
| 7 | Zoom adaptativo (1.5x → 2x) | Zoom fixo 2x | -25% CPU/RAM, atende 85% accuracy, retry automático |
| 8 | SSE + polling fallback | Só polling / WebSocket | SSE nativo no FastAPI, menos requests, progresso real-time |
| 9 | Fernet para cifra temporária | AES-256-GCM manual | API à prova de falhas, suficiente para TTL de 5-10 min |
| 10 | 1 Dockerfile, 2 entrypoints | 2 Dockerfiles | Mesmo build, menos CI, menos confusão |

## Anexo B — Resumo das respostas

| Pergunta | Resposta |
|----------|---------|
| **Filesystem vs S3?** | S3/MinIO. Filesystem não funciona em K8s (pods efêmeros, multi-nó). MinIO para POC, S3 para produção. Mesmo código via boto3. |
| **O que no lugar do Celery?** | Redis Streams (POC) → Kafka managed (produção). Interface abstraída para troca transparente. |
| **Kafka para milhões?** | Sim. Particionamento por tenant, replay, DLQ, durabilidade. Usar AWS MSK ou Confluent Cloud. |
| **Uma instância por cliente?** | Não. Multi-tenant com 7 camadas de isolamento (API Key, Kafka partitions, S3 prefixes, PostgreSQL RLS, per-tenant encryption, Network Policies, logs segregados). |
| **Como orquestrar com K8s?** | KEDA para autoscaling por queue depth. Node pools separados (API, worker-cpu, worker-gpu). Namespaces isolados. Rolling updates zero-downtime. |
| **Como evitar vazamento entre clientes?** | RLS no PostgreSQL + per-tenant encryption keys + S3 IAM policies + Kafka ACLs + Network Policies. Para um dado vazar, as 7 camadas precisariam falhar simultaneamente. |

---

## Anexo C — Referências

- [PRD](docs/PRD.md) — Product Requirements Document
- [COMPLIANCE](docs/COMPLIANCE.md) — Regulamentação e compliance (LGPD, BACEN, saúde, ISO, SOC 2)
- [STACK](docs/STACK.md) — Stack tecnológica
- [ROADMAP_2026](docs/ROADMAP_2026.md) — Roadmap 2026
- [SENIOR_REVIEW](docs/SENIOR_REVIEW.md) — Revisão sênior (Top 10)
- [TODOS](docs/TODOS.md) — TODOs passo a passo
