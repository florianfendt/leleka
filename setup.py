from setuptools import setup, find_packages

setup(
    name="leleka",  # Dein neuer Systemname! 🦅
    version="0.1",
    packages=find_packages(),
    py_modules=["main"],  # <-- WICHTIG: Das sagt Python, dass main.py im Root liegt!
    install_requires=[
        "typer",
        "rich",
        "pandas",
        "ollama"
    ],
    entry_points={
        "console_scripts": [
            "leleka=main:app",  # Verlinkt den Befehl direkt mit deiner main.py
        ],
    },
)