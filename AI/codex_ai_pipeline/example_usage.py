#!/usr/bin/env python3
"""
Codex AI Pipeline - Example Usage
Demonstrates how to use the pipeline components with environment variables
"""

from dotenv import load_dotenv
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Check if API keys are loaded
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    pinecone_key = os.getenv('PINECONE_API_KEY')
    
    print("🔑 Environment Variables Loaded:")
    print(f"✅ OpenAI Key: {'Loaded' if openai_key else 'Missing'}")
    print(f"✅ Anthropic Key: {'Loaded' if anthropic_key else 'Missing'}")
    print(f"✅ Pinecone Key: {'Loaded' if pinecone_key else 'Missing'}")
    
    return {
        'openai_key': openai_key,
        'anthropic_key': anthropic_key,
        'pinecone_key': pinecone_key
    }

def test_openai_connection(api_key):
    """Test OpenAI API connection"""
    if not api_key:
        print("❌ OpenAI API key not found")
        return False
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Say "Hello from OpenAI!"'}],
            max_tokens=20
        )
        
        print(f"✅ OpenAI Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return False

def test_anthropic_connection(api_key):
    """Test Anthropic API connection"""
    if not api_key:
        print("❌ Anthropic API key not found")
        return False
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Simple test request
        response = client.messages.create(
            model='claude-3-haiku-20240307',
            max_tokens=20,
            messages=[{'role': 'user', 'content': 'Say "Hello from Claude!"'}]
        )
        
        print(f"✅ Anthropic Response: {response.content[0].text}")
        return True
        
    except Exception as e:
        print(f"❌ Anthropic Error: {e}")
        return False

def test_local_components():
    """Test local components that don't require API keys"""
    print("\n🔧 Testing Local Components:")
    
    try:
        import chromadb
        print("✅ ChromaDB: Available")
        
        # Test ChromaDB
        client = chromadb.Client()
        collection = client.create_collection("test_collection")
        collection.add(
            documents=["This is a test document"],
            ids=["test_id"]
        )
        results = collection.query(query_texts=["test"], n_results=1)
        print("✅ ChromaDB: Working")
        
    except Exception as e:
        print(f"❌ ChromaDB Error: {e}")
    
    try:
        import langchain
        print("✅ LangChain: Available")
    except Exception as e:
        print(f"❌ LangChain Error: {e}")

def main():
    """Main function to demonstrate usage"""
    print("🚀 Codex AI Pipeline - Usage Example")
    print("=" * 50)
    
    # Step 1: Load environment variables
    print("\n📋 Step 1: Loading Environment Variables")
    env_vars = load_environment()
    
    # Step 2: Test API connections
    print("\n🌐 Step 2: Testing API Connections")
    openai_works = test_openai_connection(env_vars['openai_key'])
    anthropic_works = test_anthropic_connection(env_vars['anthropic_key'])
    
    # Step 3: Test local components
    test_local_components()
    
    # Step 4: Summary
    print("\n📊 Summary:")
    print(f"OpenAI API: {'✅ Working' if openai_works else '❌ Not Working'}")
    print(f"Anthropic API: {'✅ Working' if anthropic_works else '❌ Not Working'}")
    print("Local Components: ✅ Available")
    
    if openai_works or anthropic_works:
        print("\n🎉 Pipeline is ready to use!")
    else:
        print("\n⚠️  Add API credits to use LLM features")

if __name__ == "__main__":
    main()
