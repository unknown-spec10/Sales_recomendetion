"""
Updated main.py to use PostgreSQL database
"""

from fastapi import FastAPI, Query, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
from groq import Groq
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI-Powered Product Recommendation API", 
              description="API to recommend products using AI with PostgreSQL backend")

# Get Groq API key from environment variables (SECURE)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("⚠️ WARNING: GROQ_API_KEY not found in environment variables")
    print("   Please set GROQ_API_KEY in your .env file or environment")
    print("   The API will run with limited functionality (fallback mode only)")

# Initialize Groq client
try:
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI client initialized successfully")
    else:
        groq_client = None
        print("⚠️ Groq AI client not initialized - no API key provided")
except Exception as e:
    print(f"❌ Error initializing Groq client: {e}")
    groq_client = None

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'sales_recommendation'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Database connection pool
db_pool = None

async def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(**DB_CONFIG, min_size=5, max_size=20)
        print("✅ Database connection pool initialized")
        return True
    except Exception as e:
        print(f"❌ Database pool initialization failed: {e}")
        return False

async def get_db_connection():
    """Get database connection from pool"""
    if not db_pool:
        await init_db_pool()
    if db_pool:
        return db_pool.acquire()
    else:
        raise Exception("Database pool not available")

async def get_companies_from_db():
    """Get all companies from database"""
    if not db_pool:
        await init_db_pool()
    if not db_pool:
        return []
        
    async with db_pool.acquire() as conn:
        try:
            companies = await conn.fetch("SELECT DISTINCT name FROM companies ORDER BY name LIMIT 100")
            return [row['name'] for row in companies]
        except Exception as e:
            print(f"❌ Error fetching companies: {e}")
            return []

async def get_products_from_db():
    """Get all products from database"""
    if not db_pool:
        await init_db_pool()
    if not db_pool:
        return []
        
    async with db_pool.acquire() as conn:
        try:
            # First try to get real products from database
            products = await conn.fetch("""
                SELECT p.id, c.name as company_name, p.product_line, p.description
                FROM products p 
                JOIN companies c ON p.company_id = c.id 
                WHERE p.is_active = true
                ORDER BY c.name, p.product_line
                LIMIT 10000
            """)
            
            if products:
                # Convert to format expected by recommendation logic
                product_list = []
                for product in products:
                    product_list.append({
                        "id": str(product['id']),
                        "company_name": product['company_name'],
                        "product_line": product['product_line'],
                        "description": product.get('description', ''),
                        "tuple": [product['company_name'], product['product_line']]
                    })
                
                print(f"✅ Loaded {len(product_list)} real products from database")
                return product_list
            else:
                print("⚠️ No products found in database, creating mock products")
                return await create_mock_products_fallback(conn)
                
        except Exception as e:
            print(f"❌ Error loading products: {e}")
            return await create_mock_products_fallback(conn)

async def create_mock_products_fallback(conn):
    """Create mock products as fallback only"""
    try:
        print("⚠️ Falling back to mock products - using company data")
        # Since products table might be empty, let's create mock products from companies
        companies = await conn.fetch("SELECT name FROM companies ORDER BY name LIMIT 50")
        
        # Create mock product data structure similar to original JSON
        mock_products = []
        product_lines = [
            "VFD", "VFD Spares", "Pump", "Pump Spares", "Heater", "Boiler", 
            "Cleaner", "Sorter", "Heat Pump", "Steam Boiler", "Cooling",
            "Heating", "Water", "Chemical", "Environmental"
        ]
        
        for i, company in enumerate(companies):
            # Add 2-3 products per company
            for j, product_line in enumerate(product_lines[:3]):
                mock_products.append({
                    "id": f"mock_{i}_{j}",
                    "company_name": company['name'],
                    "product_line": f"{product_line}",
                    "tuple": [company['name'], product_line]
                })
        
        return mock_products
    except Exception as e:
        print(f"❌ Error creating mock products: {e}")
        return []

