from fastapi import FastAPI, Query, HTTPException
from typing import List, Dict, Any
import json
import os
from groq import Groq

app = FastAPI(title="AI-Powered Product Recommendation API")

GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None

# Load processed data
try:
    with open('products_with_tuples.json', 'r') as f:
        products_data = json.load(f)
    
    with open('business_line_tuples.json', 'r') as f:
        business_tuples = json.load(f)
        
    print(f"Loaded {len(products_data)} products and {len(business_tuples)} business line tuples")
    
except Exception as e:
    products_data = []
    business_tuples = []
    print(f"Error loading processed data: {e}")

def get_ai_recommendations_simple(company_name: str, product_name: str, available_products: List[Dict]) -> tuple[List[str], bool]:
    """Use Groq AI to intelligently recommend products based on company and product name"""
    
    if not groq_client:
        # Fallback to simple matching if Groq is not available
        print("❌ Groq client not available, using fallback")
        return simple_recommendation_fallback_simple(company_name, product_name, available_products), False
    
    try:
        print(f"🤖 Using Groq AI for recommendations...")
        # Prepare product information for AI
        product_info = []
        for product in available_products:
            product_info.append(f"ID: {product['id']}, Company: {product['company_name']}, Product: {product['product_line']}")
        
        prompt = f"""
You are a product recommendation expert. Based on the following request, recommend the top 5 most relevant product IDs.

Customer Request:
- Company Name: {company_name}
- Looking for product: {product_name}

Available Products:
{chr(10).join(product_info)}

Recommendation Rules:
1. PRIORITIZE products from the same company ({company_name}) if available
2. Find products that best match the requested product name "{product_name}"
3. Consider exact keyword matches and similar products
4. Return exactly 5 product IDs in order of preference

Please respond with ONLY the 5 product IDs, one per line, no additional text:
"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful product recommendation assistant. Always respond with exactly 5 product IDs, one per line."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # Extract product IDs from response
        ai_response = response.choices[0].message.content
        if ai_response:
            ai_response = ai_response.strip()
        else:
            ai_response = ""
        
        recommended_ids = []
        
        # Create a map of all available product IDs for validation
        valid_ids = {product['id'] for product in available_products}
        
        for line in ai_response.split('\n'):
            line = line.strip()
            # Remove any numbering or extra characters
            line = line.replace('.', '').replace('-', '').replace('*', '').strip()
            
            # Check if this line contains a valid product ID
            if line in valid_ids:
                recommended_ids.append(line)
            else:
                # Try to find a valid ID within the line
                for valid_id in valid_ids:
                    if valid_id in line:
                        recommended_ids.append(valid_id)
                        break
        
        print(f"AI extracted {len(recommended_ids)} valid IDs: {recommended_ids}")
        
        # Ensure we have exactly 5 recommendations
        if len(recommended_ids) < 5:
            # Fill with fallback recommendations that aren't already included
            fallback_ids = simple_recommendation_fallback_simple(company_name, product_name, available_products)
            for fid in fallback_ids:
                if fid not in recommended_ids and len(recommended_ids) < 5:
                    recommended_ids.append(fid)
        
        print(f"✅ AI successfully generated {len(recommended_ids)} recommendations")
        return recommended_ids[:5], True
        
    except Exception as e:
        print(f"❌ Error getting AI recommendations: {e}")
        return simple_recommendation_fallback_simple(company_name, product_name, available_products), False

def simple_recommendation_fallback_simple(company_name: str, product_name: str, available_products: List[Dict]) -> List[str]:
    """Fallback recommendation logic for simplified input"""
    
    print(f"Using fallback logic for company: {company_name}, product: {product_name}")
    print(f"Available products count: {len(available_products)}")
    
    same_company_products = []
    matching_products = []
    other_products = []
    
    product_name_lower = product_name.lower()
    
    for product in available_products:
        product_line_lower = product['product_line'].lower()
        
        # Check if from same company
        is_same_company = product['company_name'].lower() == company_name.lower()
        
        # Check if product matches the requested product name
        is_matching = (
            product_name_lower in product_line_lower or
            any(word in product_line_lower for word in product_name_lower.split())
        )
        
        if is_same_company:
            same_company_products.append(product['id'])
            print(f"Same company product: {product['company_name']} - {product['product_line']}")
        elif is_matching:
            matching_products.append(product['id'])
            print(f"Matching product: {product['company_name']} - {product['product_line']}")
        else:
            other_products.append(product['id'])
    
    # Prioritize same company, then matching products, then others
    recommendations = same_company_products[:5]
    if len(recommendations) < 5:
        recommendations.extend(matching_products[:5-len(recommendations)])
    if len(recommendations) < 5:
        recommendations.extend(other_products[:5-len(recommendations)])
    
    print(f"Final recommendations: {recommendations}")
    return recommendations[:5]

def get_ai_recommendations(company_name: str, business_lines: List[str], available_products: List[Dict]) -> tuple[List[str], bool]:
    """Use Groq AI to intelligently recommend products"""
    
    if not groq_client:
        # Fallback to simple matching if Groq is not available
        print("❌ Groq client not available, using fallback")
        return simple_recommendation_fallback(company_name, business_lines, available_products), False
    
    try:
        print(f"🤖 Using Groq AI for recommendations...")
        # Prepare product information for AI
        product_info = []
        for product in available_products:
            product_info.append(f"ID: {product['id']}, Company: {product['company_name']}, Product: {product['product_line']}")
        
        prompt = f"""
