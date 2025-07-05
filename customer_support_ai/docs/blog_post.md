## 1. Hook: "How We Cut Misrouted Tickets by 94% Using 73 Lines of Python (No Fine-Tuning Required)"

~300 words - Results-first opening with specific metrics

## 2. The Client's Failed Evolution: Why More Instructions Made Everything Worse

~400 words - The failure story showing their 4 attempts

## 3. The Structured Output Solution: Pydantic + Instructor for Bulletproof Classification

~400 words - Core technical implementation with code (SIMPLIFIED)

## 4. Real Categories, Real Code: Our Production-Ready Implementation

~300 words - Actual classification categories and working examples (SIMPLIFIED)

## 5. Beyond Classification: How This Powers Your Entire AI Stack

~200 words - Connection to Post 1's 6-step approach

---
## JASON LIU STYLE ANALYSIS & RECOMMENDATIONS

### **Recommended Headlines (5 sections, ~1700 words):**

#### **1. Hook: "How We Cut Misrouted Tickets by 94% Using 73 Lines of Python (No Fine-Tuning Required)"**

*~300 words - Results-first opening with specific metrics*

*Pain point context*
Most support teams drown in misrouted tickets - 127 per week on average for one specific business.

Their engineering team had tried everything: detailed prompts, complex rules, even outlined best fine-tuning approaches.

Nothing worked consistently. They were solving the wrong problem.

*Twist*
Instead of building a smarter chatbot, we built a structured data pipeline.

No training data. No fine-tuning. No complex prompt engineering.

Just 3 Python files that forced the AI to give us exactly what we needed, every single time.

*Proof / teaser*
Within one week: 127 weekly misroutes dropped to 8.

Here's how we did it and why every other approach fails.

#### **2. The Failed Prompt Evolution: Why More Instructions Made Everything Worse**
*~400 words - The failure story showing their 4 attempts*

The engineering team at this e-commerce company wasn't naive.
They'd read the prompt engineering guides. Started with best practices.
But their systematic approach to "fixing" classification accuracy reveals the trap that catches most technical teams.

##### The Prompt Evolution Story:

**Attempt 1: The Standard Starting Point**

Their first classification prompt was straightforward:

```
You are an expert customer support ticket router for a ecommerce brand.

Return ONLY the category name from this list:

• Shipping & Tracking  
• Order Issue  
• Product Question  
• Website / Tech Issue  
• Other  

Ticket: {{customer_message}}
```

It worked... sort of.

The obvious cases got classified correctly. But edge cases were inconsistent. Sometimes [TODO]"My bat arrived cracked"[TODO] went to Product Questions, sometimes to Order Issues.

The support team kept finding tickets in the wrong queues.

**Attempt 2: Adding Detail (The Logical Next Step)**

Their solution seemed obvious: be more specific, spell more criteria.

```
You are an expert customer support ticket router for a ecommerce brand.

Your goal is to analyze the provided customer support ticket and classify it based on the criteria below:

Labels + Criteria
1. Shipping_Tracking  – delivery ETA, tracking code, carrier delays
2. Order_Issue        – wrong/missing/damaged item, double charge
3. Product_Question   – specs, sizing, how-to-use
4. Website_Issue      – checkout bug, login fail, 500 errors
5. Other              – sponsorship, wholesale, anything else

Ticket: {{body}}
```

This helped with some edge cases.

But created new problems. "I ordered a large glove but received a medium, and it's also cracked" now bounced between Order Issues and Product Questions inconsistently.

The LLM was overthinking simple cases while still missing nuanced ones.

**Attempt 3: The Kitchen Sink Approach**

Goal: Throw EVERYTHING in - subcategories, decision rules, chain-of-thought:

