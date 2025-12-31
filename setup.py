"""
Setup script for Meowzon OCR Extractor
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="meowzon-ocr-extractor",
    version="3.0.0",
    author="Meowzon Team",
    description="Cat-themed AI-hybrid OCR tool for extracting Amazon order details from screenshots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/meowzon-ocr-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "pytesseract>=0.3.10",
        "pandas>=2.0.0",
        "tqdm>=4.65.0",
        "requests>=2.31.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "ai": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "google-generativeai>=0.3.0",
        ],
        "analytics": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
        "excel": [
            "openpyxl>=3.1.0",
        ],
        "full": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "google-generativeai>=0.3.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "openpyxl>=3.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "meowzon=main:main",
        ],
    },
    include_package_data=True,
    keywords="ocr amazon orders extraction tesseract ai vision computer-vision",
)
