"""
Main Meowzon extractor class
"""

import cv2
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import tempfile

from .config import ExtractorConfig
from .logging_utils import LoggerMixin
from .ocr_engine import OCREngine, ImageValidator
from .image_processor import ImageProcessor
from .data_extractor import DataExtractor, DataValidator
from .ai_providers import get_ai_provider
from .analytics import OrderAnalytics, DuplicateDetector
from .output_handler import OutputHandler, format_output_dataframe


class MeowzonExtractor(LoggerMixin):
    """Main orchestrator for order extraction"""
    
    def __init__(self, config: ExtractorConfig):
        self.config = config
        self.ocr_engine = OCREngine(config)
        self.image_processor = ImageProcessor(config)
        self.image_validator = ImageValidator(config)
        self.data_extractor = DataExtractor()
        self.data_validator = DataValidator()
        
        # Initialize AI processor if needed
        self.ai_processor = None
        if config.ai_mode != 'never':
            try:
                self.ai_processor = get_ai_provider(config)
                self.logger.info(f"AI provider initialized: {config.ai_provider}")
            except Exception as e:
                self.logger.error(f"Failed to initialize AI provider: {e}")
                if config.ai_mode == 'always':
                    raise
        
        # Create output directories
        if config.save_enhanced_images:
            Path(config.enhanced_images_folder).mkdir(parents=True, exist_ok=True)
    
    def process_single_file(self, file_path: str) -> Dict:
        """
        Process a single image file
        
        Args:
            file_path: Path to image file
        
        Returns:
            Dictionary with extraction results
        """
        filename = Path(file_path).name
        
        self.logger.debug(f"Processing: {filename}")
        
        # Load and validate image
        image, error = self.image_validator.load_and_validate(file_path)
        if error:
            self.logger.error(f"{filename}: {error}")
            return {
                "File Name": filename,
                "Status": "Failed Load",
                "Error": error
            }
        
        # Find best crop using OCR
        best_color, ocr_text, ocr_conf, best_processed, crop_params = \
            self.image_processor.find_best_crop(
                image,
                self.ocr_engine.extract_text,
                self.config.tesseract_confidence_threshold
            )
        
        crop_name = crop_params['name'] if crop_params else "Full Image"
        
        # Extract data from OCR text
        extracted = self.data_extractor.extract_all(ocr_text)
        
        # Determine if AI should be used
        use_ai = self._should_use_ai(extracted, ocr_conf)
        
        ai_used = False
        ai_provider = ""
        ai_status = ""
        
        # Use AI if determined
        if use_ai and self.ai_processor:
            self.logger.debug(f"{filename}: Using AI ({self.config.ai_provider})")
            
            # Save temporary image for AI
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                cv2.imwrite(tmp.name, best_color)
                temp_path = tmp.name
            
            try:
                ai_data, ai_status = self.ai_processor.extract(temp_path)
                
                if ai_data:
                    # Merge AI results with OCR results (prefer AI)
                    extracted = self._merge_results(extracted, ai_data)
                    ai_used = True
                    ai_provider = self.config.ai_provider
                    self.logger.info(f"{filename}: AI extraction successful")
                else:
                    self.logger.warning(f"{filename}: AI extraction failed - {ai_status}")
            
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
        
        # Calculate confidence
        overall_confidence = self.data_validator.calculate_confidence(
            extracted, ocr_conf
        )
        
        # Validate extraction
        is_valid, issues = self.data_validator.validate_extraction(extracted)
        
        # Determine status
        if extracted.get('order_ids'):
            status = "Success"
        elif extracted.get('items'):
            status = "Review Required"
        else:
            status = "Failed"
        
        # Save enhanced images if requested
        cropped_file = ""
        processed_file = ""
        
        if self.config.save_enhanced_images:
            base_name = Path(filename).stem
            ext = Path(filename).suffix
            
            # Save cropped color image
            if crop_name != "Full Image":
                safe_crop = crop_name.replace(' ', '_')
                cropped_file = f"{base_name}_cropped_{safe_crop}{ext}"
                cropped_path = Path(self.config.enhanced_images_folder) / cropped_file
                cv2.imwrite(str(cropped_path), best_color)
            
            # Save processed grayscale image
            processed_file = f"{base_name}_processed{ext}"
            processed_path = Path(self.config.enhanced_images_folder) / processed_file
            cv2.imwrite(str(processed_path), best_processed)
        
        # Build result dictionary
        result = {
            "File Name": filename,
            "Status": status,
            "Overall Confidence": round(overall_confidence, 1),
            "AI Used": "Yes" if ai_used else "No",
            "AI Provider": ai_provider,
            "AI Status": ai_status,
            "Tesseract Confidence (%)": round(ocr_conf, 1),
            "Crop Used": crop_name,
            "Order IDs": " | ".join(extracted.get('order_ids', [])),
            "Dates": " | ".join(extracted.get('dates', [])),
            "Totals": " | ".join(extracted.get('totals', [])),
            "Items": " | ".join(extracted.get('items', [])),
            "Quantities": " | ".join(extracted.get('quantities', [])),
            "Sellers": " | ".join(extracted.get('sellers', [])),
            "Prices": " | ".join(extracted.get('prices', [])),
            "Tracking Numbers": " | ".join(extracted.get('tracking_numbers', [])),
        }
        
        # Add optional fields
        if self.config.include_raw_text:
            snippet = ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text
            result["Raw Tesseract Snippet"] = snippet
        
        if self.config.include_debug_info:
            result["Cropped Image"] = cropped_file
            result["Processed Image"] = processed_file
            result["Validation Issues"] = " | ".join(issues) if issues else ""
        
        return result
    
    def _should_use_ai(self, extracted: Dict, ocr_conf: float) -> bool:
        """
        Determine if AI should be used based on OCR results
        
        Args:
            extracted: Extracted data from OCR
            ocr_conf: OCR confidence score
        
        Returns:
            True if AI should be used
        """
        if self.config.ai_mode == 'always':
            return True
        
        if self.config.ai_mode == 'never':
            return False
        
        # Hybrid mode - use AI if:
        # 1. Low OCR confidence
        # 2. No order ID found
        # 3. No items found
        if ocr_conf < self.config.tesseract_confidence_threshold:
            return True
        
        if not extracted.get('order_ids'):
            return True
        
        if not extracted.get('items'):
            return True
        
        return False
    
    def _merge_results(
        self,
        ocr_data: Dict[str, List[str]],
        ai_data: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Merge OCR and AI results, preferring AI data
        
        Args:
            ocr_data: Data from OCR extraction
            ai_data: Data from AI extraction
        
        Returns:
            Merged data dictionary
        """
        merged = {}
        
        for key in ocr_data.keys():
            # Prefer AI data if available
            ai_values = ai_data.get(key, [])
            ocr_values = ocr_data.get(key, [])
            
            if ai_values:
                merged[key] = ai_values
            elif ocr_values:
                merged[key] = ocr_values
            else:
                merged[key] = []
        
        return merged
    
    def process_files(self, file_paths: List[str]) -> List[Dict]:
        """
        Process multiple files
        
        Args:
            file_paths: List of file paths to process
        
        Returns:
            List of result dictionaries
        """
        if self.config.parallel_processing:
            return self._process_parallel(file_paths)
        else:
            return self._process_sequential(file_paths)
    
    def _process_sequential(self, file_paths: List[str]) -> List[Dict]:
        """Process files sequentially with progress bar"""
        results = []
        
        for file_path in tqdm(file_paths, desc="🐾 Processing", unit="file"):
            try:
                result = self.process_single_file(file_path)
                results.append(result)
                
                # Log result
                status_emoji = "✅" if result['Status'] == "Success" else \
                              "⚠️" if result['Status'] == "Review Required" else "❌"
                self.logger.info(
                    f"{status_emoji} {result['File Name']}: {result['Status']} "
                    f"(conf: {result['Tesseract Confidence (%)']:.1f}%)"
                )
                
            except Exception as e:
                self.logger.error(f"Error processing {Path(file_path).name}: {e}")
                results.append({
                    "File Name": Path(file_path).name,
                    "Status": "Error",
                    "Error": str(e)
                })
        
        return results
    
    def _process_parallel(self, file_paths: List[str]) -> List[Dict]:
        """Process files in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_single_file, fp): fp
                for fp in file_paths
            }
            
            # Process completed tasks with progress bar
            for future in tqdm(
                as_completed(future_to_file),
                total=len(file_paths),
                desc="🐾 Processing",
                unit="file"
            ):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing {Path(file_path).name}: {e}")
                    results.append({
                        "File Name": Path(file_path).name,
                        "Status": "Error",
                        "Error": str(e)
                    })
        
        return results
    
    def run(self):
        """
        Main execution method
        
        Returns:
            Path to output file(s)
        """
        self.logger.info("=" * 60)
        self.logger.info("🐱 MEOWZON EXTRACTION STARTING")
        self.logger.info("=" * 60)
        self.logger.info(f"Input folder: {self.config.input_folder}")
        self.logger.info(f"Output: {self.config.output_csv}")
        self.logger.info(f"AI mode: {self.config.ai_mode}")
        
        if self.config.ai_mode != 'never':
            self.logger.info(f"AI provider: {self.config.ai_provider}")
        
        # Find all image files
        input_path = Path(self.config.input_folder)
        extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        
        file_paths = [
            str(p) for p in input_path.iterdir()
            if p.is_file() and p.suffix.lower() in extensions
        ]
        
        if not file_paths:
            self.logger.warning(f"No image files found in {self.config.input_folder}")
            return None
        
        self.logger.info(f"Found {len(file_paths)} image files")
        
        # Process all files
        results = self.process_files(file_paths)
        
        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(results)
        
        # Post-processing
        if self.config.enable_duplicate_detection:
            self.logger.info("Detecting duplicates...")
            df = DuplicateDetector.find_duplicates(df)
            duplicates = DuplicateDetector.get_duplicate_groups(df)
            if duplicates:
                self.logger.warning(f"Found {len(duplicates)} duplicate order(s)")
        
        # Format output
        df = format_output_dataframe(df)
        
        # Generate analytics
        summary = None
        analytics_plot_path = None
        
        if self.config.enable_analytics:
            self.logger.info("Generating analytics...")
            summary = OrderAnalytics.generate_summary(df)
            
            # Print text summary
            text_report = OrderAnalytics.generate_text_report(df, summary)
            print("\n" + text_report)
            
            # Generate plots
            if self.config.generate_plots:
                try:
                    analytics_plot_path = str(Path(self.config.output_csv).parent / "meowzon_analytics.png")
                    OrderAnalytics.plot_statistics(df, analytics_plot_path)
                    self.logger.info(f"Analytics plot saved: {analytics_plot_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to generate plots: {e}")
        
        # Save outputs
        self.logger.info("Saving results...")
        
        if self.config.output_format == 'all':
            saved_files = OutputHandler.save_all_formats(
                df,
                self.config.output_csv,
                summary,
                analytics_plot_path
            )
            self.logger.info(f"Saved {len(saved_files)} output files")
            for f in saved_files:
                self.logger.info(f"  📄 {f}")
            
        else:
            # Save single format
            output_path = self.config.output_csv
            
            if self.config.output_format == 'csv':
                OutputHandler.save_csv(df, output_path)
            elif self.config.output_format == 'excel':
                output_path = str(Path(output_path).with_suffix('.xlsx'))
                OutputHandler.save_excel(df, output_path)
            elif self.config.output_format == 'json':
                output_path = str(Path(output_path).with_suffix('.json'))
                OutputHandler.save_json(df, output_path)
            elif self.config.output_format == 'html':
                output_path = str(Path(output_path).with_suffix('.html'))
                OutputHandler.save_html_report(df, output_path, summary, analytics_plot_path)
            
            self.logger.info(f"Results saved: {output_path}")
        
        self.logger.info("=" * 60)
        self.logger.info("✅ EXTRACTION COMPLETE!")
        self.logger.info("=" * 60)
        
        return self.config.output_csv
