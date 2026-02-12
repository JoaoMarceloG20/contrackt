# Backlog do Projeto - Contrackt/Ultrathink

> **Plataforma de extração inteligente de dados de documentos**  
> API-first, especializada no mercado brasileiro, com arquitetura LGPD-native e zero data retention.

---

## 🎯 Visão Geral

Criar um "cinto do batman" de ferramentas internas para empresas brasileiras, começando com extração de documentos e expandindo gradualmente — sempre priorizando qualidade extrema antes de quantidade.

### Público-Alvo Prioritário
- **Fase 1:** Hospitais/Clínicas (laudos médicos manuscritos)
- **Fase 2:** Bancos/Fintechs (contratos, documentoscopia)
- **Fase 3:** Empresas em geral (NF-e, documentos de identidade)

---

## 🚀 FASE 0 - PoC (MVP) 

**Período:** 17 jan - 13 fev 2026 (4 semanas)  
**Objetivo:** API funcional com extração OCR, hashes criptográficos e demo UI  
**Status:** Em andamento

### ✅ Estado Atual do Projeto

O projeto já possui:
- ✅ FastAPI com rota `/extract` para processamento de PDFs
- ✅ Motor OCR PaddleOCR funcionando (`app/services/ocr.py`)
- ✅ Extração de texto com confidence scores
- ✅ Processamento em memória (sem persistência em disco)

### 📋 Tarefas Pendentes - PoC

#### Semana 1: API v1 + Hashes (17-23 jan)
| ID | Tarefa | Status | Prioridade |
|----|--------|--------|------------|
| P0-1 | Criar rota `POST /v1/extract` com multipart/form-data | ✅ Concluída | P0 |
| P0-2 | Validar upload apenas de PDFs (content_type) | ✅ Já existe | P0 |
| P0-3 | Implementar `hashing.py` com SHA-256 | 🔄 Em andamento (`compute_document_hash` e `compute_result_hash` prontos, `build_extraction_metadata` pendente) | P0 |
| P0-4 | Calcular `document_hash` e `result_hash` | ⏳ Pendente | P0 |
| P0-5 | Criar rota `GET /v1/health` | 🔄 Migrar de `/` | P0 |
| P0-6 | Ajustar OCR para retornar `mean_confidence` por página | ⏳ Pendente | P0 |
| P0-7 | Montar resposta `ExtractionResult` completa | ⏳ Pendente | P0 |

**Nota sobre P0-1:** ✅ Rota migrada para `/v1/extract` com parâmetros `document_type` e `include_chat_package`, validação de content_type, limpeza de memória com `gc.collect()` e remoção de logs com PII.

#### Semana 2: Demo UI Base (24-30 jan)
| ID | Tarefa | Status | Prioridade |
|----|--------|--------|------------|
| P0-8 | Setup frontend Next.js + TypeScript + Bun | ⏳ Pendente | P0 |
| P0-9 | Criar `tokens.css` com design system | ⏳ Pendente | P0 |
| P0-10 | Criar componente `UploadZone` | ⏳ Pendente | P0 |
| P0-11 | Criar componente `ExtractResult` | ⏳ Pendente | P0 |
| P0-12 | Criar componente `HashBlock` com copiar | ⏳ Pendente | P0 |
| P0-13 | Criar componente `ConfidenceBadge` | ⏳ Pendente | P0 |
| P0-14 | Integrar frontend com API (`postExtract`) | ⏳ Pendente | P0 |

#### Semana 3: Docker + Refinamentos (31 jan - 6 fev)
| ID | Tarefa | Status | Prioridade |
|----|--------|--------|------------|
| P0-15 | Criar `Dockerfile` multi-stage | ⏳ Pendente | P0 |
| P0-16 | Criar `docker-compose.yml` | ⏳ Pendente | P0 |
| P0-17 | Adicionar loading states e tratamento de erro na UI | ⏳ Pendente | P0 |
| P0-18 | Garantir responsividade da UI | ⏳ Pendente | P1 |
| P0-19 | Criar `.dockerignore` | ⏳ Pendente | P0 |

#### Semana 4: Estabilização e Piloto (7-13 fev)
| ID | Tarefa | Status | Prioridade |
|----|--------|--------|------------|
| P0-20 | Testes com pytest (API contract) | ⏳ Pendente | P0 |
| P0-21 | Testes com Vitest (componentes) | ⏳ Pendente | P1 |
| P0-22 | Criar `docs/CRITERIOS_PILOTO.md` | ⏳ Pendente | P0 |
| P0-23 | Criar one-pager para stakeholders | ⏳ Pendente | P0 |
| P0-24 | **MVP Congelado para testes** | 🎯 Marco | P0 |

