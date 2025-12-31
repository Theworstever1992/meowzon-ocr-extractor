"""
Image preprocessing and cropping strategies
"""

import cv2
import numpy as np
import re
from typing import Tuple, List, Dict, Optional

from .config import ExtractorConfig
from .logging_utils import LoggerMixin


class ImageProcessor(LoggerMixin):
    """Handles image preprocessing and cropping strategies"""
    
    def __init__(self, config: ExtractorConfig):
        self.config = config
        self.crop_strategies = config.crop_strategies
    
    def apply_crop(
        self,
        image: np.ndarray,
        crop_params: Dict[str, float]
    ) -> Optional[np.ndarray]:
        """
        Apply crop parameters to image
        
        Args:
            image: Input image
            crop_params: Dict with top, bottom, left, right percentages
        
        Returns:
            Cropped image or None if invalid crop
        """
        height, width = image.shape[:2]
        
        start_y = int(height * crop_params["top"])
        end_y = height - int(height * crop_params["bottom"])
        start_x = int(width * crop_params["left"])
        end_x = width - int(width * crop_params["right"])
        
        # Validate crop dimensions
        if end_y <= start_y or end_x <= start_x:
            self.logger.warning(
                f"Invalid crop dimensions: y({start_y}:{end_y}) x({start_x}:{end_x})"
            )
            return None
        
        if end_y - start_y < 50 or end_x - start_x < 50:
            self.logger.warning("Cropped region too small")
            return None
        
        return image[start_y:end_y, start_x:end_x]
    
    def find_best_crop(
        self,
        image: np.ndarray,
        ocr_function,
        threshold_confidence: float = 70.0
    ) -> Tuple[np.ndarray, str, float, np.ndarray, Optional[Dict]]:
        """
        Try multiple cropping strategies and return the best one
        
        Args:
            image: Input image (color BGR)
            ocr_function: Function that takes image and returns (text, confidence, processed)
            threshold_confidence: Early exit if confidence exceeds this
        
        Returns:
            Tuple of (best_color_image, text, confidence, processed_image, crop_params)
        """
        best_text = ""
        best_conf = 0.0
        best_color = image.copy()
        best_processed = None
        best_crop_name = "Full Image"
        best_crop_params = None
        
        # Try full image first
        text, conf, processed = ocr_function(image)
        best_text = text
        best_conf = conf
        best_processed = processed
        
        # Calculate score (higher for having order ID)
        score = conf + 100 if self._has_order_id(text) else conf
        
        self.logger.debug(
            f"Full image: confidence={conf:.1f}%, "
            f"order_id={self._has_order_id(text)}, score={score:.1f}"
        )
        
        # Early exit if very confident
        if conf >= threshold_confidence and self._has_order_id(text):
            return best_color, best_text, best_conf, best_processed, best_crop_params
        
        # Try each cropping strategy
        for crop_dict in self.crop_strategies:
            cropped = self.apply_crop(image, crop_dict)
            
            if cropped is None:
                continue
            
            text, conf, processed = ocr_function(cropped)
            crop_score = conf + 100 if self._has_order_id(text) else conf
            
            self.logger.debug(
                f"{crop_dict['name']}: confidence={conf:.1f}%, "
                f"order_id={self._has_order_id(text)}, score={crop_score:.1f}"
            )
            
            if crop_score > score:
                score = crop_score
                best_text = text
                best_conf = conf
                best_color = cropped
                best_processed = processed
                best_crop_name = crop_dict['name']
                best_crop_params = crop_dict
                
                # Early exit if very confident
                if conf >= threshold_confidence and self._has_order_id(text):
                    break
        
        self.logger.info(
            f"Best crop: '{best_crop_name}' with confidence {best_conf:.1f}%"
        )
        
        return best_color, best_text, best_conf, best_processed, best_crop_params
    
    @staticmethod
    def _has_order_id(text: str) -> bool:
        """Check if text contains Amazon order ID pattern"""
        return bool(re.search(r'\d{3}-\d{7}-\d{7}', text))
    
    def enhance_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Apply various enhancement techniques to improve OCR
        
        Args:
            image: Input grayscale or color image
        
        Returns:
            Enhanced image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def detect_and_correct_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct image skew/rotation
        
        Args:
            image: Input image
        
        Returns:
            Deskewed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is None:
            return image
        
        # Calculate average angle
        angles = []
        for line in lines[:10]:  # Use first 10 lines
            rho, theta = line[0]
            angle = (theta * 180 / np.pi) - 90
            angles.append(angle)
        
        if not angles:
            return image
        
        avg_angle = np.median(angles)
        
        # Only correct if skew is significant
        if abs(avg_angle) < 0.5:
            return image
        
        # Rotate image
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
        rotated = cv2.warpAffine(
            image, matrix, (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        self.logger.info(f"Corrected skew angle: {avg_angle:.2f}°")
        
        return rotated
    
    def remove_background(self, image: np.ndarray) -> np.ndarray:
        """
        Attempt to remove background and enhance text
        
        Args:
            image: Input image
        
        Returns:
            Image with background removed
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Normalize
        normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            normalized,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return binary
