import os
import sys
from pathlib import Path
from dotenv import load_dotenv


project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "app"))

  # noqa: E402
load_dotenv()

from app.graph import classify_ticket  # noqa: E402

def run():
    tests = [
        ("Where is my package? It was supposed to arrive last week.", "Shipping & Tracking", "shipping"),
        ("My item arrived broken and missing the manual", "Order Issue (Missing, Damaged, Wrong Item)", "order_issue"),
        ("I bought this online but I'm not sure how to use it properly", "Product Question - Bought Online", "product_question"),
        ("Hello, I was wanting to inquire about any wholesale opportunities you may have", "Wholesale Inquiry", "wholesale"),
        ("The checkout button isn't working and I can't complete my order", "Website or Tech Issue", "website_issue"),
        ("I'm a content creator and would love to collaborate with your brand", "Collab or Sponsorship", "collaboration"),
    ]
    
    results = {}
    all_passed = True
    
    for message, expected, test_name in tests:
        result = classify_ticket(message)
        passed = result == expected
        results[test_name] = {"result": result, "passed": passed}
        if not passed:
            all_passed = False
    
    return results, all_passed

if __name__ == "__main__":
    print("Running Classification Assertion Tests\n")
    results, all_passed = run()
    
    print("\n" + "="*50)
    print("📊 FINAL RESULTS")
    print("="*50)
    
    for test_name, test_result in results.items():
        status = "✅ PASS" if test_result["passed"] else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {test_result['result']} - {status}")
    
    print(f"\n🎉 All {len(results)} tests passed!" if all_passed else "❌ Some tests failed")