from prometheus_client import Counter, Histogram, start_http_server
import time

class PipelineMonitor:
    def __init__(self):
        self.request_count = Counter('llm_requests_total', 'Total LLM requests')
        self.response_time = Histogram('llm_response_time_seconds', 'LLM response time')
        start_http_server(8000)
    
    def track_request(self, func):
        def wrapper(*args, **kwargs):
            self.request_count.inc()
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            self.response_time.observe(time.time() - start_time)
            return result
        return wrapper
