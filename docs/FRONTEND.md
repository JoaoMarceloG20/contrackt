# Ultrathink — Frontend

**Versão:** 1.0  
**Última atualização:** Janeiro 2026  
**Escopo:** Interface de demonstração (Fase 1), Admin e Chat (Fases 2–3)

---

## 1. Visão Geral

O frontend do Ultrathink cobre a **interface de demonstração** (upload, resultado, hashes), futuras telas de **admin** e a **UI de Chat** (Fase 3). A stack prioriza: tipagem forte, reuso de componentes, integração com o [Design System](DESIGN_SYSTEM.md) e contrato estável com a API.

---

## 2. Runtime, Framework e Build

### 2.1 Stack Principal

| Camada | Tecnologia | Versão mínima | Notas |
|--------|------------|---------------|-------|
| **Runtime e package manager** | Bun | 1.1+ | Instalação de deps, `bun run`, `bun install`; mais rápido que npm/pnpm |
| **Framework** | Next.js | 15 | App Router, SSR/SSG, file-based routing; reuso para Chat (Fase 3) |
| **UI** | React | 18 | Componentes, Hooks; incluído no Next.js |
| **Linguagem** | TypeScript | 5 | `strict: true`; tipos para `ExtractionResult` e API |

### 2.2 Scripts (package.json)

| Script | Uso |
|--------|-----|
| `bun run dev` | Next.js dev server em `http://localhost:3000`; rewrites para proxy da API |
| `bun run build` | Build de produção (`.next/` ou `out/` se static export) |
| `bun run start` | Servir build em produção (`next start`; só se não usar static export) |
| `bun run test` | Vitest (unit + component) ou Jest |
| `bun run test:e2e` | Playwright (opcional) |
| `bun run lint` | ESLint |

### 2.3 Configuração Next.js (exemplo)

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Proxy da API em dev (rewrites)
  async rewrites() {
    return [{ source: '/v1/:path*', destination: 'http://localhost:8000/v1/:path*' }]
  },
  // Para deploy estático (FastAPI servindo out/): output: 'export'
  // output: 'export',
}
export default nextConfig
```

---

## 3. Gerenciamento de Dependências

| Ferramenta | Uso |
|------------|-----|
| **Bun** | Instalação (`bun install`), lockfile (`bun.lockb`), scripts (`bun run`), execução de TS/JS |
| **package.json** | `dependencies`, `devDependencies`, `scripts`, `engines` (opcional: `"bun": ">=1.1"`) |

### 3.1 Engines (recomendado)

```json
"engines": {
  "bun": ">=1.1"
}
```

---

## 4. Estrutura de Código

### 4.1 Árvore de Pastas (Next.js App Router)

```
frontend/
├── app/
│   ├── layout.tsx            # Layout raiz, import globals.css, fontes
│   ├── page.tsx              # Página da demo (upload + resultado)
│   ├── globals.css           # Reset, body, @import tokens
│   └── (Fase 2+: demo/, admin/ como rotas)
├── components/
│   ├── UploadZone.tsx
│   ├── ExtractResult.tsx
│   ├── HashBlock.tsx
│   ├── ConfidenceBadge.tsx
│   ├── MetadataExtracao.tsx
│   └── (Fase 3: ChatInput, ChatMessage, Citation, etc.)
├── lib/
│   └── extract.ts            # postExtract(file, options) -> Promise<ExtractionResult>
├── hooks/
│   └── useExtract.ts         # (opcional) encapsula postExtract + loading + erro
├── types/
│   └── extract.ts            # ExtractionResult, MetadataExtracao, PageData, etc.
├── styles/
│   └── tokens.css            # Variáveis do Design System; import em globals.css
├── public/
│   └── favicon.svg
├── next.config.ts
├── package.json
├── bun.lockb
├── tsconfig.json
├── .env.example
└── .eslintrc.json
```

### 4.2 Convenções

| Regra | Exemplo |
|-------|---------|
| **Componentes** | PascalCase; um componente por arquivo; `ComponentName.tsx` |
| **Hooks** | `use` + PascalCase; `useExtract.ts` |
| **Tipos** | Em `types/` ou no próprio arquivo se local; export em `types/extract.ts` |
| **Estilos** | Tokens em `tokens.css`; componentes usam classes ou CSS modules se necessário |
| **API** | Funções em `api/`; não colocar lógica de UI em `api/` |

---

## 5. Dependências Principais

### 5.1 Produção

| Pacote | Uso |
|--------|-----|
| `next` | Framework (React, roteamento, build, SSR/SSG) |
| `react`, `react-dom` | UI (incluídos como dependência do Next.js) |
| `lucide-react` | Ícones (Upload, FileText, Check, AlertTriangle, Copy, Loader2, Shield) |

### 5.2 Desenvolvimento

| Pacote | Uso |
|--------|-----|
| `typescript` | Tipagem |
| `@types/node`, `@types/react`, `@types/react-dom` | Tipos |
| `@testing-library/react`, `@testing-library/jest-dom` | Testes de componentes |
| `vitest` ou `jest` | Runner de testes, mocks |
| `@playwright/test` | (Opcional) E2E |
| `eslint`, `eslint-config-next` | Lint (Next traz config base) |
| `prettier` | Formatação |

### 5.3 Opcionais

| Pacote | Uso |
|--------|-----|
| `ky` ou `axios` | Retry, timeout, interceptors para `POST /v1/extract` |
| `react-hook-form` | Formulários complexos (Fase 2+) |
| `tailwindcss` | Se adotado; config deve usar tokens do Design System |

---

## 6. Camada de API

### 6.1 Cliente de Extração

```ts
// lib/extract.ts
import type { ExtractionResult, ExtractOptions } from '@/types/extract'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''

