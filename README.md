# BasicChat: Your Intelligent Local AI Assistant

## Overview
BasicChat is a privacy-focused AI assistant that runs locally using Ollama. It features advanced reasoning capabilities, RAG (Retrieval Augmented Generation), multi-modal processing, and smart tools - all through a clean Streamlit interface.

![Chat Interface: Clean layout with message history and real-time response indicators](assets/chat-interface.png)

## 🌟 Key Features

### Core Capabilities
- Local LLM integration via Ollama
  - Configurable model selection (Mistral as default)
  - Multiple reasoning modes (Chain-of-Thought, Multi-Step, Agent-Based)
  - Streaming responses with thought process visualization
  - Memory-efficient processing

### Advanced Reasoning
- Chain-of-Thought reasoning
  - Step-by-step problem solving
  - Visible reasoning process
  - Confidence scoring
- Multi-Step reasoning
  - Complex query breakdown
  - Context-aware processing
  - Document-based reasoning
- Agent-Based reasoning
  - Tool integration (Calculator, Time, Web Search)
  - Dynamic tool selection
  - Real-time web search capability

### Document Processing
- Multi-format support
  - PDF, TXT, MD file processing
  - Image analysis capabilities
  - Structured data handling
- RAG implementation
  - Semantic search
  - Context retrieval
  - Dynamic knowledge integration

## 🏗️ System Architecture
```mermaid
graph TD
    classDef ui fill:#4285f4,stroke:#2956a3,color:white
    classDef logic fill:#34a853,stroke:#1e7e34,color:white
    classDef model fill:#ea4335,stroke:#b92d22,color:white
    classDef storage fill:#fbbc05,stroke:#cc9a04,color:black

    A["User Interface (Streamlit)"]:::ui
    B["App Logic & Session State"]:::logic
    C["Document Processor"]:::logic
    D["Reasoning Engine"]:::logic
    E["Ollama API (LLMs)"]:::model
    F["Web Search (DuckDuckGo)"]:::model
    G["Vector Store (ChromaDB)"]:::storage

    A -->|User Query / File Upload| B
    B -->|Document Upload| C
    B -->|Reasoning Request| D
    C -->|Embeddings| G
    D -->|RAG Query| G
    D -->|LLM Request| E
    D -->|Web Search| F
    E -->|LLM Response| D
    F -->|Search Results| D
    G -->|Context| D
    D -->|Structured Output| B
    B -->|Display| A
```

## 🧠 Reasoning Modes Flow
```mermaid
graph TD
    classDef mode fill:#4285f4,stroke:#2956a3,color:white
    classDef step fill:#34a853,stroke:#1e7e34,color:white
    classDef tool fill:#fbbc05,stroke:#cc9a04,color:black
    classDef output fill:#ea4335,stroke:#b92d22,color:white

    Q["User Query"]:::mode --> M{"Reasoning Mode"}:::mode
    M -->|Chain-of-Thought| COT["Step-by-Step Reasoning"]:::step
    M -->|Multi-Step| MS["Multi-Step Analysis"]:::step
    M -->|Agent-Based| AG["Agent & Tools"]:::tool

    COT --> TP["Thought Process"]:::output
    MS --> CTX["Context Retrieval"]:::tool
    AG --> TSEL["Tool Selection (Web, Calc, Time)"]:::tool

    TP --> FA["Final Answer"]:::output
    CTX --> FA
    TSEL --> FA
```

## 📄 Document & Image Processing Pipeline
```mermaid
graph LR
    classDef input fill:#4285f4,stroke:#2956a3,color:white
    classDef process fill:#34a853,stroke:#1e7e34,color:white
    classDef storage fill:#fbbc05,stroke:#cc9a04,color:black
    classDef output fill:#ea4335,stroke:#b92d22,color:white

    A["Document/Image Upload"]:::input --> B["Type Detection"]:::process
    B -->|PDF| C["PDF Loader"]:::process
    B -->|Image| D["Image Loader"]:::process
    B -->|Text| E["Text Loader"]:::process

    C --> F["Text Extraction"]:::process
    D --> F
    E --> F

    F --> G["Chunking & Embedding"]:::process
    G --> H["Vector Store (ChromaDB)"]:::storage
    H --> I["Context Retrieval for RAG"]:::output
```

