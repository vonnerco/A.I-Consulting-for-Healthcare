#!/bin/bash
# Activation script for Codex AI Tools environment

echo "Activating Codex AI Tools environment..."
cd "/Users/Corderio_Vonner/Library/CloudStorage/OneDrive-McKinsey&Company/Documents/AI"
source codex_ai_env/bin/activate

echo "Environment activated!"
echo "Installed packages:"
pip list | grep -E "(openai|anthropic|langchain|torch|transformers|pandas|numpy|jupyter|pytest)"

echo ""
echo "To deactivate: deactivate"
echo "To start Jupyter: jupyter lab"
echo "To test OpenAI: python -c 'import openai; print(\"OpenAI installed successfully\")'"