You are a product recommendation expert. Based on the following request, recommend the top 5 most relevant product IDs.

Customer Request:
- Company Name: {company_name}
- Looking for products related to: {', '.join(business_lines)}

Available Products:
{chr(10).join(product_info)}

Recommendation Rules:
1. PRIORITIZE products from the same company ({company_name}) if available
2. If same company products are not available, recommend products that match the business lines exactly (e.g., for "VFD" recommend VFD products, for "Pump" recommend Pump products)
3. Consider exact keyword matches in product names
4. Return exactly 5 product IDs in order of preference

IMPORTANT: For business line "VFD", prioritize products with "VFD" in the name. For "Pump", prioritize products with "Pump" in the name.

Please respond with ONLY the 5 product IDs, one per line, no additional text:
"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Updated to working model
            messages=[
                {"role": "system", "content": "You are a helpful product recommendation assistant. Always respond with exactly 5 product IDs, one per line."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # Extract product IDs from response
        ai_response = response.choices[0].message.content
        if ai_response:
            ai_response = ai_response.strip()
        else:
            ai_response = ""
        
        recommended_ids = []
        
        # Create a map of all available product IDs for validation
        valid_ids = {product['id'] for product in available_products}
        
        for line in ai_response.split('\n'):
            line = line.strip()
            # Remove any numbering or extra characters
            line = line.replace('.', '').replace('-', '').replace('*', '').strip()
            
            # Check if this line contains a valid product ID
            if line in valid_ids:
                recommended_ids.append(line)
            else:
                # Try to find a valid ID within the line
                for valid_id in valid_ids:
                    if valid_id in line:
                        recommended_ids.append(valid_id)
                        break
        
        print(f"AI extracted {len(recommended_ids)} valid IDs: {recommended_ids}")
        
        # Ensure we have exactly 5 recommendations
        if len(recommended_ids) < 5:
            # Fill with fallback recommendations that aren't already included
            fallback_ids = simple_recommendation_fallback(company_name, business_lines, available_products)
            for fid in fallback_ids:
                if fid not in recommended_ids and len(recommended_ids) < 5:
                    recommended_ids.append(fid)
        
        print(f"✅ AI successfully generated {len(recommended_ids)} recommendations")
        return recommended_ids[:5], True
        
    except Exception as e:
        print(f"❌ Error getting AI recommendations: {e}")
        return simple_recommendation_fallback(company_name, business_lines, available_products), False

def simple_recommendation_fallback(company_name: str, business_lines: List[str], available_products: List[Dict]) -> List[str]:
    """Fallback recommendation logic when AI is not available"""
    
    print(f"Using fallback logic for company: {company_name}, business_lines: {business_lines}")
    print(f"Available products count: {len(available_products)}")
    
    same_company_products = []
    other_company_products = []
    related_products = []
    
    for product in available_products:
        product_line_lower = product['product_line'].lower()
        company_name_lower = product['company_name'].lower()
        
        # Check if product is related to business lines
        is_related = any(
            bl.lower() in product_line_lower or 
            bl.lower() in company_name_lower or
            any(keyword in product_line_lower for keyword in [
                'clean', 'sort', 'heat', 'boil', 'pump', 'vfd', 'separator', 'destoner'
            ])
            for bl in business_lines
        )
        
        if product['company_name'].lower() == company_name.lower():
            same_company_products.append(product['id'])
            print(f"Same company product: {product['product_line']}")
        elif is_related:
            related_products.append(product['id'])
            print(f"Related product: {product['company_name']} - {product['product_line']}")
        else:
            other_company_products.append(product['id'])
    
    # Prioritize same company, then related, then others
    recommendations = same_company_products[:5]
    if len(recommendations) < 5:
        recommendations.extend(related_products[:5-len(recommendations)])
    if len(recommendations) < 5:
        recommendations.extend(other_company_products[:5-len(recommendations)])
    
    print(f"Final recommendations: {recommendations}")
    return recommendations[:5]

@app.get("/")
def root():
    companies = list(set(product['company_name'] for product in products_data))
    return {
        "status": "AI-Powered Product Recommendation API",
        "total_products": len(products_data),
        "ai_enabled": groq_client is not None,
        "companies": sorted(companies)
    }

@app.get("/recommend")
def recommend_products(
    company_name: str = Query(..., description="Company name seeking recommendations"),
    product_name: str = Query(..., description="Product name or type you're looking for")
):
    """
    Get AI-powered product recommendations based on company name and product name.
    Returns top 5 recommended products.
    """
    if not products_data:
        raise HTTPException(status_code=500, detail="No product data available")
    
    # Filter relevant products based on product name
    relevant_products = []
    for product in products_data:
        product_line_lower = product['product_line'].lower()
        product_name_lower = product_name.lower()
        
        # Include products that match the product name or have similar keywords
        is_relevant = (
            product_name_lower in product_line_lower or
            any(word in product_line_lower for word in product_name_lower.split()) or
            product['company_name'].lower() == company_name.lower()
        )
        
        if is_relevant:
            relevant_products.append(product)
    
    print(f"Found {len(relevant_products)} relevant products out of {len(products_data)} total")
    
    if not relevant_products:
        # If no direct matches, include all products for broader recommendation
        relevant_products = products_data
        print("No specific matches found, using all products for recommendation")
    
    # Get AI recommendations
    recommended_ids, ai_used = get_ai_recommendations_simple(company_name, product_name, relevant_products)
    
    # Get full product details for recommended IDs
    recommended_products = []
    for pid in recommended_ids:
        for product in products_data:
            if product['id'] == pid:
                recommended_products.append({
                    "id": product['id'],
                    "company_name": product['company_name'],
                    "product_line": product['product_line']
                })
                break
    
    return {
        "request": {
            "company_name": company_name,
            "product_name": product_name
        },
        "recommendations": recommended_products,
        "total_recommendations": len(recommended_products),
        "ai_used": ai_used,
        "method": "🤖 Groq AI" if ai_used else "⚙️ Fallback Logic"
    }

@app.get("/recommend-ai")
def recommend_with_ai(
    company_name: str = Query(..., description="Company name seeking recommendations"),
    business_lines: List[str] = Query(..., description="List of business lines of interest")
):
    """
    Get AI-powered product recommendations with company preference prioritization.
    Returns top 5 recommended products.
    """
    if not products_data:
        raise HTTPException(status_code=500, detail="No product data available")
    
    # Filter relevant products - be more inclusive in the search
    relevant_products = []
    for product in products_data:
        product_line_lower = product['product_line'].lower()
        company_name_lower = product['company_name'].lower()
        
        # Include products that:
        # 1. Match business lines directly
        # 2. Are from the same company
        # 3. Have related keywords
        is_relevant = (
            any(bl.lower() in product_line_lower for bl in business_lines) or
            any(bl.lower() in company_name_lower for bl in business_lines) or
            product['company_name'].lower() == company_name.lower() or
            any(keyword in product_line_lower for keyword in [
                'clean', 'sort', 'heat', 'boil', 'pump', 'vfd', 'separator', 'destoner',
                'spare', 'equipment', 'machine', 'generator', 'cooler', 'steam'
            ])
        )
        
        if is_relevant:
            relevant_products.append(product)
    
    print(f"Found {len(relevant_products)} relevant products out of {len(products_data)} total")
    
    if not relevant_products:
        # If no direct matches, include all products for broader recommendation
        relevant_products = products_data
        print("No specific matches found, using all products for recommendation")
    
    # Get AI recommendations
    recommended_ids, ai_used = get_ai_recommendations(company_name, business_lines, relevant_products)
    
    # Get full product details for recommended IDs
    recommended_products = []
    for pid in recommended_ids:
        for product in products_data:
            if product['id'] == pid:
                recommended_products.append({
                    "id": product['id'],
                    "company_name": product['company_name'],
                    "product_line": product['product_line']
                })
                break
    
    return {
        "request": {
            "company_name": company_name,
            "business_lines": business_lines
        },
        "recommendations": recommended_products,
        "total_recommendations": len(recommended_products),
        "ai_used": ai_used,
        "method": "🤖 Groq AI" if ai_used else "⚙️ Fallback Logic"
    }

@app.get("/business-tuples")
def get_business_tuples():
    """Get all available business line tuples (company, product_line)"""
    return {"business_tuples": business_tuples, "total": len(business_tuples)}

@app.get("/companies")
def get_companies():
    """Get all available companies"""
    companies = list(set(product['company_name'] for product in products_data))
    return sorted(companies)

@app.get("/products/{company_name}")
def get_products_by_company(company_name: str):
    """Get all products for a specific company"""
    company_products = [
        product for product in products_data 
        if product['company_name'].lower() == company_name.lower()
    ]
    return {
        "company": company_name,
        "products": company_products,
        "total": len(company_products)
    }
