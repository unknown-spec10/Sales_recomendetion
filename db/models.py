"""
Database models for Sales Recommendation API
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import uuid
from dataclasses import dataclass, asdict
from database import db_manager

@dataclass
class Company:
    """Company model"""
    company_id: Optional[UUID] = None
    name: str = ""
    industry: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert UUID to string for JSON serialization
        if self.company_id:
            data['company_id'] = str(self.company_id)
        return data

@dataclass
class Product:
    """Product model"""
    product_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    name: str = ""
    product_line: str = ""
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert UUIDs to strings for JSON serialization
        if self.product_id:
            data['product_id'] = str(self.product_id)
        if self.company_id:
            data['company_id'] = str(self.company_id)
        return data

@dataclass
class Sale:
    """Sale model"""
    sale_id: Optional[UUID] = None
    order_id: Optional[str] = None
    product_id: Optional[UUID] = None
    buyer_company: Optional[str] = None
    buyer_id: Optional[str] = None
    quantity: int = 1
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    sale_timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert UUIDs to strings for JSON serialization
        if self.sale_id:
            data['sale_id'] = str(self.sale_id)
        if self.product_id:
            data['product_id'] = str(self.product_id)
        return data

class CompanyRepository:
    """Repository for company operations"""
    
    @staticmethod
    async def create(company: Company) -> Company:
        """Create a new company"""
        query = """
        INSERT INTO companies (name, industry)
        VALUES ($1, $2)
        RETURNING company_id, name, industry, created_at, updated_at
        """
        
        result = await db_manager.execute_query(
            query, company.name, company.industry
        )
        
        if result:
            row = result[0]
            return Company(
                company_id=row['company_id'],
                name=row['name'],
                industry=row['industry'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        raise ValueError("Failed to create company")
    
    @staticmethod
    async def get_all() -> List[Company]:
        """Get all companies"""
        query = "SELECT * FROM companies ORDER BY name"
        results = await db_manager.execute_query(query)
        
        return [
            Company(
                company_id=row['company_id'],
                name=row['name'],
                industry=row['industry'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in results
        ]
    
    @staticmethod
    async def get_by_name(name: str) -> Optional[Company]:
        """Get company by name"""
        query = "SELECT * FROM companies WHERE name = $1"
        results = await db_manager.execute_query(query, name)
        
        if results:
            row = results[0]
            return Company(
                company_id=row['company_id'],
                name=row['name'],
                industry=row['industry'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None

class ProductRepository:
    """Repository for product operations"""
    
    @staticmethod
    async def create(product: Product) -> Product:
        """Create a new product"""
        query = """
        INSERT INTO products (company_id, name, product_line, category, description, price, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING product_id, company_id, name, product_line, category, description, price, is_active, created_at, updated_at
        """
        
        result = await db_manager.execute_query(
            query, 
            product.company_id, 
            product.name, 
            product.product_line,
            product.category,
            product.description,
            product.price,
            product.is_active
        )
        
        if result:
            row = result[0]
            return Product(
                product_id=row['product_id'],
                company_id=row['company_id'],
                name=row['name'],
                product_line=row['product_line'],
                category=row['category'],
                description=row['description'],
                price=row['price'],
                is_active=row['is_active'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        raise ValueError("Failed to create product")
    
    @staticmethod
    async def get_all() -> List[Dict[str, Any]]:
        """Get all products with company information"""
        query = """
        SELECT 
            p.product_id,
            p.name as product_name,
            p.product_line,
            p.category,
            p.description,
            p.price,
            p.is_active,
            c.company_id,
            c.name as company_name,
            c.industry
        FROM products p
        JOIN companies c ON p.company_id = c.company_id
        WHERE p.is_active = true
        ORDER BY c.name, p.product_line
        """
        
        results = await db_manager.execute_query(query)
        return [
            {
                "id": str(row['product_id']),
                "company_name": row['company_name'],
                "product_line": row['product_line'],
                "product_name": row['product_name'],
                "category": row['category'],
                "description": row['description'],
                "price": float(row['price']) if row['price'] else None,
                "industry": row['industry']
            }
            for row in results
        ]
    
    @staticmethod
    async def search_by_name(product_name: str) -> List[Dict[str, Any]]:
        """Search products by name or product line"""
        query = """
        SELECT 
            p.product_id,
            p.name as product_name,
            p.product_line,
            p.category,
            c.name as company_name
        FROM products p
        JOIN companies c ON p.company_id = c.company_id
        WHERE (LOWER(p.name) LIKE LOWER($1) OR LOWER(p.product_line) LIKE LOWER($1))
        AND p.is_active = true
        ORDER BY c.name, p.product_line
        """
        
        search_term = f"%{product_name}%"
        results = await db_manager.execute_query(query, search_term)
        
        return [
            {
                "id": str(row['product_id']),
                "company_name": row['company_name'],
                "product_line": row['product_line'],
                "product_name": row['product_name'],
                "category": row['category']
            }
            for row in results
        ]
    
    @staticmethod
    async def get_by_company(company_name: str) -> List[Dict[str, Any]]:
        """Get products by company name"""
        query = """
        SELECT 
            p.product_id,
            p.name as product_name,
            p.product_line,
            p.category,
            c.name as company_name
        FROM products p
        JOIN companies c ON p.company_id = c.company_id
        WHERE LOWER(c.name) = LOWER($1)
        AND p.is_active = true
        ORDER BY p.product_line
        """
        
        results = await db_manager.execute_query(query, company_name)
        
        return [
            {
                "id": str(row['product_id']),
                "company_name": row['company_name'],
                "product_line": row['product_line'],
                "product_name": row['product_name'],
                "category": row['category']
            }
            for row in results
        ]

class SaleRepository:
    """Repository for sales operations"""
    
    @staticmethod
    async def create(sale: Sale) -> Sale:
        """Create a new sale"""
        query = """
        INSERT INTO sales (order_id, product_id, buyer_company, buyer_id, quantity, unit_price, total_amount)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING sale_id, order_id, product_id, buyer_company, buyer_id, quantity, unit_price, total_amount, sale_timestamp, created_at
        """
        
        result = await db_manager.execute_query(
            query,
            sale.order_id,
            sale.product_id,
            sale.buyer_company,
            sale.buyer_id,
            sale.quantity,
            sale.unit_price,
            sale.total_amount
        )
        
        if result:
            row = result[0]
            return Sale(
                sale_id=row['sale_id'],
                order_id=row['order_id'],
                product_id=row['product_id'],
                buyer_company=row['buyer_company'],
                buyer_id=row['buyer_id'],
                quantity=row['quantity'],
                unit_price=row['unit_price'],
                total_amount=row['total_amount'],
                sale_timestamp=row['sale_timestamp'],
                created_at=row['created_at']
            )
        raise ValueError("Failed to create sale")
    
    @staticmethod
    async def get_popular_products(limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular products based on sales"""
        query = """
        SELECT 
            p.product_id,
            p.name as product_name,
            p.product_line,
            c.name as company_name,
            COUNT(s.sale_id) as sale_count,
            SUM(s.quantity) as total_quantity
        FROM products p
        JOIN companies c ON p.company_id = c.company_id
        LEFT JOIN sales s ON p.product_id = s.product_id
        WHERE p.is_active = true
        GROUP BY p.product_id, p.name, p.product_line, c.name
        ORDER BY sale_count DESC, total_quantity DESC
        LIMIT $1
        """
        
        results = await db_manager.execute_query(query, limit)
        
        return [
            {
                "id": str(row['product_id']),
                "company_name": row['company_name'],
                "product_line": row['product_line'],
                "product_name": row['product_name'],
                "sale_count": row['sale_count'],
                "total_quantity": row['total_quantity']
            }
            for row in results
        ]
