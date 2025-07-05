def classify_customer_support_ticket(customer_message: str) -> str:
    return f"""
    You are an expert customer support ticket router for a ecommerce brand.

    Your goal is to analyze the provided customer support ticket and classify it based on the criteria below:

    Labels + Criteria
    1. Shipping_Tracking  - delivery ETA, tracking code, carrier delays
    2. Order_Issue        - wrong/missing/damaged item, double charge
    3. Product_Question   - specs, sizing, how-to-use
    4. Website_Issue      - checkout bug, login fail, 500 errors
    5. Other              - sponsorship, wholesale, anything else

    Customer support ticket: {customer_message}
    """