"""
Streamlit Frontend for AI-Powered Product Recommendation System
Cloud-ready version with demo data (no database required)
"""

import streamlit as st
import os
import pandas as pd
from typing import Dict, List
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Product Recommendations",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration - Check for Streamlit secrets first, then environment variables
try:
    # Streamlit Cloud secrets
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
except Exception:
    # Fallback to environment variables
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Initialize Groq client
try:
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    else:
        groq_client = None
        st.warning("⚠️ Groq API key not configured. Using demo mode.")
except Exception as e:
    groq_client = None
    st.error(f"❌ Error initializing Groq client: {e}")

# Demo Data Functions (no database required)

def get_stats():
    """Get demo statistics"""
    companies = get_demo_companies()
    products = get_demo_products()
    return {
        "status": "demo_mode",
        "companies": len(companies),
        "products": len(products),
        "sales": 500,
        "note": "Using demo data - no database connection required"
    }
    
    try:
        async with db_pool.acquire() as conn:
            company_count = await conn.fetchval("SELECT COUNT(*) FROM companies")
            product_count = await conn.fetchval("SELECT COUNT(*) FROM products") 
            sales_count = await conn.fetchval("SELECT COUNT(*) FROM sales")
            
            return {
                "status": "connected",
                "companies": company_count,
                "products": product_count,
                "sales": sales_count
            }
    except Exception as e:
        return {"status": "error", "error": str(e), "companies": 0, "products": 0, "sales": 0}

def get_demo_companies():
    """Demo companies for when database is not available"""
    return ["Apple", "Samsung", "Google", "Nike", "Adidas", "Microsoft", "Sony", "Tesla", "Amazon", "Netflix"]

def get_demo_products():
    """Demo products for when database is not available"""
    demo_data = [
        {"id": "demo_1", "company_name": "Apple", "product_line": "smartphones", "description": "iPhone series"},
        {"id": "demo_2", "company_name": "Apple", "product_line": "laptops", "description": "MacBook series"},
        {"id": "demo_3", "company_name": "Samsung", "product_line": "smartphones", "description": "Galaxy series"},
        {"id": "demo_4", "company_name": "Samsung", "product_line": "televisions", "description": "Smart TV series"},
        {"id": "demo_5", "company_name": "Nike", "product_line": "shoes", "description": "Athletic footwear"},
        {"id": "demo_6", "company_name": "Nike", "product_line": "apparel", "description": "Sports clothing"},
        {"id": "demo_7", "company_name": "Microsoft", "product_line": "laptops", "description": "Surface series"},
        {"id": "demo_8", "company_name": "Sony", "product_line": "headphones", "description": "Audio equipment"},
        {"id": "demo_9", "company_name": "Google", "product_line": "smartphones", "description": "Pixel series"},
        {"id": "demo_10", "company_name": "Tesla", "product_line": "vehicles", "description": "Electric cars"},
    ]
    return demo_data

def get_ai_recommendations(company_name: str, product_name: str, available_products: List[Dict], num_recommendations: int = 5) -> tuple[List[str], bool]:
    """Use Groq AI to intelligently recommend products"""
    
    if not groq_client:
        return get_fallback_recommendations(company_name, product_name, available_products, num_recommendations), False
    
    try:
        # Smart filtering for AI
        same_company = [p for p in available_products if company_name.lower() in p['company_name'].lower()]
        matching_products = [p for p in available_products if product_name.lower() in p['product_line'].lower()]
        other_products = [p for p in available_products if p not in same_company and p not in matching_products]
        
        # Create subset for AI analysis
        ai_products = []
        ai_products.extend(same_company[:15])
        ai_products.extend(matching_products[:15])
        ai_products.extend(other_products[:10])
        
        # Remove duplicates
        seen = set()
        filtered_products = []
        for product in ai_products:
            if product['id'] not in seen:
                seen.add(product['id'])
                filtered_products.append(product)
        
        ai_products = filtered_products[:40]
        
        # Prepare product info for AI
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
5. Return exactly {num_recommendations} product IDs in order of preference (most relevant first)

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
        
        ai_response = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
        recommended_ids = []
        valid_ids = {product['id'] for product in available_products}
        
        for line in ai_response.split('\n'):
            line = line.strip().replace('.', '').replace('-', '').replace('*', '').strip()
            
            if line in valid_ids:
                recommended_ids.append(line)
            else:
                for valid_id in valid_ids:
                    if valid_id in line:
                        recommended_ids.append(valid_id)
                        break
        
        # Fill with fallback if needed
        if len(recommended_ids) < num_recommendations:
            fallback_ids = get_fallback_recommendations(company_name, product_name, available_products, num_recommendations)
            for fid in fallback_ids:
                if fid not in recommended_ids and len(recommended_ids) < num_recommendations:
                    recommended_ids.append(fid)
        
        return recommended_ids[:num_recommendations], True
        
    except Exception as e:
        st.warning(f"⚠️ AI error: {e}. Using fallback logic.")
        return get_fallback_recommendations(company_name, product_name, available_products, num_recommendations), False

