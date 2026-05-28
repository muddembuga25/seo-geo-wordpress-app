"""
api_client.py - AI Model API Client
Handles communication with OpenRouter and OpenCode APIs for content generation.
"""
import requests
import json
from typing import Dict, List, Optional, Any

class APIClient:
    """Unified API client for OpenRouter and OpenCode."""
    
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_SITES = [
        "https://github.com/muddembuga25/seo-geo-wordpress-app"
    ]
    
    def __init__(self, openrouter_key: str, opencode_key: str = ""):
        self.openrouter_key = openrouter_key
        self.opencode_key = opencode_key
        
    def _get_openrouter_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://github.com/muddembuga25/seo-geo-wordpress-app",
            "X-Title": "SEO-GEO WordPress App",
            "Content-Type": "application/json"
        }
    
    def generate_article(self, topic: str, keywords: List[str], 
                         tone: str = "professional", length: str = "long") -> str:
        """Generate a full SEO-optimized article using OpenRouter."""
        
        keyword_str = ", ".join(keywords)
        prompt = f"""Write a comprehensive, SEO-optimized blog article about: {topic}

Keywords to include: {keyword_str}

Tone: {tone}
Length: {length}

Requirements:
1. Write a compelling title (H1)
2. Include an engaging introduction
3. Use proper heading structure (H2, H3)
4. Write in HTML format with proper tags
5. Include internal linking suggestions
6. Add a FAQ section at the end
7. Make it at least 1500 words
8. Include meta description suggestion

Output ONLY the HTML content (no markdown code blocks)."""

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert SEO content writer and WordPress blogger. Always output clean HTML."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.OPENROUTER_URL,
                headers=self._get_openrouter_headers(),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            # Clean up markdown code blocks if present
            content = content.replace("```html", "").replace("```", "").strip()
            return content
        except Exception as e:
            return f"Error generating article: {str(e)}"
    
    def generate_tags(self, topic: str, keywords: List[str]) -> List[str]:
        """Generate additional relevant tags for SEO."""
        prompt = f"""Generate 10 comma-separated SEO tags for a blog post about: {topic}
Keywords: {", ".join(keywords)}
Output ONLY the tags separated by commas, no other text."""

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.OPENROUTER_URL,
                headers=self._get_openrouter_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            tags_str = data["choices"][0]["message"]["content"].strip()
            return [t.strip() for t in tags_str.split(",") if t.strip()]
        except Exception:
            return keywords[:5]
    
    def generate_meta_description(self, title: str, topic: str) -> str:
        """Generate an SEO meta description."""
        prompt = f"""Write an SEO meta description for: {title}
Topic: {topic}
Keep it under 160 characters. Output ONLY the description."""

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.OPENROUTER_URL,
                headers=self._get_openrouter_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return f"Learn about {topic} in this comprehensive guide."
    
    def improve_seo(self, content: str, keywords: List[str]) -> str:
        """Analyze and improve SEO of existing content."""
        prompt = f"""Review and improve this HTML content for SEO with keywords: {", ".join(keywords)}

Content:
{content[:3000]}

Return the improved HTML content. Focus on:
1. Better heading structure
2. Keyword placement in first paragraph
3. Adding alt text suggestions
4. Internal link opportunities

Output ONLY the improved HTML."""

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 3500,
            "temperature": 0.5
        }
        
        try:
            response = requests.post(
                self.OPENROUTER_URL,
                headers=self._get_openrouter_headers(),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            improved = data["choices"][0]["message"]["content"]
            improved = improved.replace("```html", "").replace("```", "").strip()
            return improved
        except Exception as e:
            return f"Error improving SEO: {str(e)}"
    
    def generate_article_outline(self, topic: str, keywords: List[str]) -> List[Dict[str, str]]:
        """Generate a structured article outline."""
        prompt = f"""Create an article outline for: {topic}
Keywords: {", ".join(keywords)}

Output a JSON array of sections with this format:
[{
    "heading": "H2 heading text",
    "subheadings": ["H3 subheading 1", "H3 subheading 2"],
    "key_points": "Brief description of what to cover"
}]

Output ONLY JSON."""

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.OPENROUTER_URL,
                headers=self._get_openrouter_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            # Try to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except Exception:
            return [{"heading": topic, "subheadings": [], "key_points": ""}]
