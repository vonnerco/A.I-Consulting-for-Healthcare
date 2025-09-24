# 🤖 Codex AI Pipeline - Human-Friendly Interface

## 🎯 Overview

The `AI Pipeline.py` file has been completely transformed into a beautiful, human-friendly web interface inspired by Anthropic's design. This interface provides an intuitive chat experience for interacting with your AI pipeline.

## ✨ Features

- **🎨 Anthropic-style Design**: Clean, modern interface with gradient backgrounds and smooth animations
- **💬 Real-time Chat**: Interactive chat interface with typing indicators and message bubbles
- **📝 Context Support**: Add optional context to your queries for better responses
- **📚 Session Management**: Automatic conversation history tracking
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices
- **🔄 Real-time Processing**: Live feedback during message processing
- **🌐 RESTful API**: Full API endpoints for programmatic access

## 🚀 Quick Start

1. **Start the Interface**:
   ```bash
   cd /path/to/your/api/directory
   python3 "AI Pipeline.py"
   ```

2. **Open in Browser**:
   - Main Interface: http://localhost:8003
   - API Documentation: http://localhost:8003/docs

## 🎮 How to Use

### Web Interface
1. Open http://localhost:8003 in your browser
2. Optionally add context in the context field
3. Type your message in the chat input
4. Press Enter or click "Send"
5. Watch the AI respond in real-time!

### API Endpoints

- **POST /chat**: Send a message to the AI
- **GET /sessions/{session_id}/history**: Get chat history
- **GET /health**: Check system health

### Example API Usage
```python
import requests

response = requests.post("http://localhost:8003/chat", json={
    "message": "What is machine learning?",
    "context": "I'm a beginner in AI"
})

print(response.json()["response"])
```

## 🛠 Technical Details

- **Backend**: FastAPI with async support
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Styling**: Modern gradient design with animations
- **Architecture**: Session-based conversation management
- **Compatible**: Works with existing pipeline infrastructure

## 🔧 Configuration

The interface uses the same pipeline configuration as before:
- Model: gpt-3.5-turbo
- Temperature: 0.7
- Max Tokens: 2000
- Top P: 0.9

## 📊 What Changed

### Before
- Simple command-line interface
- Basic input/output
- No session management
- No visual feedback

### After
- Beautiful web interface
- Real-time chat experience
- Session management with history
- Context support
- Professional API
- Mobile-responsive design
- Anthropic-inspired styling

## 🎨 Interface Preview

The interface features:
- **Header**: Gradient purple header with title and description
- **Chat Area**: Clean white background with message bubbles
- **Input Area**: Context field and message input with send button
- **Messages**: User messages in purple, AI responses in white
- **Animations**: Smooth fade-ins and thinking indicators

## 🔄 Backward Compatibility

The original functions are still available:
- `run_pipeline(query, context)`: Synchronous execution
- `main()`: Now launches the web interface instead of CLI

## 🎉 Next Steps

Your AI Pipeline is now ready for human-friendly interaction! The interface provides a professional, intuitive way to interact with your AI models while maintaining all the power of the underlying pipeline.

Enjoy your new Anthropic-style AI interface! 🚀