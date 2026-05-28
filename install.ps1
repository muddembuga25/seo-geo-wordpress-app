# SEO-GEO WordPress App Installer for Windows
# Professional Installation Script with Progress Bar & Desktop Shortcut
# Run as Administrator: Right-click > Run with PowerShell

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\SEOGeoWordPressApp",
    [string]$RepoUrl = "https://github.com/muddembuga25/seo-geo-wordpress-app"
)

# Colors
$ColorPrimary = "`e[36m"     # Cyan
$ColorSuccess = "`e[32m"    # Green
$ColorError = "`e[31m"      # Red
$ColorWarning = "`e[33m"    # Yellow
$ColorReset = "`e[0m"
$ColorBold = "`e[1m"

function Write-Header {
    Clear-Host
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  SEO-GEO WordPress App Installer" -ForegroundColor Cyan -BackgroundColor DarkGray
    Write-Host "  Professional Edition for Windows" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Text, [int]$Step, [int]$Total)
    $percent = [int]($Step / $Total * 100)
    $bar = ""
    for ($i = 0; $i -lt 30; $i++) {
        if ($i -lt $percent / 3.33) { $bar += "#" }
        else { $bar += " " }
    }
    Write-Host "" -NoNewline
    Write-Host "[$percent%] [$bar]" -ForegroundColor Green -NoNewline
    Write-Host " $Text" -ForegroundColor White
}

function Write-Error { param([string]$Text)
    Write-Host "  ERROR: $Text" -ForegroundColor Red
}

function Write-Success { param([string]$Text)
    Write-Host "  SUCCESS: $Text" -ForegroundColor Green
}

function Test-Prerequisites {
    Write-Step "Checking system prerequisites..." 1 8
    
    # Check PowerShell version
    if ([Environment]::OSVersion.Version.Major -lt 10) {
        Write-Error "Windows 10 or later is required"
        return $false
    }
    Write-Success "Windows version OK"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error "Python is not installed. Please install Python 3.9+ from python.org"
        return $false
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>&1
        Write-Success "pip found: $pipVersion"
    } catch {
        Write-Error "pip is not available"
        return $false
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>&1
        Write-Success "Git found: $gitVersion"
    } catch {
        Write-Error "Git is not installed"
        return $false
    }
    
    return $true
}

function Install-Dependencies {
    Write-Step "Creating installation directory..." 2 8
    
    if (Test-Path $InstallPath) {
        Write-Host "  Removing existing installation..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $InstallPath -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
    Write-Success "Created: $InstallPath"
    
    Write-Step "Downloading application files..." 3 8
    try {
        $clonePath = "$env:TEMP\seo-geo-temp"
        if (Test-Path $clonePath) { Remove-Item -Recurse -Force $clonePath }
        git clone $RepoUrl $clonePath --quiet
        Copy-Item -Path "$clonePath\*" -Destination $InstallPath -Recurse -Force
        Remove-Item -Recurse -Force $clonePath
        Write-Success "Files downloaded and installed"
    } catch {
        Write-Error "Failed to download: $_"
        return $false
    }
    
    Write-Step "Installing Python dependencies..." 4 8
    Set-Location $InstallPath
    try {
        $requirements = pip install -r requirements.txt 2>&1
        Write-Success "Dependencies installed"
    } catch {
        Write-Error "Failed to install dependencies: $_"
        return $false
    }
    
    return $true
}

function Create-DesktopShortcut {
    Write-Step "Creating desktop shortcut..." 5 8
    
    $Desktop = [System.IO.Path]::Combine(
        [System.Environment]::GetFolderPath("Desktop"),
        "SEO-GEO WordPress App.lnk"
    )
    
    $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $PythonExe) {
        $PythonExe = "python"
    }
    
    $MainScript = "$InstallPath\main.py"
    
    try {
        $WScript = New-Object -ComObject WScript.Shell
        $ShortCut = $WScript.CreateShortcut($Desktop)
        $ShortCut.TargetPath = $PythonExe
        $ShortCut.Arguments = "`"$MainScript`""
        $ShortCut.WorkingDirectory = $InstallPath
        $ShortCut.Description = "SEO-GEO WordPress Desktop Application"
        $ShortCut.IconLocation = "$InstallPath\app.ico,0"
        $ShortCut.Save()
        Write-Success "Desktop shortcut created"
        Write-Success "  Location: $Desktop"
    } catch {
        Write-Warning "  Could not create desktop shortcut: $_"
        Write-Warning "  You can manually create one using the instructions in README.md"
    }
}

function Create-StartMenuShortcut {
    Write-Step "Creating Start Menu shortcut..." 6 8
    
    $StartMenu = [System.IO.Path]::Combine(
        [System.Environment]::GetFolderPath("StartMenu"),
        "Programs", "SEO-GEO WordPress App"
    )
    
    New-Item -ItemType Directory -Force -Path $StartMenu | Out-Null
    
    $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $PythonExe) { $PythonExe = "python" }
    
    try {
        $WScript = New-Object -ComObject WScript.Shell
        $ShortCut = $WScript.CreateShortcut("$StartMenu\Launch App.lnk")
        $ShortCut.TargetPath = $PythonExe
        $ShortCut.Arguments = "`"$InstallPath\main.py`""
        $ShortCut.WorkingDirectory = $InstallPath
        $ShortCut.Description = "Launch SEO-GEO WordPress App"
        $ShortCut.Save()
        Write-Success "Start Menu shortcut created"
    } catch {
        Write-Warning "  Could not create Start Menu shortcut: $_"
    }
}