```
YOUR GOAL
• Map every ticket to one of five enums
  1) SHIPPING_TRACKING
  2) ORDER_ISSUE
  3) PRODUCT_QUESTION
  4) WEBSITE_ISSUE
  5) OTHER

PIPELINE (run in order)
1. Context Scan
   – detect sentiment, urgency words, order-IDs, channel (email/chat/phone)
2. Scoring Engine
   – keyword & pattern match (see TRIGGERS below) → score 0-100
   – thresholds: 85/80/75/70/60 by enum order
3. Tie-Breaker Matrix
   – primary intent (40 %), urgency (25 %), complexity (20 %), customer tier (15 %)
4. Quality Gate
   – if confidence < 0.70 OR top-2 scores Δ < 10 → flag_review = true
5. Output strict JSON (no extra fields)

TRIGGERS (abbrev.)
SHIPPING_TRACKING   “tracking” “delivery” “carrier”  /  10-20 chr alphanum
ORDER_ISSUE         “broken” “missing” “charged twice” “wrong size”
PRODUCT_QUESTION    “fit” “compatible” “how to” “spec”
WEBSITE_ISSUE       “checkout fail” “login” “404” “app crash”
OTHER               wholesale | jobs | policy | legal

JSON SCHEMA
{
  "classification": "<ENUM>",
  "confidence_score": <0-1 float>,
  "primary_intent": "<short text>",
  "secondary_intents": ["<opt>"],
  "urgency_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "sentiment": "SATISFIED|NEUTRAL|DISSATISFIED|FRUSTRATED",
  "flag_review": <true|false>,
  "reason": "<max 25 words>",
  "ts": "<auto>"
}

RULES
• Shipping overrides Product defects unless defect blamed on manufacturer.
• Multiple issues? choose highest business impact.
• Never invent new enums.

NOW CLASSIFY THIS TICKET:
{{message}}
```

The prompt became a 200-word monster.

Result: The AI got more confused, not more accurate.

Simple "Where's my order?" inquiries took longer to process. "I bought this glove at your Shopify store, it's too small" got classified as Website Issues because the prompt mentioned online purchases.

**Attempt 4: Rules and Validation**

Their final attempt: strict constraints.

```
Use ONLY these exact category names. If the ticket mentions both shipping and product issues, prioritize shipping. If uncertain, explain why. Always consider whether the purchase was online or in-store...
```

Now they had a different problem: the AI spent more time explaining its uncertainty than actually classifying.

"Customer bought a bat online, it arrived damaged, wants to exchange for different size" came back with a paragraph explaining why this could be shipping, order issues, or product questions.

The engineering team realized they'd made the system slower and less reliable, not better.

##### Expert Analysis
Here's the pattern I see repeatedly:

**The Fundamental Misunderstanding:**
They treated this as a prompt engineering problem when it's actually a structured data problem.

**Why More Instructions Made It Worse:**
Each additional instruction created new ways for the AI to get confused or overthink simple cases.

**The Real Issue:**
LLMs are designed for creative text generation, not consistent categorical outputs.

Adding complexity amplifies their natural inconsistency.

**What They Actually Needed:**
- Forced structured outputs (not text generation)
- Clear constraints (not flexible reasoning)
- Simple categories (not complex decision trees)

That's when we realized they weren't solving a prompt engineering problem.

They were solving a data structure problem.

#### **3. The Structured Output Solution: Pydantic + Instructor for Bulletproof Classification**
*~400 words - Core technical implementation with code*

The breakthrough wasn't smarter prompts.

It was forcing the AI to give us exactly what we needed, every single time.

Instead of asking the AI to "classify and explain," we made it impossible for the AI to return anything except one of our predefined categories.

Here's the complete implementation.

**The Core Concept**

The key insight: treat classification as a data validation problem, not a text generation problem.

Instead of this (what everyone tries):
"Please classify this ticket and explain your reasoning..."

We do this:
"Return a TicketClassification object with category field containing exactly one of these enum values."

The AI literally cannot return anything else.

**The Implementation**

Step 1: Define Your Categories
```python
class TicketCategory(str, Enum):
   SHIPPING_TRACKING = "Shipping & Tracking"
   ORDER_ISSUE = "Order Issue (Missing, Damaged, Wrong Item)"
   PRODUCT_ISSUE_ONLINE = "Product Issue or Question – Bought on Sluggers.com"
   PRODUCT_ISSUE_STORE = "Product Issue or Question – Bought in Store or at Event"
   WHOLESALE_INQUIRY = "Wholesale Inquiry"
   COLLAB_SPONSORSHIP = "Collab or Sponsorship"
   WEBSITE_TECH_ISSUE = "Website or Tech Issue"
   OTHER = "Other"

class TicketClassification(BaseModel):
    category: TicketCategory
```
Key Principles:
Constraint over creativity - AI can't deviate from our structure
Validation over instruction - Pydantic catches errors, not prompts
Real categories over generic ones - Use your actual CSV data
Simple over complex - Minimal prompt, maximum structure


