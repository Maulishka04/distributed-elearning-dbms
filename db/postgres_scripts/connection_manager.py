"""
PostgreSQL Connection Manager with Connection Pooling
Implements master-slave replication and sharding by region
"""

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List, Any, Tuple
from contextlib import contextmanager
import logging
from ..config.database_config import DatabaseConfig, PostgresNodeConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresConnectionManager:
    """Manages PostgreSQL connections with pooling and replication"""
    
    def __init__(self):
        self._master_pools: Dict[int, pool.SimpleConnectionPool] = {}
        self._slave_pools: Dict[int, List[pool.SimpleConnectionPool]] = {}
        self._initialize_pools()
    
    def _initialize_pools(self):
        """Initialize connection pools for all master and slave nodes"""
        logger.info("Initializing PostgreSQL connection pools...")
        
        # Initialize master node pools
        for node in DatabaseConfig.get_all_master_nodes():
            try:
                master_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=DatabaseConfig.POSTGRES_POOL_SIZE,
                    host=node.host,
                    port=node.port,
                    database=node.database,
                    user=node.user,
                    password=node.password
                )
                self._master_pools[node.shard_id] = master_pool
                logger.info(f"Initialized master pool for shard {node.shard_id} ({node.region})")
            except Exception as e:
                logger.error(f"Failed to initialize master pool for shard {node.shard_id}: {e}")
                raise
        
        # Initialize slave node pools
        for node in DatabaseConfig.POSTGRES_SLAVE_NODES:
            try:
                slave_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=DatabaseConfig.POSTGRES_POOL_SIZE,
                    host=node.host,
                    port=node.port,
                    database=node.database,
                    user=node.user,
                    password=node.password
                )
                
                if node.shard_id not in self._slave_pools:
                    self._slave_pools[node.shard_id] = []
                
                self._slave_pools[node.shard_id].append(slave_pool)
                logger.info(f"Initialized slave pool for shard {node.shard_id} ({node.region})")
            except Exception as e:
                logger.error(f"Failed to initialize slave pool for shard {node.shard_id}: {e}")
    
    def _get_shard_id(self, region: str) -> int:
        """Get shard ID for a given region"""
        shard_id = DatabaseConfig.REGION_MAPPING.get(region.lower())
        if not shard_id:
            raise ValueError(f"Unknown region: {region}")
        return shard_id
    
    @contextmanager
    def get_connection(self, region: str, read_only: bool = False):
        """
        Get a database connection from the appropriate pool
        
        Args:
            region: Geographic region for sharding
            read_only: If True, use slave node; if False, use master node
        
        Yields:
            Database connection
        """
        shard_id = self._get_shard_id(region)
        conn = None
        
        try:
            if read_only and shard_id in self._slave_pools and self._slave_pools[shard_id]:
                # Use slave node for read operations (load balancing)
                slave_pool = self._slave_pools[shard_id][0]  # Simple round-robin can be implemented
                conn = slave_pool.getconn()
                logger.debug(f"Retrieved slave connection for shard {shard_id}")
            else:
                # Use master node for write operations or if no slave available
                if shard_id not in self._master_pools:
                    raise ValueError(f"No master pool available for shard {shard_id}")
                conn = self._master_pools[shard_id].getconn()
                logger.debug(f"Retrieved master connection for shard {shard_id}")
            
            yield conn
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        
        finally:
            if conn:
                if read_only and shard_id in self._slave_pools and self._slave_pools[shard_id]:
                    self._slave_pools[shard_id][0].putconn(conn)
                else:
                    if shard_id in self._master_pools:
                        self._master_pools[shard_id].putconn(conn)
    
    def execute_query(
        self,
        region: str,
        query: str,
        params: Optional[Tuple] = None,
        read_only: bool = False,
        fetch_one: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query
        
        Args:
            region: Geographic region for sharding
            query: SQL query to execute
            params: Query parameters
            read_only: Whether this is a read-only query
            fetch_one: If True, return only first result
        
        Returns:
            Query results as list of dictionaries
        """
        with self.get_connection(region, read_only) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    conn.commit()
                    return None
                
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
    
    def execute_many(
        self,
        region: str,
        query: str,
        params_list: List[Tuple]
    ) -> None:
        """
        Execute a query multiple times with different parameters
        
        Args:
            region: Geographic region for sharding
            query: SQL query to execute
            params_list: List of parameter tuples
        """
        with self.get_connection(region, read_only=False) as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()
    
    def call_procedure(
        self,
        region: str,
        procedure_name: str,
        params: Optional[Tuple] = None,
        read_only: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Call a stored procedure
        
        Args:
            region: Geographic region for sharding
            procedure_name: Name of the stored procedure
            params: Procedure parameters
            read_only: Whether this is a read-only procedure
        
        Returns:
            Procedure results
        """
        with self.get_connection(region, read_only) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.callproc(procedure_name, params)
                
                try:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                except psycopg2.ProgrammingError:
                    # Procedure doesn't return results
                    conn.commit()
                    return None
    
    def execute_transaction(
        self,
        region: str,
        queries: List[Tuple[str, Optional[Tuple]]]
    ) -> None:
        """
        Execute multiple queries in a transaction
        
        Args:
            region: Geographic region for sharding
            queries: List of (query, params) tuples
        """
        with self.get_connection(region, read_only=False) as conn:
            with conn.cursor() as cursor:
                try:
                    for query, params in queries:
                        cursor.execute(query, params)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Transaction failed: {e}")
                    raise
    
    def close_all_connections(self):
        """Close all connection pools"""
        logger.info("Closing all PostgreSQL connection pools...")
        
        for shard_id, master_pool in self._master_pools.items():
            master_pool.closeall()
            logger.info(f"Closed master pool for shard {shard_id}")
        
        for shard_id, slave_pools in self._slave_pools.items():
            for slave_pool in slave_pools:
                slave_pool.closeall()
            logger.info(f"Closed slave pools for shard {shard_id}")
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health of all database connections
        
        Returns:
            Dictionary with health status of each node
        """
        health_status = {}
        
        # Check master nodes
        for shard_id, master_pool in self._master_pools.items():
            try:
                conn = master_pool.getconn()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                master_pool.putconn(conn)
                health_status[f"master_shard_{shard_id}"] = True
            except Exception as e:
                logger.error(f"Health check failed for master shard {shard_id}: {e}")
                health_status[f"master_shard_{shard_id}"] = False
        
        # Check slave nodes
        for shard_id, slave_pools in self._slave_pools.items():
            for idx, slave_pool in enumerate(slave_pools):
                try:
                    conn = slave_pool.getconn()
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                    slave_pool.putconn(conn)
                    health_status[f"slave_shard_{shard_id}_{idx}"] = True
                except Exception as e:
                    logger.error(f"Health check failed for slave shard {shard_id}_{idx}: {e}")
                    health_status[f"slave_shard_{shard_id}_{idx}"] = False
        
        return health_status


# Singleton instance
_pg_manager: Optional[PostgresConnectionManager] = None


def get_postgres_manager() -> PostgresConnectionManager:
    """Get singleton instance of PostgresConnectionManager"""
    global _pg_manager
    if _pg_manager is None:
        _pg_manager = PostgresConnectionManager()
    return _pg_manager


def close_postgres_connections():
    """Close all PostgreSQL connections"""
    global _pg_manager
    if _pg_manager:
        _pg_manager.close_all_connections()
        _pg_manager = None
