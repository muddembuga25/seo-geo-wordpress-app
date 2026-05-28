"""
Main Application - SEO-GEO WordPress Desktop App
GUI built with customtkinter for professional Windows experience.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import threading
import os
import json
import sys
import webbrowser
from datetime import datetime

import config_manager
import api_client
import wordpress_publisher
import svg_generator
import seo_analyzer


class ProgressFrame(ctk.CTkFrame):
    """Custom progress bar with status text."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(fill="x", padx=10, pady=5)
        self.progress.set(0)
        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(0, 5))
    
    def update_progress(self, value: float, status: str):
        """Update progress bar (0.0 to 1.0) and status text."""
        self.progress.set(value)
        self.status_label.configure(text=status)


class BlogPostEditor(ctk.CTkFrame):
    """Frame for composing/editing blog posts."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.title_label = ctk.CTkLabel(
            self, text="Blog Post Title", font=("", 12, "bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 2))
        
        self.title_entry = ctk.CTkEntry(self, width=800)
        self.title_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        self.content_label = ctk.CTkLabel(
            self, text="Content (Markdown)", font=("", 12, "bold")
        )
        self.content_label.pack(anchor="w", padx=10, pady=(10, 2))
        
        self.content_text = ctk.CTkTextbox(self, width=800, height=300)
        self.content_text.pack(fill="both", padx=10, pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.ai_generate_btn = ctk.CTkButton(
            btn_frame, text="Generate with AI",
            command=self._on_ai_generate
        )
        self.ai_generate_btn.pack(side="left", padx=(0, 10))
        
        self.analyze_btn = ctk.CTkButton(
            btn_frame, text="Analyze SEO",
            command=self._on_analyze
        )
        self.analyze_btn.pack(side="left", padx=(0, 10))
        
        self.generate_image_btn = ctk.CTkButton(
            btn_frame, text="Generate Featured Image",
            command=self._on_generate_image
        )
        self.generate_image_btn.pack(side="left")
    
    def get_title(self) -> str:
        return self.title_entry.get()
    
    def get_content(self) -> str:
        return self.content_text.get("1.0", "end-1c")
    
    def set_title(self, title: str):
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, title)
    
    def set_content(self, content: str):
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", content)
    
    def _on_ai_generate(self):
        if hasattr(self.master.master, "on_ai_generate"):
            self.master.master.on_ai_generate()
    
    def _on_analyze(self):
        if hasattr(self.master.master, "on_analyze"):
            self.master.master.on_analyze()
    
    def _on_generate_image(self):
        if hasattr(self.master.master, "on_generate_image"):
            self.master.master.on_generate_image()
    
    def _get_post_url(self):
        """Open blog post in browser if published."""
        if hasattr(self.master.master, "_last_post_url") and self.master.master._last_post_url:
            webbrowser.open(self.master.master._last_post_url)


class WordPressSettingsFrame(ctk.CTkScrollableFrame):
    """Frame for WordPress site configuration."""
    
    def __init__(self, parent, config: config_manager.ConfigManager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.config = config
        self.wp = wordpress_publisher.WordPressPublisher()
        self.selected_site_var = ctk.StringVar(value="")
        self.site_id_var = ctk.StringVar(value="")
        
        self._build_ui()
    
    def _build_ui(self):
        label = ctk.CTkLabel(
            self, text="WordPress Site Settings", font=("", 14, "bold")
        )
        label.pack(anchor="w", padx=10, pady=10)
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame, text="Site URL:").pack(anchor="w")
        self.url_entry = ctk.CTkEntry(frame, width=300)
        self.url_entry.pack(fill="x", pady=(2, 10))
        
        ctk.CTkLabel(frame, text="Username:").pack(anchor="w")
        self.username_entry = ctk.CTkEntry(frame, width=300)
        self.username_entry.pack(fill="x", pady=(2, 10))
        
        ctk.CTkLabel(frame, text="Password:").pack(anchor="w")
        self.password_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.password_entry.pack(fill="x", pady=(2, 10))
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        save_btn = ctk.CTkButton(btn_frame, text="Save Credentials", command=self._save_credentials)
        save_btn.pack(side="left", padx=(0, 10))
        
        test_btn = ctk.CTkButton(btn_frame, text="Test Connection", command=self._test_connection)
        test_btn.pack(side="left")
        
        ctk.CTkLabel(self, text="Saved Sites:", font=("", 12, "bold")).pack(anchor="w", padx=10, pady=(15, 5))
        self.sites_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sites_frame.pack(fill="x", padx=10)
        self._load_sites()
    
    def _load_sites(self):
        for widget in self.sites_frame.winfo_children():
            widget.destroy()
        sites = self.config.get_wordpress_sites()
        if not sites:
            label = ctk.CTkLabel(self.sites_frame, text="No sites saved")
            label.pack(anchor="w")
        else:
            for site in sites:
                site_frame = ctk.CTkFrame(self.sites_frame)
                site_frame.pack(fill="x", pady=2)
                url = site.get("url", "")
                username = site.get("username", "")
                main_text = f"{url} ({username})"
                ctk.CTkLabel(site_frame, text=main_text, anchor="w").pack(side="left", padx=5, pady=5)
                btn = ctk.CTkButton(site_frame, text="Load", width=60,
                    command=lambda s=site: self._load_site(s))
                btn.pack(side="right", padx=5, pady=5)
    
    def _load_site(self, site):
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, site.get("url", ""))
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, site.get("username", ""))
        self.password_entry.delete(0, "end")
    
    def _save_credentials(self):
        url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not url or not username:
            messagebox.showerror("Error", "Please provide URL and username")
            return
        self.config.add_wordpress_site(url, username, password)
        self._load_sites()
        messagebox.showinfo("Success", "Site credentials saved")
    
    def _test_connection(self):
        url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not all([url, username, password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        self.wp.set_credentials(url, username, password)
        try:
            result = self.wp.test_connection()
            if result["success"]:
                messagebox.showinfo("Success", "Connected to WordPress!")
            else:
                messagebox.showerror("Error", result.get("error", "Connection failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def get_wp_publisher(self) -> wordpress_publisher.WordPressPublisher:
        self.wp.set_credentials(
            self.url_entry.get().strip(),
            self.username_entry.get().strip(),
            self.password_entry.get()
        )
        return self.wp
    
    def _password_entry(self):
        self.wp.set_credentials(
            self.url_entry.get().strip(),
            self.username_entry.get().strip(),
            self.password_entry.get()
        )
        return self.wp


class APISettingsFrame(ctk.CTkScrollableFrame):
    """Frame for API key configuration."""
    
    def __init__(self, parent, config: config_manager.ConfigManager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.config = config
        self.api = api_client.APIClient()
        self.build_ui()
    
    def build_ui(self):
        label = ctk.CTkLabel(self, text="API Settings", font=("", 14, "bold"))
        label.pack(anchor="w", padx=10, pady=10)
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame, text="OpenRouter API Key:").pack(anchor="w")
        self.openrouter_key = ctk.CTkEntry(frame, width=300, show="*")
        self.openrouter_key.pack(fill="x", pady=(2, 10))
        stored_key = self.config.get("openrouter_api_key", "")
        if stored_key:
            self.openrouter_key.insert(0, stored_key if not stored_key.startswith("encrypted:") else "********")
        
        ctk.CTkLabel(frame, text="OpenCode API Key:").pack(anchor="w")
        self.opencode_key = ctk.CTkEntry(frame, width=300, show="*")
        self.opencode_key.pack(fill="x", pady=(2, 10))
        stored_key2 = self.config.get("opencode_api_key", "")
        if stored_key2:
            self.opencode_key.insert(0, stored_key2 if not stored_key2.startswith("encrypted:") else "********")
        
        save_btn = ctk.CTkButton(frame, text="Save API Keys", command=self._save_api_keys)
        save_btn.pack(fill="x", pady=10)
    
    def _save_api_keys(self):
        openrouter = self.openrouter_key.get().strip()
        opencode = self.opencode_key.get().strip()
        if openrouter:
            self.config.set("openrouter_api_key", openrouter)
        if opencode:
            self.config.set("opencode_api_key", opencode)
        self.config.save()
        messagebox.showinfo("Success", "API keys saved securely")
    
    def get_api_client(self) -> api_client.APIClient:
        openrouter = self.openrouter_key.get().strip()
        opencode = self.opencode_key.get().strip()
        self.api.set_api_key(openrouter if openrouter else opencode)
        return self.api


class SEOAnalysisFrame(ctk.CTkFrame):
    """Frame for displaying SEO analysis results."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.build_ui()
    
    def build_ui(self):
        label = ctk.CTkLabel(self, text="SEO Analysis Results", font=("", 14, "bold"))
        label.pack(anchor="w", padx=10, pady=10)
        
        self.score_label = ctk.CTkLabel(self, text="Score: --", font=("", 18, "bold"))
        self.score_label.pack(pady=10)
        
        self.results_text = ctk.CTkTextbox(self, width=600, height=300)
        self.results_text.pack(fill="both", padx=10, pady=(0, 10))
    
    def show_results(self, results: dict, grade: str):
        score = results.get("overall_score", 0)
        self.score_label.configure(text=f"Overall SEO Score: {score}/100 (Grade: {grade})")
        self.results_text.delete("1.0", "end")
        
        output = []
        output.append("=== PASSED CHECKS ===")
        for check in results.get("passed_checks", []):
            output.append(f"  [OK] {check['section']}: {check['check']}")
        
        output.append("\n=== RECOMMENDATIONS ===")
        for rec in results.get("recommendations", []):
            severity = rec.get("severity", "").upper()
            output.append(f"  [{severity}] {rec['section']}: {rec['issue']}")
        
        output.append("\n=== KEYWORD ANALYSIS ===")
        kw = results.get("keyword_analysis", {})
        output.append(f"  Keyword density: {kw.get('density', 0)}%")
        output.append(f"  Exact matches: {kw.get('exact_count', 0)}")
        
        self.results_text.insert("1.0", "\n".join(output))
    

