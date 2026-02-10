# Ultrathink — Design System

**Versão:** 1.0  
**Última atualização:** Janeiro 2026  
**Escopo:** Interface de demonstração (Fase 1), Admin e Chat (Fases 2–3)

---

## 1. Visão e Princípios

### 1.1 Propósito

O Design System do Ultrathink serve interfaces B2B para **bancos, hospitais e fintechs**. A marca deve transmitir:

- **Confiabilidade** — extração precisa, rastreável, compliance
- **Segurança e LGPD** — zero-retention, hashes, certificados
- **Profissionalismo** — utilitário, sem ruído visual
- **Clareza** — dados, métricas e estados de confiança legíveis

### 1.2 Direção Estética

**Tom:** Refinado, industrial, utilitário.

- **Refinado:** Tipografia cuidada, espaçamento consistente, hierarquia clara.
- **Industrial:** Paleta contida, superfícies neutras, bordas definidas, grid estável.
- **Utilitário:** Prioridade à legibilidade e à função; decoração só quando reforça a mensagem (ex.: ícones de confiança, indicadores de hash).

Evitar: gradientes roxo/lilás genéricos, fontes óbvias (Inter, Roboto, Arial), layouts “template” de SaaS.

### 1.3 Princípios de Design

| Princípio | Aplicação |
|-----------|-----------|
| **Clareza sobre ruído** | Menos ornamentos; cada elemento justifica sua presença. |
| **Dados em destaque** | Texto extraído, hashes, confiança e métricas são protagonistas. |
| **Estados óbvios** | Sucesso, erro, carregamento e baixa confiança devem ser imediatamente reconhecíveis. |
| **Acessibilidade** | Contraste WCAG AA, foco visível, labels em formulários, suporte a teclado. |
| **Responsividade** | Demo e admin usáveis em desktop e tablet; mobile como secundário na Fase 1. |

---

## 2. Tipografia

### 2.1 Famílias

| Uso | Família | Pesos | Fallback | Origem |
|-----|---------|-------|----------|--------|
| **Títulos e UI** | **Instrument Sans** | 400, 500, 600 | system-ui, sans-serif | Google Fonts |
| **Corpo e dados** | **IBM Plex Sans** | 400, 500 | system-ui, sans-serif | Google Fonts |
| **Monospace (hashes, código)** | **JetBrains Mono** | 400, 500 | ui-monospace, monospace | Google Fonts |

- **Instrument Sans:** geométrica, moderna, boa para headlines e labels; evita o “Inter/Roboto”.
- **IBM Plex Sans:** neutra, legível em blocos de texto e tabelas.
- **JetBrains Mono:** hashes, IDs, trechos de código e valores técnicos.

### 2.2 Escala (Modular Scale 1.25)

| Nome | Tamanho | Line-height | Uso |
|------|---------|-------------|-----|
| `--text-xs` | 0.75rem (12px) | 1.33 | Legendas, labels secundários, metadados |
| `--text-sm` | 0.875rem (14px) | 1.43 | Corpo secundário, placeholders, células de tabela |
| `--text-base` | 1rem (16px) | 1.5 | Corpo principal, inputs |
| `--text-lg` | 1.125rem (18px) | 1.44 | Destaque, primeiras linhas de cards |
| `--text-xl` | 1.25rem (20px) | 1.3 | Subtítulos de seção |
| `--text-2xl` | 1.5rem (24px) | 1.25 | Títulos de card ou painel |
| `--text-3xl` | 1.875rem (30px) | 1.2 | Títulos de página |
| `--text-4xl` | 2.25rem (36px) | 1.15 | Hero, landing (se houver) |

### 2.3 Pesos

- **400** — corpo, texto longo
- **500** — labels, botões secundários, ênfase leve
- **600** — títulos de seção, botões primários, estados ativos

### 2.4 Variáveis CSS (exemplo)

```css
:root {
  --font-display: "Instrument Sans", system-ui, sans-serif;
  --font-body: "IBM Plex Sans", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;

  --line-tight: 1.25;
  --line-normal: 1.5;
  --line-relaxed: 1.6;
}
```

---

## 3. Cores

### 3.1 Paleta Principal (Tema Claro)

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-primary` | `#0D7377` | Ações primárias, links, indicadores positivos, “processado com sucesso” |
| `--color-primary-hover` | `#0a5c5f` | Hover em botões e links primários |
| `--color-primary-muted` | `#e6f2f2` | Fundos de destaque leve, badges de confiança alta |
| `--color-surface` | `#FFFFFF` | Fundo de cards, modais, inputs |
| `--color-background` | `#F5F6F8` | Fundo da página |
| `--color-border` | `#E2E4E8` | Bordas de inputs, cards, tabelas |
| `--color-text` | `#1a1d21` | Texto principal |
| `--color-text-muted` | `#5c6269` | Texto secundário, placeholders |
| `--color-text-faint` | `#8e949c` | Metadados, desabilitado |

