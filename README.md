# 😺 Meowzon Order OCR Extractor v2.0 - AI Hybrid Edition

The **ultimate** tool for extracting Amazon order details from screenshots in 2025!

Hybrid Tesseract + AI vision for maximum accuracy 🐾

## Key Features
- Fast Tesseract baseline
- Optional AI vision models (local Ollama or cloud OpenAI GPT-4o)
- Modes: `--use-ai hybrid` (recommended - AI fallback on failure), `always`, or `never`
- Providers: `ollama` (fully local/privacy), `openai` (most accurate)
- Aggressive cropping + saves visual debug images
- Structured JSON from AI → perfect item lists!

## Installation

### Core (always)
```bash
pip install opencv-python numpy pytesseract pandas tqdm requests

For OpenAI provider
pip install openai
Set env: export OPENAI_API_KEY=sk-...
For Ollama (local AI - recommended for privacy)
Download/install Ollama: https://ollama.com
Pull a vision model:
ollama pull qwen2-vl:7b   # Top-rated for documents 2025
# or ollama pull llava:13b / phi3:medium etc.
Usage Examples
# Tesseract only (fast)
python meowzon_ocr_extractor.py --aggressive

# Hybrid with local Ollama (best privacy/accuracy balance)
python meowzon_ocr_extractor.py --aggressive --use-ai hybrid --ai-provider ollama --ollama-model qwen2-vl:7b

# AI always with OpenAI (maximum accuracy)
python meowzon_ocr_extractor.py --aggressive --use-ai always --ai-provider openai --openai-model gpt-4o

# Pure AI (skip Tesseract)
python meowzon_ocr_extractor.py --use-ai always --ai-provider ollama
Extending to Other Providers
Want Grok, Claude, Gemini, etc.?
The code is modular — add a new branch in extract_with_ai() with their API (base64 image + prompt).
For Grok/xAI vision: Check https://x.ai/api for multimodal support (as of late 2025, Grok 4 has vision).
Claude/Gemini: Similar to OpenAI, just different client.
This hybrid setup gives you the best of both worlds: speed/privacy of Tesseract/local + power of modern VLMs when needed.
Test it and tell me how it performs on your screenshots — we can tweak the prompt or add more providers! 😺
This v2.0 is now truly the "best possible" screenshot extractor:
- Flexible AI choice (local Ollama with top 2025 models like Qwen2-VL, or cloud OpenAI)
- Hybrid for efficiency
- Easy to extend for other non-local (Grok/Claude/etc.)

Run with `--use-ai hybrid --ai-provider ollama --ollama-model qwen2-vl:7b --aggressive` for the sweet spot.
