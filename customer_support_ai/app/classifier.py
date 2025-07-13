import instructor
from openai import OpenAI
from .models import TicketClassification

class TicketClassifier:
    """Structured ticket classification using Instructor + Pydantic."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.1) -> None:
        self.client = instructor.from_openai(
            OpenAI(api_key=api_key),
            mode=instructor.Mode.TOOLS
        )
        self.model_name = model_name
        self.temperature = temperature
        
    def classify(self, ticket_message: str) -> TicketClassification:
        """Classify a single support ticket."""
        return self.client.chat.completions.create(
            model=self.model_name,
            response_model=TicketClassification,
            messages=[
                {"role": "system", "content": "Classify this customer support ticket into the most appropriate category."},
                {"role": "user", "content": f"Classify this customer support ticket:\n\n{ticket_message}"}
            ],
            temperature=self.temperature,
        )
    
    def batch_predict(self, tickets: list[str]) -> list[TicketClassification]:
        """Classify multiple tickets in batch."""
        return [self.classify(ticket) for ticket in tickets]
