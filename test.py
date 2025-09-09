import requests
import json

def test_api():
    """Simple test for the Product Recommendation API"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Product Recommendation API")
    print("=" * 40)
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        result = response.json()
        print(f"✅ API Status: {result['message']}")
        print(f"📊 Total Products: {result['total_products']}")
        print(f"🤖 AI Enabled: {result['ai_enabled']}")
        
        # Test companies
        response = requests.get(f"{base_url}/companies")
        companies = response.json()['companies']
        print(f"🏢 Companies: {', '.join(companies)}")
        
        # Test recommendation for same company
        params = {
            "company_name": "Fowler",
            "business_lines": ["Cleaning", "Sorting"]
        }
        response = requests.get(f"{base_url}/recommend-ai", params=params)
        result = response.json()
        
        print(f"\n🎯 Recommendation Test (Same Company):")
        print(f"   Company: {params['company_name']}")
        print(f"   Business Lines: {params['business_lines']}")
        print(f"   Method: {result.get('method', 'Unknown')}")
        print(f"   Recommendations: {result['total_recommendations']}")
        
        for i, rec in enumerate(result['recommendations'][:3], 1):
            same_company = "✓" if rec['is_same_company'] else "✗"
            print(f"   {i}. [{same_company}] {rec['company_name']} - {rec['product_line']}")
        
        # Test cross-company recommendation
        params = {
            "company_name": "TechCorp",
            "business_lines": ["VFD", "Pump"]
        }
        response = requests.get(f"{base_url}/recommend-ai", params=params)
        result = response.json()
        
        print(f"\n🎯 Recommendation Test (Cross-Company):")
        print(f"   Company: {params['company_name']}")
        print(f"   Business Lines: {params['business_lines']}")
        print(f"   Method: {result.get('method', 'Unknown')}")
        print(f"   Recommendations: {result['total_recommendations']}")
        
        for i, rec in enumerate(result['recommendations'][:3], 1):
            same_company = "✓" if rec['is_same_company'] else "✗"
            print(f"   {i}. [{same_company}] {rec['company_name']} - {rec['product_line']}")
        
        print(f"\n✅ All tests passed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running!")
        print("💡 Start the server with: python -m uvicorn main:app --reload --port 8001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
