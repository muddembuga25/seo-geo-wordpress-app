"""
config_manager.py - Encrypted Settings Storage
Stores API keys, WordPress credentials, and app settings securely.
"""
import json
import os
import sys
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    HAS_CRYTPO = True
except ImportError:
    HAS_CRYTPO = False

def get_app_dir():
    """Get the path where the script is running (works from .exe too)."""
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent.resolve()
    else:
        app_dir = Path(__file__).parent.resolve()
    return app_dir

class ConfigManager:
    CONFIG_FILENAME = "app_config.json"
    
    DEFAULT_SETTINGS = {
        "openrouter_api_key": "",
        "opencode_api_key": "",
        "wordpress_sites": [],
        "app_theme": "light",
        "auto_save": True
    }
    
    def __init__(self):
        self.config_path = get_app_dir() / self.CONFIG_FILENAME
        self.settings = self.DEFAULT_SETTINGS.copy()
        if self.config_path.exists():
            self.load()
        self._setup_encryption()
    
    def _setup_encryption(self):
        """Setup Fernet encryption for secure storage."""
        self.cipher = None
        if HAS_CRYTPO:
            key = self._get_or_create_key()
            self.cipher = Fernet(key)
    
    def _get_or_create_key(self):
        """Get encryption key from environment or create new one."""
        key_str = os.environ.get("APP_ENCRYPTION_KEY")
        if not key_str:
            key_path = get_app_dir() / ".app_key"
            if key_path.exists():
                key_str = key_path.read_text().strip()
            else:
                key = Fernet.generate_key()
                key_str = key.decode()
                try:
                    key_path.write_text(key_str)
                except Exception:
                    pass
        return key_str.encode()
    
    def _encrypt(self, text):
        if self.cipher:
            return self.cipher.encrypt(text.encode()).decode()
        return text
    
    def _decrypt(self, text):
        if self.cipher and text and len(text) > 50:
            try:
                return self.cipher.decrypt(text.encode()).decode()
        except Exception:
            return text
        return text
    
    def load(self):
        """Load settings from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                loaded = json.load(f)
            self.settings = {**self.DEFAULT_SETTINGS, **loaded}
        except Exception:
            self.settings = self.DEFAULT_SETTINGS.copy()
    
    def save(self):
        """Save settings to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save()
    
    def set_openrouter_key(self, key):
        encrypted = self._encrypt(key)
        self.settings["openrouter_api_key"] = encrypted
        self.save()
    
    def set_opencode_key(self, key):
        encrypted = self._encrypt(key)
        self.settings["opencode_api_key"] = encrypted
        self.save()
    
    def get_openrouter_key(self):
        return self._decrypt(self.settings.get("openrouter_api_key", ""))
    
    def get_opencode_key(self):
        return self._decrypt(self.settings.get("opencode_api_key", ""))
    
    def add_wordpress_site(self, url, username, nickname, password):
        sites = self.settings.get("wordpress_sites", [])
        encrypted_pass = self._encrypt(password)
        sites.append({
            "url": url,
            "username": username,
            "nickname": nickname,
            "password": encrypted_pass
        })
        self.settings["wordpress_sites"] = sites
        self.save()
    
    def get_wp_password(self, index):
        password_key = f"wp_password_{index}"
        return self._decrypt(self.settings.get(password_key, ""))
    
    def reset_all(self):
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()

_config_instance = None

def get_config():
    """Get the singleton ConfigManager instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
