"""
Configuration management for Meowzon OCR Extractor
"""

from dataclasses import dataclass, field
from typing import List, Optional
import yaml
import os


@dataclass
class ExtractorConfig:
    """Configuration for Meowzon extractor"""
    
    # Input/Output
    input_folder: str = "./screenshots"
    output_csv: str = "meowzon_orders.csv"
    output_format: str = "csv"  # csv, excel, json, html, all
    
    # Processing
    aggressive_mode: bool = False
    parallel_processing: bool = False
    max_workers: int = 4
    batch_size: int = 10
    
    # AI Configuration
    ai_mode: str = "never"  # never, hybrid, always
    ai_provider: str = "ollama"  # ollama, openai, claude, gemini
    ollama_model: str = "qwen2-vl:7b"
    openai_model: str = "gpt-4o-mini"
    claude_model: str = "claude-3-5-sonnet-20241022"
    gemini_model: str = "gemini-1.5-flash"
    ai_max_retries: int = 3
    ai_timeout: int = 30
    
    # OCR Configuration
    tesseract_confidence_threshold: float = 70.0
    tesseract_config: str = '--psm 6 --oem 3'
    upscale_factor: float = 2.0
    
    # Image Processing
    max_image_size_mb: int = 50
    save_enhanced_images: bool = True
    enhanced_images_folder: str = "meowzon_enhanced_images"
    
    # Cropping Strategies
    crop_strategies: List[dict] = field(default_factory=lambda: [
        {"name": "No Bottom 20%", "top": 0.0, "bottom": 0.2, "left": 0.0, "right": 0.0},
        {"name": "No Top 20%", "top": 0.2, "bottom": 0.0, "left": 0.0, "right": 0.0},
        {"name": "No Top 15%", "top": 0.15, "bottom": 0.0, "left": 0.0, "right": 0.0},
        {"name": "Center 80%", "top": 0.1, "bottom": 0.1, "left": 0.1, "right": 0.1},
        {"name": "Tight Center", "top": 0.1, "bottom": 0.1, "left": 0.05, "right": 0.05},
    ])
    
    # Logging
    enable_logging: bool = True
    log_file: str = "meowzon.log"
    log_level: str = "INFO"
    
    # Features
    enable_analytics: bool = True
    enable_duplicate_detection: bool = True
    enable_validation: bool = True
    enable_interactive_review: bool = False
    generate_plots: bool = True
    
    # Output fields to include
    include_raw_text: bool = True
    include_debug_info: bool = True
    
    @classmethod
    def from_yaml(cls, path: str) -> 'ExtractorConfig':
        """Load configuration from YAML file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def to_yaml(self, path: str):
        """Save configuration to YAML file"""
        # Convert to dict, excluding non-serializable fields
        data = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def from_args(cls, args) -> 'ExtractorConfig':
        """Create config from argparse arguments"""
        return cls(
            input_folder=args.input,
            output_csv=args.output,
            output_format=args.format,
            aggressive_mode=args.aggressive,
            ai_mode=args.use_ai,
            ai_provider=args.ai_provider,
            ollama_model=args.ollama_model,
            openai_model=args.openai_model,
            parallel_processing=args.parallel,
            max_workers=args.workers,
            enable_interactive_review=args.interactive,
            generate_plots=args.plot,
            tesseract_confidence_threshold=args.confidence_threshold,
        )
    
    def validate(self):
        """Validate configuration"""
        if self.ai_mode not in ['never', 'hybrid', 'always']:
            raise ValueError(f"Invalid ai_mode: {self.ai_mode}")
        
        if self.ai_provider not in ['ollama', 'openai', 'claude', 'gemini']:
            raise ValueError(f"Invalid ai_provider: {self.ai_provider}")
        
        if self.output_format not in ['csv', 'excel', 'json', 'html', 'all']:
            raise ValueError(f"Invalid output_format: {self.output_format}")
        
        if self.tesseract_confidence_threshold < 0 or self.tesseract_confidence_threshold > 100:
            raise ValueError("tesseract_confidence_threshold must be between 0 and 100")
        
        if not os.path.exists(self.input_folder):
            raise FileNotFoundError(f"Input folder not found: {self.input_folder}")


def create_default_config(path: str = "meowzon_config.yaml"):
    """Create a default configuration file"""
    config = ExtractorConfig()
    config.to_yaml(path)
    print(f"✅ Created default config: {path}")
