from enum import Enum
from pydantic import BaseModel, ConfigDict

class TicketCategory(str, Enum):
    SHIPPING_TRACKING = "Shipping & Tracking"
    ORDER_ISSUE = "Order Issue (Missing, Damaged, Wrong Item)" 
    PRODUCT_QUESTION_ONLINE = "Product Question - Bought Online"
    PRODUCT_QUESTION_STORE = "Product Question - Bought In Store"
    WHOLESALE_INQUIRY = "Wholesale Inquiry"
    COLLAB_SPONSORSHIP = "Collab or Sponsorship"
    WEBSITE_TECH_ISSUE = "Website or Tech Issue"
    SOMETHING_ELSE = "Something Else"

class TicketClassification(BaseModel):
    category: TicketCategory
    
    model_config = ConfigDict(use_enum_values=True)
