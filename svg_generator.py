"""
svg_generator.py - SVG Featured Image Generator
Creates SEO-friendly featured images for blog posts.
"""
import random
from typing import Tuple

class SVGGenerator:
    """Generate SVG featured images for blog posts."""
    
    COLORS = {
        "blue": ["#1e3a8a", "#3b82f6", "#60a5fa", "#93c5fd"],
        "green": ["#14532d", "#22c55e", "#4ade80", "#86efac"],
        "purple": ["#4c1d95", "#a855f7", "#c084fc", "#e9d5ff"],
        "orange": ["#7c2d12", "#f97316", "#fb923c", "#fed7aa"],
        "teal": ["#134e4a", "#14b8a6", "#2dd4bf", "#99f6e4"],
        "red": ["#7f1d1d", "#ef4444", "#f87171", "#fca5a5"],
        "pink": ["#831843", "#ec4899", "#f472b6", "#fbcfe8"]
    }
    
    def __init__(self, width: int = 1200, height: int = 630):
        self.width = width
        self.height = height
        
    def generate_featured_image(self, title: str, subtitle: str = "", 
                                color_theme: str = "blue") -> str:
        """Generate a complete SVG featured image."""
        colors = self.COLORS.get(color_theme, self.COLORS["blue"])
        
        # Get text abbreviation for background pattern
        initials = self._get_initials(title)
        
        bg_svg = self._generate_background(colors, initials)
        text_svg = self._generate_text_overlay(title, subtitle, colors)
        
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">
{bg_svg}
{text_svg}
</svg>"""
    
    def _generate_background(self, colors: list, initials: str) -> str:
        """Generate gradient background with pattern."""
        return f"""  <!-- Background gradient -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors[0]}"/>
      <stop offset="50%" style="stop-color:{colors[1]}"/>
      <stop offset="100%" style="stop-color:{colors[2]}"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="dotPattern" width="60" height="60" patternUnits="userSpaceOnUse">
      <circle cx="30" cy="30" r="3" fill="{colors[3]}" opacity="0.3"/>
    </pattern>
  </defs>
  
  <!-- Background -->
  <rect width="{self.width}" height="{self.height}" fill="url(#bgGradient)"/>
  
  <!-- Dot pattern overlay -->
  <rect width="{self.width}" height="{self.height}" fill="url(#dotPattern)"/>
  
  <!-- Decorative circles -->
  <circle cx="{self.width * 0.1}" cy="{self.height * 0.1}" r="150" fill="{colors[3]}" opacity="0.15"/>
  <circle cx="{self.width * 0.9}" cy="{self.height * 0.9}" r="200" fill="{colors[3]}" opacity="0.15"/>
  <circle cx="{self.width * 0.8}" cy="{self.height * 0.2}" r="80" fill="{colors[3]}" opacity="0.2"/>
  
  <!-- Initials watermark -->
  <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" 
        font-family="Arial Black, sans-serif" font-size="400" 
        fill="{colors[3]}" opacity="0.08">{initials}</text>"""
    
    def _generate_text_overlay(self, title: str, subtitle: str, colors: list) -> str:
        """Generate text overlay on the featured image."""
        # Shorten title if too long
        display_title = self._truncate(title, 45)
        display_subtitle = self._truncate(subtitle, 60) if subtitle else ""
        
        svg = f"""
  
  <!-- Text background box -->
  <rect x="5%" y="40%" width="90%" height="25%" rx="20" 
        fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
  
  <!-- Main title -->
  <text x="50%" y="55%" text-anchor="middle" 
        font-family="Arial Black, sans-serif" font-size="52" font-weight="bold" 
        fill="white" filter="url(#glow)">{self._escape_xml(display_title)}</text>"""
        
        if display_subtitle:
            svg += f"""
  
  <!-- Subtitle -->
  <text x="50%" y="63%" text-anchor="middle" 
        font-family="Arial, sans-serif" font-size="28" 
        fill="rgba(255,255,255,0.9)">{self._escape_xml(display_subtitle)}</text>"""
        
        svg += """
  
  <!-- Brand/watermark at bottom -->
  <text x="95%" y="95%" text-anchor="end" 
        font-family="Arial, sans-serif" font-size="18" 
        fill="rgba(255,255,255,0.6)">SEOGEO</text>
</svg>"""
        
        return svg
    
    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text to max length with ellipsis."""
        if len(text) <= max_len:
            return text
        return text[:max_len-3].rsplit(" ", 1)[0] + "..."
    
    def _get_initials(self, title: str) -> str:
        """Get initials from title for background pattern."""
        words = title.split()
        if len(words) >= 2:
            return (words[0][0] + words[1][0]).upper()
        return title[:2].upper() if len(title) >= 2 else title.upper()
    
    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&apos;"))
    
    def save_svg(self, filename: str, title: str, subtitle: str = "",
                 color_theme: str = "blue") -> bool:
        """Generate SVG and save to file."""
        try:
            svg_content = self.generate_featured_image(title, subtitle, color_theme)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return True
        except Exception:
            return False
