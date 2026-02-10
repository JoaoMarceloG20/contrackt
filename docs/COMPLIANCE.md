# Ultrathink — Regulamentação e Compliance

**Versão:** 1.0  
**Data:** Janeiro 2026  
**Objetivo:** Consolidar as leis, resoluções, normas e boas práticas que o software deve observar para atender **bancos, hospitais, fintechs e empresas em geral** no Brasil.

---

## Índice

1. [Visão geral por setor](#1-visão-geral-por-setor)
2. [LGPD — Lei Geral de Proteção de Dados](#2-lgpd--lei-geral-de-proteção-de-dados)
3. [Setor financeiro — BACEN, CMN, CDC](#3-setor-financeiro--bacen-cmn-cdc)
4. [Setor saúde — CFM, ANVISA](#4-setor-saúde--cfm-anvisa)
5. [Empresas em geral e documentos fiscais/trabalhistas](#5-empresas-em-geral-e-documentos-fiscais-trabalhistas)
6. [Certificações e frameworks (ISO, SOC 2)](#6-certificações-e-frameworks-iso-soc-2)
7. [Campos regulatórios na extração de contratos](#7-campos-regulatórios-na-extração-de-contratos)
8. [Requisitos técnicos transversais](#8-requisitos-técnicos-transversais)
9. [Como o Ultrathink atende](#9-como-o-ultrathink-atende)
10. [Obrigações do cliente e do Ultrathink](#10-obrigações-do-cliente-e-do-ultrathink)
11. [Referências e links](#11-referências-e-links)

---

## 1. Visão geral por setor

| Setor | Principais normativos | Foco para o software |
|-------|------------------------|------------------------|
| **Todos** | LGPD, ANPD | Dados pessoais, bases legais, direitos do titular, segurança, notificação de incidentes, DPO, ROPA, DPIA |
| **Bancos e fintechs** | BACEN, CMN, CDC, Decreto IOF | CET, transparência em contratos, segurança cibernética, PSTI (se integrar RSFN), retenção documental (10 anos em alguns casos), campos obrigatórios em contratos |
| **Hospitais e clínicas** | LGPD (dados sensíveis saúde), CFM, ANVISA | Sigilo, prontuário, digitalização (Res. CFM 1.821/2007), confidencialidade, acesso do paciente, anonimização |
| **Empresas em geral** | LGPD, legislação fiscal e trabalhista | Retenção de documentos (5 anos fiscal, 5 anos trabalhista), NF-e, contratos, minimização de dados |
| **Certificações** | ISO 27001, ISO 27701, SOC 2 | Segurança da informação, privacidade, controles operacionais; exigidas por clientes enterprise |

---

## 2. LGPD — Lei Geral de Proteção de Dados

**Lei nº 13.709/2018.** Aplica-se ao tratamento de dados pessoais em território brasileiro, na oferta de produtos/serviços a pessoas no Brasil ou na coleta de dados no Brasil.

### 2.1 Dados sensíveis

Dados de **saúde** são sensíveis. Tratamento só em hipóteses legais: consentimento explícito, obrigação legal/regulatória, tutela da saúde, execução de contrato, proteção da vida, etc. O software que processa laudos e prontuários deve garantir que o **cliente (controlador)** tenha base legal e que o **Ultrathink (operador)** cumpra o acordado no DPA.

### 2.2 Princípios que o software deve refletir

| Princípio | Exigência para o software |
|-----------|----------------------------|
| **Finalidade** | Tratar apenas para os fins informados ao titular e ao cliente; não desviar uso (ex.: treinar modelo com dados sensíveis sem opt-in e anonimização). |
| **Necessidade / minimização** | Coletar e reter o mínimo necessário. Zero-retention no Ultrathink Cloud reduz retenção; o cliente decide o que guardar localmente. |
| **Transparência** | Documentar o que é processado, o que é retido (hashes, logs sem PII) e como; política de privacidade e termos claros. |
| **Segurança** | Medidas técnicas (criptografia, hashes, controle de acesso, logs) e administrativas (políticas, treinamento, DPA). |
| **Prevenção** | Evitar danos: arquitetura que não armazena documento nem dados extraídos no cloud reduz superfície de ataque. |
| **Responsabilização e prestação de contas** | Demonstrar conformidade: ROPA, DPIA quando couber, auditorias, certificado de processamento, DPA. |

### 2.3 Direitos dos titulares que o sistema deve suportar (no cliente)

O **cliente** é o controlador; o software do cliente (ou o SDK/API do Ultrathink) deve permitir:

- **Acesso:** o titular saber se seus dados são tratados, quais, origem, finalidade.
- **Correção:** dados incompletos, inexatos ou desatualizados.
- **Eliminação / anonimização:** apagar ou anonimizar quando aplicável.
- **Portabilidade:** exportar em formato estruturado, quando houver previsão legal.
- **Revogação de consentimento** e **oposição** ao tratamento (quando a base for consentimento ou interesse legítimo).

Como o Ultrathink **não retém** dados pessoais no cloud, a maior parte do exercício desses direitos ocorre no ambiente do **cliente**. O DPA e a documentação devem deixar claro: o que o Ultrathink faz, o que retém (apenas hashes e logs sem PII) e como o cliente pode atender a pedidos de titulares.

### 2.4 Obrigações do controlador e do operador

- **DPO (Encarregado):** o cliente deve designar; o Ultrathink deve ter canal para o DPO do cliente em incidentes ou dúvidas sobre processamento.
- **ROPA (Registro de Operações de Tratamento):** cliente e Ultrathink devem manter inventário dos processos que envolvem dados pessoais (finalidade, base legal, categorias, retenção, compartilhamento, medidas de segurança).
- **DPIA (Avaliação de Impacto):** quando o tratamento gerar risco elevado ou envolver dados sensíveis em grande escala; o cliente realiza; o Ultrathink fornece informações sobre o processamento (fluxo, retenção, segurança) para subsidiar a DPIA.
- **Políticas e normas:** privacidade, segurança da informação, tratamento de incidentes; treinamento da equipe.

### 2.5 Notificação de incidentes (ANPD)

Em caso de **incidente de segurança** que possa gerar risco aos titulares:

- **Comunicação à ANPD:** em prazo razoável (a LGPD não fixa prazo; a ANPD pode regulamentar). Na prática, orienta-se **até 72 horas** (2 dias úteis) a partir do conhecimento do fato, quando aplicável.
- **Comunicação ao titular:** quando houver risco relevante, de forma clara e acessível.
- O **operador (Ultrathink)** deve notificar o **controlador (cliente)** em prazo contractually definido (ex.: 24–72h) para que o cliente cumpra suas obrigações perante a ANPD e os titulares.

### 2.6 Transferência internacional de dados

Se o Ultrathink ou subcontratados (ex.: modelos em cloud no exterior) processarem dados no exterior:

- País ou organismo internacional com **grau de proteção adequado**, ou
- **Garantias** (cláusulas contratuais, certificações, etc.) aprovadas pela ANPD, ou
- **Consentimento específico**, **execução de contrato**, **proteção da vida** ou outras hipóteses da LGPD.

A arquitetura **zero-retention** (documento e dados extraídos não saem do cliente ou são processados em memória e devolvidos sem persistência no cloud) reduz o volume de dados transferidos; hashes e logs sem PII têm tratamento específico no DPA.

---

## 3. Setor financeiro — BACEN, CMN, CDC

### 3.1 CET e transparência em contratos de crédito

- **Resolução CMN nº 3.517/2007** (objetivos consolidados na **Resolução CMN nº 4.881/2020**): instituições devem informar o **Custo Efetivo Total (CET)** em operações de crédito e arrendamento para PF (e, em certas condições, ME/EPP). O CET inclui juros, tributos, tarifas, seguros e demais despesas.
- **Resolução CMN nº 3.909/2010:** estendeu exigências de CET a micro e pequenas empresas.
- **Aplicação ao Ultrathink:** o **schema de extração** de contratos bancários deve incluir **CET (mensal e anual)**, **taxa de juros nominal**, **valor total a pagar**, **sistema de amortização** e **IOF** como campos obrigatórios, para que o cliente (banco/fintech) possa auditar, comparar e garantir transparência. Ver [PRD](PRD.md) e [seção 7](#7-campos-regulatórios-na-extração-de-contratos) abaixo.

### 3.2 Código de Defesa do Consumidor (CDC — Lei 8.078/1990)

- Contratos de adesão (incluindo muitos contratos de crédito) devem ser **claros**, com **destaque** para cláusulas que limitem direitos. O consumidor tem direito a **informação prévia** sobre custos e condições.
- **Aplicação:** a extração deve permitir localizar e validar **valor total a pagar**, **taxa de juros**, **CET** e **sistema de amortização** para suportar a conformidade do cliente com o CDC.

### 3.3 IOF — Decreto nº 6.306/2007

- Regulamenta a incidência e a cobrança do IOF em operações de crédito, câmbio e seguros.
- **Aplicação:** o schema de extração deve incluir **valor do IOF** e, quando relevante, a base de cálculo, para que o cliente verifique a conformidade do contrato.

### 3.4 BACEN — Segurança cibernética e PSTI

- **Resolução CMN 5.274/2025** e **Resolução BCB 538/2025:** política de segurança cibernética e requisitos para instituições financeiras (prazo de adequação em 1º de março de 2026). Incluem: gestão de certificados, autenticação multifatorial, monitoramento de credenciais, proteção de redes, **testes de intrusão independentes anuais**, documentação e retenção de relatórios por **cinco anos**.
- **Resolução BCB 498/2025:** credenciamento de **PSTI (Provedores de Serviços de TI)** que processam dados para acesso à RSFN. Exige: capital/patrimônio mínimos, governança, diretores (segurança, compliance, riscos), certificação internacional ou asseguração reconhecida pelo Bacen, PCN, seguro, testes de contingência. PSTIs em operação têm **quatro meses** para iniciar adequação.
- **Resoluções BCB 494–497/2025:** limites e regras para Pix/TED quando há uso de PSTI não credenciado (ex.: limite de R$ 15.000 por transação em certas condições).
- **Aplicação ao Ultrathink:**
  - Se o Ultrathink atuar como **PSTI** ou processar dados que acessem RSFN/Pix/STR, precisará avaliar o enquadramento na Res. 498 e nas demais.
  - Na maioria dos cenários (extração de documentos, integração via API com core banking do **cliente**), o Ultrathink pode atuar como **fornecedor de tecnologia** do banco/fintech, que continua responsável perante o Bacen. O **contrato e o DPA** devem delimitar papéis (controlador x operador, responsabilidades de segurança e de auditoria).
  - O software deve oferecer: **criptografia** (trânsito e, no cliente, repouso), **logs de processamento** (sem PII), **audit trail** (hashes, certificado), **controle de acesso** (API Key, etc.) e documentação para que o cliente atenda às resoluções de cibersegurança.

### 3.5 Documentação e retenção — Resolução BCB 476/2025

- Altera a Res. 96/2021: na abertura e alteração de **contas de pagamento**, a instituição deve consultar o sistema de restrições do Bacen e manter **documentação por pelo menos 10 anos**, inclusive em decisões excepcionais (ex.: abrir conta com restrição registrada).
- **Aplicação:** o **cliente** é responsável pela guarda dos documentos e dos dados extraídos. O Ultrathink, com **zero-retention**, não guarda o documento; o **certificado de processamento** e os **hashes** ajudam o cliente a comprovar que determinado documento foi processado em determinada data, para fins de auditoria e de retenção regulatória no ambiente do cliente.

### 3.6 Contratos com PSTIs e terceiros (Res. conjunta Bacen/CMN)

- Contratos com PSTIs (e, por analogia, com fornecedores de TI) devem prever: **segurança**, **confidencialidade**, **continuidade de negócios**, **relatórios** e **auditorias**. Há responsabilização entre contratante e PSTI.
- **Aplicação:** o **DPA** e o contrato comercial do Ultrathink devem cobrir: finalidade do processamento, subcontratados (se houver), medidas de segurança, confidencialidade, notificação de incidentes, direito de auditoria do cliente e de autoridades, e destinação dos dados (zero-retention no cloud).

---

## 4. Setor saúde — CFM, ANVISA

### 4.1 Código de Ética Médica (CFM — Res. CFM 1.931/2009)

- **Art. 73:** sigilo — o médico não pode revelar fatos ligados à profissão sem justa causa, dever legal ou consentimento do paciente.
- **Art. 87:** o prontuário deve conter dados clínicos atualizados, em ordem cronológica, com data, hora, assinatura e CRM do médico.
- **Art. 88:** o paciente tem direito de **acesso** ao prontuário e a **cópia** quando solicitar, com explicações, salvo risco para si ou para terceiros.
- **Art. 89:** liberar cópia do prontuário somente com **autorização expressa do paciente**, **ordem judicial** ou para **defesa própria**.
- **Aplicação:** o software que processa **laudos e prontuários** lida com **dados de saúde** e deve garantir que apenas **pessoas autorizadas** (pelo controlador, o hospital/clínica) tenham acesso. O Ultrathink, como operador, **não retém** o conteúdo; o **cliente** deve ter controles de acesso, logs e políticas alinhadas ao CFM. A extração (OCR) é um meio de **digitalização e estruturação**; a **guarda** e o **acesso** ficam sob responsabilidade do estabelecimento de saúde.

### 4.2 Digitalização de prontuários — Resolução CFM nº 1.821/2007

- Regulamenta a **digitalização** e o uso de **sistemas informatizados** para prontuários: eliminação do papel, padrões de segurança no registro eletrônico, **certificado digital**, **criptografia**, **controle de acesso**, **registro de logs**.
- **Aplicação:** quando o Ultrathink for usado para **extrair texto de laudos/prontuários** que serão armazenados no sistema do cliente, o **cliente** deve garantir que o sistema de prontuário eletrônico (onde os dados extraídos serão inseridos ou vinculados) atenda à Res. 1.821/2007. O Ultrathink deve oferecer **rastreabilidade** (hashes, certificado) e **não reter** o documento nem o texto no cloud, alinhado à minimização e à segurança.

### 4.3 ANVISA e dados de saúde

- A ANVISA possui **Política de Privacidade e de Tratamento de Dados Pessoais** e **Política de Proteção de Dados** (Port. 1.184/2023), alinhadas à LGPD: controlador, operador, direitos dos titulares, bases legais, compartilhamento (fundamentado em lei, regulamento ou convênio).
- **Aplicação:** estabelecimentos de saúde regulados pela ANVISA que usem o Ultrathink devem garantir que o tratamento (inclusive pelo operador) observe a LGPD e as políticas setoriais. O DPA e a documentação do Ultrathink devem descrever o papel de operador, a ausência de retenção de dados de saúde no cloud e as medidas de segurança.

### 4.4 Boas práticas em dados de saúde

- Mapeamento de dados de saúde (quais, quem gera, onde, como são armazenados).
- Consentimento explícito quando exigido (além das bases legais da LGPD).
- Anonimização ou pseudonimização quando possível (ex.: treinos com dados anonimizados, opt-in).
- Políticas internas de privacidade, termos de confidencialidade para equipes e fornecedores.
- Auditoria e governança: monitoramento, registros de acesso, avaliações de risco.
- Segurança: criptografia em trânsito e repouso, controle de acessos, adequação ao padrão do prontuário eletrônico (Res. 1.821/2007).

---

## 5. Empresas em geral e documentos fiscais/trabalhistas

### 5.1 Retenção documental

- **Fiscal (NF-e, livros, etc.):** Lei 8.212/1991, Decreto 8.638/2016 e normas da Receita: guarda por **5 anos** (em regra, a contar do ano seguinte ao da ocorrência dos fatos).
- **Trabalhista:** CLT e normas do eSocial: documentos por **5 anos** após a extinção do contrato (em certos casos, prazos maiores).
- **Aplicação:** o Ultrathink **não define** a política de retenção do cliente; o **cliente** é responsável por reter os documentos e os dados extraídos conforme a lei. O **certificado de processamento** e os **hashes** auxiliam na **comprovação** de que um documento foi processado em determinada data, para fins de auditoria e de retenção no ambiente do cliente.

### 5.2 NF-e, NFS-e e documentos de identidade

- **NF-e:** legislação da Secretaria da Receita Federal e das secretarias estaduais; formato e validade do XML; obrigações de guarda.
- **NFS-e:** varia por município; exigências de armazenamento e de integração com sistemas da prefeitura.
- **CNH, CPF, RG:** dados de identificação são **pessoais** (LGPD); uso deve ter base legal e finalidade definida. Evitar reter além do necessário; no Ultrathink, zero-retention no cloud reduz exposição.

---

## 6. Certificações e frameworks (ISO, SOC 2)

### 6.1 ISO/IEC 27001 (Segurança da informação)

- Requisitos para **Sistema de Gestão de Segurança da Informação (SGSI)**: liderança, planejamento, avaliação de riscos, operação, suporte, monitoramento e melhoria.
- **Anexo A:** controles (acesso, criptografia, comunicações, operações, fornecedores, etc.). A organização pode excluir controles na **Declaração de Aplicabilidade (SoA)** com justificativa.
- **Aplicação:** o Ultrathink deve alinhar políticas, procedimentos e controles técnicos (acesso, criptografia, logs, gestão de incidentes, terceiros) à ISO 27001 quando buscar a certificação. A arquitetura zero-retention e o uso de hashes e certificados são elementos que **reduzem riscos** e apoiam o SGSI.

### 6.2 ISO/IEC 27701 (Privacidade)

- Extensão da ISO 27001 para **gestão de privacidade** (PIMS). Cobre controladores e operadores de dados pessoais.
- **Aplicação:** quando o Ultrathink buscar ISO 27701, o DPA, o ROPA, as políticas de privacidade e os fluxos de dados (incluindo zero-retention e subcontratados) devem estar documentados e auditáveis.

### 6.3 SOC 2 (AICPA — EUA)

- **Trust Services Criteria:** Segurança (obrigatório), Disponibilidade, Integridade do Processamento, Confidencialidade, Privacidade. A organização escolhe, além de Segurança, quais critérios aplicar.
- **Tipo I:** design dos controles em um momento. **Tipo II:** eficácia operacional ao longo de 6–12 meses.
- **Aplicação:** o PRD prevê **SOC 2 no roadmap**. O Ultrathink deve manter evidências de controles (acesso, criptografia, monitoramento, gestão de incidentes, privacidade) para auditoria. A zero-retention e o certificado de processamento são **diferenciais** para os critérios de Confidencialidade e Privacidade.

---

## 7. Campos regulatórios na extração de contratos

Para **contratos de crédito** (em especial PF e, quando aplicável, ME/EPP), o schema de extração deve incluir os campos abaixo, conforme [PRD](PRD.md) e normativos:

| Campo | Obrigatoriedade | Normativo |
|-------|-----------------|-----------|
| **CET (Custo Efetivo Total)** — mensal e anual | Obrigatório | Res. CMN 3.517/2007 (consolidada na 4.881/2020) |
| **Taxa de juros nominal** (mensal e anual) | Obrigatório | CDC, transparência ao consumidor |
| **IOF** | Obrigatório | Decreto 6.306/2007 |
| **Valor total a pagar** | Obrigatório | CDC |
| **Sistema de amortização** (PRICE, SAC, SAM, etc.) | Obrigatório | Transparência, Res. CMN |
| **Valor total financiado / valor da operação** | Obrigatório | Transparência, planilha CET |
| **Parcelas, datas de vencimento, valor da parcela** | Obrigatório | Transparência, CDC |
| **Encargos de inadimplência** (juros de mora, multa) | Recomendado | Transparência, CDC |
| **Seguros (prestamista, MIP, etc.) e prêmios** | Recomendado | CET, Res. CMN |

O **software** deve extrair, validar e sinalizar (ex.: `fields_not_found`, `low_confidence_fields`) esses itens para que o **cliente** audite e cumpra BACEN/CMN e CDC.

---

## 8. Requisitos técnicos transversais

| Requisito | Implementação no Ultrathink (ou no cliente) |
|-----------|---------------------------------------------|
| **Criptografia em trânsito** | TLS 1.3 (reverse proxy em produção) |
| **Criptografia em repouso** | No **cliente**: AES-256 para dados no SQLite local (conforme PRD). No Ultrathink Cloud: não há repouso de documento nem de dados extraídos; hashes e logs sem PII conforme política. |
| **Controle de acesso** | API Key (Fase 2); autenticação forte; níveis de acesso conforme perfil (admin, operador, etc.) no cliente. |
| **Logs e auditoria** | Logs de processamento (hashes, `document_type`, `processing_time_ms`, sem PII); audit trail (Fase 2) com retenção definida (ex.: 5 anos para fins regulatórios); logs de acesso a sistemas. |
| **Retenção e descarte** | **Zero-retention** no Ultrathink Cloud para documento e dados extraídos. Política de retenção de **hashes e logs** (ex.: 5 anos) para auditoria e atendimento a autoridades. **Deleção segura** (overwrite 3-pass) quando houver arquivos temporários em disco (Fase 2, batch). |
| **Anonimização e pseudonimização** | Para **treinamento** e **opt-in**: anonimizar dados (substituir CPF, nomes, valores por equivalentes sintéticos; borrar imagens) conforme [PRD](PRD.md) seção 8. |
| **Resposta a incidentes** | Política de detecção, contenção, notificação ao cliente (24–72h) e, quando couber, à ANPD; documentação e lições aprendidas. |
| **Transferência internacional** | Se houver processamento ou subcontratados fora do Brasil: cláusulas no DPA, garantias (cláusulas-padrão, certificações) ou bases legais da LGPD; preferência por processamento e armazenamento no Brasil quando possível. |

---

## 9. Como o Ultrathink atende

| Exigência | Atendimento |
|-----------|-------------|
| **Minimização e zero-retention (LGPD)** | Documento e dados extraídos **não são armazenados** no Ultrathink Cloud; processamento em memória; apenas hashes e logs sem PII são retidos. |
| **Transparência e prestação de contas** | **Certificado de processamento** com `document_hash`, `result_hash`, declaração de não-retenção; **`/v1/verify/{id}`** para verificação; documentação e DPA. |
| **Segurança (LGPD, BACEN, ISO, SOC 2)** | Criptografia (TLS, AES no cliente), hashes SHA-256, deleção segura (overwrite 3-pass quando houver arquivo em disco), controle de acesso (API Key), logs e audit trail. |
| **Campos regulatórios (CET, IOF, CDC)** | Schema de extração com CET, taxa nominal, IOF, valor total, sistema de amortização, parcelas; `extraction_metadata` com `fields_not_found` e `low_confidence_fields` para auditoria. |
| **Sigilo e dados de saúde (CFM, LGPD)** | Zero-retention evita que laudos/prontuários fiquem no cloud; o cliente mantém o dado no seu ambiente, com controles de acesso e conformidade à Res. CFM 1.821/2007. |
| **Rastreabilidade e auditoria (BACEN, fiscal, trabalhista)** | Hashes e certificado permitem comprovar **que** um documento foi processado e **quando**; o cliente guarda o documento e os dados extraídos conforme prazos legais. |
| **Operador (LGPD)** | DPA define finalidade, instruções do controlador, subcontratados, medidas de segurança, notificação de incidentes e que o Ultrathink **não retém** dados pessoais no cloud. |
| **Notificação de incidentes (ANPD, LGPD)** | Compromisso de notificar o cliente em prazo contractually definido (ex.: 24–72h) para o cliente cumprir obrigações perante a ANPD e os titulares. |

---

## 10. Obrigações do cliente e do Ultrathink

### 10.1 Cliente (controlador ou responsável pelo uso)

- Ter **base legal** e **finalidade** para o tratamento dos dados (incluindo dados de saúde e financeiros).
- Manter **ROPA** e **DPIA** quando exigido; designar **DPO**.
- Garantir que o **ambiente local** (onde armazena documento e dados extraídos) atenda à LGPD, às normas setoriais (BACEN, CFM, fiscal, trabalhista) e às políticas de retenção e de acesso.
- **Reter** documentos e dados extraídos conforme prazos legais (ex.: 5 anos fiscal/trabalhista; 10 anos em certos casos BACEN).
- Exercer os **direitos dos titulares** (acesso, correção, eliminação, etc.) no seu sistema; o Ultrathink, ao não reter dados no cloud, não é o destinatário direto desses pedidos, mas o DPA pode prever cooperação em investigações.
- Celebrar **DPA** com o Ultrathink e garantir que subcontratados e integrações (core banking, prontuário eletrônico) também estejam em conformidade.

### 10.2 Ultrathink (operador)

- Processar **apenas** conforme instruções do cliente e do **DPA**.
- **Não reter** documento nem dados extraídos no Ultrathink Cloud; manter apenas hashes e logs sem PII, conforme política e DPA.
- Aplicar **medidas de segurança** (criptografia, hashes, deleção segura, controle de acesso, logs) e documentá-las.
- **Notificar** o cliente em caso de incidente de segurança em prazo definido no DPA (ex.: 24–72h).
- Permitir **auditorias** e **inspeções** pelo cliente ou por autoridades, na extensão contractually acordada e na medida do que for aplicável (evidências, políticas, logs de processamento, sem expor dados de outros clientes).
- Manter **política de privacidade**, **termos de uso** e **DPA** atualizados; **ROPA** do processamento realizado em nome dos clientes.
- Avançar no roadmap de **SOC 2** e, quando aplicável, **ISO 27001/27701**, conforme [PRD](PRD.md) e [ROADMAP_2026](ROADMAP_2026.md).

### 10.3 DPA (Data Processing Agreement)

O **DPA** deve cobrir, no mínimo:

- Papéis: controlador (cliente) x operador (Ultrathink).
- Finalidade e instruções de processamento; proibição de uso para outros fins.
- **Zero-retention**: confirmação de que o Ultrathink não armazena documento nem dados extraídos no cloud; descrição do que é retido (hashes, logs sem PII) e por quanto tempo.
- Subcontratados (se houver): lista, finalidade, garantias equivalentes.
- Medidas de segurança (resumidas) e conformidade à LGPD.
- **Notificação de incidentes** (prazo, formato, responsabilidade do cliente perante ANPD e titulares).
- **Direito de auditoria** e de inspeção; confidencialidade.
- **Transferência internacional** (se aplicável): garantias ou bases legais.
- **Destruição/retorno** de dados ao término: no modelo zero-retention, não há “devolução” de dados armazenados; o DPA deve deixar explícito que não há retenção e que os hashes/logs são mantidos conforme política de retenção (ex.: 5 anos) para auditoria e obrigações legais.

---

## 11. Referências e links

### Legislação e normas

- **LGPD:** Lei nº 13.709/2018 — [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- **ANPD:** [gov.br/anpd](https://www.gov.br/anpd/pt-br)
- **CDC:** Lei 8.078/1990 — [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/leis/l8078.htm)
- **Decreto 6.306/2007 (IOF)** — [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2007/decreto/d6306.htm)
- **Resolução CMN 3.517/2007 (CET)** — [bcb.gov.br](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=3517)
- **Resolução CMN 4.881/2020 (consolidação CET)** — [bcb.gov.br](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=4881)
- **Resolução BCB 498/2025 (PSTI)** — [bcb.gov.br](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=498)
- **Resolução BCB 476/2025 (contas de pagamento)** — [bcb.gov.br](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=476)
- **Resolução CMN 5.274/2025 e BCB 538/2025 (segurança cibernética)** — [bcb.gov.br](https://www.bcb.gov.br/estabilidadefinanceira)
- **Código de Ética Médica (CFM Res. 1.931/2009)** — [portal.cfm.org.br](https://portal.cfm.org.br/)
- **Resolução CFM 1.821/2007 (digitalização de prontuários)** — [gov.br/conarq](https://www.gov.br/conarq/pt-br/legislacao-arquivistica/resolucoes/resolucao-cfm-no-1-821-de-11-de-julho-de-2007)
- **ANVISA — Tratamento de dados pessoais** — [gov.br/anvisa](https://www.gov.br/anvisa/pt-br/acessoainformacao/tratamento-de-dados-pessoais)

### Certificações e boas práticas

- **ISO/IEC 27001** — [iso.org](https://www.iso.org/standard/27001)
- **ISO/IEC 27701** — [iso.org](https://www.iso.org/standard/71670.html)
- **SOC 2 (AICPA Trust Services)** — [aicpa.org](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/trustdataintegritytaskforce)

### Documentação do projeto

- [PRD](PRD.md) — Campos regulatórios, LGPD, certificado, zero-retention
- [ROADMAP_2026](ROADMAP_2026.md) — Cronograma e fases
- [README](README.md) — Índice da documentação
