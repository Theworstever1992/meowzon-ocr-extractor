"""
AI provider implementations for vision-based extraction
"""

from abc import ABC, abstractmethod
import base64
import json
import time
import requests
from typing import Dict, List, Optional, Tuple

from .config import ExtractorConfig
from .logging_utils import LoggerMixin


# AI extraction prompt template
AI_EXTRACTION_PROMPT = """
You are an expert Amazon order analyst. Extract structured data from this Amazon order screenshot.

Return ONLY valid JSON with this exact structure (no markdown, no extra text):

{
  "order_id": "string or null",
  "order_date": "string or null",
  "total": "string or null",
  "items": [
    {
      "name": "string",
      "quantity": "integer or null",
      "price": "string or null"
    }
  ],
  "seller": "string or null",
  "tracking_number": "string or null",
  "other_prices": ["array of strings"],
  "shipping_address": "string or null"
}

Rules:
- Use null for missing data, never leave fields undefined
- Keep prices in "$X.XX" format
- Extract ALL items visible
- Be precise and accurate
- Return ONLY the JSON object
""".strip()


class AIProvider(ABC):
    """Base class for AI vision providers"""
    
    def __init__(self, config: ExtractorConfig):
        self.config = config
        self.max_retries = config.ai_max_retries
        self.timeout = config.ai_timeout
    
    @abstractmethod
    def extract(self, image_path: str) -> Tuple[Optional[Dict], str]:
        """
        Extract data from image using AI
        
        Args:
            image_path: Path to image file
        
        Returns:
            Tuple of (extracted_data_dict, status_message)
        """
        pass
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """
        Parse JSON from AI response, handling markdown code blocks
        
        Args:
            content: Raw response content
        
        Returns:
            Parsed JSON dict or None
        """
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith('```'):
            # Remove opening ```json or ```
            lines = content.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            # Remove closing ```
            if lines[-1].strip() == '```':
                lines = lines[:-1]
            content = '\n'.join(lines)
        
        # Try to parse JSON
        try:
            data = json.loads(content)
            return data
        except json.JSONDecodeError as e:
            # Try to find JSON object in text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return None
    
    def _normalize_to_lists(self, data: Dict) -> Dict[str, List[str]]:
        """
        Normalize AI response to expected list format
        
        Args:
            data: Raw AI response dict
        
        Returns:
            Normalized dict with list values
        """
        result = {
            'order_ids': [],
            'prices': [],
            'dates': [],
            'totals': [],
            'quantities': [],
            'sellers': [],
            'tracking_numbers': [],
            'items': [],
        }
        
        # Order ID
        if data.get('order_id'):
            result['order_ids'].append(str(data['order_id']))
        
        # Date
        if data.get('order_date'):
            result['dates'].append(str(data['order_date']))
        
        # Total
        if data.get('total'):
            result['totals'].append(str(data['total']))
        
        # Seller
        if data.get('seller'):
            result['sellers'].append(str(data['seller']))
        
        # Tracking
        if data.get('tracking_number'):
            result['tracking_numbers'].append(str(data['tracking_number']))
        
        # Items
        items_data = data.get('items', [])
        if isinstance(items_data, list):
            for item in items_data:
                if isinstance(item, dict):
                    # Extract item name
                    if item.get('name'):
                        result['items'].append(str(item['name']))
                    
                    # Extract quantity
                    if item.get('quantity'):
                        result['quantities'].append(str(item['quantity']))
                    
                    # Extract price
                    if item.get('price'):
                        result['prices'].append(str(item['price']))
        
        # Other prices
        other_prices = data.get('other_prices', [])
        if isinstance(other_prices, list):
            result['prices'].extend([str(p) for p in other_prices if p])
        
        return result


class OllamaProvider(AIProvider, LoggerMixin):
    """Ollama local AI provider"""
    
    def __init__(self, config: ExtractorConfig):
        super().__init__(config)
        self.model = config.ollama_model
        self.base_url = "http://localhost:11434"
    
    def extract(self, image_path: str) -> Tuple[Optional[Dict], str]:
        """Extract data using Ollama"""
        base64_image = self._encode_image(image_path)
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": AI_EXTRACTION_PROMPT,
                                "images": [base64_image]
                            }
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistency
                        }
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                content = response.json()["message"]["content"]
                data = self._parse_json_response(content)
                
                if data:
                    normalized = self._normalize_to_lists(data)
                    return normalized, "Ollama Success"
                else:
                    return None, "Ollama JSON Parse Failed"
                
            except requests.exceptions.ConnectionError:
                return None, "Ollama Not Running (start with 'ollama serve')"
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Ollama timeout, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2 ** attempt)
                else:
                    return None, "Ollama Timeout"
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Ollama error: {e}, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2 ** attempt)
                else:
                    return None, f"Ollama Error: {str(e)[:50]}"
        
        return None, "Ollama Failed After Retries"


