# Changelog

All notable changes to Meowzon OCR Extractor will be documented in this file.

## [3.0.0] - 2024-12-29

### 🎉 Major Rewrite - Production Ready!

This is a complete rewrite with professional architecture and extensive new features.

### Added
- **Modular Architecture**: Clean separation into focused modules
  - `config.py`: Configuration management with YAML support
  - `ocr_engine.py`: Tesseract OCR operations
  - `image_processor.py`: Image preprocessing and cropping
  - `data_extractor.py`: Regex-based data extraction
  - `ai_providers.py`: Multi-AI provider support
  - `analytics.py`: Statistics and reporting
  - `output_handler.py`: Multiple output formats
  - `extractor.py`: Main orchestrator
  - `interactive_review.py`: Manual correction system
  
- **Multi-AI Provider Support**:
  - Ollama (local, free, private)
  - OpenAI GPT-4 Vision
  - Anthropic Claude 3.5 Sonnet
  - Google Gemini 1.5
  
- **Advanced Features**:
  - Parallel processing for speed
  - Interactive review mode
  - Duplicate detection
  - Data validation with confidence scoring
  - Enhanced analytics with visualizations
  - Multiple output formats (CSV, Excel, JSON, HTML)
  
- **Quality Improvements**:
  - Comprehensive error handling
  - Retry logic with exponential backoff
  - Structured logging with file and console output
  - Image validation and size checks
  - Configuration validation
  
- **Developer Experience**:
  - Type hints throughout
  - Proper package structure
  - setup.py for pip installation
  - Comprehensive documentation
  - Test installation script
  - Example configuration files

### Changed
- Improved cropping strategies with better heuristics
- Better OCR preprocessing with multiple techniques
- Enhanced AI prompt for more accurate extraction
- More reliable JSON parsing from AI responses
- Better status reporting with emojis and colors

### Technical Improvements
- Proper exception handling everywhere
- Logging instead of print statements
- Clean class hierarchy with mixins
- Factory pattern for AI providers
- Dataclass-based configuration
- Thread-safe parallel processing

## [2.0.0] - 2024-12 (Previous Version)

### Added
- Initial AI support with Ollama and OpenAI
- Hybrid mode (AI fallback on low confidence)
- Aggressive cropping mode
- Enhanced image saving

## [1.0.0] - Initial Release

### Added
- Basic Tesseract OCR extraction
- Simple cropping strategies
- CSV output
- Order ID and basic data extraction

---

## Version Naming

- **Major** (X.0.0): Breaking changes, major rewrites
- **Minor** (0.X.0): New features, non-breaking changes
- **Patch** (0.0.X): Bug fixes, minor improvements
