"""
Database Configuration Module
Centralizes all database connection settings for PostgreSQL and MongoDB
"""

import os
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PostgresNodeConfig:
    """Configuration for a PostgreSQL node"""
    host: str
    port: int
    database: str
    user: str
    password: str
    role: str  # 'master' or 'slave'
    region: str  # Geographic region for sharding
    shard_id: int  # Shard identifier


@dataclass
class MongoNodeConfig:
    """Configuration for a MongoDB node"""
    host: str
    port: int
    database: str
    user: str
    password: str
    replica_set: str = None


class DatabaseConfig:
    """Centralized database configuration"""
    
    # PostgreSQL Configuration
    POSTGRES_MASTER_NODES = [
        PostgresNodeConfig(
            host=os.getenv('PG_MASTER_NA_HOST', 'localhost'),
            port=int(os.getenv('PG_MASTER_NA_PORT', 5432)),
            database=os.getenv('PG_DATABASE', 'elearning_na'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            role='master',
            region='north_america',
            shard_id=1
        ),
        PostgresNodeConfig(
            host=os.getenv('PG_MASTER_EU_HOST', 'localhost'),
            port=int(os.getenv('PG_MASTER_EU_PORT', 5433)),
            database=os.getenv('PG_DATABASE', 'elearning_eu'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            role='master',
            region='europe',
            shard_id=2
        ),
        PostgresNodeConfig(
            host=os.getenv('PG_MASTER_ASIA_HOST', 'localhost'),
            port=int(os.getenv('PG_MASTER_ASIA_PORT', 5434)),
            database=os.getenv('PG_DATABASE', 'elearning_asia'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            role='master',
            region='asia',
            shard_id=3
        )
    ]
    
    POSTGRES_SLAVE_NODES = [
        PostgresNodeConfig(
            host=os.getenv('PG_SLAVE_NA_HOST', 'localhost'),
            port=int(os.getenv('PG_SLAVE_NA_PORT', 5435)),
            database=os.getenv('PG_DATABASE', 'elearning_na'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            role='slave',
            region='north_america',
            shard_id=1
        ),
        PostgresNodeConfig(
            host=os.getenv('PG_SLAVE_EU_HOST', 'localhost'),
            port=int(os.getenv('PG_SLAVE_EU_PORT', 5436)),
            database=os.getenv('PG_DATABASE', 'elearning_eu'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            role='slave',
            region='europe',
            shard_id=2
        ),
        PostgresNodeConfig(
            host=os.getenv('PG_SLAVE_ASIA_HOST', 'localhost'),
            port=int(os.getenv('PG_SLAVE_ASIA_PORT', 5437)),
            database=os.getenv('PG_DATABASE', 'elearning_asia'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            role='slave',
            region='asia',
            shard_id=3
        )
    ]
    
    # MongoDB Configuration
    MONGO_NODES = [
        MongoNodeConfig(
            host=os.getenv('MONGO_HOST', 'localhost'),
            port=int(os.getenv('MONGO_PORT', 27017)),
            database=os.getenv('MONGO_DATABASE', 'elearning_content'),
            user=os.getenv('MONGO_USER', 'admin'),
            password=os.getenv('MONGO_PASSWORD', 'admin'),
            replica_set=os.getenv('MONGO_REPLICA_SET', None)
        )
    ]
    
    # Connection Pool Settings
    POSTGRES_POOL_SIZE = int(os.getenv('PG_POOL_SIZE', 10))
    POSTGRES_MAX_OVERFLOW = int(os.getenv('PG_MAX_OVERFLOW', 20))
    POSTGRES_POOL_TIMEOUT = int(os.getenv('PG_POOL_TIMEOUT', 30))
    
    MONGO_POOL_SIZE = int(os.getenv('MONGO_POOL_SIZE', 10))
    MONGO_MAX_POOL_SIZE = int(os.getenv('MONGO_MAX_POOL_SIZE', 50))
    
    # Sharding Configuration
    REGION_MAPPING = {
        'north_america': 1,
        'south_america': 1,
        'europe': 2,
        'africa': 2,
        'asia': 3,
        'oceania': 3
    }
    
    @classmethod
    def get_master_node_by_region(cls, region: str) -> PostgresNodeConfig:
        """Get master node configuration for a specific region"""
        shard_id = cls.REGION_MAPPING.get(region.lower())
        if not shard_id:
            raise ValueError(f"Unknown region: {region}")
        
        for node in cls.POSTGRES_MASTER_NODES:
            if node.shard_id == shard_id:
                return node
        
        raise ValueError(f"No master node found for region: {region}")
    
    @classmethod
    def get_slave_nodes_by_region(cls, region: str) -> List[PostgresNodeConfig]:
        """Get all slave nodes for a specific region"""
        shard_id = cls.REGION_MAPPING.get(region.lower())
        if not shard_id:
            raise ValueError(f"Unknown region: {region}")
        
        return [node for node in cls.POSTGRES_SLAVE_NODES if node.shard_id == shard_id]
    
    @classmethod
    def get_all_master_nodes(cls) -> List[PostgresNodeConfig]:
        """Get all master nodes"""
        return cls.POSTGRES_MASTER_NODES
    
    @classmethod
    def get_mongo_config(cls) -> MongoNodeConfig:
        """Get MongoDB configuration"""
        return cls.MONGO_NODES[0]
