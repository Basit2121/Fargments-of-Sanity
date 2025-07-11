# Fragments of Sanity

A psychological text-based escape game powered by AI.

![screenshot](screenshot.png)

## Game Objective

You find yourself trapped in a mysterious place. Your only way out is to convince Maya, an unpredictable character, to open the door for you. Every message you send counts as a move. You have 50 moves to escape—choose your words wisely!

## Features
- AI-powered interactive dialogue (Gemini API)
- Atmospheric retro visuals and sound
- Move-limited challenge (50 moves)
- Responsive, modern web interface

## Dependencies
- Python 3.8+
- [Eel](https://github.com/ChrisKnott/Eel)
- [python-vlc](https://pypi.org/project/python-vlc/)
- [google-generativeai](https://pypi.org/project/google-generativeai/)
- [pydub](https://pypi.org/project/pydub/)
- [psutil](https://pypi.org/project/psutil/)
- [ffmpeg](https://ffmpeg.org/) (required by pydub for audio playback)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Basit2121/Fargments-of-Sanity.git
   cd Fargments-of-Sanity-main
   ```

2. **Install Python dependencies**
   ```bash
   pip install eel python-vlc google-generativeai pydub psutil
   ```

3. **Install FFmpeg**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system PATH.

4. **Set up your Google Generative AI API key**
   - The API key is currently hardcoded in `game.py`. For security, you may want to use an environment variable instead.

5. **Run the game**
   ```bash
   python game.py
   ```
   The game will open in a Chrome window. If Chrome is not running, it will launch in kiosk mode.

6. **How to Play**
   - Enter your username and select a difficulty.
   - Interact with Maya by typing messages. Try to convince her to open the door.
   - You win if Maya agrees to open the door within 50 moves.

## Project Structure

- `assets/` — HTML, images, and audio files
- `game.py` — Main backend logic
- `README.md` — This file
- `screenshot.png` — Game screenshot

## License
This project is for educational and personal use.
