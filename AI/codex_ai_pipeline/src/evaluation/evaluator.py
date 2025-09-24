from langsmith import Client
from langchain.evaluation import load_evaluator
import wandb

class PipelineEvaluator:
    def __init__(self):
        self.client = Client()
        self.evaluator = load_evaluator("qa")
        wandb.init(project="codex-ai-pipeline")
    
    def evaluate_response(self, question: str, answer: str, reference: str):
        result = self.evaluator.evaluate_strings(
            prediction=answer,
            reference=reference,
            input=question
        )
        
        # Log to wandb
        wandb.log({
            "question": question,
            "answer": answer,
            "score": result["score"]
        })
        
        return result
