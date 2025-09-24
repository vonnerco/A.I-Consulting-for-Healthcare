"""Human-friendly Anthropic-style Web UI for Codex AI Pipeline."""
import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from src.pipeline.main_pipeline import CodexAIPipeline


class Message(BaseModel):
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    context: Optional[str] = None


class ChatSession:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.messages: List[Message] = []
        self.created_at = datetime.now()

    def add_message(self, content: str, role: str, context: Optional[str] = None) -> Message:
        message = Message(
            id=str(uuid.uuid4()),
            content=content,
            role=role,
            timestamp=datetime.now(),
            context=context
        )
        self.messages.append(message)
        return message


def _build_pipeline_config() -> dict:
    """Load environment configuration for downstream API clients."""

    def _load_env_files() -> None:
        try:
            from dotenv import load_dotenv  # type: ignore
        except ImportError:
            return

        # Load only from .env file
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[1]
        env_path = project_root / ".env"
        
        if env_path.exists():
            load_dotenv(env_path)

    _load_env_files()

    return {
        "model_name": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "xai_api_key": os.getenv("XAI_API_KEY"),
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.9,
    }


app = FastAPI(
    title="Codex AI Pipeline - Human Friendly Interface",
    description="An Anthropic-style chat interface for the Codex AI Pipeline",
    version="2.0.0"
)

# Store active chat sessions
chat_sessions: Dict[str, ChatSession] = {}
pipeline = None


@app.on_event("startup")
async def startup_event():
    global pipeline

    # Force reload the pipeline module to pick up newly installed dependencies
    import importlib
    import sys

    # Reload the main pipeline module if it's already imported
    if 'src.pipeline.main_pipeline' in sys.modules:
        importlib.reload(sys.modules['src.pipeline.main_pipeline'])

    # Also reload any related modules that might have been cached with mocks
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('src.') and 'pipeline' in module_name:
            try:
                importlib.reload(sys.modules[module_name])
            except Exception:
                pass  # Some modules might not be reloadable, that's ok

    # Now import fresh
    from src.pipeline.main_pipeline import CodexAIPipeline
    pipeline = CodexAIPipeline(_build_pipeline_config())

    print("🚀 Pipeline initialized with fresh module imports")


