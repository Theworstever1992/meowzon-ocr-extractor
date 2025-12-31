"""
Interactive review mode for correcting extractions
"""

import pandas as pd
from pathlib import Path
import cv2
from typing import Optional

from .logging_utils import LoggerMixin


class InteractiveReviewer(LoggerMixin):
    """Interactive review system for low-confidence extractions"""
    
    def __init__(self, confidence_threshold: float = 70.0):
        self.confidence_threshold = confidence_threshold
    
    def review_results(self, df: pd.DataFrame, image_folder: Optional[str] = None) -> pd.DataFrame:
        """
        Allow user to interactively review and correct low-confidence extractions
        
        Args:
            df: DataFrame with extraction results
            image_folder: Path to folder containing original images
        
        Returns:
            Modified DataFrame with corrections
        """
        # Filter low-confidence results
        low_conf_mask = (
            (df['Overall Confidence'] < self.confidence_threshold) |
            (df['Status'] == 'Review Required') |
            (df['Status'] == 'Failed')
        )
        
        low_conf = df[low_conf_mask]
        
        if len(low_conf) == 0:
            print("\n✅ All extractions have high confidence! No review needed.\n")
            return df
        
        print("\n" + "=" * 70)
        print(f"📋 INTERACTIVE REVIEW MODE")
        print("=" * 70)
        print(f"\nFound {len(low_conf)} extractions that need review:\n")
        
        for idx in low_conf.index:
            row = df.loc[idx]
            
            # Display extraction info
            self._display_extraction(row, idx + 1, len(low_conf))
            
            # Show image if available
            if image_folder:
                self._show_image(row['File Name'], image_folder)
            
            # Get user action
            action = self._get_user_action()
            
            if action == 'skip':
                continue
            elif action == 'delete':
                df = df.drop(idx)
                print("❌ Deleted\n")
            elif action == 'edit':
                df.loc[idx] = self._edit_extraction(row)
                print("✅ Updated\n")
            elif action == 'quit':
                print("\n🚪 Exiting review mode...\n")
                break
        
        return df.reset_index(drop=True)
    
    def _display_extraction(self, row: pd.Series, current: int, total: int):
        """Display extraction information"""
        print("\n" + "-" * 70)
        print(f"📄 {current}/{total}: {row['File Name']}")
        print("-" * 70)
        print(f"Status: {row['Status']}")
        print(f"Confidence: {row.get('Overall Confidence', 'N/A')}%")
        print(f"OCR Confidence: {row.get('Tesseract Confidence (%)', 'N/A')}%")
        print(f"AI Used: {row.get('AI Used', 'No')}")
        
        print("\n📦 Extracted Data:")
        print(f"  Order ID(s):  {row.get('Order IDs', 'None')}")
        print(f"  Date(s):      {row.get('Dates', 'None')}")
        print(f"  Total(s):     {row.get('Totals', 'None')}")
        print(f"  Items:        {row.get('Items', 'None')}")
        print(f"  Seller(s):    {row.get('Sellers', 'None')}")
        
        if row.get('Validation Issues'):
            print(f"\n⚠️  Issues: {row['Validation Issues']}")
        
        if row.get('Raw Tesseract Snippet'):
            print(f"\n📝 OCR Text Preview:")
            print(f"  {row['Raw Tesseract Snippet'][:150]}...")
    
    def _show_image(self, filename: str, image_folder: str):
        """Display image in a window"""
        image_path = Path(image_folder) / filename
        
        if not image_path.exists():
            return
        
        try:
            import platform
            
            # Try to open image
            img = cv2.imread(str(image_path))
            if img is None:
                return
            
            # Resize if too large
            height, width = img.shape[:2]
            max_dimension = 800
            
            if height > max_dimension or width > max_dimension:
                scale = max_dimension / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height))
            
            # Show image
            window_name = f"Review: {filename}"
            cv2.imshow(window_name, img)
            
            print(f"\n🖼️  Image displayed in window. Press any key to continue...")
            cv2.waitKey(0)
            cv2.destroyWindow(window_name)
            
        except Exception as e:
            self.logger.debug(f"Could not display image: {e}")
    
    def _get_user_action(self) -> str:
        """Get user's desired action"""
        print("\n" + "=" * 70)
        print("Actions:")
        print("  [E]dit   - Correct the extraction")
        print("  [D]elete - Remove this entry")
        print("  [K]eep   - Keep as-is and continue")
        print("  [S]kip   - Skip to next (same as Keep)")
        print("  [Q]uit   - Exit review mode")
        print("=" * 70)
        
        while True:
            choice = input("\nYour choice: ").strip().lower()
            
            if choice in ['e', 'edit']:
                return 'edit'
            elif choice in ['d', 'delete', 'del']:
                confirm = input("❓ Are you sure you want to delete? (y/n): ").strip().lower()
                if confirm == 'y':
                    return 'delete'
            elif choice in ['k', 'keep', 's', 'skip', '']:
                return 'skip'
            elif choice in ['q', 'quit', 'exit']:
                return 'quit'
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _edit_extraction(self, row: pd.Series) -> pd.Series:
        """Allow user to edit extraction fields"""
        print("\n✏️  EDIT MODE")
        print("Press Enter to keep current value, or type new value:")
        print("-" * 70)
        
        # Order ID
        current = row.get('Order IDs', '')
        new_value = input(f"Order ID(s) [{current}]: ").strip()
        if new_value:
            row['Order IDs'] = new_value
        
        # Date
        current = row.get('Dates', '')
        new_value = input(f"Date(s) [{current}]: ").strip()
        if new_value:
            row['Dates'] = new_value
        
        # Total
        current = row.get('Totals', '')
        new_value = input(f"Total(s) [{current}]: ").strip()
        if new_value:
            row['Totals'] = new_value
        
        # Items
        current = row.get('Items', '')
        print(f"\nItems (separate multiple with |):")
        print(f"Current: {current}")
        new_value = input("New value: ").strip()
        if new_value:
            row['Items'] = new_value
        
        # Seller
        current = row.get('Sellers', '')
        new_value = input(f"Seller(s) [{current}]: ").strip()
        if new_value:
            row['Sellers'] = new_value
        
        # Update status if corrected
        if row.get('Order IDs'):
            row['Status'] = 'Success (Manual)'
        
        return row


def run_interactive_review(
    csv_path: str,
    image_folder: Optional[str] = None,
    confidence_threshold: float = 70.0
) -> str:
    """
    Run interactive review on a CSV file
    
    Args:
        csv_path: Path to CSV file with extraction results
        image_folder: Path to folder with original images
        confidence_threshold: Confidence threshold for review
    
    Returns:
        Path to corrected CSV file
    """
    # Load results
    df = pd.read_csv(csv_path)
    
    # Create reviewer
    reviewer = InteractiveReviewer(confidence_threshold)
    
    # Run review
    df_corrected = reviewer.review_results(df, image_folder)
    
    # Save corrected results
    output_path = str(Path(csv_path).with_stem(Path(csv_path).stem + "_corrected"))
    df_corrected.to_csv(output_path, index=False)
    
    print(f"\n✅ Corrected results saved to: {output_path}\n")
    
    return output_path