def get_fallback_recommendations(company_name: str, product_name: str, available_products: List[Dict], num_recommendations: int = 5) -> List[str]:
    """Fallback recommendation logic"""
    
    same_company_products = []
    matching_products = []
    other_products = []
    
    product_name_lower = product_name.lower()
    
    for product in available_products:
        product_line_lower = product['product_line'].lower()
        
        is_same_company = product['company_name'].lower() == company_name.lower()
        is_matching = (
            product_name_lower in product_line_lower or
            any(word in product_line_lower for word in product_name_lower.split())
        )
        
        if is_same_company:
            same_company_products.append(product['id'])
        elif is_matching:
            matching_products.append(product['id'])
        else:
            other_products.append(product['id'])
    
    # Prioritize same company, then matching products, then others
    recommendations = same_company_products[:num_recommendations]
    if len(recommendations) < num_recommendations:
        recommendations.extend(matching_products[:num_recommendations-len(recommendations)])
    if len(recommendations) < num_recommendations:
        recommendations.extend(other_products[:num_recommendations-len(recommendations)])
    
    return recommendations[:num_recommendations]

def check_api_status():
    """Check if the system is properly configured"""
    has_groq = groq_client is not None
    
    return {
        "ai_enabled": has_groq,
        "database": "Demo Mode",
        "status": "ready"
    }

# Main App
@st.cache_data
def get_companies():
    """Get companies with caching"""
    return get_demo_companies()

@st.cache_data
def get_products():
    """Get products with caching"""
    return get_demo_products()

def get_recommendations(company_name: str, product_name: str, num_recommendations: int):
    """Get product recommendations"""
    try:
        all_products = get_products()
        recommended_ids, ai_used = get_ai_recommendations(company_name, product_name, all_products, num_recommendations)
        
        # Get full product details for recommended IDs
        recommended_products = []
        for pid in recommended_ids:
            for product in all_products:
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
            "database": "Demo Mode"
        }
    except Exception as e:
        return {"error": f"Error getting recommendations: {str(e)}"}

