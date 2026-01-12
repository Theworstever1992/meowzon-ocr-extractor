#!/usr/bin/env python3

"""
Meowzon Order OCR Extractor - Main CLI
Cat-Themed AI-Hybrid Edition v3.0
"""

import sys
import argparse
from pathlib import Path

# Initialize colorama for Windows color support
try:
    import colorama
    colorama.just_fix_windows_console()
except ImportError:
    pass  # colorama not installed, colors will be disabled

from meowzon.config import ExtractorConfig, create_default_config
from meowzon.extractor import MeowzonExtractor
from meowzon.logging_utils import setup_logging
from meowzon.interactive_review import run_interactive_review


def print_banner():
    """Print ASCII art banner"""
    banner = """
\033[1;35m
      /\\_/\\      ███╗   ███╗███████╗ ██████╗ ██╗    ██╗███████╗ ██████╗ ███╗   ██╗
     ( o.o )     ████╗ ████║██╔════╝██╔═══██╗██║    ██║╚══███╔╝██╔═══██╗████╗  ██║
      > ^ <      ██╔████╔██║█████╗  ██║   ██║██║ █╗ ██║  ███╔╝ ██║   ██║██╔██╗ ██║
                 ██║╚██╔╝██║██╔══╝  ██║   ██║██║███╗██║ ███╔╝  ██║   ██║██║╚██╗██║
      /\\_/\\      ██║ ╚═╝ ██║███████╗╚██████╔╝╚███╔███╔╝███████╗╚██████╔╝██║ ╚████║
     ( o.o )     ╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
      > ^ <      
                  ██████╗  ██████╗██████╗     ███████╗██╗  ██╗████████╗██████╗  █████╗  ██████╗████████╗ ██████╗ ██████╗ 
                 ██╔═══██╗██╔════╝██╔══██╗    ██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
                 ██║   ██║██║     ██████╔╝    █████╗   ╚███╔╝    ██║   ██████╔╝███████║██║        ██║   ██║   ██║██████╔╝
                 ██║   ██║██║     ██╔══██╗    ██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══██║██║        ██║   ██║   ██║██╔══██╗
                 ╚██████╔╝╚██████╗██║  ██║    ███████╗██╔╝ ██╗   ██║   ██║  ██║██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║
                  ╚═════╝  ╚═════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
\033[0m
    """
    print(banner)
    print("\033[1;36m😺 Meowzon Order OCR Extractor v3.0 - AI Hybrid Edition 😺\033[0m")
    print("\033[90mProduction-grade extraction with Tesseract + Multi-AI support!\033[0m\n")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="😺 Meowzon - AI-powered Amazon order extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic Tesseract-only extraction
  python main.py -i ./screenshots -o orders.csv

  # With aggressive cropping and enhanced images
  python main.py -i ./screenshots -o orders.csv --aggressive

  # Hybrid mode with local Ollama (recommended)
  python main.py -i ./screenshots --use-ai hybrid --ai-provider ollama --ollama-model qwen2-vl:7b

  # Always use OpenAI GPT-4 Vision
  python main.py -i ./screenshots --use-ai always --ai-provider openai

  # Parallel processing with all outputs
  python main.py -i ./screenshots --parallel --workers 4 --format all

  # Interactive review mode
  python main.py -i ./screenshots --interactive

  # Create default config file
  python main.py --create-config

  # Use config file
  python main.py --config meowzon_config.yaml

Supported AI Providers:
  - ollama: Local AI (qwen2-vl:7b, llava:13b, etc.)
  - openai: GPT-4 Vision (requires OPENAI_API_KEY)
  - claude: Claude 3.5 Sonnet (requires ANTHROPIC_API_KEY)
  - gemini: Gemini 1.5 (requires GOOGLE_API_KEY)
        """
    )
    
    # Config file
    parser.add_argument(
        '--config',
        type=str,
        help='Load configuration from YAML file'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create default configuration file and exit'
    )
    
    # Input/Output
    parser.add_argument(
        '-i', '--input',
        default='./screenshots',
        help='Input folder with screenshots (default: ./screenshots)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='meowzon_orders.csv',
        help='Output file path (default: meowzon_orders.csv)'
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'excel', 'json', 'html', 'all'],
        default='csv',
        help='Output format (default: csv)'
    )
    
    # Processing options
    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='Enable aggressive cropping and save enhanced images'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel processing'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )
    
    # AI configuration
    parser.add_argument(
        '--use-ai',
        choices=['never', 'hybrid', 'always'],
        default='never',
        help='AI mode: never (Tesseract only), hybrid (fallback), always (default: never)'
    )
    
    parser.add_argument(
        '--ai-provider',
        choices=['ollama', 'openai', 'claude', 'gemini'],
        default='ollama',
        help='AI provider (default: ollama)'
    )
    
    parser.add_argument(
        '--ollama-model',
        default='qwen2-vl:7b',
        help='Ollama model name (default: qwen2-vl:7b)'
    )
    
    parser.add_argument(
        '--openai-model',
        default='gpt-4o-mini',
        help='OpenAI model (default: gpt-4o-mini)'
    )
    
    # Features
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Enable interactive review mode for low-confidence extractions'
    )
    
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Disable analytics plot generation'
    )
    
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=70.0,
        help='OCR confidence threshold for AI fallback (default: 70.0)'
    )
    
    # Logging
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--no-log-file',
        action='store_true',
        help='Disable file logging'
    )
    
    return parser


def main():
    """Main entry point"""
    # Print banner
    print_banner()
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle config creation
    if args.create_config:
        create_default_config()
        return 0
    
    # Load or create config
    if args.config:
        try:
            config = ExtractorConfig.from_yaml(args.config)
            print(f"✅ Loaded config from: {args.config}\n")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return 1
    else:
        config = ExtractorConfig.from_args(args)
        config.aggressive_mode = args.aggressive
        config.parallel_processing = args.parallel
        config.max_workers = args.workers
        config.enable_interactive_review = args.interactive
        config.generate_plots = not args.no_plot
        config.tesseract_confidence_threshold = args.confidence_threshold
        config.enable_logging = not args.no_log_file
        config.log_level = args.log_level
    
    # Validate config
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Setup logging
    logger = setup_logging(
        log_file=config.log_file if config.enable_logging else None,
        log_level=config.log_level,
        enable_file_logging=config.enable_logging
    )
    
    # Run extraction
    try:
        extractor = MeowzonExtractor(config)
        output_path = extractor.run()
        
        # Interactive review if requested
        if config.enable_interactive_review and output_path:
            print("\n" + "=" * 70)
            print("🔍 Starting interactive review mode...")
            print("=" * 70)
            run_interactive_review(
                output_path,
                config.input_folder,
                config.tesseract_confidence_threshold
            )
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        print("Check log file for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
