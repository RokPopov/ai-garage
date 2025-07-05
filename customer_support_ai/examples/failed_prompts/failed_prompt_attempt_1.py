def classify_customer_support_ticket(customer_message: str) -> str:
    return """
    You are an expert customer support ticket router for a ecommerce brand.

    Return ONLY the category name from this list:

    • Shipping & Tracking  
    • Order Issue  
    • Product Question  
    • Website / Tech Issue  
    • Other  

    Ticket: {{customer_message}}
    """