### 3.2 Cores Semânticas

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-success` | `#0d9488` | Confiança alta, sucesso, “documento processado” |
| `--color-success-bg` | `#ccfbf1` | Fundo de alertas/badges de sucesso |
| `--color-warning` | `#c17a0b | Baixa confiança, revisão recomendada |
| `--color-warning-bg` | `#fef3c7` | Fundo de avisos |
| `--color-error` | `#b91c1c` | Erro de processamento, validação, falha de upload |
| `--color-error-bg` | `#fee2e2` | Fundo de mensagens de erro |
| `--color-info` | `#0369a1` | Informação neutra, hashes, certificado |
| `--color-info-bg` | `#e0f2fe` | Fundo de blocos de hash/certificado |

### 3.3 Tema Escuro (opcional para Fase 2+)

| Token | Hex |
|-------|-----|
| `--color-background-dark` | `#0f1114` |
| `--color-surface-dark` | `#1a1d21` |
| `--color-border-dark` | `#2d3239` |
| `--color-text-dark` | `#f0f2f4` |
| `--color-text-muted-dark` | `#9ca3af` |
| `--color-primary-dark` | `#14b8a6` |

### 3.4 Variáveis CSS

```css
:root {
  --color-primary: #0d7377;
  --color-primary-hover: #0a5c5f;
  --color-primary-muted: #e6f2f2;
  --color-surface: #ffffff;
  --color-background: #f5f6f8;
  --color-border: #e2e4e8;
  --color-text: #1a1d21;
  --color-text-muted: #5c6269;
  --color-text-faint: #8e949c;

  --color-success: #0d9488;
  --color-success-bg: #ccfbf1;
  --color-warning: #c17a0b;
  --color-warning-bg: #fef3c7;
  --color-error: #b91c1c;
  --color-error-bg: #fee2e2;
  --color-info: #0369a1;
  --color-info-bg: #e0f2fe;
}
```

---

## 4. Espaçamento e Grid

### 4.1 Escala de Espaçamento (base 4px)

| Token | Valor | Uso |
|-------|-------|-----|
| `--space-1` | 4px | Entre ícone e texto, padding mínimo |
| `--space-2` | 8px | Entre itens inline, padding de badge |
| `--space-3` | 12px | Padding interno de botões pequenos |
| `--space-4` | 16px | Padding de cards, gaps em formulários |
| `--space-5` | 20px | Entre seções pequenas |
| `--space-6` | 24px | Entre blocos de conteúdo |
| `--space-8` | 32px | Entre seções de página |
| `--space-10` | 40px | Margem de layout |
| `--space-12` | 48px | Separação de blocos grandes |
| `--space-16` | 64px | Margem de página em desktop |

### 4.2 Grid

- **Desktop:** 12 colunas, gutter 24px, max-width do conteúdo 1200px.
- **Tablet:** 8 colunas, gutter 20px.
- **Mobile (Fase 2+):** 4 colunas, gutter 16px.

### 4.3 Border Radius

| Token | Valor | Uso |
|-------|-------|-----|
| `--radius-sm` | 4px | Badges, chips, inputs |
| `--radius-md` | 8px | Botões, cards pequenos |
| `--radius-lg` | 12px | Cards, modais |
| `--radius-xl` | 16px | Painéis, blocos de hash/certificado |

---

## 5. Componentes

### 5.1 Botões

| Variante | Background | Texto | Borda | Uso |
|----------|------------|-------|-------|-----|
| **Primário** | `--color-primary` | branco | nenhuma | Ação principal (Processar, Enviar) |
| **Secundário** | transparente | `--color-text` | `--color-border` | Cancelar, Voltar |
| **Ghost** | transparente | `--color-text-muted` | nenhuma | Ações terciárias |
| **Perigo** | `--color-error` | branco | nenhuma | Excluir, limpar (quando houver) |

- Altura: 40px (md), 36px (sm). Padding horizontal: 16px (md), 12px (sm).
- Hover: escurecer levemente ou `--color-primary-hover`.
- Disabled: opacidade 0.5, cursor not-allowed.

### 5.2 Inputs

- Altura: 40px. Padding: 12px 16px.
- Borda: 1px `--color-border`, `--radius-md`.
- Focus: outline 2px `--color-primary`, offset 2px.
- Placeholder: `--color-text-faint`.
- Erro: borda `--color-error`, texto de ajuda em `--color-error`.

### 5.3 Cards

- Background: `--color-surface`. Borda: 1px `--color-border`. `--radius-lg`.
- Padding: `--space-6`. Sombra leve (opcional): `0 1px 3px rgba(0,0,0,0.06)`.
- Uso: resultado por página, bloco de hashes, resumo de `metadata_extracao`.

### 5.4 Badges (Confiança e Estado)

| Estado | Cor de fundo | Cor de texto |
|--------|---------------|--------------|
| Alta confiança (≥ 0.9) | `--color-success-bg` | `--color-success` |
| Média (0.7–0.9) | `--color-warning-bg` | `--color-warning` |
| Baixa (&lt; 0.7) | `--color-error-bg` | `--color-error` |
| Neutro (info) | `--color-info-bg` | `--color-info` |

