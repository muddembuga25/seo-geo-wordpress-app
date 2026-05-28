"""
wordpress_publisher.py - WordPress REST API Integration
Handles publishing, updating, and managing posts on WordPress sites.
"""
import requests
import json
from typing import Dict, Optional, List, Any
from urllib.parse import urljoin, urlparse

class WordPressPublisher:
    """WordPress REST API client for publishing blog posts."""
    
    def __init__(self, site_url: str, username: str, password: str):
        self.base_url = self._normalize_url(site_url)
        self.api_url = urljoin(self.base_url, "/wp-json/wp/v2/")
        self.auth = (username, password)
        self._site_info = None
        
    def _normalize_url(self, url: str) -> str:
        """Normalize URL, removing trailing slash and /wp-admin."""
        url = url.strip().rstrip('/')
        parsed = urlparse(url)
        if '/wp-admin' in parsed.path:
            url = f"{parsed.scheme}://{parsed.netloc}"
        return url
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the WordPress connection and return site info."""
        try:
            # Try to get site info
            response = requests.get(
                urljoin(self.base_url, "/wp-json/"),
                auth=self.auth,
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                self._site_info = {
                    "name": data.get("name", "Unknown"),
                    "description": data.get("description", ""),
                    "url": self.base_url,
                    "connected": True
                }
                return self._site_info
            return {"connected": False, "error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def create_post(self, title: str, content: str, status: str = "draft",
                    categories: List[int] = None, tags: List[str] = None,
                    featured_image_id: int = None,
                    meta_description: str = None) -> Dict[str, Any]:
        """Create a new blog post on WordPress."""
        
        post_data = {
            "title": title,
            "content": content,
            "status": status,
        }
        
        if categories:
            post_data["categories"] = categories
            
        if meta_description:
            # Add meta description via Yoast SEO or similar
            post_data["yoast_head"] = f'<meta name="description" content="{meta_description}" />'
            post_data["yoast_head_json"] = {
                "meta_description": meta_description
            }
        
        try:
            response = requests.post(
                urljoin(self.api_url, "posts"),
                json=post_data,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "post_id": data.get("id"),
                    "post_url": data.get("link"),
                    "title": data.get("title", {}).get("rendered", title),
                    "status": data.get("status"),
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text[:200]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_post(self, post_id: int, title: str = None, content: str = None,
                    status: str = None, categories: List[int] = None) -> Dict[str, Any]:
        """Update an existing WordPress post."""
        update_data = {}
        if title:
            update_data["title"] = title
        if content:
            update_data["content"] = content
        if status:
            update_data["status"] = status
        if categories:
            update_data["categories"] = categories
            
        try:
            response = requests.post(
                urljoin(self.api_url, f"posts/{post_id}"),
                json=update_data,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "post_id": data.get("id"),
                    "post_url": data.get("link"),
                    "data": data
                }
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "message": response.text[:200]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_post(self, post_id: int) -> Dict[str, Any]:
        """Get a specific WordPress post."""
        try:
            response = requests.get(
                urljoin(self.api_url, f"posts/{post_id}"),
                auth=self.auth,
                timeout=15
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def publish_post(self, post_id: int) -> Dict[str, Any]:
        """Change a draft post to published."""
        return self.update_post(post_id, status="publish")
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a WordPress post."""
        try:
            response = requests.delete(
                urljoin(self.api_url, f"posts/{post_id}"),
                auth=self.auth,
                timeout=15
            )
            return response.status_code in [200, 204]
        except Exception:
            return False
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all WordPress categories."""
        try:
            response = requests.get(
                urljoin(self.api_url, "categories"),
                auth=self.auth,
                timeout=15
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
    
    def create_category(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new category on WordPress."""
        try:
            response = requests.post(
                urljoin(self.api_url, "categories"),
                json={"name": name, "description": description},
                auth=self.auth,
                timeout=15
            )
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all WordPress tags."""
        try:
            response = requests.get(
                urljoin(self.api_url, "tags"),
                auth=self.auth,
                timeout=15
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
    
    def create_tag(self, name: str) -> Dict[str, Any]:
        """Create a new tag on WordPress."""
        try:
            response = requests.post(
                urljoin(self.api_url, "tags"),
                json={"name": name},
                auth=self.auth,
                timeout=15
            )
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_media(self, image_url: str, alt_text: str = "") -> Dict[str, Any]:
        """Upload media from URL to WordPress."""
        try:
            # Download image
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code != 200:
                return {"success": False, "error": "Failed to download image"}
            
            # Determine filename
            filename = image_url.split("/")[-1].split("?")[0]
            if not filename:
                filename = "image.jpg"
            
            # Upload to WordPress
            response = requests.post(
                urljoin(self.api_url, "media"),
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
                auth=self.auth,
                data=img_response.content,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "media_id": data.get("id"),
                    "media_url": data.get("source_url"),
                    "data": data
                }
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_featured_image(self, post_id: int, media_id: int) -> Dict[str, Any]:
        """Set featured image for a post."""
        return self.update_post(post_id, content=None)  # Handled in update via featured_media
