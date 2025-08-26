import requests
import json
from config import Config

class LLMAnalyzer:
    def __init__(self):
        self.config = Config()
        self.provider = self.config.LLM_PROVIDER.lower()
    
    def analyze_message(self, message: str) -> dict:
        """
        Phân tích message bằng LLM
        Returns: {
            'is_spam': bool,
            'confidence': float,
            'reason': str,
            'classification': str
        }
        """
        try:
            if self.provider == 'openai':
                return self._analyze_with_openai(message)
            elif self.provider == 'groq':
                return self._analyze_with_groq(message)
            elif self.provider == 'openrouter':
                return self._analyze_with_openrouter(message)
            else:
                # Fallback: mock response for demo
                return self._mock_analysis(message)
        except Exception as e:
            print(f"LLM Analysis error: {e}")
            # Trả về kết quả an toàn khi có lỗi
            return {
                'is_spam': True,  # Conservative approach
                'confidence': 0.5,
                'reason': f'Analysis failed: {str(e)}',
                'classification': 'suspicious'
            }
    
    def _create_prompt(self, message: str) -> str:
        """Tạo prompt cho LLM"""
        return f"""
Analyze the following Vietnamese message for spam/scam detection:

Message: "{message}"

Please analyze and respond in JSON format:
{{
    "is_spam": true/false,
    "confidence": 0.0-1.0,
    "reason": "explanation in Vietnamese",
    "classification": "legitimate/suspicious/spam"
}}

Consider these factors:
- Urgent money requests
- Suspicious links or downloads
- Too-good-to-be-true offers
- Requests for personal information
- Grammar and spelling patterns
- Social engineering tactics

Response (JSON only):
"""
    
    def _analyze_with_openai(self, message: str) -> dict:
        """Phân tích bằng OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": self._create_prompt(message)}
            ],
            "max_tokens": 200,
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return self._parse_llm_response(content)
    
    def _analyze_with_groq(self, message: str) -> dict:
        """Phân tích bằng Groq API"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "user", "content": self._create_prompt(message)}
            ],
            "max_tokens": 200,
            "temperature": 0.3
        }
        
        print(f"🔄 Calling Groq API with model: {payload['model']}")
    
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(f"📡 Groq Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Groq Error Response: {response.text}")
                
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Groq Raw Response: {content[:200]}...")
            
            return self._parse_llm_response(content)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Groq Request Error: {e}")
            raise
        except Exception as e:
            print(f"❌ Groq Processing Error: {e}")
            raise
    
    def _analyze_with_openrouter(self, message: str) -> dict:
        """Phân tích bằng OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Spam Filter Demo"
        }
        
        payload = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": [
                {"role": "user", "content": self._create_prompt(message)}
            ],
            "max_tokens": 200,
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return self._parse_llm_response(content)
    
    def _mock_analysis(self, message: str) -> dict:
        """Mock analysis cải tiến cho demo"""
        message_lower = message.lower()
        
        # Từ khóa spam mạnh
        strong_spam_keywords = [
            'trúng giải', 'vay tiền', 'không cần thế chấp', 'miễn phí', 
            'click link', 'cảnh báo', 'tài khoản bị khóa', 'xác thực ngay',
            'làm giàu', 'lợi nhuận', 'triệu/tháng'
        ]
        
        # Từ khóa spam nhẹ
        mild_spam_keywords = [
            'chuyển khoản', 'mã otp', 'đầu tư', 'khuyến mãi',
            'ưu đãi', 'giảm giá', 'mua ngay', 'nhanh tay'
        ]
        
        # Từ khóa yêu cầu tiền
        money_request_keywords = [
            'cho tôi tiền', 'đưa tiền', 'vui lòng chuyển', 'cần tiền',
            'mượn tiền', 'giúp tiền'
        ]
        
        strong_count = sum(1 for keyword in strong_spam_keywords if keyword in message_lower)
        mild_count = sum(1 for keyword in mild_spam_keywords if keyword in message_lower)
        money_count = sum(1 for keyword in money_request_keywords if keyword in message_lower)
        
        # Phân loại cải tiến
        if strong_count >= 1:
            return {
                'is_spam': True,
                'confidence': 0.9,
                'reason': f'Phát hiện {strong_count} từ khóa spam mạnh',
                'classification': 'spam'
            }
        elif money_count >= 1:
            return {
                'is_spam': True,
                'confidence': 0.8,
                'reason': f'Phát hiện yêu cầu tiền: {money_count} từ khóa',
                'classification': 'spam'
            }
        elif mild_count >= 2:
            return {
                'is_spam': False,
                'confidence': 0.6,
                'reason': f'Phát hiện {mild_count} từ khóa spam nhẹ - cần xem xét',
                'classification': 'suspicious'
            }
        elif mild_count == 1:
            return {
                'is_spam': False,
                'confidence': 0.7,
                'reason': 'Có 1 từ khóa nghi vấn nhưng có thể là hợp lệ',
                'classification': 'suspicious'
            }
        else:
            return {
                'is_spam': False,
                'confidence': 0.9,
                'reason': 'Không phát hiện từ khóa spam',
                'classification': 'legitimate'
            }
    
    def _parse_llm_response(self, content: str) -> dict:
        """Parse JSON response từ LLM"""
        try:
            # Tìm JSON trong response
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = content[start:end]
                result = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['is_spam', 'confidence', 'reason', 'classification']
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing field: {field}")
                
                return result
            else:
                raise ValueError("No JSON found in response")
        
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw content: {content}")
            
            # Fallback response
            return {
                'is_spam': True,
                'confidence': 0.5,
                'reason': 'Không thể phân tích response từ LLM',
                'classification': 'suspicious'
            }