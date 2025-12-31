"""
OCR Engine for text extraction using Tesseract
"""

import cv2
import numpy as np
import pytesseract
import platform
import os
from typing import Tuple, Optional
from pathlib import Path

from .config import ExtractorConfig
from .logging_utils import LoggerMixin


class OCREngine(LoggerMixin):
    """Handles Tesseract OCR operations"""
    
    def __init__(self, config: ExtractorConfig):
        self.config = config
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """Auto-detect and configure Tesseract executable"""
        if platform.system() == "Windows":
            # Common Windows installation paths
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Tesseract-OCR\tesseract.exe",
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.logger.info(f"Tesseract found at: {path}")
                    break
            else:
                self.logger.warning("Tesseract not found in common Windows paths")
        
        # Verify Tesseract is accessible
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract version: {version}")
        except Exception as e:
            self.logger.error(f"Tesseract not accessible: {e}")
            raise RuntimeError(
                "Tesseract is not installed or not in PATH. "
                "Please install from https://github.com/tesseract-ocr/tesseract"
            )
    
    def preprocess_image(
        self,
        image: np.ndarray,
        upscale_factor: Optional[float] = None
    ) -> Tuple[str, float, np.ndarray]:
        """
        Preprocess image for optimal OCR
        
        Args:
            image: Input image (BGR format)
            upscale_factor: Factor to upscale image (default from config)
        
        Returns:
            Tuple of (text, confidence, processed_image)
        """
        if upscale_factor is None:
            upscale_factor = self.config.upscale_factor
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Reduce noise with median blur
        gray = cv2.medianBlur(gray, 3)
        
        # Upscale for better OCR
        if upscale_factor > 1.0:
            gray = cv2.resize(
                gray,
                None,
                fx=upscale_factor,
                fy=upscale_factor,
                interpolation=cv2.INTER_CUBIC
            )
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15
        )
        
        # Also try inverted threshold (some screenshots have inverted contrast)
        inv_thresh = cv2.bitwise_not(thresh)
        
        # OCR on both and choose better result
        text_normal, conf_normal = self._ocr_with_confidence(thresh)
        text_inv, conf_inv = self._ocr_with_confidence(inv_thresh)
        
        if conf_normal >= conf_inv:
            return text_normal, conf_normal, thresh
        else:
            return text_inv, conf_inv, inv_thresh
    
    def _ocr_with_confidence(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Perform OCR and calculate mean confidence
        
        Args:
            image: Preprocessed image
        
        Returns:
            Tuple of (text, mean_confidence)
        """
        try:
            # Get detailed data with confidence scores
            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
                config=self.config.tesseract_config
            )
            
            # Calculate mean confidence (excluding -1 values)
            confidences = [int(c) for c in data['conf'] if c != '-1']
            mean_conf = np.mean(confidences) if confidences else 0.0
            
            # Get full text
            text = pytesseract.image_to_string(
                image,
                config=self.config.tesseract_config
            )
            
            return text.strip(), mean_conf
            
        except Exception as e:
            self.logger.error(f"OCR error: {e}")
            return "", 0.0
    
    def extract_text(
        self,
        image: np.ndarray
    ) -> Tuple[str, float, np.ndarray]:
        """
        Main method to extract text from image
        
        Args:
            image: Input image (BGR format)
        
        Returns:
            Tuple of (text, confidence, processed_image)
        """
        return self.preprocess_image(image)


class ImageValidator(LoggerMixin):
    """Validate images before processing"""
    
    def __init__(self, config: ExtractorConfig):
        self.config = config
    
    def validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate image file
        
        Args:
            file_path: Path to image file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_image_size_mb:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {self.config.max_image_size_mb}MB)"
        
        # Check file extension
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        if path.suffix.lower() not in valid_extensions:
            return False, f"Unsupported file format: {path.suffix}"
        
        return True, None
    
    def validate_image(self, image: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Validate loaded image
        
        Args:
            image: OpenCV image array
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if image is None:
            return False, "Failed to load image (corrupted or unsupported format)"
        
        # Check dimensions
        height, width = image.shape[:2]
        if height < 100 or width < 100:
            return False, f"Image too small: {width}x{height} (min: 100x100)"
        
        if height > 10000 or width > 10000:
            return False, f"Image too large: {width}x{height} (max: 10000x10000)"
        
        return True, None
    
    def load_and_validate(self, file_path: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Load and validate image file
        
        Args:
            file_path: Path to image file
        
        Returns:
            Tuple of (image, error_message)
        """
        # Validate file
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            return None, error
        
        # Load image
        try:
            image = cv2.imread(file_path)
        except Exception as e:
            return None, f"Error loading image: {e}"
        
        # Validate loaded image
        is_valid, error = self.validate_image(image)
        if not is_valid:
            return None, error
        
        return image, None
