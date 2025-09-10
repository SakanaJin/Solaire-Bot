@echo off

python -m venv .venv

call .venv\Scrips\activate.bat

pip install -r requirements.txt

call deactivate