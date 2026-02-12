# PoC — Features de Performance e Roteamento OCR

> **Objetivo**: Monitorar tempo por página, paralelizar processamento, usar GPU (RTX 5080 16GB VRAM) e criar um router que direciona manuscritos para OCR pesado na GPU e texto digital para OCR leve na CPU.

---

## Índice

1. [Visão Geral do Estado Atual](#1-visão-geral-do-estado-atual)
2. [Feature 1 — Monitorar Tempo por Página](#2-feature-1--monitorar-tempo-por-página)
3. [Feature 2 — Paralelizar Processamento de Páginas](#3-feature-2--paralelizar-processamento-de-páginas)
4. [Feature 3 — Usar GPU (RTX 5080, 16GB VRAM)](#4-feature-3--usar-gpu-rtx-5080-16gb-vram)
5. [Feature 4 — Router: Handwriting → GPU / Digital → CPU](#5-feature-4--router-handwriting--gpu--digital--cpu)
6. [Fluxo Completo do Pipeline](#6-fluxo-completo-do-pipeline)
7. [Ordem de Implementação Recomendada](#7-ordem-de-implementação-recomendada)
8. [Checklist Pré-Implementação](#8-checklist-pré-implementação)

---

## 1. Visão Geral do Estado Atual

O pipeline atual em `app/services/ocr.py`:

- **Um único engine** PaddleOCR (`use_angle_cls=True, lang="pt"`)
- Roda **100% na CPU** (dependência é `paddlepaddle`, não `paddlepaddle-gpu`)
- Processamento **sequencial** — página por página no loop `for`
- **Sem métricas de tempo** por página — só o tempo total no endpoint
- **Sem distinção** entre texto digital e manuscrito

### Dependências atuais relevantes (pyproject.toml)

```
paddleocr>=3.3.2
paddlepaddle>=3.2.2
opencv-python>=4.12.0.88
pymupdf>=1.26.7
```

---

## 2. Feature 1 — Monitorar Tempo por Página

> **Complexidade**: Baixa (~15 minutos)
> **Impacto**: Alto — dá a baseline para medir todas as outras otimizações

### O que fazer

Envolver o processamento de cada página com `time.perf_counter()` (mais preciso que `time.time()` para medir intervalos curtos).

### Onde mexer

Arquivo: `app/services/ocr.py`, dentro do loop principal (linhas 21-56).

### Orientação passo a passo

1. **Importar `time`** no topo do arquivo
2. **Capturar `time.perf_counter()`** antes do `get_pixmap` e depois do OCR terminar
3. **Adicionar o tempo ao `page_data` dict** — campo `"processing_time_ms"` convertendo com `round((end - start) * 1000, 2)`
4. **Separar sub-etapas** para diagnóstico granular:
   - Tempo de rasterização (pixmap → numpy)
   - Tempo de OCR puro
   - Isso será **crucial** quando o router existir, para saber onde está o gargalo

### Exemplo conceitual

```python
import time

# Dentro do loop de páginas:
page_start = time.perf_counter()

# Rasterização
raster_start = time.perf_counter()
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
image = ...  # conversão para numpy
raster_time = time.perf_counter() - raster_start

# OCR
ocr_start = time.perf_counter()
result = ocr_engine.ocr(image)
ocr_time = time.perf_counter() - ocr_start

total_page_time = time.perf_counter() - page_start

page_data["processing_time_ms"] = round(total_page_time * 1000, 2)
page_data["raster_time_ms"] = round(raster_time * 1000, 2)
page_data["ocr_time_ms"] = round(ocr_time * 1000, 2)
```

### Dica de arquitetura

Considere criar um `dataclass` ou `TypedDict` para `page_data` em vez de montar o dict manualmente:

```python
from dataclasses import dataclass, field

@dataclass
class PageResult:
    page_number: int
    text: list[dict] = field(default_factory=list)
    low_confidence_alert: bool = False
    processing_time_ms: float = 0.0
    raster_time_ms: float = 0.0
    ocr_time_ms: float = 0.0
    engine_used: str = "paddle_cpu"  # útil para o router depois
```

Isso vai facilitar muito quando existirem múltiplos caminhos de processamento (GPU/CPU).

---

## 3. Feature 2 — Paralelizar Processamento de Páginas

> **Complexidade**: Média-Alta
> **Impacto**: Alto — reduz tempo total linearmente com número de workers

### ⚠️ Armadilhas importantes

O PaddleOCR **não é thread-safe** por padrão. Se você simplesmente jogar `concurrent.futures.ThreadPoolExecutor` no loop de páginas, vai ter race conditions no modelo.

### Estratégias possíveis

#### Opção A — `ProcessPoolExecutor` (mais seguro, mais simples)

- Cada processo carrega sua própria instância do modelo
- **Problema**: alto consumo de memória RAM (cada worker carrega o modelo inteiro)
- Bom para CPU, ruim para GPU (competiriam pela VRAM)

#### Opção B — Pool de engines com `ThreadPoolExecutor` (recomendado para CPU)

- Crie N instâncias do `PaddleOCR` na inicialização
- Use uma `queue.Queue` como pool de engines
- Cada thread pega um engine do pool, usa, e devolve
- Isso é o **Object Pool Pattern**

```python
import queue
from concurrent.futures import ThreadPoolExecutor

class OCREnginePool:
    def __init__(self, size: int = 4):
        self._pool = queue.Queue(maxsize=size)
        for _ in range(size):
            engine = PaddleOCR(use_angle_cls=True, lang="pt")
            self._pool.put(engine)
    
    def acquire(self) -> PaddleOCR:
        return self._pool.get()  # bloqueia se não tem engine disponível
    
    def release(self, engine: PaddleOCR):
        self._pool.put(engine)
```

#### Opção C — Separar rasterização de OCR (melhor arquitetura) ✅ RECOMENDADA

- **Fase 1 (paralela, CPU):** Rasterize todas as páginas em imagens numpy usando threads (PyMuPDF libera o GIL)
- **Fase 2 (sequencial ou batched):** Passe as imagens pelo OCR (GPU batch ou CPU pool)

### Orientação concreta

Para o caso deste projeto, a **Opção C** é recomendada porque se encaixa perfeitamente com o router GPU/CPU da Feature 4.

#### Passo 1 — Separar a função em etapas

Extraia de `extract_pdf` duas funções:

```python
def rasterize_page(doc: fitz.Document, page_index: int) -> np.ndarray:
    """Converte uma página do PDF em imagem numpy."""
    page = doc.load_page(page_index)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    image_bytes = np.frombuffer(pix.samples, dtype=np.uint8)
    image = image_bytes.reshape(pix.h, pix.w, pix.n)
    
    if pix.n == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif pix.n == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    
    return image

def ocr_page(image: np.ndarray, engine: PaddleOCR) -> list[dict]:
    """Roda OCR numa imagem e retorna lista de textos com confidence."""
    result = engine.ocr(image)
    # ... parse dos resultados
    return parsed_texts
```

#### Passo 2 — Paralelizar a rasterização

```python
from concurrent.futures import ThreadPoolExecutor

def rasterize_all_pages(doc: fitz.Document) -> list[np.ndarray]:
    """Rasteriza todas as páginas em paralelo."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(rasterize_page, doc, i)
            for i in range(len(doc))
        ]
        return [f.result() for f in futures]
```

#### Passo 3 — OCR em paralelo ou batch

- **Na CPU**: use o pool de engines (Opção B) + ThreadPoolExecutor
- **Na GPU**: pode usar batch mode ou fila sequencial (a GPU já paraleliza internamente)

### Nota sobre thread-safety do PyMuPDF

O `fitz.Document` é seguro para **leitura simultânea de páginas diferentes** em threads. Cada thread pode chamar `doc.load_page(i)` com índices diferentes sem problemas. Porém, se quiser ser mais cauteloso, extraia os bytes de cada página no thread principal antes de rasterizar.

---

## 4. Feature 3 — Usar GPU (RTX 5080, 16GB VRAM)

> **Complexidade**: Média
> **Impacto**: Alto — OCR na GPU é 5-10x mais rápido que na CPU

### Mudança de dependência

Atualmente o `pyproject.toml` usa `paddlepaddle` (versão CPU). Para GPU:

1. **Remover** `paddlepaddle` do `pyproject.toml`
2. **Adicionar** `paddlepaddle-gpu` com a versão CUDA correta
3. A RTX 5080 é arquitetura Blackwell — precisa de **CUDA 12.x** (provavelmente 12.6+)

#### Verificar CUDA instalado

```bash
# Verifica a versão do driver e CUDA máximo suportado
nvidia-smi

# Verifica a versão do toolkit CUDA instalado
nvcc --version
```

#### ⚠️ Alerta: RTX 5080 é muito nova

O PaddlePaddle pode não ter suporte nativo para a arquitetura Blackwell ainda. Verifique:

- [PaddlePaddle GPU compatibility](https://www.paddlepaddle.org.cn/install/quick)
- Se não houver suporte, o **PyTorch** (usado pelo TrOCR) provavelmente já suporta via CUDA 12.8+

#### Instalação do PaddlePaddle GPU

```bash
# Exemplo para CUDA 12.x (ajuste conforme sua versão)
pip install paddlepaddle-gpu==3.2.2 -f https://www.paddlepaddle.org.cn/whl/linux/cudnnin/stable.html
```

### Configurar o engine para GPU

No `PaddleOCR`, basta passar `use_gpu=True`:

```python
gpu_engine = PaddleOCR(
    use_angle_cls=True,
    lang="pt",
    use_gpu=True,
    gpu_mem=8000,  # limitar memória GPU em MB (opcional)
)
```

### Gerenciamento de VRAM (16GB disponíveis)

| Componente | VRAM estimada |
|------------|---------------|
| PaddleOCR GPU (1 instância) | ~1-2 GB |
| TrOCR base (1 instância) | ~1-2 GB |
| TrOCR large (1 instância) | ~3-4 GB |
| Imagens em processamento | ~0.5-1 GB |
| **Overhead CUDA** | ~1-2 GB |
| **Total estimado** | **~5-8 GB** |
| **Margem livre** | **~8-11 GB** |

Com 16GB você está confortável para rodar ambos os engines simultaneamente.

### Monitoramento durante desenvolvimento

```bash
# Em um terminal separado, monitore VRAM em tempo real
watch -n 1 nvidia-smi

# Ou use o Python:
# pip install gputil
import GPUtil
gpus = GPUtil.getGPUs()
print(f"VRAM usada: {gpus[0].memoryUsed}MB / {gpus[0].memoryTotal}MB")
```

---

## 5. Feature 4 — Router: Handwriting → GPU / Digital → CPU

> **Complexidade**: Alta
> **Impacto**: Muito Alto — otimiza custo computacional e qualidade de extração

### Sub-problema 1: Como detectar se uma página tem texto manuscrito?

#### Abordagem A — Heurística com texto nativo do PDF (rápido, sem modelo extra) ✅ COMEÇAR POR AQUI

- Extraia o texto "nativo" do PDF usando PyMuPDF (`page.get_text()`) **antes** do OCR
- Se a página tem texto extraível nativamente → é texto digital, vai para CPU
- Se a página não tem texto extraível → provavelmente é manuscrito/escaneado, vai para GPU

```python
def classify_page(page: fitz.Page) -> str:
    """Classifica se a página é digital ou manuscrita/escaneada."""
    native_text = page.get_text().strip()
    
    # Se tem texto nativo substancial, é digital
    if len(native_text) > 50:
        return "digital"
    
    return "handwritten"
```

- **Vantagem**: custo computacional zero, funciona como pré-filtro
- **Limitação**: PDFs escaneados digitalmente (ex: scanner de impressora) seriam classificados como "manuscritos" mesmo sendo texto impresso. Na prática, isso é aceitável porque o OCR pesado na GPU vai lidar bem com ambos.

#### Abordagem B — Classificador leve de imagem (mais preciso)

- Treine ou use um classificador binário simples (ResNet18 ou MobileNet) que classifica a imagem como "manuscrito" ou "digital/impresso"
- Roda na CPU em ~10-50ms por página
- Mais preciso, mas requer um modelo extra e dados de treino

#### Abordagem C — Heurística híbrida (pragmática, recomendada após PoC)

1. Tente extrair texto nativo com `page.get_text()`
2. Se extraiu texto → OCR leve na CPU (só para validação/confidence)
3. Se **não** extraiu texto → rode o OCR leve primeiro, verifique o confidence score médio
4. Se confidence < threshold (ex: 0.70) → reprocessa na GPU com OCR pesado
5. Se confidence >= threshold → aceita o resultado da CPU

```python
def classify_with_fallback(page: fitz.Page, image: np.ndarray, cpu_engine) -> str:
    """Classificação com fallback baseado em confidence."""
    # Nível 1: texto nativo
    native_text = page.get_text().strip()
    if len(native_text) > 50:
        return "digital"
    
    # Nível 2: OCR rápido na CPU + análise de confidence
    quick_result = cpu_engine.ocr(image)
    avg_confidence = compute_avg_confidence(quick_result)
    
    if avg_confidence >= 0.70:
        return "digital"  # texto impresso escaneado, CPU dá conta
    
    return "handwritten"  # confidence baixa, mandar para GPU
```

### Sub-problema 2: Qual OCR "pesado" usar na GPU?

| Engine | Prós | Contras |
|--------|------|---------|
| PaddleOCR com `use_gpu=True` | Já integrado no projeto | Não é especialista em manuscrito |
| **TrOCR** (Microsoft, via HuggingFace) | Estado da arte para manuscrito, PyTorch | Nova dependência (`transformers`) |
| EasyOCR com GPU | Boa qualidade, fácil setup | Mais lento que PaddleOCR |

**Recomendação**: **TrOCR na GPU** para manuscritos. Isso já está no backlog como `P0-OPT-1: Integrar TrOCR para manuscritos`. É baseado em PyTorch, que tem excelente suporte CUDA.

#### Setup do TrOCR (conceitual)

```python
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

class TrOCREngine:
    def __init__(self, model_name: str = "microsoft/trocr-base-handwritten"):
        self.processor = TrOCRProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.model.to("cuda")  # Mover para GPU
    
    def ocr(self, image: np.ndarray) -> list[dict]:
        """Processa uma imagem e retorna textos com confidence."""
        # TrOCR espera imagens PIL
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        pixel_values = self.processor(
            images=pil_image, return_tensors="pt"
        ).pixel_values.to("cuda")
        
        generated_ids = self.model.generate(pixel_values)
        text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        
        return [{"content": text, "confidence": 0.0}]  # TrOCR não dá confidence nativo
```

> **Nota**: O TrOCR processa **linhas de texto**, não páginas inteiras. Você precisaria de um detector de linhas (ex: o próprio PaddleOCR para detecção de bboxes) + TrOCR para reconhecimento. Isso é um pipeline de 2 estágios.

### Sub-problema 3: Arquitetura do Router

Criar um módulo novo: `app/services/page_router.py`

```python
# Conceito de design — adaptar conforme implementação real

class PageRouter:
    def __init__(self):
        # Engine leve para texto digital (CPU)
        self.cpu_engine = PaddleOCR(
            use_angle_cls=True,
            lang="pt",
            use_gpu=False,
        )
        
        # Engine pesado para manuscritos (GPU)
        self.gpu_engine = TrOCREngine(
            model_name="microsoft/trocr-base-handwritten"
        )
    
    def classify(self, page: fitz.Page, image: np.ndarray) -> str:
        """Retorna 'digital' ou 'handwritten'."""
        native_text = page.get_text().strip()
        if len(native_text) > 50:
            return "digital"
        return "handwritten"
    
    def process(self, page: fitz.Page, image: np.ndarray) -> PageResult:
        """Processa uma página escolhendo o engine correto."""
        classification = self.classify(page, image)
        
        if classification == "digital":
            return self._process_cpu(image)
        else:
            return self._process_gpu(image)
    
    def _process_cpu(self, image: np.ndarray) -> PageResult:
        result = self.cpu_engine.ocr(image)
        # ... parse
        return PageResult(engine_used="paddle_cpu", ...)
    
    def _process_gpu(self, image: np.ndarray) -> PageResult:
        result = self.gpu_engine.ocr(image)
        # ... parse
        return PageResult(engine_used="trocr_gpu", ...)
```

---

## 6. Fluxo Completo do Pipeline

```
PDF Upload via POST /v1/extract
    │
    ▼
Validação (content_type, tamanho, etc.)
    │
    ▼
Abrir PDF em memória (PyMuPDF)
    │
    ▼
┌─────────────────────────────────────────────┐
│  FASE 1 — Rasterização (paralela, CPU)      │
│                                             │
│  ThreadPoolExecutor(max_workers=4)          │
│  Para cada página:                          │
│    - page.get_pixmap(zoom=2)                │
│    - Converter para numpy array             │
│    - Classificar: digital vs manuscrito     │
│      (via page.get_text() heurística)       │
└─────────────────────────────────────────────┘
    │
    ├── Páginas classificadas como "digital"
    │   │
    │   ▼
    │   ┌─────────────────────────────────┐
    │   │  ROTA CPU — OCR Leve            │
    │   │                                 │
    │   │  PaddleOCR (CPU)                │
    │   │  Pool de engines + ThreadPool   │
    │   │  ~100-300ms por página           │
    │   └─────────────────────────────────┘
    │
    ├── Páginas classificadas como "handwritten"
    │   │
    │   ▼
    │   ┌─────────────────────────────────┐
    │   │  ROTA GPU — OCR Pesado          │
    │   │                                 │
    │   │  TrOCR (GPU, CUDA)              │
    │   │  Engine único, fila sequencial  │
    │   │  ~500-1000ms por página          │
    │   └─────────────────────────────────┘
    │
    ▼
Agregar resultados (manter ordem das páginas)
    │
    ▼
Montar resposta com timing por página
    │
    ▼
Response JSON
{
  "file": "contrato.pdf",
  "time_process_seconds": 3.45,
  "process_pages": 10,
  "data": [
    {
      "page_number": 1,
      "text": [...],
      "low_confidence_alert": false,
      "processing_time_ms": 245.3,
      "raster_time_ms": 45.1,
      "ocr_time_ms": 200.2,
      "engine_used": "paddle_cpu",
      "classification": "digital"
    },
    {
      "page_number": 2,
      "text": [...],
      "low_confidence_alert": true,
      "processing_time_ms": 812.7,
      "raster_time_ms": 43.8,
      "ocr_time_ms": 768.9,
      "engine_used": "trocr_gpu",
      "classification": "handwritten"
    }
  ]
}
```

---

## 7. Ordem de Implementação Recomendada

A ordem importa — cada feature é fundação para a próxima.

### Etapa 1: Timing por página
- **Tempo estimado**: 15-30 minutos
- **Arquivos**: `app/services/ocr.py`
- **O que fazer**: Adicionar `time.perf_counter()` no loop, separar tempo de rasterização e OCR
- **Validação**: Processar um PDF e verificar os tempos no response JSON

### Etapa 2: Refatorar — Separar rasterização do OCR
- **Tempo estimado**: 1-2 horas
- **Arquivos**: `app/services/ocr.py`
- **O que fazer**: Extrair `rasterize_page()` e `ocr_page()` como funções independentes
- **Validação**: O resultado deve ser idêntico ao anterior (mesmos textos, mesmos scores)
- **Por que antes da GPU**: sem essa separação, as próximas features viram espaguete

### Etapa 3: GPU setup
- **Tempo estimado**: 1-3 horas (pode ter dor de cabeça com CUDA)
- **Arquivos**: `pyproject.toml`, `app/services/ocr.py`
- **O que fazer**: Trocar `paddlepaddle` por `paddlepaddle-gpu`, testar com `use_gpu=True`
- **Validação**: `nvidia-smi` mostra consumo de VRAM quando processar um PDF
- **Risco**: Compatibilidade RTX 5080 (Blackwell) com PaddlePaddle

### Etapa 4: Router com heurística simples
- **Tempo estimado**: 2-3 horas
- **Arquivos**: novo `app/services/page_router.py`, adaptar `app/services/ocr.py`
- **O que fazer**: Implementar classificação via `page.get_text()`, criar dois caminhos
- **Validação**: Processar um PDF misto e verificar que páginas diferentes usam engines diferentes (campo `engine_used` no response)

### Etapa 5: Paralelização
- **Tempo estimado**: 2-4 horas
- **Arquivos**: `app/services/ocr.py`, possível `app/services/engine_pool.py`
- **O que fazer**: Paralelizar rasterização com ThreadPool, implementar pool de engines CPU
- **Validação**: Comparar tempo total antes/depois com o mesmo PDF. Deve ser significativamente mais rápido para PDFs com muitas páginas.

### Etapa 6: TrOCR para manuscritos
- **Tempo estimado**: 4-8 horas
- **Arquivos**: `pyproject.toml` (nova dep: `transformers`, `torch`), novo `app/services/trocr_engine.py`
- **O que fazer**: Integrar TrOCR como engine GPU para manuscritos
- **Validação**: Processar um laudo médico manuscrito e comparar qualidade com PaddleOCR
- **Atenção**: TrOCR processa linhas, não páginas — precisa de detector de linhas como pré-estágio

---

## 8. Checklist Pré-Implementação

Antes de começar a codar, verificar:

- [ ] **CUDA**: Rodar `nvidia-smi` e anotar a versão do driver + CUDA máximo suportado
- [ ] **CUDA Toolkit**: Rodar `nvcc --version` e verificar se está instalado
- [ ] **Compatibilidade PaddlePaddle**: Verificar se `paddlepaddle-gpu` suporta RTX 5080 (Blackwell/SM 100)
- [ ] **Compatibilidade PyTorch**: Verificar se `torch` suporta RTX 5080 (provavelmente precisa de CUDA 12.8+)
- [ ] **RAM disponível**: Pool de 4 engines PaddleOCR consome ~4-8GB de RAM
- [ ] **PDF de teste manuscrito**: Ter pelo menos um PDF com texto manuscrito para validar o router
- [ ] **PDF de teste digital**: Ter pelo menos um PDF com texto digital/impresso para comparação
- [ ] **PDF misto**: Idealmente ter um PDF com páginas digitais e manuscritas misturadas

---

## Referências

- [PaddleOCR Documentação](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddlePaddle GPU Install](https://www.paddlepaddle.org.cn/install/quick)
- [TrOCR Paper](https://arxiv.org/abs/2109.10282)
- [TrOCR HuggingFace](https://huggingface.co/microsoft/trocr-base-handwritten)
- [PyMuPDF Threading](https://pymupdf.readthedocs.io/en/latest/recipes-multiprocessing.html)
- [Object Pool Pattern](https://en.wikipedia.org/wiki/Object_pool_pattern)

---

*Criado em: Fevereiro 2026*
*Status: Planejamento*