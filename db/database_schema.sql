-- PostgreSQL Schema for Sales Recommendation API
-- Created: September 10, 2025

-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- Companies table
CREATE TABLE companies (
    company_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    industry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    product_line TEXT NOT NULL,
    category TEXT,
    description TEXT,
    price NUMERIC(10, 2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales table
CREATE TABLE sales (
    sale_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id TEXT,
    product_id UUID REFERENCES products(product_id) ON DELETE CASCADE,
    buyer_company TEXT,
    buyer_id TEXT,
    quantity INTEGER DEFAULT 1,
    unit_price NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),
    sale_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_products_company_id ON products(company_id);
CREATE INDEX idx_products_product_line ON products(product_line);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_sales_timestamp ON sales(sale_timestamp);
CREATE INDEX idx_companies_name ON companies(name);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample companies from your existing data
INSERT INTO companies (name, industry) VALUES 
    ('Thermax', 'Industrial Equipment'),
    ('Danfoss', 'Industrial Automation'),
    ('Grundfos', 'Pump Solutions'),
    ('Fowler', 'Agricultural Processing');

-- Comments for documentation
COMMENT ON TABLE companies IS 'Company information and business details';
COMMENT ON TABLE products IS 'Product catalog with company associations';
COMMENT ON TABLE sales IS 'Sales transactions and order history';

COMMENT ON COLUMN companies.company_id IS 'Unique identifier for company';
COMMENT ON COLUMN companies.name IS 'Company name (unique)';
COMMENT ON COLUMN companies.industry IS 'Industry sector';

COMMENT ON COLUMN products.product_id IS 'Unique identifier for product';
COMMENT ON COLUMN products.company_id IS 'Reference to company that makes this product';
COMMENT ON COLUMN products.name IS 'Product name';
COMMENT ON COLUMN products.product_line IS 'Product line or category';
COMMENT ON COLUMN products.is_active IS 'Whether product is currently available';

COMMENT ON COLUMN sales.sale_id IS 'Unique identifier for sale transaction';
COMMENT ON COLUMN sales.order_id IS 'External order reference';
COMMENT ON COLUMN sales.buyer_company IS 'Company that purchased the product';
COMMENT ON COLUMN sales.quantity IS 'Number of units sold';
COMMENT ON COLUMN sales.total_amount IS 'Total sale amount';
