# Vietnamese TTS Book Reader

A powerful web application designed for reading large Vietnamese book chapters (16-20K characters) using a natural young adult female voice.

## Features

- **Smart Chunking**: Automatically splits large texts into optimal ~4K character segments.
- **Speed Control**: Adjust playback speed from 0.5x to 2.0x.
- **Young Adult Female Voice**: Uses the high-quality `nguyen-ngoc-ngan` model.
- **Self-Healing Diagnostics**: Real-time server status and manual restart controls.
- **Auto-Cleanup**: Temporary audio files are cleaned on system exit.

## Setup Instructions

### 1. Prerequisites

Ensure you have Python 3 and `ffmpeg` installed.

### 2. Install Dependencies

```bash
pip install gradio openai viet-tts pydub requests
```

### 3. Run the Application

Start the application by running:

```bash
python3 tts_web.py
```

The application launches at `http://localhost:7860`.

### 4. Restarting the App

- **To Restart the Web UI**: Press `Ctrl+C` in your terminal and run `python3 tts_web.py` again.
- **To Restart the Synthesis Engine**: Use the **🔄 Restart Backend Server** button in the right sidebar of the application.

## Usage

1. Paste your text into the **📖 Text Canvas**.
2. Adjust the **⚡ Speed** slider.
3. Click **🎤 Read Aloud Full Chapter**.
4. Monitor progress via the **📊 Status** panel.
5. Play the final audio once synthesis is complete.

## Troubleshooting

- **Status is "🔴 Offline"**: Click the **🔄 Restart Backend Server** button in the sidebar.
- **Connection Errors**: Check the **🛠️ Technical Details** accordion at the bottom for full tracebacks.
- **Audio Issues**: Ensure `ffmpeg` is correctly installed and in your PATH.

---

**April 2026 Refactor (Premium Soft Design)**

- Reorganized components into a widescreen-friendly sidebar layout.
- Integrated robust server lifecycle management and diagnostic reporting.
