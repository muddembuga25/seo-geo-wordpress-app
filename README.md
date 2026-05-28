# SEO-GEO WordPress App

Professional SEO & GEO WordPress Desktop Application with OpenRouter & OpenCode AI integration.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **AI-Powered Content Generation** - Generate SEO-optimized blog posts using OpenRouter or OpenCode AI
- **WordPress Integration** - Publish directly to WordPress sites via REST API
- **SEO Analysis** - Built-in SEO checker with scoring and recommendations
- **Featured Image Generation** - Auto-generate SVG featured images for blog posts
- **Professional Windows Installer** - High-budget style installation experience with:
  - Animated progress bar
  - Desktop shortcut creation
  - Start Menu entry
  - Built-in uninstaller
- **Secure API Key Storage** - Encrypted credential management
- **Dark Mode GUI** - Modern, professional dark-themed interface

## Prerequisites

- Windows 10 or later
- Python 3.9+
- Git
- WordPress site with REST API access
- OpenRouter API key (optional, for AI features)

## Installation

### Quick Install (Recommended)

1. Download `install.ps1` from this repository
2. Right-click `install.ps1` and select **Run with PowerShell**
3. Follow the on-screen prompts

The installer will:
- Check all prerequisites
- Download the application
- Install Python dependencies
- Create a desktop shortcut
- Create a Start Menu entry
- Install an uninstaller

### Manual Install

```bash
# Clone the repository
git clone https://github.com/muddembuga25/seo-geo-wordpress-app
cd seo-geo-wordpress-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

### 1. API Settings
- Open the app and navigate to the **API Settings** tab
- Enter your **OpenRouter API Key** or **OpenCode API Key**
- Click **Save API Keys**

### 2. WordPress Settings
- Go to the **WordPress Settings** tab
- Enter your WordPress site URL, username, and password
- Click **Save Credentials**
- Click **Test Connection** to verify

### 3. Create a Blog Post
- Go to the **Editor** tab
- Enter a title or click **Generate with AI** to auto-generate content
- Click **Analyze SEO** to check your content
- Click **Generate Featured Image** to create a visual

### 4. Publish
- Go to the **Publish** tab
- Select **Draft** or **Published** status
- Click **Publish to WordPress**
- Watch the progress bar and status updates
- Click **Open Post in Browser** to view the published post

## Project Structure

```
seo-geo-wordpress-app/
├── main.py                    # Main GUI application
├── config_manager.py          # Encrypted settings storage
├── api_client.py              # OpenRouter/OpenCode API client
├── wordpress_publisher.py     # WordPress REST API publisher
├── svg_generator.py           # Featured image generator
├── seo_analyzer.py            # SEO analysis engine
├── install.ps1                # Windows installer script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
└── .gitignore                 # Git ignore rules
```

## Security

- API keys are encrypted before storage using the `cryptography` library
- WordPress passwords are stored securely via the `keyring` module
- No credentials are sent to third-party services except the target WordPress site and AI provider

## Build Executable

To create a standalone Windows executable:

```bash
pip install PyInstaller
pyinstaller --onefile --windowed --name "SEO-Geo-WordPress" main.py
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

muddembuga25 - [GitHub Profile](https://github.com/muddembuga25)

---

*Professional SEO + GEO WordPress Desktop App with OpenRouter & OpenCode AI integration*