export async function postExtract(
  file: File,
  options: ExtractOptions = {}
): Promise<ExtractionResult> {
  const form = new FormData()
  form.append('file', file)
  if (options.document_type) form.append('document_type', options.document_type)
  if (options.include_chat_package != null) {
    form.append('include_chat_package', String(options.include_chat_package))
  }

  const res = await fetch(`${API_BASE}/v1/extract`, {
    method: 'POST',
    body: form
    // headers: Authorization quando houver API Key (Fase 2)
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Erro ${res.status}`)
  }

  return res.json()
}
```

Em dev, com `rewrites` em `next.config.ts` apontando `/v1` para `http://localhost:8000`, usar `API_BASE = ''` (ou `NEXT_PUBLIC_API_URL` vazio) para que o `fetch` use a mesma origem e o rewrite funcione.

### 6.2 Variáveis de Ambiente

| Variável | Uso | Exemplo (dev) |
|---------|-----|----------------|
| `NEXT_PUBLIC_API_URL` | Base da API no cliente; vazio = mesma origem (rewrites em dev) | `''` ou `http://localhost:8000` |

Arquivo `.env.example`:

```
NEXT_PUBLIC_API_URL=
```

### 6.3 Tipos (types/extract.ts)

```ts
export interface PageData {
  page_number: number
  text: Array<{ content: string; confidence: number }>
  low_confidence_alert: boolean
}

export interface MetadataExtracao {
  confianca_geral: number
  campos_baixa_confianca: string[]
  campos_nao_encontrados: string[]
  paginas_processadas: number
  tempo_processamento_ms: number
}

export interface ExtractionResult {
  data: { pages: PageData[]; full_text?: string }
  document_hash: string
  result_hash: string
  confidence: number
  processing_time_ms: number
  metadata_extracao: MetadataExtracao
  chat_package: null | object
}
```

---

## 7. Estado e Roteamento

### 7.1 Fase 1 (Demo)

- **Estado local (useState):** `file`, `result`, `loading`, `error`. Um `useExtract` ou lógica em `app/page.tsx` (ou em um client component) é suficiente.
- **Roteamento:** Next.js usa **file-based routing**. A demo fica em `app/page.tsx` (rota `/`). Não é necessário React Router.

### 7.2 Fase 2+

- **Rotas:** `app/demo/page.tsx` → `/demo`; `app/admin/page.tsx` → `/admin`; etc.
- **Estado global (se necessário):** Context ou Zustand para preferências (ex. `document_type` padrão, `include_chat_package`).

---

## 8. Estilos e Design System

### 8.1 Referência

O design visual está em [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md): tipografia, cores, espaçamento, componentes (botões, inputs, cards, badges, bloco de hash, área de upload).

### 8.2 Implementação no Código

- **`styles/tokens.css`:** Variáveis `--color-*`, `--space-*`, `--font-*`, `--radius-*`, `--text-*`. Em `app/globals.css`: `@import '../styles/tokens.css'` (ou path relativo ao `globals.css`).
- **`app/globals.css`:** Reset mínimo, `body { font-family: var(--font-body); }`, `box-sizing: border-box`. Importar em `app/layout.tsx`: `import './globals.css'`.
- **Componentes:** Usar as variáveis nos estilos (inline, CSS modules ou classes). Ex.: `backgroundColor: 'var(--color-primary)'`, `padding: 'var(--space-4)'`, `fontFamily: 'var(--font-mono)'` para hashes.
- **Ícones:** `lucide-react`; tamanhos 16, 20, 24; cor `currentColor` ou `var(--color-text-muted)`.

### 8.3 Fontes

Em `app/layout.tsx`, usar `next/font` (recomendado) ou link para Google Fonts:

```tsx
// app/layout.tsx
import { IBM_Plex_Sans, JetBrains_Mono } from 'next/font/google'

const ibmPlex = IBM_Plex_Sans({ weight: ['400', '500'], subsets: ['latin'] })
const jetbrains = JetBrains_Mono({ weight: ['400', '500'], subsets: ['latin'] })

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className={ibmPlex.className}>
      <body>{children}</body>
    </html>
  )
}
```

Para Instrument Sans ou Source Serif (Design System / Harvey), usar `next/font/google` se disponível, ou `<link>` em `layout.tsx` dentro de `<head>`.

---

## 9. Testes

### 9.1 Unit e Componentes (Vitest)

| Alvo | Ferramenta | Exemplo |
|------|------------|---------|
| `api/extract.ts` | Vitest + `vi.mock('...', () => ({ fetch: ... }))` | `postExtract` retorna `ExtractionResult` ou lança |
| `utils/format.ts` | Vitest | Funções puras |
| Componentes | Vitest + `@testing-library/react` | `UploadZone` com arquivo selecionado; `HashBlock` com botão copiar; `ConfidenceBadge` por faixa |

### 9.2 E2E (Playwright, opcional)

- Fluxo: escolher PDF → upload → aguardar → ver resultado, hashes e `metadata_extracao`.
- Rodar com `bun run test:e2e`; config em `playwright.config.ts`. Garantir que o app esteja em `http://localhost:3000` (Next) e que a API ou o mock esteja acessível.

### 9.3 Cobertura

- Mínimo: `api/extract`, `format`, e componentes principais; E2E para happy path na Fase 1.

---

## 10. Build e Deploy

### 10.1 Build

- `bun run build` → `.next/` (modo padrão) ou `out/` (com `output: 'export'` em `next.config.ts` para export estático).
- Variáveis `NEXT_PUBLIC_*` são embutidas em build-time; não colocar secrets.

### 10.2 Deploy

- **Opção A — Static export (FastAPI servindo):** Em `next.config.ts`, `output: 'export'`. O build gera `out/` com HTML, JS e CSS estáticos. FastAPI com `StaticFiles(directory="frontend/out", html=True)` em `/` ou `/demo`; proxy `/v1` para a API. Ou nginx servindo `out/` e fazendo proxy de `/v1` para a API.
- **Opção B — Next como serviço:** `bun run start` (ou `next start`) em produção; Next escuta em 3000. Nginx (ou docker-compose) faz proxy de `/` para 3000 e de `/v1` para 8000. Permite SSR, API Routes e recursos server-side.

### 10.3 Docker (frontend no mesmo image da API, com static export)

Exemplo de stage no `Dockerfile`:

```dockerfile
FROM oven/bun:1-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/bun.lockb* ./
RUN bun install --frozen-lockfile
COPY frontend/ .
# next.config com output: 'export'
RUN bun run build
# ... depois: COPY --from=frontend /app/frontend/out /app/static
```

Se não usar static export, o stage de frontend produz `.next/` e a imagem final precisa de Node/Bun para `bun run start`; nesse caso, convém rodar Next como serviço separado no `docker-compose`.

---

## 11. Ferramentas de Desenvolvimento

| Ferramenta | Uso |
|------------|-----|
| **Bun** | `bun install`, `bun run dev`, `bun run build`, `bun run test` |
| **ESLint** | `eslint-config-next` (Next traz config base); `eslint-config-prettier` para evitar conflito |
| **Prettier** | Formatação; integração com ESLint |
| **pre-commit** (opcional) | `lint-staged` com `eslint` e `prettier` nos arquivos staged |

---

## 12. Segurança (Frontend)

| Aspecto | Prática |
|---------|---------|
| **Secrets** | Nunca commitar `NEXT_PUBLIC_*` com API keys; em Fase 2, API Key no backend ou em proxy, não no bundle |
| **CORS** | Backend restringe origens em produção; em dev, `localhost` permitido |
| **CSP** | (Fase 2+) Content-Security-Policy via servidor para mitigar XSS |
| **Dados sensíveis** | Não persistir `data` ou `file` em `localStorage` sem necessidade; hashes são ok para exibição |

---

## 13. Acessibilidade

- **Contraste:** Cores do [Design System](DESIGN_SYSTEM.md) atendem WCAG AA.
- **Foco:** `:focus-visible` e `outline` em botões, inputs e links.
- **Labels:** Todo `input` com `<label>` ou `aria-label`; `aria-describedby` para mensagens de erro.
- **Carregamento:** `aria-busy="true"` na área de resultado durante o request; `aria-live="polite"` para mensagem de sucesso/erro.
- **Hashes:** Botão “Copiar” com `aria-label` descritivo.

---

## 14. Fluxo de Dados (Arquitetura)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   UploadZone │────▶│  useExtract   │────▶│ lib/extract  │
│   (file)     │     │  ou page      │     │ postExtract  │
└──────────────┘     └───────┬───────┘     └──────┬───────┘
                            │                     │
                            │                     │ fetch /v1/extract
                            │                     ▼
                            │             ┌──────────────┐
                            │             │   Backend    │
                            │             │   FastAPI    │
                            │             └──────┬───────┘
                            │                     │
                            │◀───────────────────┘
                            │   ExtractionResult
                            ▼
┌──────────────────────────────────────────────────────────┐
│  ExtractResult, HashBlock, MetadataExtracao, Badges     │
└──────────────────────────────────────────────────────────┘
```

---

## 15. Resumo por Fase (Frontend)

| Fase | Funcionalidades | Stack |
|------|-----------------|-------|
| **1** | Upload, resultado por página, hashes, `metadata_extracao`, badges de confiança | Next.js 15, Bun, React 18, TS, tokens.css, lucide-react |
| **2** | (Opc.) Rotas `/demo`, `/admin`; preferências; integração com batch (polling ou webhook UI) | File-based routing (app/demo/, app/admin/); estado global se necessário |
| **3** | Chat: input, mensagens, citações; busca por contrato; histórico | + componentes Chat; `chat_package` na API |
| **4+** | Novos fluxos (documentoscopia, export, etc.) | Estender componentes e rotas |

---

## 16. Referências

- [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) — Tokens, componentes, acessibilidade
- [STACK.md](STACK.md) — Visão full-stack, infra, testes
- [PRD.md](PRD.md) — Produto, API, Chat, certificados