### 📦 Entregáveis Opcionais (Se houver tempo)
| ID | Tarefa | Status | Prioridade |
|----|--------|--------|------------|
| P0-OPT-1 | Integrar TrOCR para manuscritos | ⏳ Pendente | P2 |
| P0-OPT-2 | Design System estilo Harvey | ⏳ Pendente | P2 |
| P0-OPT-3 | Audit trail persistido (SQLite) | ⏳ Pendente | P2 |
| P0-OPT-4 | E2E tests com Playwright | ⏳ Pendente | P2 |

---

## 🏦 FASE 1 - Banking MVP

**Período:** 14 fev - abr 2026 (8 semanas)  
**Objetivo:** Templates bancários, batch processing, zero-retention completo  
**Dependências:** MVP estável

### Core Banking
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P1-1 | Definir schema para Empréstimo Pessoal | P0 |
| P1-2 | Definir schema para Consignado | P0 |
| P1-3 | Implementar extração estruturada (OCR + NER) | P0 |
| P1-4 | Mapear campos regulatórios (CET, IOF, etc.) | P0 |

### Batch & Webhooks
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P1-5 | Criar `POST /v1/extract/batch` | P0 |
| P1-6 | Implementar processamento assíncrono | P0 |
| P1-7 | Implementar webhooks com retry | P0 |
| P1-8 | Adicionar `httpx` para chamadas webhook | P0 |

### Zero-Retention & Compliance
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P1-9 | Implementar `secure_delete` (overwrite 3-pass) | P0 |
| P1-10 | Gerar certificado de processamento | P0 |
| P1-11 | Criar `GET /v1/verify/{id}` | P0 |
| P1-12 | Implementar audit trail (SQLite/Postgres) | P0 |

### Segurança
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P1-13 | Implementar autenticação por API Key | P0 |
| P1-14 | Criar middleware de autenticação | P0 |
| P1-15 | Adicionar CORS restritivo | P1 |

### Admin
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P1-16 | Criar interface admin básica | P1 |
| P1-17 | Dashboard de batches e status | P1 |

---

## 💬 FASE 2 - Chat on Contracts

**Período:** Mai - jun 2026 (6 semanas)  
**Objetivo:** Funcionalidade de chat com RAG sobre documentos  
**Dependências:** Fase 1 (API Key, audit)

### RAG & Embeddings
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P2-1 | Implementar geração de `chat_package` | P0 |
| P2-2 | Criar chunks de texto por bloco | P0 |
| P2-3 | Gerar embeddings (OpenAI ou local) | P0 |
| P2-4 | Adicionar `include_chat_package` na API | P0 |

### API de Chat
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P2-5 | Criar `POST /v1/chat` | P0 |
| P2-6 | Implementar busca vetorial de chunks | P0 |
| P2-7 | Integrar com LLM para respostas | P0 |
| P2-8 | Retornar citações no contexto | P0 |

### UI de Chat
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P2-9 | Criar interface de chat no frontend | P0 |
| P2-10 | Implementar histórico de conversas | P1 |
| P2-11 | Busca por número de contrato | P1 |

### Storage Client-Side
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P2-12 | Implementar SQLite local (cliente) | P0 |
| P2-13 | Armazenar chunks e embeddings localmente | P0 |
| P2-14 | Guia de integração SDK | P1 |

---

## 📄 FASE 3 - Expansão de Contratos

**Período:** Jul - set 2026 (8 semanas)  
**Objetivo:** Novos tipos de contrato e templates por banco  
**Dependências:** Fase 1 (templates e schema)

### Novos Tipos de Contrato
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P3-1 | Template: Financiamento de Veículos | P1 |
| P3-2 | Template: Cartão de Crédito | P1 |
| P3-3 | Template: Capital de Giro (PJ) | P1 |

### Templates por Banco
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P3-4 | Template específico: Itaú | P2 |
| P3-5 | Template específico: Banco do Brasil | P2 |
| P3-6 | Template específico: Bradesco | P2 |

### Melhorias OCR
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P3-7 | Ajustes de schema e pipeline | P1 |
| P3-8 | Otimização de performance | P2 |

---

## 🔌 FASE 4 - Integrações Enterprise

**Período:** Set - out 2026 (6 semanas)  
**Objetivo:** Integrações com sistemas legados e deploy produtivo  
**Dependências:** Fase 1 (batch, webhooks)

