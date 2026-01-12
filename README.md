# 😺 Meowzon Order OCR Extractor v3.0 - AI Hybrid Edition

The **ultimate** tool for extracting Amazon order details from screenshots in 2025!

Hybrid Tesseract + AI vision for maximum accuracy 🐾

## Key Features
- 🚀 Fast Tesseract OCR baseline
- 🤖 Optional AI vision models (local Ollama or cloud OpenAI GPT-4, Claude, Gemini)
- ⚙️ Modes: `hybrid` (AI fallback), `always` (AI only), or `never` (Tesseract only)
- 🎯 Providers: `ollama` (local/privacy), `openai`, `claude`, `gemini`
- ✂️ Aggressive cropping for better accuracy
- 📊 Multiple output formats: CSV, Excel, JSON, HTML
- 🔍 Interactive review mode for low-confidence extractions
- 📈 Analytics and visualization
- 🪟 **Full Windows support with one-click installers!**

---

## 🪟 Windows Installation (Recommended)

### Quick Start
1. **Install Python 3.8+** from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation!

2. **Install Tesseract OCR**
   - Download from: [Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to default location: `C:\Program Files\Tesseract-OCR`

3. **Run the installer**
   ```cmd
   install_windows.bat
   ```

4. **Start extracting!**
   ```cmd
   run_meowzon.bat -i ./screenshots -o orders.csv
   ```

### Alternative: Manual Installation
```cmd
pip install -r requirements.txt
python main.py --help
```

---

## 🐧 Linux/Mac Installation

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Install Tesseract
**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

---

## 📖 Usage Examples

### Basic Usage
```bash
# Windows
run_meowzon.bat -i ./screenshots -o orders.csv

# Linux/Mac
python main.py -i ./screenshots -o orders.csv
```

### With Aggressive Cropping (Recommended)
```bash
python main.py -i ./screenshots -o orders.csv --aggressive
```

### AI Hybrid Mode (Best Accuracy)
```bash
# With local Ollama (privacy-friendly)
python main.py -i ./screenshots --use-ai hybrid --ai-provider ollama --ollama-model qwen2-vl:7b

# With OpenAI GPT-4 Vision (most accurate)
python main.py -i ./screenshots --use-ai always --ai-provider openai
```

### Output Formats
```bash
# CSV (default)
python main.py -i ./screenshots -o orders.csv

# Excel
python main.py -i ./screenshots -o orders.xlsx --format excel

# JSON
python main.py -i ./screenshots -o orders.json --format json

# All formats at once
python main.py -i ./screenshots --format all
```

### Parallel Processing
```bash
python main.py -i ./screenshots --parallel --workers 4
```

### Interactive Review Mode
```bash
python main.py -i ./screenshots --interactive
```

---

## 🤖 AI Providers Setup

### Ollama (Local AI - Recommended for Privacy)
1. Download from [ollama.com](https://ollama.com)
2. Install and run Ollama
3. Pull a vision model:
   ```bash
   ollama pull qwen2-vl:7b    # Recommended for documents
   ollama pull llava:13b       # Alternative
   ollama pull phi3:medium     # Another option
   ```
4. Use with Meowzon:
   ```bash
   python main.py -i ./screenshots --use-ai hybrid --ai-provider ollama
   ```

### OpenAI GPT-4 Vision
1. Get API key from [platform.openai.com](https://platform.openai.com/)
2. Set environment variable:
   ```bash
   # Linux/Mac
   export OPENAI_API_KEY=sk-...

   # Windows CMD
   set OPENAI_API_KEY=sk-...

   # Windows PowerShell
   $env:OPENAI_API_KEY="sk-..."
   ```
3. Use with Meowzon:
   ```bash
   python main.py -i ./screenshots --use-ai always --ai-provider openai
   ```

### Claude (Anthropic)
```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python main.py -i ./screenshots --use-ai always --ai-provider claude
```

### Gemini (Google)
```bash
pip install google-generativeai
export GOOGLE_API_KEY=...
python main.py -i ./screenshots --use-ai always --ai-provider gemini
```

---

## 📋 Configuration File

Create a config file for reusable settings:

```bash
# Create default config
python main.py --create-config

# Edit meowzon_config.yaml to your preferences

# Use config file
python main.py --config meowzon_config.yaml
```

---

## 🎯 Recommended Settings

**Best accuracy with privacy:**
```bash
python main.py -i ./screenshots --aggressive --use-ai hybrid --ai-provider ollama --ollama-model qwen2-vl:7b --parallel --workers 4
```

**Fast processing (no AI):**
```bash
python main.py -i ./screenshots --aggressive --parallel --workers 4
```

**Maximum accuracy (cloud AI):**
```bash
python main.py -i ./screenshots --use-ai always --ai-provider openai --openai-model gpt-4o
```

---

## 📊 Output

Meowzon extracts:
- 📝 Order IDs
- 📅 Dates
- 💰 Totals
- 📦 Item names and quantities
- 🏪 Sellers
- 💵 Individual prices
- 📫 Tracking numbers

### Output Files
- `meowzon_orders.csv` - Main results
- `meowzon_enhanced_images/` - Processed images (if `--aggressive` used)
- `meowzon_analytics.png` - Statistics visualization
- `meowzon.log` - Detailed logs

---

## 🔧 Troubleshooting

### Windows: "Python not found"
- Make sure Python is installed and added to PATH
- Restart your terminal/command prompt after installation

### "Tesseract not found"
**Windows:** Install from [Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki) to default location
**Linux:** `sudo apt-get install tesseract-ocr`
**Mac:** `brew install tesseract`

### "No images found"
- Check that your screenshots are in the input folder
- Supported formats: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.webp`

### Poor extraction quality
- Use `--aggressive` flag for better cropping
- Try AI hybrid mode: `--use-ai hybrid --ai-provider ollama`
- Ensure screenshots are clear and readable

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Credits

Built with:
- Tesseract OCR
- OpenCV
- Pandas
- Various AI vision models (Ollama, OpenAI, Claude, Gemini)

---

## 📧 Support

For issues and feature requests, please visit the GitHub repository.

---

**Happy extracting! 😺🐾**
