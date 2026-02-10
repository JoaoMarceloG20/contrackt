# Documentação — Ultrathink / Contrackt

Índice de todos os arquivos em `docs/`.

---

## Arquivos

| Arquivo                               | Descrição                                                                                                                                                                                                                                                                                                                    |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ARCHITECTURE.md](../ARCHITECTURE.md) | **Relatório de Arquitetura para Produção** — decisões de storage (Filesystem vs S3), filas (Redis Streams vs Celery vs Kafka), multi-tenancy com 7 camadas de isolamento, Kubernetes (KEDA, node pools, network policies), segurança e compliance LGPD, estimativa de custos (POC → 1M jobs/dia) e roadmap de implementação. |
| [PRD.md](PRD.md)                      | **Product Requirements Document** — visão do produto, contexto, público, tipos de documentos, schema de extração, arquitetura, API, Chat, dados para treinamento, certificado, integrações, preços, requisitos não-funcionais, roadmap, métricas, riscos, glossário e anexos.                                                |
| [STACK.md](STACK.md)                  | **Stack tecnológica** — backend (Python, FastAPI, Uvicorn, uv), OCR/ML (PaddleOCR, TrOCR), frontend (Next.js, Bun, React, TypeScript), infra (Docker, docker-compose), persistência, segurança, observabilidade, testes e ferramentas.                                                                                       |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)  | **Design System** — tipografia, cores, espaçamento, grid, componentes (botões, inputs, cards, badges, hash, upload), ícones, motion, responsividade, acessibilidade e tokens CSS. Inspiração Harvey (em evolução).                                                                                                           |
| [FRONTEND.md](FRONTEND.md)            | **Frontend** — Next.js 15, Bun, React, TypeScript; App Router; estrutura de pastas, `lib/extract` (`postExtract`), estado e roteamento, estilos e Design System, testes, build (static export ou `next start`), deploy, segurança, acessibilidade e fluxo de dados.                                                          |
| [ROADMAP_2026.md](ROADMAP_2026.md)    | **Roadmap 2026** — inventário de tecnologias e serviços por categoria; roadmap jan–dez/2026 com **MVP testável em 13/fev**; detalhamento por semana (MVP) e por fase (2–7); diagrama Gantt e dependências.                                                                                                                   |
| [TODOS.md](TODOS.md)                  | **TODOs passo a passo** — lista detalhada e acionável: MVP (API v1, hashes, OCR, Demo UI, Docker, piloto), Design System Harvey, manutenção do ROADMAP, Fase 2 (Banking) e visão geral das Fases 3–7.                                                                                                                        |
| [COMPLIANCE.md](COMPLIANCE.md)        | **Regulamentação e compliance** — LGPD, BACEN/CMN, CDC, IOF; CFM, ANVISA (saúde); fiscal e trabalhista; ISO 27001, SOC 2; campos regulatórios na extração; como o Ultrathink atende; obrigações do cliente e do Ultrathink; DPA.                                                                                             |

---

## Ordem de leitura sugerida

1. **PRD** — entender o produto e o que será construído.
2. **ARCHITECTURE** — decisões de arquitetura, escalabilidade, isolamento e custos para produção.
3. **STACK** — visão da stack e onde cada tecnologia entra.
4. **ROADMAP_2026** — cronograma, tecnologias e prazos (MVP 13/fev).
5. **COMPLIANCE** — regulamentação e compliance por setor (LGPD, BACEN, saúde, ISO, SOC 2).
6. **SENIOR_REVIEW** — revisão sênior das próximas mudanças no MVP.
7. **TODOS** — tarefas detalhadas para executar o MVP e as fases seguintes.
8. **DESIGN_SYSTEM** — ao implementar a UI.
9. **FRONTEND** — ao implementar o frontend (estrutura, API, componentes).

---

## Resumo

- **MVP (13 fev 2026):** API v1 (`/v1/extract`, `/v1/health`), hashes, metadata, demo (upload, resultado, hashes), Docker, critérios de piloto. Ver [TODOS](TODOS.md) e [ROADMAP_2026](ROADMAP_2026.md).
- **Fase 2 (fev–abr):** Banking (templates, batch, webhooks, certificado, zero-retention, admin).
- **Fases 3–7:** Chat, expansão de contratos, integrações, documentoscopia, training. Ver [ROADMAP_2026](ROADMAP_2026.md) e [PRD](PRD.md) seção 13.
- **Compliance:** LGPD, BACEN, saúde (CFM, ANVISA), ISO, SOC 2, DPA. Ver [COMPLIANCE](COMPLIANCE.md).
