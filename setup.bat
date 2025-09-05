@echo off

if not exist ".venv\Scripts\activate.bat" (
    python -m venv .venv
)

call .venv\Scrips\activate.bat

if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Skipping package installation.
)

deactivate