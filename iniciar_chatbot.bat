@echo off
cd /d "C:\OPENCODE\HACKATON"
python -m streamlit run chatbot.py --server.headless true
pause