### Conectores Core Banking
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P4-1 | Export XML para core banking | P1 |
| P4-2 | Export TXT posicional (mainframe) | P1 |
| P4-3 | Integração SFTP | P1 |
| P4-4 | Integração MQ (IBM MQ) | P2 |

### Webhooks Avançados
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P4-5 | Retry com exponential backoff | P1 |
| P4-6 | Dead-letter queue | P1 |
| P4-7 | Assinatura de webhooks (HMAC) | P1 |

### Infraestrutura
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P4-8 | Deploy com nginx/Caddy | P0 |
| P4-9 | TLS 1.3 em produção | P0 |
| P4-10 | Opção on-premise (pacote Docker/K8s) | P2 |
| P4-11 | SSO/SAML para admin | P2 |

---

## 🔍 FASE 5 - Documentoscopia

**Período:** Nov - dez 2026 (8 semanas)  
**Objetivo:** Detecção de fraudes e adulterações em documentos  
**Dependências:** Pode evoluir em paralelo com Fases 3-4

### Detecção de Adulterações
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P5-1 | Análise de inconsistências visuais | P1 |
| P5-2 | Detecção de recompressão JPEG | P1 |
| P5-3 | Análise de metadados PDF | P1 |

### Validação de Assinaturas
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P5-4 | Análise de padrões de assinatura | P1 |
| P5-5 | Integração com certificados digitais | P2 |

### Score de Fraude
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P5-6 | Algoritmo de score de risco | P1 |
| P5-7 | Dashboard de alertas | P1 |
| P5-8 | Modelos específicos por tipo de documento | P2 |

---

## 🧠 FASE 6 - Training e Modelos (Contínuo)

**Período:** A partir de Fase 1  
**Objetivo:** Melhoria contínua dos modelos via active learning

### Active Learning
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P6-1 | Identificar documentos com baixa confiança | P1 |
| P6-2 | UI para coleta de correções | P1 |
| P6-3 | Pipeline de anonimização | P1 |
| P6-4 | Fine-tuning de modelos | P2 |

### Opt-in e Coleta
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P6-5 | Configuração de opt-in no cliente | P1 |
| P6-6 | Métricas anônimas de uso | P2 |
| P6-7 | Feedback de correções anonimizado | P2 |

### Federated Learning
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P6-8 | Pesquisa e definição de protocolo | P3 |
| P6-9 | Implementação do agregador | P3 |
| P6-10 | Experimentos com clientes-piloto | P3 |

### Benchmarks
| ID | Tarefa | Prioridade |
|----|--------|------------|
| P6-11 | Construir datasets anonimizados | P2 |
| P6-12 | Publicar benchmarks comparativos | P3 |

---

## 📊 Resumo por Fase

| Fase | Período | Entrega Principal | Impacto |
|------|---------|-------------------|---------|
| **0 - PoC** | 17 jan - 13 fev | API v1 + Demo UI | Prova de conceito funcional |
| **1 - Banking** | 14 fev - abr | Templates + Batch + Zero-retention | Primeiro cliente pagante |
| **2 - Chat** | Mai - jun | RAG + Chat sobre documentos | Diferencial competitivo |
| **3 - Contratos** | Jul - set | +3 tipos de contrato | Expansão de mercado |
| **4 - Enterprise** | Set - out | Integrações + Deploy produtivo | Clientes enterprise |
| **5 - Documentoscopia** | Nov - dez | Anti-fraude + Dashboard | Segurança avançada |
| **6 - Training** | Contínuo | Active learning + Benchmarks | Qualidade contínua |

---

## 🎯 Próximos Passos Imediatos

Baseado no estado atual do projeto, as 5 tarefas prioritárias para a próxima semana são:

1. **P0-3**: Implementar `hashing.py` - *core do diferencial de compliance*
2. **P0-4**: Calcular `document_hash` e `result_hash` - *necessário para o certificado*
3. **P0-1**: Migrar rota para `/v1/extract` com nova estrutura de resposta
4. **P0-6**: Ajustar OCR para retornar `mean_confidence` por página
5. **P0-7**: Montar resposta `ExtractionResult` completa conforme PRD

---

## 📚 Documentação Relacionada

- [PRD](docs/PRD.md) - Product Requirements Document
- [ROADMAP_2026](docs/ROADMAP_2026.md) - Roadmap técnico detalhado
- [ARCHITECTURE](ARCHITECTURE.md) - Arquitetura de produção
- [COMPLIANCE](docs/COMPLIANCE.md) - LGPD e regulamentações
- [TODOS](docs/TODOS.md) - TODOs passo a passo

---

*Última atualização: 10 de fevereiro de 2026*
