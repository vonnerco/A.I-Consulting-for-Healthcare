import sys
import os
from typing import Optional

# Ensure project root is importable for `src` and `config`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from src.pipeline.main_pipeline import CodexAIPipeline


def _build_pipeline_config() -> dict:
    return {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
    }


app = FastAPI(title="Codex AI Pipeline API")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve a minimal UI for humans to explore the pipeline easily."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Codex AI Pipeline</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            :root {
                color-scheme: light dark;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }
            body {
                margin: 0;
                padding: 2.5rem 1rem;
                background: #f5f5f7;
                color: #1f2933;
            }
            main {
                max-width: 940px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 16px;
                box-shadow: 0 20px 60px -24px rgba(15, 23, 42, 0.4);
                padding: 2.5rem;
            }
            h1 {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
            p.description {
                margin-top: 0;
                margin-bottom: 1.5rem;
                color: #4b5563;
            }
            form {
                display: grid;
                gap: 1rem;
                margin-bottom: 2.5rem;
            }
            label {
                font-weight: 600;
                letter-spacing: 0.02em;
            }
            textarea {
                resize: vertical;
                min-height: 140px;
                padding: 0.75rem;
                font-size: 1rem;
                border-radius: 12px;
                border: 1px solid #d1d5db;
                background: #f9fafb;
                color: inherit;
            }
            button {
                justify-self: start;
                background: #2563eb;
                color: #ffffff;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 999px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s ease;
            }
            button:hover {
                background: #1d4ed8;
            }
            button:disabled {
                background: #9ca3af;
                cursor: wait;
            }
            section.output {
                display: grid;
                gap: 1rem;
            }
            .panel {
                background: #0b1727;
                color: #f8fafc;
                border-radius: 12px;
                padding: 1.25rem;
                overflow: auto;
                max-height: 320px;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-family: "SFMono-Regular", Menlo, Consolas, monospace;
                font-size: 0.95rem;
            }
            .panel.light {
                background: #f8fafc;
                color: #0f172a;
                border: 1px solid #e2e8f0;
            }
            .panels {
                display: grid;
                gap: 1rem;
            }
            @media (min-width: 840px) {
                .panels {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }
        </style>
    </head>
    <body>
        <main>
            <h1>Codex AI Pipeline</h1>
            <p class="description">
                Send a prompt to the pipeline and review both a clean summary and the raw JSON reply.
            </p>
            <form id="query-form">
                <div>
                    <label for="query-input">Prompt to analyse</label>
                    <textarea id="query-input" name="query" placeholder="Ask a question or describe a task" required></textarea>
                </div>
                <div>
                    <label for="context-input">Optional context</label>
                    <textarea id="context-input" name="context" placeholder="Add any additional context (optional)"></textarea>
                </div>
                <button type="submit" id="submit-btn">Run Pipeline</button>
            </form>
            <section class="output">
                <div class="panels">
                    <div>
                        <h2>Human friendly response</h2>
                        <div id="output-text" class="panel light">Your results will appear here.</div>
                    </div>
                    <div>
                        <h2>Raw JSON response</h2>
                        <div id="output-json" class="panel">Waiting for a response.</div>
                    </div>
                </div>
            </section>
        </main>
        <script>
            const form = document.getElementById("query-form");
            const submitButton = document.getElementById("submit-btn");
            const outputText = document.getElementById("output-text");
            const outputJson = document.getElementById("output-json");

            function setLoading(isLoading) {
                submitButton.disabled = isLoading;
                submitButton.textContent = isLoading ? "Running..." : "Run Pipeline";
            }

            function extractFriendlyText(data) {
                if (!data) {
                    return "No response data available.";
                }

                if (typeof data === "string") {
                    return data;
                }

                if (data.answer) {
                    return data.answer;
                }

                if (data.response) {
                    return data.response;
                }

                if (data.output) {
                    return data.output;
                }

                return JSON.stringify(data, null, 2);
            }

            form.addEventListener("submit", async (event) => {
                event.preventDefault();
                setLoading(true);
                outputText.textContent = "Request sent. Awaiting response...";
                outputJson.textContent = "...";

                const payload = {
                    query: document.getElementById("query-input").value,
                    context: document.getElementById("context-input").value.trim() || null
                };

                try {
                    const response = await fetch("/query", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });

                    if (!response.ok) {
                        const message = await response.text();
                        throw new Error(message || "Unexpected server error.");
                    }

                    const data = await response.json();
                    outputJson.textContent = JSON.stringify(data, null, 2);
                    outputText.textContent = extractFriendlyText(data);
                } catch (error) {
                    outputText.textContent = "Error: " + error.message;
                    outputJson.textContent = "No JSON available.";
                } finally {
                    setLoading(false);
                }
            });
        </script>
    </body>
    </html>
    """


@app.on_event("startup")
def _init_pipeline():
    # Initialize once per process to avoid heavy per-request setup
    app.state.pipeline = CodexAIPipeline(_build_pipeline_config())


class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None


@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        pipeline: CodexAIPipeline = getattr(app.state, "pipeline", None)
        if pipeline is None:
            pipeline = CodexAIPipeline(_build_pipeline_config())
            app.state.pipeline = pipeline

        result = await pipeline.process_query(request.query, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