async def search_products_in_db(company_name: Optional[str] = None, product_name: Optional[str] = None):
    """Search products in database"""
    if not db_pool:
        await init_db_pool()
    if not db_pool:
        return []
        
    async with db_pool.acquire() as conn:
        try:
            # For now, use mock data since products table is empty
            all_products = await get_products_from_db()
            
            if company_name:
                filtered = [p for p in all_products if company_name.lower() in p['company_name'].lower()]
            elif product_name:
                filtered = [p for p in all_products if product_name.lower() in p['product_line'].lower()]
            else:
                filtered = all_products
            
            return filtered
        except Exception as e:
            print(f"❌ Error searching products: {e}")
            return []

def get_ai_recommendations_simple(company_name: str, product_name: str, available_products: List[Dict], num_recommendations: int = 5) -> tuple[List[str], bool]:
    """Use Groq AI to intelligently recommend products based on company and product name"""
    
    if not groq_client:
        print("❌ Groq client not available, using fallback")
        return simple_recommendation_fallback_simple(company_name, product_name, available_products, num_recommendations), False
    
    try:
        print(f"🤖 Using Groq AI for {num_recommendations} recommendations...")
        print(f"📊 Total available products: {len(available_products)}")
        
        # SMART FILTERING: Limit products sent to AI to prevent token overflow
        # 1. Prioritize same company products
        same_company = [p for p in available_products if company_name.lower() in p['company_name'].lower()]
        
        # 2. Find products matching the search term
        matching_products = [p for p in available_products if product_name.lower() in p['product_line'].lower()]
        
        # 3. Get other products as backup
        other_products = [p for p in available_products if p not in same_company and p not in matching_products]
        
        # 4. Create a smart subset (max 50 products to stay within token limits)
        ai_products = []
        ai_products.extend(same_company[:20])  # Max 20 same company
        ai_products.extend(matching_products[:20])  # Max 20 matching products
        ai_products.extend(other_products[:10])  # Max 10 other products
        
        # Remove duplicates while preserving order
        seen = set()
        filtered_products = []
        for product in ai_products:
            if product['id'] not in seen:
                seen.add(product['id'])
                filtered_products.append(product)
        
        ai_products = filtered_products[:50]  # Hard limit of 50 products
        
        print(f"🔍 Filtered to {len(ai_products)} products for AI analysis")
        print(f"   📋 Same company: {len([p for p in ai_products if company_name.lower() in p['company_name'].lower()])}")
        print(f"   🎯 Matching products: {len([p for p in ai_products if product_name.lower() in p['product_line'].lower()])}")
        
        # Prepare product information for AI
        product_info = []
        for product in ai_products:
            product_info.append(f"ID: {product['id']}, Company: {product['company_name']}, Product: {product['product_line']}")
        
        prompt = f"""
You are a product recommendation expert. Based on the following request, recommend the top {num_recommendations} most relevant product IDs.

Customer Request:
- Company Name: {company_name}
- Looking for product: {product_name}
- Number of recommendations needed: {num_recommendations}

Available Products:
{chr(10).join(product_info)}

Recommendation Rules:
1. PRIORITIZE products from the same company ({company_name}) if available
2. If {company_name} products are not available or insufficient, recommend similar products from other companies
3. Find products that best match the requested product name "{product_name}"
4. Consider exact keyword matches and similar products across all companies
5. If requesting Apple smartphones but Apple not available, suggest Samsung, Google, OnePlus smartphones
6. If requesting Nike shoes but Nike not available, suggest Adidas, Puma, Under Armour shoes
7. Return exactly {num_recommendations} product IDs in order of preference (most relevant first)

Please respond with ONLY the {num_recommendations} product IDs, one per line, no additional text:
"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"You are a helpful product recommendation assistant. Always respond with exactly {num_recommendations} product IDs, one per line."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
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
        
        # Ensure we have exactly the requested number of recommendations
        if len(recommended_ids) < num_recommendations:
            # Fill with fallback recommendations that aren't already included
            fallback_ids = simple_recommendation_fallback_simple(company_name, product_name, available_products, num_recommendations)
            for fid in fallback_ids:
                if fid not in recommended_ids and len(recommended_ids) < num_recommendations:
                    recommended_ids.append(fid)
        
        print(f"✅ AI successfully generated {len(recommended_ids)} recommendations")
        return recommended_ids[:num_recommendations], True
        
    except Exception as e:
        print(f"❌ Error getting AI recommendations: {e}")
        return simple_recommendation_fallback_simple(company_name, product_name, available_products, num_recommendations), False

def simple_recommendation_fallback_simple(company_name: str, product_name: str, available_products: List[Dict], num_recommendations: int = 5) -> List[str]:
    """Fallback recommendation logic for simplified input"""
    
    print(f"Using fallback logic for company: {company_name}, product: {product_name}")
    print(f"Available products count: {len(available_products)}")
    print(f"Requesting {num_recommendations} recommendations")
    
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
    recommendations = same_company_products[:num_recommendations]
    if len(recommendations) < num_recommendations:
        recommendations.extend(matching_products[:num_recommendations-len(recommendations)])
    if len(recommendations) < num_recommendations:
        recommendations.extend(other_products[:num_recommendations-len(recommendations)])
    
    print(f"Final recommendations: {recommendations}")
    return recommendations[:num_recommendations]

@app.on_event("startup")
async def startup_event():
    """Initialize database pool on startup"""
    await init_db_pool()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database pool on shutdown"""
    if db_pool:
        await db_pool.close()
        print("🔒 Database connection pool closed")

