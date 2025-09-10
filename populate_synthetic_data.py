#!/usr/bin/env python3
"""
Synthetic Data Generator for Sales Recommendation API
Creates realistic test data with well-known companies and logical product categories.
"""

import asyncio
import asyncpg
import uuid
import random
from datetime import datetime, timedelta

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'sales_recommendation',
    'user': 'postgres',
    'password': 'salespass123'
}

# Realistic company data with their typical product categories
COMPANIES_DATA = {
    # Technology Companies
    'Apple': ['smartphones', 'laptops', 'tablets', 'headphones', 'smartwatches', 'computers'],
    'Samsung': ['smartphones', 'tablets', 'TVs', 'monitors', 'appliances', 'headphones'],
    'Microsoft': ['software', 'computers', 'gaming consoles', 'tablets', 'keyboards', 'mice'],
    'Google': ['smartphones', 'smart speakers', 'streaming devices', 'software', 'tablets'],
    'Sony': ['gaming consoles', 'headphones', 'cameras', 'TVs', 'speakers', 'smartphones'],
    'Dell': ['laptops', 'computers', 'monitors', 'keyboards', 'mice', 'servers'],
    'HP': ['laptops', 'computers', 'printers', 'monitors', 'keyboards', 'mice'],
    'Intel': ['processors', 'motherboards', 'SSDs', 'networking equipment'],
    'AMD': ['processors', 'graphics cards', 'motherboards', 'cooling systems'],
    'NVIDIA': ['graphics cards', 'AI hardware', 'gaming equipment', 'workstations'],
    
    # Fashion & Clothing
    'Nike': ['running shoes', 'sneakers', 'sportswear', 'athletic clothing', 'sports equipment'],
    'Adidas': ['running shoes', 'sneakers', 'sportswear', 'athletic clothing', 'soccer gear'],
    'Puma': ['running shoes', 'sneakers', 'sportswear', 'athletic clothing', 'lifestyle wear'],
    'Under Armour': ['athletic clothing', 'running shoes', 'sports equipment', 'fitness gear'],
    'Levi\'s': ['jeans', 'casual wear', 'jackets', 'shirts', 'accessories'],
    'H&M': ['fashion clothing', 'casual wear', 'accessories', 'shoes', 'seasonal wear'],
    'Zara': ['fashion clothing', 'business wear', 'casual wear', 'shoes', 'accessories'],
    'Uniqlo': ['basic clothing', 'casual wear', 'seasonal wear', 'accessories'],
    
    # Automotive
    'Toyota': ['cars', 'SUVs', 'trucks', 'hybrid vehicles', 'car parts'],
    'Honda': ['cars', 'motorcycles', 'SUVs', 'car parts', 'lawn equipment'],
    'Ford': ['cars', 'trucks', 'SUVs', 'electric vehicles', 'car parts'],
    'Tesla': ['electric vehicles', 'charging equipment', 'solar panels', 'energy storage'],
    'BMW': ['luxury cars', 'motorcycles', 'SUVs', 'car parts', 'accessories'],
    'Mercedes-Benz': ['luxury cars', 'SUVs', 'trucks', 'car parts', 'accessories'],
    
    # Food & Beverage
    'Coca-Cola': ['soft drinks', 'energy drinks', 'water', 'juices', 'sports drinks'],
    'PepsiCo': ['soft drinks', 'snacks', 'energy drinks', 'juices', 'food products'],
    'Nestlé': ['coffee', 'chocolate', 'baby food', 'pet food', 'frozen meals'],
    'McDonald\'s': ['fast food', 'beverages', 'breakfast items', 'desserts', 'coffee'],
    'Starbucks': ['coffee', 'beverages', 'food items', 'merchandise', 'coffee equipment'],
    
    # Home & Lifestyle
    'IKEA': ['furniture', 'home decor', 'kitchen items', 'storage solutions', 'textiles'],
    'Home Depot': ['tools', 'building materials', 'garden supplies', 'appliances', 'hardware'],
    'Target': ['clothing', 'home goods', 'electronics', 'groceries', 'toys'],
    'Walmart': ['groceries', 'clothing', 'electronics', 'home goods', 'pharmacy'],
    
    # Gaming & Entertainment
    'Nintendo': ['gaming consoles', 'video games', 'gaming accessories', 'toys'],
    'PlayStation': ['gaming consoles', 'video games', 'gaming accessories', 'VR equipment'],
    'Xbox': ['gaming consoles', 'video games', 'gaming accessories', 'subscriptions'],
    
    # Health & Beauty
    'Johnson & Johnson': ['healthcare products', 'baby care', 'personal care', 'medical devices'],
    'P&G': ['personal care', 'cleaning products', 'beauty products', 'health products'],
    'L\'Oréal': ['cosmetics', 'hair care', 'skin care', 'beauty tools'],
}

