# 📁 Meowzon Project Structure

```
meowzon-ocr-extractor/
│
├── 📄 main.py                      # Main CLI entry point
├── 📄 setup.py                     # Package installation configuration
├── 📄 requirements.txt             # Python dependencies
├── 📄 .gitignore                   # Git ignore rules
│
├── 📚 Documentation
│   ├── README.md                   # Comprehensive documentation
│   ├── QUICKSTART.md              # 5-minute getting started guide
│   ├── CHANGELOG.md               # Version history
│   ├── LICENSE                     # MIT License
│   └── PROJECT_STRUCTURE.md       # This file
│
├── ⚙️ Configuration
│   └── meowzon_config.yaml        # Example configuration file
│
├── 🧪 Testing
│   └── test_installation.py       # Installation verification script
│
└── 📦 meowzon/                    # Main package
    │
    ├── __init__.py                # Package initialization
    │
    ├── 🔧 Core Modules
    │   ├── config.py              # Configuration management
    │   ├── extractor.py           # Main orchestrator class
    │   └── logging_utils.py       # Logging setup and utilities
    │
    ├── 🖼️ Image Processing
    │   ├── ocr_engine.py          # Tesseract OCR operations
    │   └── image_processor.py     # Cropping and preprocessing
    │
    ├── 📊 Data Processing
    │   ├── data_extractor.py      # Regex-based extraction
    │   └── analytics.py           # Statistics and reporting
    │
    ├── 🤖 AI Integration
    │   └── ai_providers.py        # Multi-AI provider support
    │                              # (Ollama, OpenAI, Claude, Gemini)
    │
    ├── 💾 Output
    │   └── output_handler.py      # CSV, Excel, JSON, HTML export
    │
    └── ✏️ Interactive
        └── interactive_review.py  # Manual correction interface

```

## 📋 Module Descriptions

### Core Components

#### `main.py`
- CLI argument parsing
- Configuration loading
- Workflow orchestration
- Beautiful ASCII banner
- Entry point for the application

#### `meowzon/config.py`
- `ExtractorConfig` dataclass
- YAML configuration support
- Configuration validation
- Default values management

#### `meowzon/extractor.py`
- `MeowzonExtractor` main class
- Orchestrates all components
- Handles single and batch processing
- Parallel processing support
- Progress tracking with tqdm

### Image Processing

#### `meowzon/ocr_engine.py`
- `OCREngine` class for Tesseract
- Image preprocessing
- Confidence calculation
- Multiple OCR strategies (normal/inverted)
- `ImageValidator` for file validation

#### `meowzon/image_processor.py`
- Smart cropping strategies
- Best crop selection algorithm
- Image enhancement techniques
- Skew detection and correction
- Background removal

### Data Processing

#### `meowzon/data_extractor.py`
- `DataExtractor` with regex patterns
- Extract order IDs, prices, dates, items
- `DataValidator` for validation
- Confidence scoring
- Extraction validation

#### `meowzon/analytics.py`
- `OrderAnalytics` for statistics
- Summary generation
- Text reports
- Visualization plots (matplotlib)
- `DuplicateDetector` for finding duplicates

### AI Integration

#### `meowzon/ai_providers.py`
- `AIProvider` abstract base class
- `OllamaProvider` for local AI
- `OpenAIProvider` for GPT-4 Vision
- `ClaudeProvider` for Claude 3.5
- `GeminiProvider` for Gemini 1.5
- Factory pattern for provider creation
- Retry logic and error handling

### Output

#### `meowzon/output_handler.py`
- `OutputHandler` class
- CSV export
- Excel export with formatting
- JSON export
- HTML report generation
- Multi-format export

### Interactive Features

#### `meowzon/interactive_review.py`
- `InteractiveReviewer` class
- Low-confidence filtering
- Manual correction interface
- Image display support
- Edit/Delete/Keep actions

### Utilities

