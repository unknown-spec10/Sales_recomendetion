#!/usr/bin/env python3
"""
Quick Database Reset Script
Instantly clears all data and resets the database to empty state.
Use for development/testing only.
"""

import asyncio
import asyncpg

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'sales_recommendation',
    'user': 'postgres',
    'password': 'salespass123'
}

async def reset_database():
    """Reset database to empty state"""
    
    print("🔄 Quick Database Reset...")
    
    try:
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        
        # Get current counts
        try:
            companies = await conn.fetchval("SELECT COUNT(*) FROM companies")
            products = await conn.fetchval("SELECT COUNT(*) FROM products") 
            sales = await conn.fetchval("SELECT COUNT(*) FROM sales")
            total = companies + products + sales
            
            print(f"📊 Current: {companies:,} companies, {products:,} products, {sales:,} sales")
            
            if total == 0:
                print("✅ Database already empty!")
                await conn.close()
                return
            
        except Exception as e:
            print(f"⚠️  Could not check current state: {e}")
        
        # Clear all tables
        print("🗑️  Clearing all data...")
        
        await conn.execute("TRUNCATE TABLE sales CASCADE")
        await conn.execute("TRUNCATE TABLE products CASCADE") 
        await conn.execute("TRUNCATE TABLE companies CASCADE")
        
        # Reset auto-increment sequences (only if they exist)
        try:
            await conn.execute("ALTER SEQUENCE sales_id_seq RESTART WITH 1")
        except:
            pass
        try:
            await conn.execute("ALTER SEQUENCE companies_id_seq RESTART WITH 1")
        except:
            pass
        
        print("✅ Database reset complete!")
        print("📭 All tables are now empty")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(reset_database())