class OpenAIProvider(AIProvider, LoggerMixin):
    """OpenAI GPT-4 Vision provider"""
    
    def __init__(self, config: ExtractorConfig):
        super().__init__(config)
        self.model = config.openai_model
        
        try:
            from openai import OpenAI
            self.client = OpenAI()  # Uses OPENAI_API_KEY env var
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    def extract(self, image_path: str) -> Tuple[Optional[Dict], str]:
        """Extract data using OpenAI GPT-4 Vision"""
        base64_image = self._encode_image(image_path)
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": AI_EXTRACTION_PROMPT},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.1,
                )
                
                content = response.choices[0].message.content
                data = self._parse_json_response(content)
                
                if data:
                    normalized = self._normalize_to_lists(data)
                    return normalized, "OpenAI Success"
                else:
                    return None, "OpenAI JSON Parse Failed"
                
            except Exception as e:
                error_msg = str(e)
                if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                    return None, "OpenAI Auth Error (check OPENAI_API_KEY)"
                
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"OpenAI error: {e}, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2 ** attempt)
                else:
                    return None, f"OpenAI Error: {str(e)[:50]}"
        
        return None, "OpenAI Failed After Retries"


class ClaudeProvider(AIProvider, LoggerMixin):
    """Anthropic Claude Vision provider"""
    
    def __init__(self, config: ExtractorConfig):
        super().__init__(config)
        self.model = config.claude_model
        
        try:
            import anthropic
            self.client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
        except ImportError:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
    
    def extract(self, image_path: str) -> Tuple[Optional[Dict], str]:
        """Extract data using Claude Vision"""
        base64_image = self._encode_image(image_path)
        
        # Detect media type
        media_type = "image/jpeg"
        if image_path.lower().endswith('.png'):
            media_type = "image/png"
        elif image_path.lower().endswith('.webp'):
            media_type = "image/webp"
        
        for attempt in range(self.max_retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.1,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": AI_EXTRACTION_PROMPT
                            }
                        ],
                    }],
                )
                
                content = message.content[0].text
                data = self._parse_json_response(content)
                
                if data:
                    normalized = self._normalize_to_lists(data)
                    return normalized, "Claude Success"
                else:
                    return None, "Claude JSON Parse Failed"
                
            except Exception as e:
                error_msg = str(e)
                if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                    return None, "Claude Auth Error (check ANTHROPIC_API_KEY)"
                
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Claude error: {e}, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2 ** attempt)
                else:
                    return None, f"Claude Error: {str(e)[:50]}"
        
        return None, "Claude Failed After Retries"


class GeminiProvider(AIProvider, LoggerMixin):
    """Google Gemini Vision provider"""
    
    def __init__(self, config: ExtractorConfig):
        super().__init__(config)
        self.model = config.gemini_model
        
        try:
            import google.generativeai as genai
            import os
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("Google AI library not installed. Run: pip install google-generativeai")
    
    def extract(self, image_path: str) -> Tuple[Optional[Dict], str]:
        """Extract data using Gemini Vision"""
        import PIL.Image
        
        for attempt in range(self.max_retries):
            try:
                # Load image
                image = PIL.Image.open(image_path)
                
                # Generate content
                response = self.client.generate_content(
                    [AI_EXTRACTION_PROMPT, image],
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 1000,
                    }
                )
                
                content = response.text
                data = self._parse_json_response(content)
                
                if data:
                    normalized = self._normalize_to_lists(data)
                    return normalized, "Gemini Success"
                else:
                    return None, "Gemini JSON Parse Failed"
                
            except Exception as e:
                error_msg = str(e)
                if "api key" in error_msg.lower():
                    return None, "Gemini Auth Error (check GOOGLE_API_KEY)"
                
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Gemini error: {e}, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2 ** attempt)
                else:
                    return None, f"Gemini Error: {str(e)[:50]}"
        
        return None, "Gemini Failed After Retries"


def get_ai_provider(config: ExtractorConfig) -> AIProvider:
    """
    Factory function to get appropriate AI provider
    
    Args:
        config: Extractor configuration
    
    Returns:
        AIProvider instance
    """
    providers = {
        'ollama': OllamaProvider,
        'openai': OpenAIProvider,
        'claude': ClaudeProvider,
        'gemini': GeminiProvider,
    }
    
    provider_class = providers.get(config.ai_provider)
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {config.ai_provider}")
    
    return provider_class(config)
