#!/usr/bin/env python3
"""
BasicChat - Setup Script

This setup script installs the BasicChat application and its dependencies.
It follows Python packaging best practices for production-ready applications.

Usage:
    python setup.py install
    python setup.py develop
"""

import subprocess
import sys
import os
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "BasicChat - AI Chat Application with Advanced Reasoning"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = Path(__file__).parent / "requirements.txt"
    if requirements_path.exists():
        return requirements_path.read_text().splitlines()
    return []

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Ollama is installed and accessible")
            return True
        else:
            print("⚠️  Ollama is installed but not responding")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed. Please install from https://ollama.ai")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Ollama check timed out")
        return False

def install_requirements():
    """Install required packages"""
    requirements = read_requirements()
    if requirements:
        print("📦 Installing required packages...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [
        "chroma_db",
        "logs",
        "temp",
        "assets"
    ]
    
    print("📁 Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ Created {directory}/")

def main():
    """Main setup function"""
    print("🚀 Starting BasicChat setup...")
    
    # Install dependencies
    if not install_requirements():
        print("❌ Setup failed during dependency installation")
        return
    
    # Setup directories
    setup_directories()
    
    # Check Ollama
    check_ollama()
    
    print("✨ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Start Ollama: ollama serve")
    print("2. Pull required models: ollama pull mistral")
    print("3. Run the application: streamlit run app.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    # Setup configuration
    setup(
        name="basic-chat",
        version="1.0.0",
        author="Souriya Khaosanga",
        author_email="souriya@chainable.ai",
        description="AI Chat Application with Advanced Reasoning Capabilities",
        long_description=read_readme(),
        long_description_content_type="text/markdown",
        url="https://github.com/khaosans/basic-chat-template",
        packages=find_packages(),
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        python_requires=">=3.11",
        install_requires=read_requirements(),
        extras_require={
            "dev": [
                "pytest>=7.0.0",
                "pytest-asyncio>=0.21.0",
                "pytest-cov>=4.0.0",
                "black>=23.0.0",
                "flake8>=6.0.0",
                "mypy>=1.0.0",
            ],
        },
        entry_points={
            "console_scripts": [
                "basic-chat=src.core.app:main",
            ],
        },
        include_package_data=True,
        zip_safe=False,
    )
    
    # Run additional setup steps
    main() 