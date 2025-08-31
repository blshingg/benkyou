#!/bin/bash

# Build script for Benkyou application
# This script uses uv to manage dependencies and PyInstaller to create an executable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}🚀 Starting build process for Benkyou...${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}📦 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}🔨 $1${NC}"
}

print_config() {
    echo -e "${BLUE}📝 $1${NC}"
}

print_cleanup() {
    echo -e "${BLUE}🧹 $1${NC}"
}

print_status

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed or not in PATH"
    echo "Please install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if we're in the project directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

# Clean previous builds
print_cleanup "Cleaning previous builds..."
if [ -d "dist" ]; then
    rm -rf dist
fi
if [ -d "build" ]; then
    rm -rf build
fi
if [ -f "*.spec" ]; then
    rm -f *.spec
fi

# Install PyInstaller if not already installed
print_info "Installing PyInstaller..."
uv add --dev pyinstaller

# Install all dependencies
print_info "Installing dependencies..."
uv sync

# Create PyInstaller spec file
print_config "Creating PyInstaller configuration..."

# Determine the appropriate executable extension based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (WSL/Git Bash)
    EXE_EXT=".exe"
    EXE_NAME="benkyou.exe"
    OUTPUT_PATH="dist/benkyou.exe"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    EXE_EXT=""
    EXE_NAME="benkyou"
    OUTPUT_PATH="dist/benkyou"
else
    # Linux and other Unix-like systems
    EXE_EXT=""
    EXE_NAME="benkyou"
    OUTPUT_PATH="dist/benkyou"
fi

cat > benkyou.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('vocab_files', 'vocab_files'),
        ('progress_files', 'progress_files'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'frontend.widgets.main_menu',
        'frontend.widgets.study_menu',
        'frontend.widgets.progress',
        'frontend.widgets.study_session',
        'frontend.widgets.progress_menu',
        'spaced_repetition.card',
        'spaced_repetition.deck',
        'translation.romaji_to_kana',
        'utils.fuzzy_match',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='$EXE_NAME',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
EOF

# Build the executable
print_step "Building executable with PyInstaller..."
uv run pyinstaller benkyou.spec

# Check if build was successful
if [ -f "$OUTPUT_PATH" ]; then
    print_success "Build successful!"
    echo "📁 Executable created at: $OUTPUT_PATH"
    
    # Get file size
    if command -v stat &> /dev/null; then
        # Linux/macOS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            file_size=$(stat -f%z "$OUTPUT_PATH")
        else
            # Linux
            file_size=$(stat -c%s "$OUTPUT_PATH")
        fi
        file_size_mb=$(echo "scale=2; $file_size / 1024 / 1024" | bc -l 2>/dev/null || echo "scale=2; $file_size / 1024 / 1024" | awk '{printf "%.2f", $1}')
        echo -e "${CYAN}📊 Executable size: ${file_size_mb} MB${NC}"
    else
        echo -e "${CYAN}📊 Executable size: Check manually${NC}"
    fi
    
    # Clean up spec file
    rm -f benkyou.spec
    
    print_success "You can now run $OUTPUT_PATH"
    
    # Make executable on Unix-like systems
    if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "cygwin" ]]; then
        chmod +x "$OUTPUT_PATH"
        echo "🔒 Made executable file executable"
    fi
    
else
    print_error "Build failed! Check the output above for errors."
    exit 1
fi
