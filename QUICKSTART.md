# 🚀 Meowzon Quick Start Guide

Get up and running with Meowzon in 5 minutes!

## Step 1: Install Prerequisites

### Install Python 3.8+
Download from [python.org](https://www.python.org/downloads/)

### Install Tesseract OCR

**Windows:**
1. Download installer from [GitHub](https://github.com/tesseract-ocr/tesseract)
2. Install to default location: `C:\Program Files\Tesseract-OCR`

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

## Step 2: Install Meowzon

```bash
# Clone or download the repository
cd meowzon-ocr-extractor

# Install dependencies
pip install -r requirements.txt

# Verify installation
python test_installation.py
```

## Step 3: Prepare Your Screenshots

1. Create a folder called `screenshots`
2. Add your Amazon order screenshots (PNG, JPG, etc.)

```
meowzon-ocr-extractor/
├── screenshots/
│   ├── order1.png
│   ├── order2.jpg
│   └── order3.png
└── ...
```

## Step 4: Run Basic Extraction

```bash
python main.py -i ./screenshots -o my_orders.csv --aggressive
```

This will:
- Process all images in `screenshots/`
- Try multiple crop strategies
- Save results to `my_orders.csv`
- Save enhanced images for debugging

## Step 5: Review Results

Open `my_orders.csv` in Excel or any spreadsheet app!

## 🎯 Next Steps

### Want Better Accuracy? Use AI!

#### Option A: Local AI with Ollama (Free, Private)

```bash
# 1. Install Ollama
# Download from: https://ollama.com

# 2. Pull a vision model
ollama pull qwen2-vl:7b

# 3. Run with AI hybrid mode
python main.py -i ./screenshots \
  --use-ai hybrid \
  --ai-provider ollama \
  --ollama-model qwen2-vl:7b \
  --aggressive
```

#### Option B: Cloud AI with OpenAI (Best Quality)

```bash
# 1. Get API key from: https://platform.openai.com
export OPENAI_API_KEY="your-key-here"

# 2. Run with AI
python main.py -i ./screenshots \
  --use-ai hybrid \
  --ai-provider openai \
  --aggressive
```

### Want All Output Formats?

```bash
python main.py -i ./screenshots --format all
```

Creates:
- CSV file
- Excel file (with formatting)
- JSON file
- HTML report (with charts)
- Analytics plot

### Need to Correct Results?

```bash
python main.py -i ./screenshots --interactive
```

Lets you manually review and correct low-confidence extractions.

## 📊 Understanding Output

### CSV Columns

| Column | Description |
|--------|-------------|
| **File Name** | Screenshot filename |
| **Status** | Success / Review Required / Failed |
| **Overall Confidence** | 0-100% confidence score |
| **AI Used** | Whether AI was used (Yes/No) |
| **Order IDs** | Amazon order numbers |
| **Items** | Product names |
| **Totals** | Order total amounts |
| **Dates** | Order dates |
| **Sellers** | Seller names |
| **Prices** | Individual prices |

### Status Meanings

- ✅ **Success**: Order ID and items found
- ⚠️ **Review Required**: Some data found, needs verification
- ❌ **Failed**: No data extracted

## 🔧 Common Issues

### "Tesseract not found"
- **Windows**: Check it's installed to `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **Mac/Linux**: Run `which tesseract` to verify installation

### "No images found"
- Check images are in the correct folder
- Supported formats: PNG, JPG, JPEG, BMP, TIFF, WEBP

### "Low accuracy"
1. Use `--aggressive` mode
2. Switch to `--use-ai hybrid`
3. Try higher quality screenshots
4. Use `--interactive` to manually correct

### "Ollama connection error"
```bash
# Start Ollama server
ollama serve
```

## 💡 Pro Tips

1. **Use Hybrid Mode**: Best balance of speed and accuracy
   ```bash
   --use-ai hybrid --ai-provider ollama
   ```

2. **Parallel Processing**: Much faster for many files
   ```bash
   --parallel --workers 4
   ```

3. **Save All Formats**: Useful for different tools
   ```bash
   --format all
   ```

4. **Review Low Confidence**: Catch and fix errors
   ```bash
   --interactive
   ```

5. **Use Config File**: Save your preferred settings
   ```bash
   python main.py --create-config
   # Edit meowzon_config.yaml
   python main.py --config meowzon_config.yaml
   ```

## 📚 More Information

- Full documentation: See `README.md`
- Configuration options: See `meowzon_config.yaml`
- Troubleshooting: Check `README.md` troubleshooting section

## 🎉 That's It!

You're now extracting Amazon orders like a pro! 😺

Need help? Check the README or open an issue on GitHub.

---

**Happy extracting! 🐾**