async def recreate_database_schema(conn):
    """Drop existing tables and create a new clean schema"""
    
    print("�️  Clearing existing database schema...")
    
    # Drop tables in reverse dependency order
    try:
        await conn.execute("DROP TABLE IF EXISTS sales CASCADE")
        print("   ✅ Dropped sales table")
    except Exception as e:
        print(f"   ⚠️  Error dropping sales table: {e}")
    
    try:
        await conn.execute("DROP TABLE IF EXISTS products CASCADE")
        print("   ✅ Dropped products table")
    except Exception as e:
        print(f"   ⚠️  Error dropping products table: {e}")
    
    try:
        await conn.execute("DROP TABLE IF EXISTS companies CASCADE")
        print("   ✅ Dropped companies table")
    except Exception as e:
        print(f"   ⚠️  Error dropping companies table: {e}")
    
    print()
    print("📋 Creating new clean database schema...")
    
    # Create companies table with clean structure
    await conn.execute('''
        CREATE TABLE companies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) UNIQUE NOT NULL,
            industry VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("   ✅ Created companies table")
    
    # Create products table with clean structure
    await conn.execute('''
        CREATE TABLE products (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            company_name VARCHAR(255) NOT NULL,
            product_line VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            description TEXT,
            price DECIMAL(10,2),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("   ✅ Created products table")
    
    # Create sales table with clean structure
    await conn.execute('''
        CREATE TABLE sales (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            product_id UUID REFERENCES products(id) ON DELETE CASCADE,
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            company_name VARCHAR(255) NOT NULL,
            product_line VARCHAR(255) NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(12,2) NOT NULL,
            sale_date DATE NOT NULL,
            customer_segment VARCHAR(50),
            region VARCHAR(50),
            sales_rep VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("   ✅ Created sales table")
    
    # Create indexes for better performance
    await conn.execute('CREATE INDEX idx_products_company_id ON products(company_id)')
    await conn.execute('CREATE INDEX idx_products_category ON products(category)')
    await conn.execute('CREATE INDEX idx_products_company_name ON products(company_name)')
    await conn.execute('CREATE INDEX idx_sales_product_id ON sales(product_id)')
    await conn.execute('CREATE INDEX idx_sales_company_id ON sales(company_id)')
    await conn.execute('CREATE INDEX idx_sales_date ON sales(sale_date)')
    print("   ✅ Created database indexes")
    
    print("✅ New database schema created successfully!")

async def populate_companies(conn):
    """Populate companies table"""
    
    print("🏢 Populating companies...")
    
    # Define industry mapping
    industry_mapping = {
        'Apple': 'Technology', 'Samsung': 'Technology', 'Microsoft': 'Technology',
        'Google': 'Technology', 'Sony': 'Technology', 'Dell': 'Technology',
        'HP': 'Technology', 'Intel': 'Technology', 'AMD': 'Technology', 'NVIDIA': 'Technology',
        
        'Nike': 'Fashion & Apparel', 'Adidas': 'Fashion & Apparel', 'Puma': 'Fashion & Apparel',
        'Under Armour': 'Fashion & Apparel', 'Levi\'s': 'Fashion & Apparel',
        'H&M': 'Fashion & Apparel', 'Zara': 'Fashion & Apparel', 'Uniqlo': 'Fashion & Apparel',
        
        'Toyota': 'Automotive', 'Honda': 'Automotive', 'Ford': 'Automotive',
        'Tesla': 'Automotive', 'BMW': 'Automotive', 'Mercedes-Benz': 'Automotive',
        
        'Coca-Cola': 'Food & Beverage', 'PepsiCo': 'Food & Beverage', 'Nestlé': 'Food & Beverage',
        'McDonald\'s': 'Food & Beverage', 'Starbucks': 'Food & Beverage',
        
        'IKEA': 'Home & Lifestyle', 'Home Depot': 'Home & Lifestyle',
        'Target': 'Retail', 'Walmart': 'Retail',
        
        'Nintendo': 'Gaming & Entertainment', 'PlayStation': 'Gaming & Entertainment',
        'Xbox': 'Gaming & Entertainment',
        
        'Johnson & Johnson': 'Health & Beauty', 'P&G': 'Health & Beauty', 'L\'Oréal': 'Health & Beauty'
    }
    
    company_count = 0
    company_ids = {}  # Store company_id mapping for products
    
    for company_name in COMPANIES_DATA.keys():
        try:
            industry = industry_mapping.get(company_name, 'Other')
            
            # Insert company and get the generated ID
            company_id = await conn.fetchval(
                'INSERT INTO companies (name, industry) VALUES ($1, $2) RETURNING id',
                company_name, industry
            )
            
            company_ids[company_name] = company_id
            company_count += 1
            
        except Exception as e:
            print(f"   ⚠️  Error inserting company {company_name}: {e}")
    
    print(f"✅ Inserted {company_count} companies")
    return company_ids

async def populate_products(conn, company_ids):
    """Populate products table with realistic product data"""
    
    print("📦 Populating products...")
    
    # Price ranges by category
    price_ranges = {
        'smartphones': (200, 1500),
        'laptops': (500, 3000),
        'tablets': (150, 1200),
        'headphones': (20, 500),
        'smartwatches': (100, 800),
        'computers': (400, 4000),
        'TVs': (300, 3000),
        'monitors': (100, 1500),
        'running shoes': (60, 300),
        'sneakers': (50, 400),
        'sportswear': (20, 200),
        'athletic clothing': (15, 150),
        'cars': (15000, 80000),
        'SUVs': (20000, 100000),
        'trucks': (25000, 90000),
        'soft drinks': (1, 5),
        'coffee': (5, 50),
        'furniture': (50, 2000),
        'gaming consoles': (200, 600),
        'video games': (20, 80),
        'cosmetics': (10, 200),
        'default': (10, 100)
    }
    
    product_count = 0
    
    for company_name, product_categories in COMPANIES_DATA.items():
        # Get company ID
        company_id = company_ids.get(company_name)
        
        if not company_id:
            continue
        
        # Create 3-8 products per company
        num_products = random.randint(3, 8)
        
        for _ in range(num_products):
            # Select random product category
            product_line = random.choice(product_categories)
            
            # Generate realistic price
            price_range = price_ranges.get(product_line, price_ranges['default'])
            price = round(random.uniform(price_range[0], price_range[1]), 2)
            
            # Determine category from product line
            category_mapping = {
                'smartphones': 'Electronics', 'laptops': 'Electronics', 'tablets': 'Electronics',
                'headphones': 'Electronics', 'smartwatches': 'Electronics', 'computers': 'Electronics',
                'TVs': 'Electronics', 'monitors': 'Electronics', 'software': 'Electronics',
                'gaming consoles': 'Electronics', 'keyboards': 'Electronics', 'mice': 'Electronics',
                
                'running shoes': 'Footwear', 'sneakers': 'Footwear',
                'sportswear': 'Clothing', 'athletic clothing': 'Clothing', 'jeans': 'Clothing',
                'casual wear': 'Clothing', 'fashion clothing': 'Clothing',
                
                'cars': 'Vehicles', 'SUVs': 'Vehicles', 'trucks': 'Vehicles',
                'electric vehicles': 'Vehicles', 'hybrid vehicles': 'Vehicles',
                
                'soft drinks': 'Beverages', 'coffee': 'Beverages', 'energy drinks': 'Beverages',
                'fast food': 'Food', 'snacks': 'Food',
                
                'furniture': 'Home & Garden', 'home decor': 'Home & Garden', 'tools': 'Home & Garden',
                
                'video games': 'Entertainment', 'gaming accessories': 'Entertainment',
                
                'cosmetics': 'Beauty & Health', 'personal care': 'Beauty & Health'
            }
            
            category = category_mapping.get(product_line, 'Other')
            description = f"High-quality {product_line} from {company_name}"
            
            try:
                await conn.execute('''
                    INSERT INTO products (company_id, company_name, product_line, category, description, price)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''', company_id, company_name, product_line, category, description, price)
                
                product_count += 1
                
            except Exception as e:
                print(f"   ⚠️  Error inserting product: {e}")
    
    print(f"✅ Inserted {product_count} products")

async def populate_sales(conn):
    """Populate sales table with realistic sales data"""
    
    print("💰 Populating sales data...")
    
    # Get all products with their company information
    products = await conn.fetch('''
        SELECT p.id, p.company_id, p.company_name, p.product_line, p.price 
        FROM products p
    ''')
    
    if not products:
        print("❌ No products found, skipping sales generation")
        return
    
    # Customer segments and regions for realistic data
    customer_segments = ['Enterprise', 'SMB', 'Individual', 'Government', 'Education']
    regions = ['North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Middle East & Africa']
    sales_reps = ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Lisa Williams', 'David Brown', 
                  'Emma Davis', 'Chris Wilson', 'Anna Garcia', 'Tom Anderson', 'Maria Rodriguez']
    
    sales_count = 0
    
    # Generate sales for the last 2 years
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now()
    
    # Generate 5-15 sales per product
    for product in products:
        num_sales = random.randint(5, 15)
        
        for _ in range(num_sales):
            # Random sale date
            sale_date = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )
            
            # Random quantity (higher for cheaper items)
            if product['price'] < 50:
                quantity = random.randint(1, 100)
            elif product['price'] < 500:
                quantity = random.randint(1, 20)
            else:
                quantity = random.randint(1, 5)
            
            unit_price = product['price']
            total_amount = round(unit_price * quantity, 2)
            customer_segment = random.choice(customer_segments)
            region = random.choice(regions)
            sales_rep = random.choice(sales_reps)
            
            try:
                await conn.execute('''
                    INSERT INTO sales (product_id, company_id, company_name, product_line, 
                                     quantity, unit_price, total_amount, sale_date, 
                                     customer_segment, region, sales_rep)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ''', product['id'], product['company_id'], product['company_name'], 
                    product['product_line'], quantity, unit_price, total_amount, 
                    sale_date.date(), customer_segment, region, sales_rep)
                
                sales_count += 1
                
            except Exception as e:
                print(f"   ⚠️  Error inserting sale: {e}")
    
    print(f"✅ Inserted {sales_count} sales records")

async def generate_synthetic_data():
    """Main function to generate all synthetic data"""
    
    print("🎯 Synthetic Data Generator for Sales Recommendation API")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Connect to database
        print("🔌 Connecting to PostgreSQL...")
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        print("✅ Connected successfully!")
        print()
        
        # Recreate database schema
        await recreate_database_schema(conn)
        print()
        
        # Check if data already exists after schema recreation
        companies_count = await conn.fetchval("SELECT COUNT(*) FROM companies")
        products_count = await conn.fetchval("SELECT COUNT(*) FROM products")
        sales_count = await conn.fetchval("SELECT COUNT(*) FROM sales")
        
        print(f"📊 Current Database Status:")
        print(f"   👥 Companies: {companies_count}")
        print(f"   📦 Products: {products_count}")
        print(f"   💰 Sales: {sales_count}")
        print()
        
        # Generate data
        company_ids = await populate_companies(conn)
        print()
        
        await populate_products(conn, company_ids)
        print()
        
        await populate_sales(conn)
        print()
        
        # Final statistics
        final_companies = await conn.fetchval("SELECT COUNT(*) FROM companies")
        final_products = await conn.fetchval("SELECT COUNT(*) FROM products")
        final_sales = await conn.fetchval("SELECT COUNT(*) FROM sales")
        
        print("🎉 Synthetic Data Generation Completed!")
        print("=" * 40)
        print(f"📊 Final Database Statistics:")
        print(f"   👥 Companies: {final_companies}")
        print(f"   📦 Products: {final_products}")
        print(f"   💰 Sales: {final_sales}")
        print()
        print(f"💡 Ready for testing with realistic data!")
        print(f"   • {len(COMPANIES_DATA)} major brands")
        print(f"   • Diverse product categories")
        print(f"   • 2 years of sales history")
        print(f"   • Realistic pricing")
        print()
        print(f"🚀 You can now test recommendations like:")
        print(f"   • Samsung + phone")
        print(f"   • Nike + shoes")
        print(f"   • Apple + laptop")
        print(f"   • Tesla + car")
        
        await conn.close()
        print("🔒 Database connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(generate_synthetic_data())