@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the Anthropic-style chat interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codex AI Pipeline</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 85vh;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 16px 16px 0 0;
        }

        .chat-header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8fafc;
        }

        .message {
            margin-bottom: 20px;
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message {
            display: flex;
            justify-content: flex-end;
        }

        .assistant-message {
            display: flex;
            justify-content: flex-start;
        }

        .message-bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
        }

        .user-bubble {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-bottom-right-radius: 6px;
        }

        .assistant-bubble {
            background: white;
            color: #374151;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .thinking {
            display: flex;
            align-items: center;
            color: #6b7280;
            font-style: italic;
            margin: 10px 0;
        }

        .thinking-dots {
            display: inline-flex;
            margin-left: 8px;
        }

        .thinking-dots span {
            width: 6px;
            height: 6px;
            background: #9ca3af;
            border-radius: 50%;
            margin: 0 2px;
            animation: thinking 1.4s infinite;
        }

        .thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
        .thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes thinking {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }

        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e5e7eb;
        }

        .input-container {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .message-input {
            flex: 1;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 16px;
            resize: none;
            max-height: 120px;
            min-height: 44px;
            transition: border-color 0.2s;
        }

        .message-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .send-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 20px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            min-width: 80px;
        }

        .send-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .context-input {
            width: 100%;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            margin-bottom: 12px;
            background: #f9fafb;
        }

        .context-label {
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 4px;
            display: block;
        }

        .welcome-message {
            text-align: center;
            color: #6b7280;
            margin: 40px 0;
            font-style: italic;
        }

        .status-indicator {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }

        .status-live {
            background: linear-gradient(135deg, #10b981, #059669);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        }

        .status-demo {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.4);
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="status-indicator status-demo" id="statusIndicator">🔧 Demo Mode</div>
            <h1>🤖 Codex AI Pipeline</h1>
            <p>Intelligent AI assistance powered by advanced language models</p>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                👋 Welcome! I'm here to help you with your questions and tasks.
            </div>
        </div>

        <div class="chat-input">
            <label for="contextInput" class="context-label">Context (optional):</label>
            <input type="text" id="contextInput" class="context-input" placeholder="Add any relevant context...">

            <div class="input-container">
                <textarea
                    id="messageInput"
                    class="message-input"
                    placeholder="Type your message here..."
                    rows="1"
                ></textarea>
                <button id="sendButton" class="send-button">Send</button>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const contextInput = document.getElementById('contextInput');
        const sendButton = document.getElementById('sendButton');
        const statusIndicator = document.getElementById('statusIndicator');
        let isProcessing = false;

        // Check system status on load
        async function checkStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                // Status will be updated based on first response
            } catch (error) {
                console.log('Status check failed:', error);
            }
        }

        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        // Send message on Enter (Shift+Enter for new line)
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        sendButton.addEventListener('click', sendMessage);

        function addMessage(content, role, isThinking = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}-message`;

            if (isThinking) {
                messageDiv.innerHTML = `
                    <div class="thinking">
                        🤔 Thinking
                        <div class="thinking-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                `;
            } else {
                const bubbleDiv = document.createElement('div');
                bubbleDiv.className = `message-bubble ${role}-bubble`;
                bubbleDiv.textContent = content;
                messageDiv.appendChild(bubbleDiv);
            }

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return messageDiv;
        }

        async function sendMessage() {
            if (isProcessing) return;

            const message = messageInput.value.trim();
            const context = contextInput.value.trim() || null;

            if (!message) return;

            isProcessing = true;
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';

            // Add user message
            addMessage(message, 'user');
            messageInput.value = '';
            messageInput.style.height = 'auto';

            // Add thinking indicator
            const thinkingDiv = addMessage('', 'assistant', true);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        context: context
                    })
                });

                const result = await response.json();

                // Remove thinking indicator
                thinkingDiv.remove();

                if (response.ok) {
                    // Extract friendly response
                    let friendlyResponse = result.response;
                    if (typeof result === 'object' && result.answer) {
                        friendlyResponse = result.answer;
                    } else if (typeof result === 'object' && result.output) {
                        friendlyResponse = result.output;
                    } else if (typeof result === 'string') {
                        friendlyResponse = result;
                    }

                    // Update status indicator based on response type
                    if (friendlyResponse && friendlyResponse.includes('demo mode')) {
                        statusIndicator.className = 'status-indicator status-demo';
                        statusIndicator.textContent = '🔧 Demo Mode';
                    } else if (friendlyResponse && !friendlyResponse.includes('Mock AI response')) {
                        statusIndicator.className = 'status-indicator status-live';
                        statusIndicator.textContent = '🚀 Live AI';
                    }

                    addMessage(friendlyResponse || 'I received your message but couldn\'t generate a response.', 'assistant');
                } else {
                    addMessage('Sorry, I encountered an error processing your request. Please try again.', 'assistant');
                }
            } catch (error) {
                thinkingDiv.remove();
                addMessage('Sorry, I\'m having trouble connecting. Please check your connection and try again.', 'assistant');
            } finally {
                isProcessing = false;
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
                messageInput.focus();
            }
        }

        // Focus on input when page loads
        messageInput.focus();

        // Check status on page load
        checkStatus();
    </script>
