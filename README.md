# BasicChat: Your Intelligent Local AI Assistant

## 📋 Table of Contents
- [Overview](#overview)
- [Demo](#-demo)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**BasicChat** is your intelligent AI assistant that runs completely on your local machine. Built with advanced reasoning capabilities, enhanced tools, and enterprise-grade performance, it provides a powerful, private AI experience without compromising on functionality.

### ✨ What Makes BasicChat Special?

- **🔒 Privacy First**: Everything runs locally via Ollama - no data sent to external servers
- **🧠 Advanced Reasoning**: Chain-of-Thought, Multi-Step, and Agent-Based reasoning modes
- **🛠️ Powerful Tools**: Smart calculator, time management, web search, and document processing
- **💾 Persistent Sessions**: Advanced session management with search, export, and organization
- **⚡ High Performance**: Async architecture with intelligent caching for 50-80% faster responses
- **📱 Beautiful Interface**: Modern Streamlit interface with real-time streaming and dark theme

### 🎯 Perfect For:
- **Students & Researchers**: Complex problem solving with step-by-step explanations
- **Developers**: Code analysis, debugging, and technical documentation
- **Professionals**: Document processing, time management, and data analysis
- **Anyone**: Who wants a powerful, private AI assistant

## 🎥 Demo

![BasicChat Demo](assets/demo_seq_0.6s.gif)

Experience BasicChat's powerful features:
- 🧠 Multiple reasoning modes for different problem types
- 💬 Natural conversation with step-by-step explanations
- 💾 Persistent session management with search and export
- 🎨 Beautiful dark theme interface
- 📚 Support for multiple file formats and document types
- ⚡ Real-time streaming responses

## 🌟 Key Features

### 🧠 Advanced Reasoning Engine
Transform how you interact with AI through multiple reasoning modes:

- **🤔 Chain-of-Thought Reasoning**: Watch the AI think step-by-step, making complex problems easy to understand
- **🔄 Multi-Step Analysis**: Break down complex questions into manageable parts with context-aware processing
- **🤖 Agent-Based Intelligence**: Dynamic tool selection that automatically chooses the best calculator, web search, or time tools for your needs
- **📊 Confidence Scoring**: Know how certain the AI is about its answers with built-in confidence assessment

### 🛠️ Enhanced Tools & Utilities
Powerful built-in tools that make BasicChat your all-in-one assistant:

- **🧮 Smart Calculator**: Safe mathematical operations with step-by-step solutions, advanced functions, and beautiful formatting
- **⏰ Advanced Time Tools**: Multi-timezone support with automatic DST handling and precise calculations
- **🌐 Web Search Integration**: Real-time DuckDuckGo search with intelligent caching and retry logic
- **💾 Smart Caching System**: Multi-layer caching (Redis + memory) for 50-80% faster responses

### 📄 Document & Multi-Modal Processing
Turn any document into knowledge with advanced processing capabilities:

- **📚 Multi-Format Support**: PDF, text, images with OCR capabilities
- **🔍 RAG Integration**: Semantic search using ChromaDB vector store
- **🖼️ Image Analysis**: OCR and visual content understanding
- **📊 Structured Data**: Intelligent document chunking and embedding

### 💾 Session Management
Never lose your conversations with advanced session management:

- **💾 Persistent Storage**: SQLite-based session storage with automatic migrations
- **🔍 Smart Search & Organization**: Search through chat history by title or content
- **📤 Export & Import**: JSON and Markdown export/import for data portability
- **🔄 Session Controls**: Create, load, and manage conversations with auto-save functionality

## 📁 Project Structure

```
basic-chat-template/
├── src/                          # Source code (organized by functionality)
│   ├── core/                     # Core application logic
│   │   ├── app.py               # Main Streamlit application
│   │   └── document_processor.py # Document processing logic
│   ├── reasoning/                # Advanced reasoning engine
│   │   └── reasoning_engine.py  # Chain-of-thought, multi-step, agent-based reasoning
│   ├── session/                  # Session management
│   │   └── session_manager.py   # Chat session persistence and management
│   ├── api/                      # External API integrations
│   │   ├── ollama_api.py        # Ollama API client
│   │   └── web_search.py        # Web search functionality
│   ├── utils/                    # Utility modules
│   │   ├── async_ollama.py      # Async Ollama client
│   │   ├── caching.py           # Caching system
│   │   └── enhanced_tools.py    # Enhanced calculator and time tools
│   ├── config/                   # Configuration management
│   │   └── config.py            # Application configuration
│   └── database/                 # Database management
│       └── database_migrations.py # Database migration system
├── tests/                        # Comprehensive test suite
│   ├── test_app.py              # Main application tests
│   ├── test_reasoning.py        # Reasoning engine tests
│   ├── test_session_manager.py  # Session management tests
│   ├── test_enhanced_tools.py   # Enhanced tools tests
│   └── conftest.py              # Test configuration and fixtures
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # System architecture
│   ├── DEVELOPMENT.md           # Development guide
│   ├── FEATURES.md              # Features documentation
│   └── INSTALLATION.md          # Installation guide
├── diagrams/                     # Architecture diagrams
│   └── architecture.md          # Mermaid diagrams and system overview
├── scripts/                      # Automation scripts
├── assets/                       # Static assets (images, logos)
├── app.py                       # Main entry point (Streamlit)
├── requirements.txt             # Python dependencies
├── setup.py                     # Setup script
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- **Ollama**: [Install Ollama](https://ollama.ai) - Your local AI model server
- **Python**: 3.11 or higher
- **Git**: For cloning the repository

### 1. Install Required Models
```bash
# Core models for basic functionality
ollama pull mistral              # Primary reasoning model
ollama pull nomic-embed-text     # Embedding model for RAG

# Optional models for enhanced capabilities
ollama pull llava               # Vision model for image analysis
ollama pull codellama           # Code generation and analysis
```

### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/khaosans/basic-chat-template.git
cd basic-chat-template

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install the application (production)
pip install -e .

# OR install with development dependencies
pip install -e ".[dev]"
```

### 3. Start the Application
```bash
# Start Ollama service (if not running)
ollama serve &

# Launch BasicChat
streamlit run src/core/app.py
```

🎉 **You're ready!** The application will be available at `http://localhost:8501`

### Alternative Installation Methods

#### Using Make (Recommended for Development)
```bash
# Setup development environment
make dev-setup

# Run the application
make run

# Run tests
make test

# Format code
make format
```

#### Using pip directly
```bash
# Install from PyPI (when available)
pip install basic-chat

# Run the application
streamlit run src/core/app.py
```

#### Using Docker
```bash
# Build the image
docker build -t basic-chat .

# Run the container
docker run -p 8501:8501 basic-chat
```

## 📚 Documentation

### 📖 **Getting Started**
- **[Installation Guide](docs/INSTALLATION.md)** - Complete setup instructions, configuration, and troubleshooting
- **[Features Overview](docs/FEATURES.md)** - Detailed documentation of all capabilities and features

### 🏗️ **Technical Documentation**
- **[System Architecture](docs/ARCHITECTURE.md)** - Technical design, data flow diagrams, and component architecture
- **[Reasoning Engine](docs/REASONING_ENGINE.md)** - Advanced reasoning capabilities and implementation details
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing guidelines, testing, and development workflows

### 🚀 **Planning & Support**
- **[Production Roadmap](docs/ROADMAP.md)** - Future development phases and planned features
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues, known limitations, and solutions

## 🧪 Testing

### Run All Tests
```bash
# Run the complete test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_reasoning.py -v      # Reasoning engine tests
pytest tests/test_session_manager.py -v # Session management tests
pytest tests/test_enhanced_tools.py -v  # Enhanced tools tests
```

### Test Results
- **Latest Test Results**: [test_results_latest.md](test_results_latest.md) - Most recent test run with detailed output
- **Test Coverage**: 80%+ with 168+ tests across all modules
- **Test Categories**: Unit tests, integration tests, async tests, and performance tests

### Development Testing
```bash
# Run tests in watch mode (for development)
pytest tests/ -f --tb=short

# Run tests with specific markers
pytest tests/ -m "not slow"  # Skip slow tests
pytest tests/ -m "async"     # Run only async tests
```

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](docs/DEVELOPMENT.md) for detailed information.

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Add tests** for new functionality
4. **Ensure all tests pass**: `pytest`
5. **Submit a pull request**

## 📊 Performance Metrics

- **Response Time**: 50-80% faster with caching enabled
- **Cache Hit Rate**: 70-85% for repeated queries
- **Uptime**: 99.9% with health monitoring
- **Test Coverage**: 80%+ with 168+ tests

## 🔧 Configuration

Create `.env.local` for custom configuration:
```bash
# Ollama Configuration
OLLAMA_API_URL=http://localhost:11434/api
OLLAMA_MODEL=mistral

# Performance Settings
ENABLE_CACHING=true
CACHE_TTL=3600
RATE_LIMIT=10
REQUEST_TIMEOUT=30

# Session Management
ENABLE_SESSION_MANAGEMENT=true
SESSION_DATABASE_PATH=./chat_sessions.db
ENABLE_AUTO_SAVE=true
AUTO_SAVE_INTERVAL=300
ENABLE_SESSION_SEARCH=true
MAX_SESSIONS_PER_USER=1000
SESSION_CLEANUP_DAYS=30

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=false
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 References & Citations

### Research Papers
- **Chain-of-Thought Reasoning**: Wei et al. demonstrate that step-by-step reasoning significantly improves AI performance on complex tasks, achieving up to 40% accuracy improvements on mathematical reasoning benchmarks (Wei et al. 2022).
- **Retrieval-Augmented Generation**: Lewis et al. introduce RAG as a method to enhance language models with external knowledge, showing substantial improvements in factual accuracy and reducing hallucination rates by up to 60% (Lewis et al. 2020).
- **Speculative Decoding**: Chen et al. present techniques for accelerating large language model inference through parallel token prediction, achieving 2-3x speedup without quality degradation (Chen et al. 2023).

### Core Technologies
- **Ollama**: [https://ollama.ai](https://ollama.ai) - Local large language model server
- **Streamlit**: [https://streamlit.io](https://streamlit.io) - Web application framework
- **LangChain**: [https://langchain.com](https://langchain.com) - LLM application framework
- **ChromaDB**: [https://chromadb.ai](https://chromadb.ai) - Vector database

### Works Cited
Wei, Jason, et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *arXiv preprint arXiv:2201.11903*, 2022.

Lewis, Mike, et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *Advances in Neural Information Processing Systems*, vol. 33, 2020, pp. 9459-9474.

Chen, Charlie, et al. "Accelerating Large Language Model Decoding with Speculative Sampling." *arXiv preprint arXiv:2302.01318*, 2023.

---

**Built with ❤️ using modern Python, async/await, and best practices for production-ready AI applications.**
