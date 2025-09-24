from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackIntegration:
    def __init__(self, token: str):
        self.client = WebClient(token=token)
    
    def send_message(self, channel: str, text: str):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text
            )
            return response
        except SlackApiError as e:
            print(f"Error: {e}")
