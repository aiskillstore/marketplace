#!/bin/bash

echo "====================================="
echo "Music Generation Skill Installation"
echo "====================================="
echo ""

# Update package list
echo "Updating package list..."
apt-get update -qq

# Install FluidSynth and SoundFonts
echo "Installing FluidSynth and SoundFonts..."
apt-get install -y fluidsynth fluid-soundfont-gm fluid-soundfont-gs

# Install FFmpeg for audio conversion
echo "Installing FFmpeg..."
apt-get install -y ffmpeg

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Verify installations
echo ""
echo "====================================="
echo "Verification"
echo "====================================="

# Check FluidSynth
if command -v fluidsynth &> /dev/null; then
    echo "✓ FluidSynth installed successfully"
else
    echo "✗ FluidSynth installation failed"
fi

# Check FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg installed successfully"
else
    echo "✗ FFmpeg installation failed"
fi

# Check SoundFont files
if [ -f "/usr/share/sounds/sf2/FluidR3_GM.sf2" ] || [ -f "/usr/share/sounds/sf2/default.sf2" ]; then
    echo "✓ SoundFont files found"
    ls -lh /usr/share/sounds/sf2/*.sf2 2>/dev/null || ls -lh /usr/share/soundfonts/*.sf2
else
    echo "✗ SoundFont files not found"
fi

# Check Python packages
echo ""
python3 -c "import music21; print('✓ music21 version:', music21.__version__)"
python3 -c "import midi2audio; print('✓ midi2audio installed')"
python3 -c "import pydub; print('✓ pydub installed')"

echo ""
echo "====================================="
echo "Installation Complete!"
echo "====================================="
echo ""
echo "You can now run: python music_generator.py"
echo "Or import the module in your own code"
