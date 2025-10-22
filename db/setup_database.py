"""
Database Setup Script
Initialize PostgreSQL and MongoDB for the e-learning platform
"""

import sys
import os
import psycopg2
from pymongo import MongoClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.database_config import DatabaseConfig


class DatabaseSetup:
    """Setup databases and load schemas"""
    
    def __init__(self):
        self.config = DatabaseConfig()
    
    def setup_postgres(self):
        """Setup PostgreSQL databases and load schema"""
        print("\n" + "="*60)
        print("Setting up PostgreSQL Databases")
        print("="*60)
        
        # Read SQL scripts
        script_dir = os.path.join(os.path.dirname(__file__), 'postgres_scripts')
        
        with open(os.path.join(script_dir, 'schema.sql'), 'r') as f:
            schema_sql = f.read()
        
        with open(os.path.join(script_dir, 'stored_procedures.sql'), 'r') as f:
            procedures_sql = f.read()
        
        # Setup each master node
        for node in DatabaseConfig.POSTGRES_MASTER_NODES:
            print(f"\nSetting up {node.region} (Shard {node.shard_id}) - Master Node")
            print(f"  Host: {node.host}:{node.port}")
            print(f"  Database: {node.database}")
            
            try:
                # Connect to default postgres database first to create our database
                conn = psycopg2.connect(
                    host=node.host,
                    port=node.port,
                    database='postgres',
                    user=node.user,
                    password=node.password
                )
                conn.autocommit = True
                cursor = conn.cursor()
                
                # Create database if not exists
                cursor.execute(f"""
                    SELECT 1 FROM pg_database WHERE datname = '{node.database}'
                """)
                
                if not cursor.fetchone():
                    print(f"  Creating database: {node.database}")
                    cursor.execute(f"CREATE DATABASE {node.database}")
                else:
                    print(f"  Database already exists: {node.database}")
                
                cursor.close()
                conn.close()
                
                # Connect to our database and load schema
                conn = psycopg2.connect(
                    host=node.host,
                    port=node.port,
                    database=node.database,
                    user=node.user,
                    password=node.password
                )
                conn.autocommit = True
                cursor = conn.cursor()
                
                print("  Loading schema...")
                cursor.execute(schema_sql)
                
                print("  Loading stored procedures...")
                cursor.execute(procedures_sql)
                
                cursor.close()
                conn.close()
                
                print(f"  ✓ Successfully setup {node.region}")
                
            except Exception as e:
                print(f"  ✗ Error setting up {node.region}: {e}")
        
        print("\n✓ PostgreSQL setup completed")
    
    def setup_mongodb(self):
        """Setup MongoDB database and collections"""
        print("\n" + "="*60)
        print("Setting up MongoDB Database")
        print("="*60)
        
        config = DatabaseConfig.get_mongo_config()
        
        print(f"\nConnecting to MongoDB")
        print(f"  Host: {config.host}:{config.port}")
        print(f"  Database: {config.database}")
        
        try:
            # Build connection string
            if config.user and config.password:
                connection_string = (
                    f"mongodb://{config.user}:{config.password}@"
                    f"{config.host}:{config.port}/{config.database}"
                )
            else:
                connection_string = f"mongodb://{config.host}:{config.port}"
            
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            db = client[config.database]
            
            # Test connection
            client.admin.command('ping')
            print("  ✓ Connected to MongoDB")
            
            # Create collections with schema validation
            print("\n  Creating collections...")
            
            # Course Content Collection
            try:
                db.create_collection('course_content', validator={
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['content_id', 'course_id', 'lesson_id', 'content_type'],
                        'properties': {
                            'content_id': {'bsonType': 'string'},
                            'course_id': {'bsonType': 'string'},
                            'lesson_id': {'bsonType': 'string'},
                            'content_type': {
                                'enum': ['video', 'document', 'quiz', 'assignment']
                            },
                            'created_at': {'bsonType': 'date'},
                            'updated_at': {'bsonType': 'date'}
                        }
                    }
                })
                print("    ✓ Created course_content collection")
            except Exception as e:
                if 'already exists' in str(e):
                    print("    - course_content collection already exists")
                else:
                    raise
            
            # User Preferences Collection
            try:
                db.create_collection('user_preferences', validator={
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['user_id', 'preferences'],
                        'properties': {
                            'user_id': {'bsonType': 'string'},
                            'preferences': {'bsonType': 'object'},
                            'created_at': {'bsonType': 'date'},
                            'updated_at': {'bsonType': 'date'}
                        }
                    }
                })
                print("    ✓ Created user_preferences collection")
            except Exception as e:
                if 'already exists' in str(e):
                    print("    - user_preferences collection already exists")
                else:
                    raise
            
            # Create indexes
            print("\n  Creating indexes...")
            db.course_content.create_index('content_id', unique=True)
            db.course_content.create_index('course_id')
            db.course_content.create_index('lesson_id')
            db.user_preferences.create_index('user_id', unique=True)
            print("    ✓ Indexes created")
            
            client.close()
            print("\n✓ MongoDB setup completed")
            
        except Exception as e:
            print(f"  ✗ Error setting up MongoDB: {e}")
    
    def run_setup(self):
        """Run complete database setup"""
        print("\n" + "="*60)
        print("E-Learning Platform - Database Setup")
        print("="*60)
        
        try:
            self.setup_postgres()
            self.setup_mongodb()
            
            print("\n" + "="*60)
            print("✓ Database setup completed successfully!")
            print("="*60)
            print("\nNext steps:")
            print("1. Run sample_data_generator.py to populate with test data")
            print("2. Test the API endpoints")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error during setup: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    setup = DatabaseSetup()
    setup.run_setup()
