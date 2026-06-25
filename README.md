# IndicTrans2 Translation API

A REST API for translating English text into 22 Indian languages using [AI4Bharat's IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) model (`ai4bharat/indictrans2-en-indic-1B`).

## Features

- Translate English into 22 Indian languages in a single API call
- Returns token usage (input, output, total) and wall-clock time per request
- Auto-detects GPU (CUDA) and falls back to CPU transparently
- Interactive API docs at `/docs` (Swagger UI) and `/redoc`

## Python Version

**Python 3.12** is required. The project was built and tested against Python 3.12.0.

Earlier versions (3.10, 3.11) may work but are not tested. Python 3.13+ is not recommended due to limited PyTorch wheel availability.

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.12 | [python.org/downloads](https://www.python.org/downloads/) |
| pip 23+ | Comes with Python 3.12 |
| CUDA 11.8+ *(optional)* | Required for GPU acceleration |
| ~5 GB disk space | Model weights are downloaded on first run |
| ~4 GB RAM (CPU) / ~3 GB VRAM (GPU) | For running inference |

## Project Structure

```
translator/
├── main.py          # FastAPI app, request/response models, routes
├── translator.py    # TranslationService: model loading & inference
├── languages.py     # Supported language codes and validation helper
└── requirements.txt # Python dependencies
```

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd translator
```

### 2. Create a virtual environment

```bash
python3.12 -m venv venv
```

Activate it:

- **Windows**: `venv\Scripts\activate`
- **macOS / Linux**: `source venv/bin/activate`

### 3. Install dependencies

**CPU only:**

```bash
pip install -r requirements.txt
```

**GPU (CUDA 11.8):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

**GPU (CUDA 12.1):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

> When a CUDA-enabled PyTorch is already installed, the `torch>=2.5.0` line in `requirements.txt` will not downgrade it.

### 4. Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server starts on `http://localhost:8000`.

**First run**: the model weights (~2.5 GB) are downloaded automatically from Hugging Face and cached in `~/.cache/huggingface/`. Subsequent starts load from cache and take 15–60 seconds depending on hardware.

## API Endpoints

### `GET /health`

Liveness check. Returns `ready` when the model is loaded.

**Response**

```json
{ "status": "ready" }
```

---

### `GET /languages`

Returns the source language and all supported target languages.

**Response**

```json
{
  "source_language": { "eng_Latn": "English" },
  "target_languages": {
    "asm_Beng": "Assamese",
    "ben_Beng": "Bengali",
    "hin_Deva": "Hindi",
    ...
  }
}
```

---

### `POST /translate`

Translates English text into a target language.

**Request body**

| Field | Type | Required | Description |
|---|---|---|---|
| `text` | string | yes | English text to translate (must not be blank) |
| `target_language` | string | yes | BCP-47 language code from `/languages` |

```json
{
  "text": "Hello, how are you?",
  "target_language": "hin_Deva"
}
```

**Response**

| Field | Type | Description |
|---|---|---|
| `source_language` | string | Always `eng_Latn` |
| `translated_text` | string | Translated output |
| `time_taken_ms` | float | Inference time in milliseconds |
| `token_usage.input_tokens` | int | Tokens in the source sentence |
| `token_usage.output_tokens` | int | Tokens in the translated sentence |
| `token_usage.total_tokens` | int | Sum of input and output tokens |

```json
{
  "source_language": "eng_Latn",
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "time_taken_ms": 342.17,
  "token_usage": {
    "input_tokens": 9,
    "output_tokens": 12,
    "total_tokens": 21
  }
}
```

**Error responses**

| Status | Cause |
|---|---|
| `422 Unprocessable Entity` | Empty `text`, missing fields, or unsupported `target_language` |
| `500 Internal Server Error` | Model inference failure |

---

## Supported Languages

| Code | Language | Script |
|---|---|---|
| `asm_Beng` | Assamese | Bengali |
| `ben_Beng` | Bengali | Bengali |
| `brx_Deva` | Bodo | Devanagari |
| `doi_Deva` | Dogri | Devanagari |
| `guj_Gujr` | Gujarati | Gujarati |
| `hin_Deva` | Hindi | Devanagari |
| `kan_Knda` | Kannada | Kannada |
| `kas_Arab` | Kashmiri | Perso-Arabic |
| `kas_Deva` | Kashmiri | Devanagari |
| `gom_Deva` | Konkani | Devanagari |
| `mai_Deva` | Maithili | Devanagari |
| `mal_Mlym` | Malayalam | Malayalam |
| `mni_Beng` | Manipuri | Bengali |
| `mni_Mtei` | Manipuri | Meitei |
| `mar_Deva` | Marathi | Devanagari |
| `npi_Deva` | Nepali | Devanagari |
| `ory_Orya` | Odia | Odia |
| `pan_Guru` | Punjabi | Gurmukhi |
| `san_Deva` | Sanskrit | Devanagari |
| `sat_Olck` | Santali | Ol Chiki |
| `snd_Arab` | Sindhi | Perso-Arabic |
| `snd_Deva` | Sindhi | Devanagari |
| `tam_Taml` | Tamil | Tamil |
| `tel_Telu` | Telugu | Telugu |
| `urd_Arab` | Urdu | Perso-Arabic |

## Example: cURL

```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "The weather is beautiful today.", "target_language": "tam_Taml"}'
```

## Interactive Docs

Once the server is running:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Model Details

| Property | Value |
|---|---|
| Model | `ai4bharat/indictrans2-en-indic-1B` |
| Architecture | Encoder–Decoder Transformer (Seq2Seq) |
| Direction | English → 22 Indian languages |
| Precision | float16 on CUDA, float32 on CPU |
| Decoding | Beam search, `num_beams=5`, `max_length=256` |
| Input limit | 512 tokens |

## Troubleshooting

**`RuntimeError: CUDA out of memory`** — reduce batch size or switch to CPU by unsetting CUDA:

```bash
CUDA_VISIBLE_DEVICES="" uvicorn main:app --host 0.0.0.0 --port 8000
```

**`ModuleNotFoundError: No module named 'IndicTransToolkit'`** — ensure the virtual environment is activated before running.

**Slow first startup** — the model downloads ~2.5 GB on the first run. Subsequent starts use the Hugging Face cache and are faster.

**`422` on a valid language code** — language codes are case-sensitive. Use the exact codes returned by `GET /languages`.
