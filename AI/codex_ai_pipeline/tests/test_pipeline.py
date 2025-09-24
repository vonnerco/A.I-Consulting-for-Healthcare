import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_import():
    """Test that basic imports work"""
    try:
        import openai
        import anthropic
        import langchain
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_environment_variables():
    """Test environment variable loading"""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    # Check if API keys are available
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    assert openai_key is not None, "OPENAI_API_KEY not found"
    assert anthropic_key is not None, "ANTHROPIC_API_KEY not found"
    assert len(openai_key) > 10, "OPENAI_API_KEY appears invalid"
    assert len(anthropic_key) > 10, "ANTHROPIC_API_KEY appears invalid"

def test_config_loading():
    """Test configuration loading"""
    try:
        from config.llm_config import LLMConfig
        config = LLMConfig()
        assert config.model_name == "gpt-4"
        assert config.temperature == 0.7
    except ImportError:
        pytest.skip("Config module not available")