#### `meowzon/logging_utils.py`
- `setup_logging()` function
- `ColoredFormatter` for console
- File and console handlers
- `LoggerMixin` for easy logging

## 🎯 Data Flow

```
┌─────────────────┐
│  User Input     │
│  (Screenshots)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Main Entry Point (main.py)         │
│  • Parse arguments                  │
│  • Load configuration               │
│  • Setup logging                    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  MeowzonExtractor                   │
│  • Initialize components            │
│  • Validate configuration           │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Image Processing Loop              │
│  For each screenshot:               │
└────────┬────────────────────────────┘
         │
         ├──▶ ImageValidator: Check file
         │
         ├──▶ ImageProcessor: Find best crop
         │
         ├──▶ OCREngine: Extract text
         │
         ├──▶ DataExtractor: Parse data
         │
         ├──▶ [Conditional] AIProvider: Enhance
         │
         └──▶ DataValidator: Check quality
         │
         ▼
┌─────────────────────────────────────┐
│  Post-Processing                    │
│  • Duplicate detection              │
│  • Analytics generation             │
│  • Validation                       │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Output Generation                  │
│  • Format data                      │
│  • Generate reports                 │
│  • Create visualizations            │
│  • Export files                     │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  [Optional] Interactive Review      │
│  • Manual corrections               │
│  • Re-save corrected data           │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Final Output   │
│  (CSV/Excel/    │
│   JSON/HTML)    │
└─────────────────┘
```

## 🔌 Extension Points

### Adding a New AI Provider

1. Create new provider class in `ai_providers.py`
2. Inherit from `AIProvider`
3. Implement `extract()` method
4. Add to factory in `get_ai_provider()`
5. Update config with model name

### Adding a New Output Format

1. Add method to `OutputHandler` class
2. Update `output_format` choices in config
3. Add logic in `save_all_formats()`

### Adding a New Data Field

1. Add regex pattern to `DataExtractor`
2. Add extraction method
3. Update `extract_all()` to include it
4. Update AI prompt in `ai_providers.py`
5. Add to output dataframe in `extractor.py`

## 📦 Dependencies

### Required
- opencv-python (Image processing)
- numpy (Numerical operations)
- pytesseract (OCR interface)
- pandas (Data manipulation)
- tqdm (Progress bars)
- requests (HTTP for Ollama)
- pyyaml (Configuration files)

### Optional
- openai (GPT-4 Vision)
- anthropic (Claude API)
- google-generativeai (Gemini API)
- matplotlib (Plotting)
- openpyxl (Excel export)

## 🚀 Usage Patterns

### Basic CLI
```bash
python main.py -i ./screenshots -o orders.csv
```

### Programmatic
```python
from meowzon import MeowzonExtractor, ExtractorConfig

config = ExtractorConfig(
    input_folder="./screenshots",
    ai_mode="hybrid",
    ai_provider="ollama"
)

extractor = MeowzonExtractor(config)
extractor.run()
```

### As a Library
```python
from meowzon.ocr_engine import OCREngine
from meowzon.config import ExtractorConfig

config = ExtractorConfig()
ocr = OCREngine(config)

import cv2
image = cv2.imread("order.png")
text, confidence, processed = ocr.extract_text(image)
```

## 📝 Configuration Hierarchy

1. **Default values** in `ExtractorConfig` dataclass
2. **YAML file** if `--config` specified
3. **Command-line arguments** override all

## 🎨 Design Patterns Used

- **Factory Pattern**: AI provider creation
- **Strategy Pattern**: Cropping strategies
- **Mixin Pattern**: Logger mixin for classes
- **Dataclass Pattern**: Configuration management
- **Orchestrator Pattern**: Main extractor class

## 🧪 Testing

Run installation test:
```bash
python test_installation.py
```

This verifies:
- All required packages installed
- Tesseract accessible
- Meowzon package importable
- Ollama running (optional)

---

**Made with 😺 and careful architecture!**