class PublishFrame(ctk.CTkFrame):
    """Frame for publishing to WordPress."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._last_post_url = None
        self.build_ui()
    
    def build_ui(self):
        label = ctk.CTkLabel(self, text="Publish to WordPress", font=("", 14, "bold"))
        label.pack(anchor="w", padx=10, pady=10)
        
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(form, text="Slug:").pack(anchor="w")
        self.slug_entry = ctk.CTkEntry(form, width=300)
        self.slug_entry.pack(fill="x", pady=(2, 10))
        
        self.status_var = ctk.StringVar(value="Draft")
        status_frame = ctk.CTkFrame(form, fg_color="transparent")
        status_frame.pack(anchor="w")
        ctk.CTkRadioButton(status_frame, text="Draft", variable=self.status_var, value="draft").pack(side="left")
        ctk.CTkRadioButton(status_frame, text="Published", variable=self.status_var, value="publish").pack(side="left", padx=10)
        
        self.progress = ProgressFrame(form)
        self.progress.pack(fill="x", pady=(15, 10))
        
        self.publish_btn = ctk.CTkButton(
            form, text="Publish to WordPress", fg_color="#007cba",
            command=self._on_publish
        )
        self.publish_btn.pack(fill="x", pady=5)
        
        self.open_btn = ctk.CTkButton(
            form, text="Open Post in Browser", command=self._open_post
        )
        self.open_btn.pack(fill="x", pady=5)
    
    def _on_publish(self):
        self.publish_btn.configure(state="disabled")
        self.publish_btn.configure(text="Publishing...")
        self._last_post_url = None
    
    def _open_post(self):
        if self._last_post_url:
            webbrowser.open(self._last_post_url)
        else:
            messagebox.showinfo("Info", "No post URL available yet")


class SEOGeoApp(ctk.CTk):
    """Main Application Window."""
    
    def __init__(self):
        super().__init__()
        self.title("SEO-GEO WordPress App")
        self.geometry("950x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.config = config_manager.ConfigManager()
        self._last_post_url = None
        self._build_ui()
    
    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_editor = self.tabview.add("Editor")
        self.tab_wp = self.tabview.add("WordPress Settings")
        self.tab_api = self.tabview.add("API Settings")
        self.tab_seo = self.tabview.add("SEO Analysis")
        self.tab_publish = self.tabview.add("Publish")
        
        self.editor = BlogPostEditor(self.tab_editor)
        self.editor.pack(fill="both", expand=True)
        
        self.wp_settings = WordPressSettingsFrame(self.tab_wp, self.config)
        self.wp_settings.pack(fill="both", expand=True)
        
        self.api_settings = APISettingsFrame(self.tab_api, self.config)
        self.api_settings.pack(fill="both", expand=True)
        
        self.seo_frame = SEOAnalysisFrame(self.tab_seo)
        self.seo_frame.pack(fill="both", expand=True)
        
        self.publish_frame = PublishFrame(self.tab_publish)
        self.publish_frame.pack(fill="both", expand=True)
        
        self.publish_frame._on_publish = self.on_publish
        self.publish_frame.publish_btn.configure(command=self.on_publish)
    
    def on_ai_generate(self):
        """Generate blog post with AI."""
        prompt = self.editor.get_title()
        if not prompt or len(prompt) < 5:
            messagebox.showwarning("Warning", "Please enter a title/topic for AI generation")
            return
        
        self.editor.content_text.delete("1.0", "end")
        self.editor.content_text.insert("1.0", "Generating with AI... (this may take a moment)")
        
        def generate():
            try:
                api = self.api_settings.get_api_client()
                article = api.generate_article(prompt)
                if article and article.get("content"):
                    self.editor.set_title(article.get("title", prompt))
                    self.editor.set_content(article.get("content", ""))
                else:
                    self.editor.set_content("API returned no content. Check your API key.")
            except Exception as e:
                self.editor.set_content(f"Error: {str(e)}")
        
        thread = threading.Thread(target=generate)
        thread.start()
    
    def on_analyze(self):
        """Analyze current content for SEO."""
        title = self.editor.get_title()
        content = self.editor.get_content()
        if not content.strip():
            messagebox.showwarning("Warning", "Please enter content to analyze")
            return
        
        analyzer = seo_analyzer.SEOAnalyzer()
        results = analyzer.analyze(title, content, keyword=title)
        grade = analyzer.get_score_grade(results["overall_score"])
        self.seo_frame.show_results(results, grade)
        messagebox.showinfo("SEO Analysis", f"Overall Score: {results['overall_score']}/100 (Grade: {grade})")
    
    def on_generate_image(self):
        """Generate SVG featured image."""
        title = self.editor.get_title()
        if not title.strip():
            messagebox.showwarning("Warning", "Please enter a title first")
            return
        
        svg_gen = svg_generator.SVGImageGenerator()
        try:
            filename = "featured_image.svg"
            success = svg_gen.save_svg(filename, title)
            if success:
                messagebox.showinfo("Success", f"Featured image saved as {filename}")
                webbrowser.open("file:///" + os.path.abspath(filename))
            else:
                messagebox.showerror("Error", "Failed to generate image")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def on_publish(self):
        """Publish current post to WordPress."""
        title = self.editor.get_title()
        content = self.editor.get_content()
        
        if not title.strip() or not content.strip():
            messagebox.showwarning("Warning", "Please provide title and content")
            return
        
        self.publish_frame.progress.update_progress(0.1, "Connecting to WordPress...")
        self.publish_frame.publish_btn.configure(state="disabled")
        self.publish_frame.publish_btn.configure(text="Publishing...")
        
        def publish_thread():
            try:
                wp = self.wp_settings.get_wp_publisher()
                title_slug = title.lower().replace(" ", "-")[:60]
                
                self.publish_frame.progress.update_progress(0.3, "Uploading featured image...")
                svg_gen = svg_generator.SVGImageGenerator()
                svg_content = svg_gen.generate_featured_image(title)
                
                self.publish_frame.progress.update_progress(0.5, "Creating post...")
                result = wp.create_post(
                    title=title,
                    content=content,
                    status=self.publish_frame.status_var.get(),
                    slug=title_slug,
                )
                
                if result and result.get("success"):
                    post_url = result.get("url", "")
                    self._last_post_url = post_url
                    self.publish_frame.progress.update_progress(1.0, "Published successfully!")
                    self.publish_frame.update()
                    def show_success():
                        messagebox.showinfo("Success", f"Post published!\n\n{post_url}")
                        self.publish_frame.open_btn.configure(state="normal")
                        self.publish_frame.publish_btn.configure(state="normal")
                        self.publish_frame.publish_btn.configure(text="Publish to WordPress")
                        if post_url:
                            webbrowser.open(post_url)
                    self.after(0, show_success)
                else:
                    error = result.get("error", "Unknown error") if result else "Publish failed"
                    self.publish_frame.progress.update_progress(0, f"Error: {error}")
                    def show_error():
                        messagebox.showerror("Error", error)
                        self.publish_frame.publish_btn.configure(state="normal")
                        self.publish_frame.publish_btn.configure(text="Publish to WordPress")
                    self.after(0, show_error)
            except Exception as e:
                def show_exception():
                    messagebox.showerror("Error", str(e))
                    self.publish_frame.publish_btn.configure(state="normal")
                    self.publish_frame.publish_btn.configure(text="Publish to WordPress")
                self.after(0, show_exception)
        
        thread = threading.Thread(target=publish_thread)
        thread.start()


def main():
    app = SEOGeoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
