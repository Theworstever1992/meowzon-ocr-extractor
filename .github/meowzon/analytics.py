"""
Analytics and reporting utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path

from .logging_utils import LoggerMixin


class OrderAnalytics(LoggerMixin):
    """Generate analytics from extracted order data"""
    
    @staticmethod
    def generate_summary(df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics
        
        Args:
            df: DataFrame with extracted order data
        
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_files': len(df),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'review_required': 0,
            'ai_used_count': 0,
            'ai_usage_rate': 0.0,
            'avg_confidence': 0.0,
            'total_orders': 0,
            'total_items': 0,
            'unique_sellers': 0,
            'avg_items_per_order': 0.0,
        }
        
        if len(df) == 0:
            return summary
        
        # Status counts
        if 'Status' in df.columns:
            summary['successful_extractions'] = df['Status'].str.contains('Success', case=False, na=False).sum()
            summary['review_required'] = df['Status'].str.contains('Review', case=False, na=False).sum()
            summary['failed_extractions'] = len(df) - summary['successful_extractions'] - summary['review_required']
        
        # AI usage
        if 'AI Used' in df.columns:
            summary['ai_used_count'] = (df['AI Used'] == 'Yes').sum()
            summary['ai_usage_rate'] = (summary['ai_used_count'] / len(df)) * 100
        
        # Confidence
        if 'Tesseract Confidence (%)' in df.columns:
            summary['avg_confidence'] = df['Tesseract Confidence (%)'].mean()
        
        # Orders
        if 'Order IDs' in df.columns:
            order_counts = df['Order IDs'].str.split('|').str.len()
            summary['total_orders'] = order_counts.sum()
        
        # Items
        if 'Items' in df.columns:
            item_counts = df['Items'].str.split('|').str.len()
            summary['total_items'] = item_counts.sum()
            if summary['total_orders'] > 0:
                summary['avg_items_per_order'] = summary['total_items'] / summary['total_orders']
        
        # Sellers
        if 'Sellers' in df.columns:
            all_sellers = df['Sellers'].str.split('|').dropna()
            unique_sellers = set()
            for sellers in all_sellers:
                unique_sellers.update(sellers)
            summary['unique_sellers'] = len(unique_sellers)
        
        return summary
    
    @staticmethod
    def generate_text_report(df: pd.DataFrame, summary: Dict) -> str:
        """
        Generate a text summary report
        
        Args:
            df: DataFrame with extracted order data
            summary: Summary statistics dictionary
        
        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 60)
        report.append("  🐱 MEOWZON EXTRACTION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overview
        report.append("📊 OVERVIEW")
        report.append("-" * 60)
        report.append(f"Total Files Processed: {summary['total_files']}")
        report.append(f"Successful Extractions: {summary['successful_extractions']} "
                     f"({summary['successful_extractions']/summary['total_files']*100:.1f}%)")
        report.append(f"Review Required: {summary['review_required']}")
        report.append(f"Failed: {summary['failed_extractions']}")
        report.append("")
        
        # AI Usage
        report.append("🤖 AI USAGE")
        report.append("-" * 60)
        report.append(f"AI Used: {summary['ai_used_count']} files ({summary['ai_usage_rate']:.1f}%)")
        report.append(f"Average OCR Confidence: {summary['avg_confidence']:.1f}%")
        report.append("")
        
        # Order Data
        report.append("📦 ORDER DATA")
        report.append("-" * 60)
        report.append(f"Total Orders Found: {summary['total_orders']}")
        report.append(f"Total Items Found: {summary['total_items']}")
        report.append(f"Avg Items per Order: {summary['avg_items_per_order']:.1f}")
        report.append(f"Unique Sellers: {summary['unique_sellers']}")
        report.append("")
        
        # Crop strategies
        if 'Crop Used' in df.columns:
            report.append("✂️ CROP STRATEGIES")
            report.append("-" * 60)
            crop_counts = df['Crop Used'].value_counts()
            for crop, count in crop_counts.items():
                report.append(f"  {crop}: {count} ({count/len(df)*100:.1f}%)")
            report.append("")
        
        # AI providers
        if 'AI Provider' in df.columns:
            ai_df = df[df['AI Used'] == 'Yes']
            if len(ai_df) > 0:
                report.append("🔮 AI PROVIDERS")
                report.append("-" * 60)
                provider_counts = ai_df['AI Provider'].value_counts()
                for provider, count in provider_counts.items():
                    report.append(f"  {provider}: {count}")
                report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    @staticmethod
    def plot_statistics(df: pd.DataFrame, output_path: str):
        """
        Generate visualization plots
        
        Args:
            df: DataFrame with extracted order data
            output_path: Path to save plot image
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
        except ImportError:
            raise ImportError("Matplotlib not installed. Run: pip install matplotlib")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('🐱 Meowzon Extraction Analytics', fontsize=16, fontweight='bold')
        
        # 1. Confidence distribution
        if 'Tesseract Confidence (%)' in df.columns:
            conf_data = df['Tesseract Confidence (%)'].dropna()
            if len(conf_data) > 0:
                axes[0, 0].hist(conf_data, bins=20, color='skyblue', edgecolor='black')
                axes[0, 0].set_title('OCR Confidence Distribution')
                axes[0, 0].set_xlabel('Confidence (%)')
                axes[0, 0].set_ylabel('Count')
                axes[0, 0].axvline(conf_data.mean(), color='red', linestyle='--', 
                                  label=f'Mean: {conf_data.mean():.1f}%')
                axes[0, 0].legend()
        
        # 2. AI usage pie chart
        if 'AI Used' in df.columns:
            ai_counts = df['AI Used'].value_counts()
            if len(ai_counts) > 0:
                colors = ['#90EE90', '#FFB6C1']
                axes[0, 1].pie(ai_counts.values, labels=ai_counts.index, autopct='%1.1f%%',
                              colors=colors, startangle=90)
                axes[0, 1].set_title('AI Usage')
        
        # 3. Status distribution
        if 'Status' in df.columns:
            # Simplify status for plotting
            status_simple = df['Status'].apply(lambda x: 
                'Success' if 'Success' in str(x) else
                'Review' if 'Review' in str(x) else
                'Failed'
            )
            status_counts = status_simple.value_counts()
            colors_status = {'Success': '#90EE90', 'Review': '#FFD700', 'Failed': '#FFB6C1'}
            axes[1, 0].bar(status_counts.index, status_counts.values,
                          color=[colors_status.get(s, 'gray') for s in status_counts.index])
            axes[1, 0].set_title('Extraction Status')
            axes[1, 0].set_ylabel('Count')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Crop strategies
        if 'Crop Used' in df.columns:
            crop_counts = df['Crop Used'].value_counts().head(10)
            if len(crop_counts) > 0:
                axes[1, 1].barh(crop_counts.index, crop_counts.values, color='coral')
                axes[1, 1].set_title('Crop Strategies Used')
                axes[1, 1].set_xlabel('Count')
                axes[1, 1].invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()


class DuplicateDetector(LoggerMixin):
    """Detect and handle duplicate orders"""
    
    @staticmethod
    def find_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Flag duplicate orders in dataframe
        
        Args:
            df: DataFrame with order data
        
        Returns:
            DataFrame with is_duplicate column added
        """
        if 'Order IDs' not in df.columns:
            df['is_duplicate'] = False
            return df
        
        # Create a column with first order ID
        df['_first_order_id'] = df['Order IDs'].str.split('|').str[0]
        
        # Mark duplicates (keep first occurrence)
        df['is_duplicate'] = df.duplicated(subset=['_first_order_id'], keep='first')
        
        # Clean up temp column
        df.drop('_first_order_id', axis=1, inplace=True)
        
        return df
    
    @staticmethod
    def get_duplicate_groups(df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Get groups of duplicate files by order ID
        
        Args:
            df: DataFrame with order data
        
        Returns:
            Dictionary mapping order_id -> list of filenames
        """
        if 'Order IDs' not in df.columns or 'File Name' not in df.columns:
            return {}
        
        duplicates = {}
        
        for _, row in df.iterrows():
            order_ids = str(row['Order IDs']).split('|')
            if order_ids and order_ids[0] and order_ids[0] != 'nan':
                order_id = order_ids[0].strip()
                if order_id not in duplicates:
                    duplicates[order_id] = []
                duplicates[order_id].append(row['File Name'])
        
        # Keep only actual duplicates (more than one file)
        duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
        
        return duplicates
    
    @staticmethod
    def merge_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge duplicate order entries, keeping best data
        
        Args:
            df: DataFrame with order data
        
        Returns:
            DataFrame with duplicates merged
        """
        if 'Order IDs' not in df.columns:
            return df
        
        # Get first order ID for grouping
        df['_first_order_id'] = df['Order IDs'].str.split('|').str[0]
        
        # Group by order ID
        grouped = df.groupby('_first_order_id')
        
        merged_rows = []
        
        for order_id, group in grouped:
            if len(group) == 1:
                # No duplicates, keep as is
                merged_rows.append(group.iloc[0])
            else:
                # Merge duplicates - keep row with highest confidence
                if 'Tesseract Confidence (%)' in group.columns:
                    best_row = group.loc[group['Tesseract Confidence (%)'].idxmax()]
                else:
                    best_row = group.iloc[0]
                
                # Merge file names
                filenames = ' + '.join(group['File Name'].tolist())
                best_row['File Name'] = filenames
                best_row['is_duplicate'] = True
                
                merged_rows.append(best_row)
        
        result = pd.DataFrame(merged_rows)
        result.drop('_first_order_id', axis=1, inplace=True, errors='ignore')
        
        return result.reset_index(drop=True)
