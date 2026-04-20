@echo off
echo Starting Viet-TTS Reader...
wsl.exe -d Ubuntu-24.04 -e bash -c "cd /home/tonyh/side-projects/Viet-TTS && python3 tts_web.py"
pause
