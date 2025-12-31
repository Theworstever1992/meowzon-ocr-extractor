"""
Data extraction utilities for parsing OCR text
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class DataExtractor:
    """Extract structured data from OCR text using regex patterns"""
    
    # Regex patterns
    ORDER_ID_PATTERN = r'\d{3}-\d{7}-\d{7}'
    PRICE_PATTERN = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
    DATE_PATTERN = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}'
    TOTAL_PATTERN = r'(?:Order Total|Grand Total|Total|Subtotal)[\s:]*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    QUANTITY_PATTERN = r'(?:Qty|Quantity)[\.:]?\s*(\d+)'
    SELLER_PATTERN = r'Sold by[:\s]*(.+?)(?:\n|$)'
    TRACKING_PATTERN = r'(?:Tracking|Track)[:\s]*([A-Z0-9]{10,})'
    
    @staticmethod
    def extract_order_ids(text: str) -> List[str]:
        """Extract Amazon order IDs (format: XXX-XXXXXXX-XXXXXXX)"""
        order_ids = re.findall(DataExtractor.ORDER_ID_PATTERN, text)
        return list(set(order_ids))  # Remove duplicates
    
    @staticmethod
    def extract_prices(text: str) -> List[str]:
        """Extract all price values"""
        return re.findall(DataExtractor.PRICE_PATTERN, text)
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """Extract dates in various formats"""
        dates = re.findall(DataExtractor.DATE_PATTERN, text, re.IGNORECASE)
        # Normalize dates
        normalized = []
        for date_str in dates:
            try:
                # Try to parse and reformat
                parsed = datetime.strptime(date_str.replace(',', ''), '%b %d %Y')
                normalized.append(parsed.strftime('%Y-%m-%d'))
            except:
                normalized.append(date_str)
        return normalized
    
    @staticmethod
    def extract_totals(text: str) -> List[str]:
        """Extract order total amounts"""
        totals = re.findall(DataExtractor.TOTAL_PATTERN, text, re.IGNORECASE)
        return totals
    
    @staticmethod
    def extract_quantities(text: str) -> List[str]:
        """Extract item quantities"""
        quantities = re.findall(DataExtractor.QUANTITY_PATTERN, text, re.IGNORECASE)
        return quantities
    
    @staticmethod
    def extract_sellers(text: str) -> List[str]:
        """Extract seller names"""
        sellers = re.findall(DataExtractor.SELLER_PATTERN, text)
        # Clean up seller names
        cleaned = [s.strip() for s in sellers if len(s.strip()) > 2]
        return list(set(cleaned))
    
    @staticmethod
    def extract_tracking_numbers(text: str) -> List[str]:
        """Extract tracking numbers"""
        tracking = re.findall(DataExtractor.TRACKING_PATTERN, text, re.IGNORECASE)
        return list(set(tracking))
    
    @staticmethod
    def extract_items(text: str) -> List[str]:
        """
        Extract item names from text using heuristics
        Looks for lines that likely represent product names
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        items = []
        for line in lines:
            # Remove prices and order IDs from line
            clean = re.sub(r'\$[\d,]+\.?\d*|\d{3}-\d{7}.*', '', line).strip()
            
            # Skip if line is too short or contains common non-item keywords
            if len(clean) < 15:
                continue
            
            skip_keywords = [
                'total', 'shipping', 'tax', 'qty', 'quantity', 'sold by',
                'order', 'delivery', 'arrives', 'return', 'refund',
                'customer', 'account', 'payment', 'credit', 'gift'
            ]
            
            if any(keyword in clean.lower() for keyword in skip_keywords):
                continue
            
            # Should start with capital letter (product names typically do)
            if clean and clean[0].isupper():
                items.append(clean)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        
        return unique_items
    
    @staticmethod
    def extract_all(text: str) -> Dict[str, List[str]]:
        """
        Extract all data types from text
        
        Returns:
            Dictionary with all extracted data
        """
        return {
            'order_ids': DataExtractor.extract_order_ids(text),
            'prices': DataExtractor.extract_prices(text),
            'dates': DataExtractor.extract_dates(text),
            'totals': DataExtractor.extract_totals(text),
            'quantities': DataExtractor.extract_quantities(text),
            'sellers': DataExtractor.extract_sellers(text),
            'tracking_numbers': DataExtractor.extract_tracking_numbers(text),
            'items': DataExtractor.extract_items(text),
        }


class DataValidator:
    """Validate extracted data"""
    
    @staticmethod
    def validate_order_id(order_id: str) -> bool:
        """Validate Amazon order ID format (XXX-XXXXXXX-XXXXXXX)"""
        if not order_id:
            return False
        return bool(re.match(r'^\d{3}-\d{7}-\d{7}$', order_id))
    
    @staticmethod
    def validate_price(price: str) -> bool:
        """Validate price format ($X,XXX.XX)"""
        if not price:
            return False
        return bool(re.match(r'^\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?$', price))
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format"""
        if not date_str:
            return False
        
        # Try common date formats
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%b %d, %Y', '%B %d, %Y']
        for fmt in formats:
            try:
                datetime.strptime(date_str.replace(',', ''), fmt)
                return True
            except ValueError:
                continue
        return False
    
    @staticmethod
    def calculate_confidence(
        extracted_data: Dict[str, List[str]],
        ocr_confidence: float
    ) -> float:
        """
        Calculate overall data extraction confidence score
        
        Args:
            extracted_data: Dictionary of extracted data
            ocr_confidence: Base OCR confidence (0-100)
        
        Returns:
            Confidence score (0-100)
        """
        score = ocr_confidence * 0.4  # Base OCR contributes 40%
        
        # Add points for valid data
        if extracted_data.get('order_ids'):
            if DataValidator.validate_order_id(extracted_data['order_ids'][0]):
                score += 25
        
        if extracted_data.get('items'):
            score += min(len(extracted_data['items']) * 5, 20)
        
        if extracted_data.get('totals'):
            score += 10
        
        if extracted_data.get('dates'):
            score += 5
        
        return min(score, 100.0)
    
    @staticmethod
    def validate_extraction(extracted_data: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
        """
        Validate extracted data and return issues
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for order ID
        if not extracted_data.get('order_ids'):
            issues.append("No order ID found")
        elif not DataValidator.validate_order_id(extracted_data['order_ids'][0]):
            issues.append("Invalid order ID format")
        
        # Check for items
        if not extracted_data.get('items'):
            issues.append("No items found")
        
        # Check for prices
        if extracted_data.get('prices'):
            invalid_prices = [p for p in extracted_data['prices'] 
                            if not DataValidator.validate_price(p)]
            if invalid_prices:
                issues.append(f"Invalid price formats: {invalid_prices}")
        
        return (len(issues) == 0, issues)