- Padding: 4px 10px. `--radius-sm`. `--text-sm`, peso 500.

### 5.5 Bloco de Hash / Certificado

- Fundo: `--color-info-bg` ou `--color-surface` com borda `--color-info`.
- Fonte: `--font-mono`, `--text-sm`. Hash em uma linha, truncado no fim com ellipsis; tooltip ou “copiar” com valor completo.
- Ícone de “copiar” discreto à direita.

### 5.6 Área de Upload

- Borda: 2px dashed `--color-border`. `--radius-lg`. Padding: `--space-8`.
- Estado idle: texto “Arraste o PDF ou clique para selecionar” em `--color-text-muted`.
- Hover/drag-over: borda `--color-primary`, fundo `--color-primary-muted`.
- Após seleção: nome do arquivo, tamanho, botão “Remover”.

### 5.7 Trecho de Baixa Confiança (texto extraído)

- Fundo: `--color-warning-bg` com padding 2px 6px e `--radius-sm`.
- Ou sublinhado tracejado `--color-warning`. Tooltip: “Confiança: X%”.

---

## 6. Ícones

- **Biblioteca recomendada:** Lucide React (`lucide-react`) ou Phosphor (`@phosphor-icons/react`).
- Tamanhos: 16px (inline com texto), 20px (botões), 24px (headers, empty states).
- Cor: herdar do texto ou `--color-text-muted`; primário em botões primários.
- Ícones essenciais: `Upload`, `FileText`, `Check`, `AlertTriangle`, `X`, `Copy`, `Loader2` (spinner), `Shield` (certificado/segurança), `Hash`.

---

## 7. Motion

- **Transições:** 150–200ms `ease-out` para hover, focus, mudança de cor/opacidade.
- **Carregamento:** spinner (Loader2) ou skeleton para a área de resultado; evitar “flash” brusco.
- **Upload:** feedback imediato em drag-over; após processamento, transição suave ao exibir o resultado (opacity ou slide curto).
- **Erro:** shake leve (opcional) no campo ou card de erro.
- Evitar animações longas ou decorativas na Fase 1.

---

## 8. Responsividade

### 8.1 Breakpoints

| Nome | Min-width | Uso |
|------|-------------|-----|
| `sm` | 640px | Mobile landscape, tablet portrait |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop |
| `xl` | 1280px | Desktop largo |

### 8.2 Comportamento da Demo (Fase 1)

- **&lt; 768px:** Upload em coluna única; resultado em abas ou accordion (Página 1, 2, …); hashes em bloco abaixo, com quebra de linha.
- **≥ 768px:** Upload à esquerda ou no topo; resultado (páginas) em coluna principal; painel lateral ou seção colapsável para hashes e `metadata_extracao`.

---

## 9. Acessibilidade

- **Contraste:** Mínimo 4.5:1 para texto normal; 3:1 para texto grande e UI.
- **Foco:** Outline visível em todos os elementos interativos (botões, inputs, links).
- **Labels:** Todo input associado a `<label>`; `aria-describedby` para mensagens de erro ou ajuda.
- **Estado de carregamento:** `aria-busy="true"` e `aria-live="polite"` na área de resultado.
- **Hashes longos:** `aria-label` em botão “Copiar” com descrição do que será copiado.

---

## 10. Tokens CSS Consolidados (resumo)

Arquivo sugerido: `frontend/src/styles/tokens.css` (ou equivalente).

```css
:root {
  /* Typography */
  --font-display: "Instrument Sans", system-ui, sans-serif;
  --font-body: "IBM Plex Sans", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  /* Colors - Light */
  --color-primary: #0d7377;
  --color-primary-hover: #0a5c5f;
  --color-primary-muted: #e6f2f2;
  --color-surface: #ffffff;
  --color-background: #f5f6f8;
  --color-border: #e2e4e8;
  --color-text: #1a1d21;
  --color-text-muted: #5c6269;
  --color-text-faint: #8e949c;
  --color-success: #0d9488;
  --color-success-bg: #ccfbf1;
  --color-warning: #c17a0b;
  --color-warning-bg: #fef3c7;
  --color-error: #b91c1c;
  --color-error-bg: #fee2e2;
  --color-info: #0369a1;
  --color-info-bg: #e0f2fe;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  /* Motion */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --ease-out: cubic-bezier(0.33, 1, 0.68, 1);
}
```

---

## 11. Referências e Manutenção

- **Figma (opcional):** Criar biblioteca com componentes e tokens para design e dev.
- **Changelog:** Alterações de tokens ou componentes devem ser registradas neste documento (versão e data).
- **Escopo futuro:** Tema escuro, componentes de Chat (Fase 3), tabelas de contratos (Fase 2) e módulo de Documentoscopia (Fase 6) devem estender este Design System sem quebrar a base.