function Create-Uninstaller {
    Write-Step "Creating uninstaller..." 7 8
    
    $UninstallScript = @"
# SEO-GEO WordPress App Uninstaller
param([switch]$Force)

`$InstallPath = "$InstallPath"
`$Desktop = [System.IO.Path]::Combine(
    [System.Environment]::GetFolderPath("Desktop"),
    "SEO-GEO WordPress App.lnk"
)
`$StartMenu = [System.IO.Path]::Combine(
    [System.Environment]::GetFolderPath("StartMenu"),
    "Programs", "SEO-GEO WordPress App"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SEO-GEO WordPress App Uninstaller" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (-not `$Force) {
    `$response = Read-Host "Remove SEO-GEO WordPress App from `$InstallPath ? [Y/N]"
    if (`$response -ne "Y" -and `$response -ne "y") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit
    }
}

try {
    Remove-Item -Recurse -Force `$InstallPath -ErrorAction SilentlyContinue
    Write-Host "  Application files removed" -ForegroundColor Green
} catch { }

try {
    Remove-Item `$Desktop -ErrorAction SilentlyContinue
    Write-Host "  Desktop shortcut removed" -ForegroundColor Green
} catch { }

try {
    Remove-Item -Recurse -Force `$StartMenu -ErrorAction SilentlyContinue
    Write-Host "  Start Menu entry removed" -ForegroundColor Green
} catch { }

Write-Host "`nUninstallation complete!" -ForegroundColor Green
"@
    
    Set-Content -Path "$InstallPath\uninstall.ps1" -Value $UninstallScript
    Write-Success "Uninstaller created: $InstallPath\uninstall.ps1"
}

function Show-Completion {
    Write-Step "Finalizing installation..." 8 8
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan -BackgroundColor DarkGray
    Write-Host "  INSTALLATION COMPLETE!" -ForegroundColor Green -BackgroundColor DarkGray
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Application installed to: $InstallPath" -ForegroundColor White
    Write-Host "  Desktop shortcut created" -ForegroundColor White
    Write-Host "  Start Menu shortcut created" -ForegroundColor White
    Write-Host "  Uninstaller available" -ForegroundColor White
    Write-Host ""
    Write-Host "  To launch the application:" -ForegroundColor Yellow
    Write-Host "  1. Double-click 'SEO-GEO WordPress App' on your desktop" -ForegroundColor Gray
    Write-Host "  2. Or run: python `"$InstallPath\main.py`"" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  First steps:" -ForegroundColor Yellow
    Write-Host "  1. Open the app and go to API Settings tab" -ForegroundColor Gray
    Write-Host "  2. Enter your OpenRouter or OpenCode API key" -ForegroundColor Gray
    Write-Host "  3. Go to WordPress Settings tab and add your site" -ForegroundColor Gray
    Write-Host "  4. Start creating and publishing blog posts!" -ForegroundColor Gray
    Write-Host ""
}

# Main installer
Write-Header

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "  WARNING: Not running as Administrator." -ForegroundColor Yellow
    Write-Host "  Some features may not work correctly." -ForegroundColor Yellow
    Write-Host "" -NoNewline
}

if (-not (Test-Prerequisites)) {
    Write-Host "`nInstallation aborted due to missing prerequisites." -ForegroundColor Red
    exit 1
}

if (-not (Install-Dependencies)) {
    Write-Host "`nInstallation failed during dependency installation." -ForegroundColor Red
    exit 1
}

Create-DesktopShortcut
Create-StartMenuShortcut
Create-Uninstaller
Show-Completion

exit 0