def main():
    st.title("🤖 AI-Powered Product Recommendation System")
    st.markdown("---")
    
    # Initialize demo mode
    st.info("🎯 Running in Demo Mode - No database connection required")
    
    # Sidebar - Minimal status
    with st.sidebar:
        st.header("🔧 System Status")
        
        # System Status Check
        api_info = check_api_status()
        if api_info["ai_enabled"]:
            st.success("✅ AI Connected")
        else:
            st.warning("⚠️ AI Demo Mode")
        
        st.info(f"Database: {api_info['database']}")
        
        # Database Stats
        db_stats = get_stats()
        if db_stats:
            st.markdown("**📊 Database:**")
            st.text(f"Companies: {db_stats.get('companies', 0)}")
            st.text(f"Products: {db_stats.get('products', 0)}")
            st.text(f"Sales: {db_stats.get('sales', 0)}")
            st.text("Status: Demo Mode")
        
        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.markdown("• Try different companies")
        st.markdown("• Use specific product names")
        st.markdown("• Adjust recommendation count")
    
    # Handle example button clicks first
    if 'company_example' in st.session_state:
        company_name = st.session_state.company_example
        product_name = st.session_state.product_example
        num_recommendations = st.session_state.count_example
        
        # Clear session state
        del st.session_state.company_example
        del st.session_state.product_example  
        del st.session_state.count_example
        
        # Process the example automatically
        with st.spinner("🤖 Getting AI recommendations..."):
            recommendations = get_recommendations(company_name, product_name, num_recommendations)
        
        if "error" not in recommendations:
            st.success(f"✅ Example results for {company_name} → {product_name}")
            
            # Display the example results
            request_info = recommendations.get('request', {})
            if isinstance(request_info, dict):
                display_company = request_info.get('company_name', company_name)
                display_product = request_info.get('product_name', product_name)
            else:
                display_company = company_name
                display_product = product_name
            
            st.subheader(f"📋 Recommendations for: {display_company} → {display_product}")
            
            # Method used
            method = recommendations.get('method', 'Unknown')
            ai_used = recommendations.get('ai_used', False)
            
            if ai_used:
                st.info(f"🤖 Generated using: {method}")
            else:
                st.warning(f"⚙️ Generated using: {method}")
            
            # Recommendations table
            recs = recommendations.get('recommendations', [])
            if recs:
                df = pd.DataFrame(recs)
                df.index = df.index + 1  # Start index from 1
                df.columns = ['Product ID', 'Company', 'Product Line']
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=False
                )
                
                # Additional info
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Recommendations", len(recs))
                with col2:
                    st.metric("AI Powered", "Yes" if ai_used else "No")
                with col3:
                    st.metric("Database", recommendations.get('database', 'Unknown'))
            else:
                st.warning("No recommendations found")
        else:
            st.error(f"❌ Error: {recommendations['error']}")

    # Main Content - Centered Form
    st.header("🔍 Product Recommendation Request")
    st.markdown("### Enter your requirements below:")
    
    # Simple centered form with just the three inputs
    with st.form("recommendation_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Company name input
            company_name = st.text_input(
                "**Company Name:**",
                placeholder="e.g., Apple, Samsung, Nike",
                help="Enter the company name you're interested in"
            )
        
        with col2:
            # Product input
            product_name = st.text_input(
                "**Product Type:**",
                placeholder="e.g., smartphone, laptop, shoes",
                help="Enter the type of product you're looking for"
            )
        
        with col3:
            # Number of recommendations
            num_recommendations = st.selectbox(
                "**Number of Recommendations:**",
                options=list(range(1, 11)),
                index=4,  # Default to 5
                help="Select how many recommendations (1-10)"
            )
        
        # Submit button - full width
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🤖 Get AI Recommendations", use_container_width=True, type="primary")
        
        # Process form submission
        if submitted:
            if not company_name or not product_name:
                st.error("⚠️ Please fill in both company name and product type")
            else:
                with st.spinner("🤖 Getting AI recommendations..."):
                    recommendations = get_recommendations(company_name, product_name, num_recommendations)
                
                if "error" in recommendations:
                    st.error(f"❌ Error: {recommendations['error']}")
                else:
                    # Display results
                    st.success(f"✅ Found {len(recommendations.get('recommendations', []))} recommendations")
                    
                    # Request info
                    request_info = recommendations.get('request', {})
                    if isinstance(request_info, dict):
                        display_company = request_info.get('company_name', company_name)
                        display_product = request_info.get('product_name', product_name)
                    else:
                        display_company = company_name
                        display_product = product_name
                    
                    st.subheader(f"📋 Recommendations for: {display_company} → {display_product}")
                    
                    # Method used
                    method = recommendations.get('method', 'Unknown')
                    ai_used = recommendations.get('ai_used', False)
                    
                    if ai_used:
                        st.info(f"🤖 Generated using: {method}")
                    else:
                        st.warning(f"⚙️ Generated using: {method}")
                    
                    # Recommendations table
                    recs = recommendations.get('recommendations', [])
                    if recs:
                        df = pd.DataFrame(recs)
                        df.index = df.index + 1  # Start index from 1
                        df.columns = ['Product ID', 'Company', 'Product Line']
                        
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=False
                        )
                        
                        # Additional info
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Recommendations", len(recs))
                        with col2:
                            st.metric("AI Powered", "Yes" if ai_used else "No")
                        with col3:
                            st.metric("Database", recommendations.get('database', 'Unknown'))
                    else:
                        st.warning("No recommendations found")

    # Quick Examples Section
    st.markdown("---")
    st.header("📝 Quick Examples")
    st.markdown("Click any example below to try it instantly:")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    examples = [
        ("Apple", "smartphone", 5),
        ("Nike", "shoes", 7),
        ("Samsung", "television", 6),
        ("Microsoft", "laptop", 4),
        ("Sony", "headphones", 8)
    ]
    
    cols = [col1, col2, col3, col4, col5]
    for i, (company, product, count) in enumerate(examples):
        with cols[i]:
            if st.button(f"🔍 {company}\n{product}\n({count})", key=f"example_{i}", use_container_width=True):
                st.session_state.company_example = company
                st.session_state.product_example = product
                st.session_state.count_example = count
                st.rerun()

if __name__ == "__main__":
    main()
