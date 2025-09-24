# Codex AI Pipeline

End-to-end LLM pipeline implementation following Senior AI Engineer requirements.

## Quick Start

1. **Setup Environment**
```bash
python3 -m venv codex_ai_env
source codex_ai_env/bin/activate
pip install -r requirements.txt
```

2. **Configure API Keys**
```bash
cp env.example .env
# Edit .env with your API keys
```

3. **Run Pipeline**
```bash
python -m src.pipeline.main_pipeline
```

4. **Start API Server**
```bash
python api/main.py
```

## Project Structure

```
codex_ai_pipeline/
├── src/
│   ├── agents/          # Multi-agent workflows
│   ├── llm/            # LLM configurations
│   ├── rag/            # RAG system components
│   ├── evaluation/     # Evaluation framework
│   ├── monitoring/     # Monitoring & metrics
│   ├── voice/          # Voice processing
│   ├── messaging/      # Platform integrations
│   └── pipeline/       # Main pipeline orchestration
├── config/             # Configuration files
├── tests/              # Unit tests
├── api/                # FastAPI deployment
├── data/               # Data storage
└── notebooks/          # Jupyter notebooks
```

## Features

- **RAG System**: Document processing with ChromaDB
- **Multi-Agent Workflows**: Research and analysis agents
- **Evaluation Framework**: LangSmith + WandB integration
- **Voice Processing**: Whisper + ElevenLabs
- **Monitoring**: Prometheus metrics
- **API Deployment**: FastAPI server
