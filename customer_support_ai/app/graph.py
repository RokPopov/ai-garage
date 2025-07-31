import time
import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from .classifier import TicketClassifier

class TicketState(TypedDict):
    message: str
    category: str | None
    error: str | None
    api_key: str | None
    model_name: str
    temperature: float

def classify_node(state: TicketState) -> TicketState:
    """Core classification logic."""
    print(f"Processing: '{state['message'][:50]}...'")
    start_time = time.time()
    
    try:
        api_key = state.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key is required")

        classifier = TicketClassifier(
            api_key=api_key,
            model_name=state.get("model_name", "gpt-4.1"),
            temperature=state.get("temperature", 0.1)
        )
        result = classifier.classify(state["message"])
        
        processing_time = time.time() - start_time
        print(f"Category: {result.category} ({processing_time:.2f}s)")
        
        return {
            **state,
            "category": result.category,
            "error": None
        }
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Error: {str(e)} ({processing_time:.2f}s)")
        return {
            **state,
            "category": None,
            "error": str(e)
        }

def build_classification_graph():
    """Build the LangGraph workflow."""
    graph = StateGraph(TicketState)
    graph.add_node("classify", classify_node)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", END)
    return graph.compile()

def classify_ticket(message: str, api_key: str | None = None, model_name: str = "gpt-4.1", temperature: float = 0.1) -> str:
    """Classify a ticket using LangGraph workflow."""
    graph = build_classification_graph()

    initial_state = {
        "message": message,
        "category": None,
        "error": None,
        "api_key": api_key,
        "model_name": model_name,
        "temperature": temperature
    }

    result = graph.invoke(initial_state)
    
    if result.get("error"):
        raise Exception(f"Classification failed: {result['error']}")
        
    return result["category"]