## 🧠 Memory Management System
```mermaid
graph TD
    classDef memory fill:#4285f4,stroke:#2956a3,color:white
    classDef process fill:#34a853,stroke:#1e7e34,color:white
    classDef storage fill:#fbbc05,stroke:#cc9a04,color:black
    classDef output fill:#ea4335,stroke:#b92d22,color:white

    A["Chat History"]:::memory --> B{"Memory Manager"}:::process
    C["Context Window"]:::memory --> B
    D["Vector Store"]:::storage --> B

    B --> E["Short-term Memory"]:::memory
    B --> F["Long-term Memory"]:::memory

    E --> G["Active Context"]:::output
    F --> H["Persistent Storage"]:::storage

    G --> I["Response Generation"]:::output
    H --> J["Knowledge Retrieval"]:::output
```

## 🤖 Model Interaction Flow
```mermaid
graph TD
    classDef model fill:#4285f4,stroke:#2956a3,color:white
    classDef process fill:#34a853,stroke:#1e7e34,color:white
    classDef data fill:#fbbc05,stroke:#cc9a04,color:black
    classDef output fill:#ea4335,stroke:#b92d22,color:white

    A["User Input"]:::data --> B{"Input Type"}:::process
    B -->|Text| C["Mistral (LLM)"]:::model
    B -->|Image| D["LLaVA (Vision)"]:::model
    B -->|Document| E["Text Embeddings"]:::model

    C --> F["Response Generation"]:::process
    D --> F
    E --> G["Vector Database"]:::data

    G -->|Context| F
    F --> H["Final Output"]:::output
```

## 🧩 Data Flow: End-to-End User Query
```mermaid
graph TD
    classDef user fill:#4285f4,stroke:#2956a3,color:white
    classDef sys fill:#34a853,stroke:#1e7e34,color:white
    classDef model fill:#ea4335,stroke:#b92d22,color:white
    classDef store fill:#fbbc05,stroke:#cc9a04,color:black
    classDef out fill:#b892f4,stroke:#6c3ebf,color:white

    U["User"]:::user --> Q["Query/Input"]:::sys
    Q --> RM["Reasoning Mode Selection"]:::sys
    RM -->|Agent| AG["Agent & Tools"]:::model
    RM -->|CoT| COT["Chain-of-Thought"]:::model
    RM -->|Multi-Step| MS["Multi-Step Reasoning"]:::model
    AG --> T["Tool Use (Web, Calc, Time)"]:::model
    COT --> LLM1["LLM (Mistral)"]:::model
    MS --> LLM2["LLM (Mistral)"]:::model
    T --> LLM3["LLM (Mistral)"]:::model
    LLM1 --> OUT["Output"]:::out
    LLM2 --> OUT
    LLM3 --> OUT
```

## 🚀 Quick Start

### Prerequisites
1. Install [Ollama](https://ollama.ai)
2. Python 3.11+
3. Git

### Required Models
```bash
# Install core models
ollama pull mistral        # Primary reasoning model
ollama pull nomic-embed-text   # Embedding model

# Optional models for specific tasks
ollama pull llava         # Vision model (optional)
ollama pull codellama    # Code tasks (optional)
```

### Installation
```bash
# Clone repository
git clone https://github.com/khaosans/basic-chat-template.git
cd basic-chat-template

# Set up environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the app
streamlit run app.py
```

## 🧪 Testing
The project includes comprehensive tests for all components:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_reasoning.py  # Test reasoning capabilities
pytest tests/test_processing.py # Test document processing
pytest tests/test_web_search.py # Test web search functionality
```

## 🔧 Development

### Project Structure
```
basic-chat-template/
├── app.py                 # Main Streamlit application
├── reasoning_engine.py    # Reasoning capabilities
├── document_processor.py  # Document handling
├── web_search.py         # Web search integration
├── ollama_api.py         # Ollama API interface
├── tests/                # Test suite
└── assets/              # Images and resources
```

### Adding New Features
1. Follow the existing module structure
2. Add appropriate tests
3. Update documentation
4. Ensure all tests pass

## 📝 License
MIT License - See LICENSE file for details.

## 🤝 Contributing
Contributions are welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.

## 🐛 Troubleshooting
- Ensure Ollama is running (`ollama serve`)
- Check model downloads (`ollama list`)
- Verify port 8501 is available
- Check logs for detailed error messages

## 📚 Documentation
- [Reasoning Capabilities](REASONING_FEATURES.md)
- [Known Issues](BUGS.md)
- [License](LICENSE)