Step 2: Create the Classification Model
```python
# [CODE PLACEHOLDER 2: Your complete Pydantic model]
```

Step 3: The Classification Function
```python
# [CODE PLACEHOLDER 3: Your instructor-powered classification function]
```

**Why This Works**

**Constraint Forces Consistency:**
The AI cannot return "Product Question" vs "product_questions" vs "PRODUCT_QUESTIONS"
It must return exactly `TicketCategory.PRODUCT`

**Validation Catches Errors:**
If the AI tries to return an invalid category, Pydantic throws an error
We catch it and handle it

**The Results**

Same ticket, same classification, every time.

No more "Product Question" vs "product_questions" chaos.
No more overthinking simple cases.
No more verbose explanations nobody reads.

Just reliable, fast, structured classification that builds the foundation for everything else.

**What Makes This Different**

Most approaches: Try to make the AI smarter
Our approach: Make the problem simpler

Most approaches: Add more instructions
Our approach: Add more constraints

This is why it works in production when prompt engineering fails.

#### **4. Real Categories, Real Code: Our Production-Ready Implementation**
*~300 words - Actual classification categories and working examples*

Generic examples don't help you implement this in your business.

Here's the actual implementation we used for the e-commerce client.

Here's the actual implementation we used for the e-commerce client, with their real support categories and edge cases.

*The Real Business Categories*
Most tutorials show you "spam vs not spam" or "positive vs negative sentiment."

That's useless for customer support.

Here are the actual categories this e-commerce company needed:

```python
class TicketCategory(str, Enum):
    SHIPPING_TRACKING = "Shipping & Tracking"
    ORDER_ISSUE = "Order Issue (Missing, Damaged, Wrong Item)"
    PRODUCT_ISSUE_ONLINE = "Product Issue or Question – Bought on Sluggers.com"
    PRODUCT_ISSUE_STORE = "Product Issue or Question – Bought in Store or at Event"
    WHOLESALE_INQUIRY = "Wholesale Inquiry"
    COLLAB_SPONSORSHIP = "Collab or Sponsorship"
    WEBSITE_TECH_ISSUE = "Website or Tech Issue"
    SOMETHING_ELSE = "Something Else"
```

**Real Ticket Examples**

Here's what actual classification looks like:

**Example 1: Clear Case**
Customer: "I was charged twice for order #12345"
```python
# [CODE PLACEHOLDER 2: Show classification result]
```

**Example 2: Edge Case**  
Customer: "My phone case arrived cracked and doesn't fit my phone"
```python
# [CODE PLACEHOLDER 3: Show how edge case gets resolved]
```

**The Distribution Secret**

Your examples should match your real ticket volume.

This company's actual distribution:
- 40% Shipping & Tracking (where's my order, delivery issues)
- 25% Order Issues (missing, damaged, wrong items)
- 15% Product Issues - Online (questions about online purchases)
- 8% Product Issues - Store (questions about in-store purchases)
- 5% Website/Tech Issues (app bugs, website problems)
- 4% Something Else (miscellaneous inquiries)
- 2% Wholesale Inquiries (B2B requests)
- 1% Collab/Sponsorship (partnership requests)

```python
# [CODE PLACEHOLDER 4: How you structure examples to match distribution]
```

That's it. 

No complex logic. No fancy features. Just reliable classification.

This gives you the labeled data you need for Step 2: Automatic Routing.

#### **5. Beyond Classification: How This Powers Your Entire AI Stack**
*~200 words - Connection to Post 1's 6-step approach*

This isn't just about classification.

It's about building the foundation for your entire AI system.

**What This Enables:**

Step 2: Automatic Routing (you have clean categories)
Step 3: Thread Summarization (you know ticket types)
Step 4: Data Enrichment (you can pull relevant context)
Step 5: Translations (you understand ticket intent)
Step 6: Suggested Replies (you have all the context)

**The Compound Effect:**

Week 1: Clean classification
Week 2: Perfect routing
Week 3: Context-aware summaries
Week 4: Intelligent data pulling
Week 5: Accurate translations
Week 6: Suggested replies that actually work

Each step builds on the last.

But it all starts with reliable classification.

**Next Steps:**

Download the complete code implementation.
Test it with your actual tickets.
See the results in your first week.

Then move to Step 2: Automatic Routing.

The systematic approach that actually works.
