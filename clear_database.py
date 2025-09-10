#!/usr/bin/env python3
"""
Database Clear/Depopulation Script
Removes all data from the PostgreSQL database tables.
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'sales_recommendation',
    'user': 'postgres',
    'password': 'salespass123'
}

async def clear_database():
    """Clear all data from the database tables"""
    
    print("🗑️  Database Depopulation Script")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Connect to database
        print("🔌 Connecting to PostgreSQL database...")
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        print("✅ Connected successfully!")
        print()
        
        # Get current record counts before clearing
        print("📊 Current Database Status:")
        
        try:
            companies_count = await conn.fetchval("SELECT COUNT(*) FROM companies")
            print(f"   👥 Companies: {companies_count:,}")
        except Exception:
            companies_count = 0
            print(f"   👥 Companies: Table not found or empty")
            
        try:
            products_count = await conn.fetchval("SELECT COUNT(*) FROM products")
            print(f"   📦 Products: {products_count:,}")
        except Exception:
            products_count = 0
            print(f"   📦 Products: Table not found or empty")
            
        try:
            sales_count = await conn.fetchval("SELECT COUNT(*) FROM sales")
            print(f"   💰 Sales: {sales_count:,}")
        except Exception:
            sales_count = 0
            print(f"   💰 Sales: Table not found or empty")
        
        print()
        
        # Ask for confirmation
        total_records = companies_count + products_count + sales_count
        if total_records == 0:
            print("📭 Database is already empty!")
            await conn.close()
            return
        
        print(f"⚠️  WARNING: This will DELETE {total_records:,} total records!")
        print("   This action cannot be undone.")
        print()
        
        confirm = input("   Type 'YES' to confirm deletion: ").strip()
        if confirm != 'YES':
            print("❌ Operation cancelled by user")
            await conn.close()
            return
        
        print()
        print("🗑️  Starting database cleanup...")
        
        # Clear tables in correct order (due to foreign key constraints)
        tables_to_clear = [
            ('sales', 'Sales records'),
            ('products', 'Product catalog'),
            ('companies', 'Company directory')
        ]
        
        for table_name, description in tables_to_clear:
            try:
                print(f"   🧹 Clearing {description}...")
                
                # Get count before deletion
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                
                if count > 0:
                    # Delete all records
                    await conn.execute(f"DELETE FROM {table_name}")
                    
                    # Reset sequence if it exists
                    try:
                        await conn.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1")
                    except Exception:
                        pass  # Sequence might not exist
                    
                    print(f"      ✅ Deleted {count:,} records from {table_name}")
                else:
                    print(f"      📭 {table_name} was already empty")
                    
            except Exception as e:
                print(f"      ⚠️  Error clearing {table_name}: {e}")
        
        print()
        
        # Verify cleanup
        print("🔍 Verifying cleanup...")
        
        for table_name, description in tables_to_clear:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                if count == 0:
                    print(f"   ✅ {description}: Empty")
                else:
                    print(f"   ⚠️  {description}: Still has {count} records")
            except Exception as e:
                print(f"   ❌ {description}: Error checking - {e}")
        
        print()
        print("🎉 Database cleanup completed!")
        print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await conn.close()
        print("🔒 Database connection closed")
        
    except asyncpg.exceptions.InvalidCatalogNameError:
        print("❌ Database 'sales_recommendations' does not exist!")
        print("   Please create the database first or check the database name.")
        
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ Authentication failed!")
        print("   Please check the username and password.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Please check your database connection settings.")

async def quick_clear():
    """Quick clear without confirmation (for scripts)"""
    
    try:
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        
        # Clear in order
        await conn.execute("DELETE FROM sales")
        await conn.execute("DELETE FROM products") 
        await conn.execute("DELETE FROM companies")
        
        # Reset sequences
        try:
            await conn.execute("ALTER SEQUENCE sales_id_seq RESTART WITH 1")
            await conn.execute("ALTER SEQUENCE products_id_seq RESTART WITH 1")
            await conn.execute("ALTER SEQUENCE companies_id_seq RESTART WITH 1")
        except:
            pass
        
        await conn.close()
        print("✅ Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick mode for automation
        asyncio.run(quick_clear())
    else:
        # Interactive mode with confirmation
        asyncio.run(clear_database())