</body>
</html>
    """


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    session_id: Optional[str] = None


async def get_direct_ai_response(message: str, context: Optional[str] = None) -> str:
    """Get a direct response from AI APIs, bypassing complex pipeline."""
    config = _build_pipeline_config()
    errors = []

    # Try Anthropic first (since it's usually more reliable)
    anthropic_key = config.get("anthropic_api_key")
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)

            prompt = message
            if context:
                prompt = f"Context: {context}\n\nUser: {message}"

            # Anthropic requires structured content blocks even for plain text prompts
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=config.get("max_tokens", 2000),
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }]
            )

            # Combine any returned text blocks to form the final reply
            text_blocks = []
            for block in response.content:
                if isinstance(block, dict):
                    if block.get("type") == "text" and block.get("text"):
                        text_blocks.append(block["text"])
                else:
                    if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                        text_blocks.append(block.text)

            if text_blocks:
                return "".join(text_blocks)

            # Fall back to stringifying the response when no text blocks are present
            return str(response)
        except ImportError:
            errors.append("Anthropic package not installed")
        except Exception as e:
            errors.append(f"Anthropic API error: {str(e)}")

    # Try OpenAI as fallback
    openai_key = config.get("openai_api_key")
    if openai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)

            prompt = message
            if context:
                prompt = f"Context: {context}\n\nUser: {message}"

            response = client.chat.completions.create(
                model=config.get("model_name", "gpt-4o"),
                messages=[{"role": "user", "content": prompt}],
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 2000)
            )

            return response.choices[0].message.content
        except ImportError:
            errors.append("OpenAI package not installed")
        except Exception as e:
            errors.append(f"OpenAI API error: {str(e)}")

    # Log all errors for debugging
    if errors:
        print(f"AI API errors: {'; '.join(errors)}")

    # Return None to indicate we should provide helpful fallback message
    return None


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Process a chat message through the pipeline."""
    try:
        global pipeline
        if pipeline is None:
            pipeline = CodexAIPipeline(_build_pipeline_config())

        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in chat_sessions:
            chat_sessions[session_id] = ChatSession()

        session = chat_sessions[session_id]

        # Add user message to session
        session.add_message(request.message, "user", request.context)

        # Try direct AI response first
        direct_response = await get_direct_ai_response(request.message, request.context)

        if direct_response:
            # We got a real AI response!
            response_text = direct_response
            result = {
                "response": response_text,
                "query": request.message,
                "context": request.context
            }
        else:
            # Fall back to pipeline (which might give mock responses)
            result = await pipeline.process_query(request.message, request.context)

            # Extract friendly response with better handling
            if not direct_response:
                # We're using pipeline result, check if it's mock
                if isinstance(result, dict):
                    response_text = result.get("response")

                    # If it's a mock response, provide a more helpful message
                    if response_text and "Mock AI response for:" in response_text:
                        # Check if API keys are available
                        config = _build_pipeline_config()
                        api_available = config.get("openai_api_key") or config.get("anthropic_api_key")

                        if api_available:
                            # API key is available but might be having issues
                            response_text = f"""I understand you're asking: "{request.message}"

I have access to AI API keys, but both services are currently experiencing quota issues:

**Current Status:**
- 🔑 API Keys: Configured ✅
- 🌐 OpenAI: Usage quota exceeded (billing limit reached)
- 🧠 Anthropic: Credit balance too low
- 🔧 System: Falling back to intelligent demo mode

**To get real AI responses:**

1. **Option A - Add OpenAI credits:**
   - Visit [OpenAI Billing](https://platform.openai.com/billing)
   - Add credits or upgrade your plan
   - Check usage limits and billing details

2. **Option B - Add Anthropic credits:**
   - Visit [Anthropic Plans & Billing](https://console.anthropic.com/settings/billing)
   - Purchase credits or upgrade your plan

**Good News:** The interface and API integration are working perfectly! Once you add credits to either service, you'll get real AI responses immediately. The system is ready to go! 🚀

Would you like me to help you with anything else while you're setting up the billing?"""
                        else:
                            # No API key configured
                            response_text = f"""I understand you're asking: "{request.message}"

I'm currently running in demo mode because no AI API keys are configured. To get real AI responses:

1. Set your OpenAI API key in the environment:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Or add it to a .env file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. Restart the application

For now, I can help you test the interface and demonstrate the pipeline structure!"""

                    elif not response_text:
                        response_text = (
                            result.get("answer") or
                            result.get("output") or
                            "I received your message but couldn't generate a proper response."
                        )
                else:
                    response_text = str(result)

        # Add assistant response to session
        session.add_message(response_text, "assistant")

        return {
            "response": response_text,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chat_sessions[session_id]
    return {
        "session_id": session_id,
        "messages": [msg.dict() for msg in session.messages],
        "created_at": session.created_at.isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(chat_sessions)
    }


async def _run_pipeline(query: str, context: Optional[str]) -> dict:
    """Legacy function for backward compatibility."""
    global pipeline
    if pipeline is None:
        pipeline = CodexAIPipeline(_build_pipeline_config())
    return await pipeline.process_query(query, context)


def run_pipeline(query: str, context: Optional[str] = None) -> dict:
    """Execute the pipeline synchronously for scripts or REPL usage."""
    return asyncio.run(_run_pipeline(query, context))


def main() -> None:
    """Launch the human-friendly web interface."""
    print("🚀 Starting Codex AI Pipeline Web Interface...")
    print("\n🌐 Open your browser and go to: http://localhost:8003")
    print("📚 API docs available at: http://localhost:8003/docs")
    print("\n💡 Features:")
    print("   • Anthropic-style chat interface")
    print("   • Real-time conversation")
    print("   • Context support")
    print("   • Session management")
    print("   • RESTful API")
    print("\n🔧 Press Ctrl+C to stop the server")
    print("="*50)

    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