@app.get("/")
async def root():
    companies = await get_companies_from_db()
    return {
        "status": "AI-Powered Product Recommendation API with PostgreSQL",
        "total_companies": len(companies),
        "ai_enabled": groq_client is not None,
        "database": "PostgreSQL",
        "companies": companies[:10]  # Show first 10 companies
    }

@app.get("/companies")
async def get_companies():
    """Get all available companies from database"""
    companies = await get_companies_from_db()
    return companies

@app.get("/recommend")
async def recommend_products(
    company_name: str = Query(..., description="Company name seeking recommendations"),
    product_name: str = Query(..., description="Product name or type you're looking for"),
    num_recommendations: int = Query(5, ge=1, le=10, description="Number of recommendations (1-10)")
):
    """
    Get AI-powered product recommendations based on company name and product name.
    Returns configurable number of recommended products (1-10).
    """
    
    # Get relevant products from database
    relevant_products = await search_products_in_db(product_name=product_name)
    
    if not relevant_products:
        # If no matches, get all products
        relevant_products = await get_products_from_db()
    
    print(f"Found {len(relevant_products)} relevant products")
    
    if not relevant_products:
        raise HTTPException(status_code=404, detail="No products found")
    
    # Get AI recommendations
    recommended_ids, ai_used = get_ai_recommendations_simple(company_name, product_name, relevant_products, num_recommendations)
    
    # Get full product details for recommended IDs
    recommended_products = []
    for pid in recommended_ids:
        for product in relevant_products:
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
            "product_name": product_name,
            "num_recommendations": num_recommendations
        },
        "recommendations": recommended_products,
        "total_recommendations": len(recommended_products),
        "ai_used": ai_used,
        "method": "🤖 Groq AI" if ai_used else "⚙️ Fallback Logic",
        "database": "PostgreSQL"
    }

@app.get("/db-stats")
async def get_db_stats():
    """Get database statistics"""
    if not db_pool:
        await init_db_pool()
    if not db_pool:
        return {"error": "Database pool not available", "status": "error"}
        
    async with db_pool.acquire() as conn:
        try:
            company_count = await conn.fetchval("SELECT COUNT(*) FROM companies")
            product_count = await conn.fetchval("SELECT COUNT(*) FROM products") 
            sales_count = await conn.fetchval("SELECT COUNT(*) FROM sales")
            
            return {
                "database": "PostgreSQL",
                "companies": company_count,
                "products": product_count,
                "sales": sales_count,
                "status": "connected"
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
