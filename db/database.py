"""
Database configuration and connection management for Sales Recommendation API
"""

import os
import asyncpg
import asyncio
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration settings"""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", 5432)
        self.database = os.getenv("DB_NAME", "sales_recommendation")
        self.username = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.min_connections = int(os.getenv("DB_MIN_CONNECTIONS", "5"))
        self.max_connections = int(os.getenv("DB_MAX_CONNECTIONS", "20"))
    
    @property
    def connection_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class DatabaseManager:
    """Database connection and query management"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections,
                command_timeout=60
            )
            logger.info("✅ Database connection pool initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            return False
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("🔒 Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dictionaries"""
        async with self.get_connection() as conn:
            try:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"❌ Query execution failed: {e}")
                raise
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute INSERT/UPDATE/DELETE command"""
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(command, *args)
                logger.info(f"✅ Command executed: {result}")
                return result
            except Exception as e:
                logger.error(f"❌ Command execution failed: {e}")
                raise
    
    async def execute_transaction(self, commands: List[tuple]) -> bool:
        """Execute multiple commands in a transaction"""
        async with self.get_connection() as conn:
            try:
                async with conn.transaction():
                    for command, args in commands:
                        await conn.execute(command, *args)
                logger.info("✅ Transaction completed successfully")
                return True
            except Exception as e:
                logger.error(f"❌ Transaction failed: {e}")
                raise
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                if result == 1:
                    logger.info("✅ Database connection test successful")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

async def get_db():
    """Dependency injection for database"""
    return db_manager

# Database utility functions
async def init_database():
    """Initialize database connection"""
    success = await db_manager.initialize_pool()
    if success:
        # Test the connection
        await db_manager.test_connection()
    return success

async def close_database():
    """Close database connections"""
    await db_manager.close_pool()
