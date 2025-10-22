"""
MongoDB Connection Manager with Connection Pooling
Handles unstructured data like course content and user preferences
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime
from ..config.database_config import DatabaseConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoConnectionManager:
    """Manages MongoDB connections with connection pooling"""
    
    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._db = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        config = DatabaseConfig.get_mongo_config()
        
        try:
            # Build connection string
            if config.user and config.password:
                connection_string = (
                    f"mongodb://{config.user}:{config.password}@"
                    f"{config.host}:{config.port}/{config.database}"
                )
            else:
                connection_string = f"mongodb://{config.host}:{config.port}"
            
            # Add replica set if configured
            if config.replica_set:
                connection_string += f"?replicaSet={config.replica_set}"
            
            # Create client with connection pooling
            self._client = MongoClient(
                connection_string,
                maxPoolSize=DatabaseConfig.MONGO_MAX_POOL_SIZE,
                minPoolSize=DatabaseConfig.MONGO_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Get database
            self._db = self._client[config.database]
            
            # Test connection
            self._client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {config.database}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            self._initialize_connection()
        return self._db
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self.db[collection_name]
    
    def health_check(self) -> bool:
        """Check MongoDB connection health"""
        try:
            self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")
            self._client = None
            self._db = None


class CourseContentManager:
    """Manages course content in MongoDB"""
    
    def __init__(self, mongo_manager: MongoConnectionManager):
        self.mongo_manager = mongo_manager
        self.collection = mongo_manager.get_collection('course_content')
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        self.collection.create_index('content_id', unique=True)
        self.collection.create_index('course_id')
        self.collection.create_index('lesson_id')
        self.collection.create_index('content_type')
        self.collection.create_index([('course_id', 1), ('lesson_id', 1)])
    
    def create_content(self, content_data: Dict[str, Any]) -> str:
        """
        Create new course content
        
        Args:
            content_data: Dictionary containing content information
        
        Returns:
            Content ID
        """
        content_data['created_at'] = datetime.utcnow()
        content_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.insert_one(content_data)
        logger.info(f"Created course content: {result.inserted_id}")
        return str(result.inserted_id)
    
    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        return self.collection.find_one({'content_id': content_id})
    
    def get_content_by_lesson(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Get content for a specific lesson"""
        return self.collection.find_one({'lesson_id': lesson_id})
    
    def get_course_contents(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all content for a course"""
        return list(self.collection.find({'course_id': course_id}))
    
    def update_content(self, content_id: str, update_data: Dict[str, Any]) -> bool:
        """Update course content"""
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'content_id': content_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_content(self, content_id: str) -> bool:
        """Delete course content"""
        result = self.collection.delete_one({'content_id': content_id})
        return result.deleted_count > 0
    
    def add_video_content(
        self,
        content_id: str,
        course_id: str,
        lesson_id: str,
        title: str,
        video_url: str,
        duration_seconds: int,
        thumbnail_url: Optional[str] = None,
        subtitles: Optional[List[Dict[str, str]]] = None,
        quality_options: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Add video content"""
        content_data = {
            'content_id': content_id,
            'course_id': course_id,
            'lesson_id': lesson_id,
            'content_type': 'video',
            'title': title,
            'video_url': video_url,
            'duration_seconds': duration_seconds,
            'thumbnail_url': thumbnail_url,
            'subtitles': subtitles or [],
            'quality_options': quality_options or [],
            'views': 0,
            'metadata': {
                'format': 'mp4',
                'encoding': 'h264'
            }
        }
        return self.create_content(content_data)
    
    def add_document_content(
        self,
        content_id: str,
        course_id: str,
        lesson_id: str,
        title: str,
        document_url: str,
        document_type: str,
        file_size_bytes: int,
        page_count: Optional[int] = None
    ) -> str:
        """Add document content (PDF, etc.)"""
        content_data = {
            'content_id': content_id,
            'course_id': course_id,
            'lesson_id': lesson_id,
            'content_type': 'document',
            'title': title,
            'document_url': document_url,
            'document_type': document_type,
            'file_size_bytes': file_size_bytes,
            'page_count': page_count,
            'downloads': 0
        }
        return self.create_content(content_data)
    
    def increment_views(self, content_id: str) -> bool:
        """Increment view count for video content"""
        result = self.collection.update_one(
            {'content_id': content_id, 'content_type': 'video'},
            {'$inc': {'views': 1}}
        )
        return result.modified_count > 0
    
    def increment_downloads(self, content_id: str) -> bool:
        """Increment download count for document content"""
        result = self.collection.update_one(
            {'content_id': content_id, 'content_type': 'document'},
            {'$inc': {'downloads': 1}}
        )
        return result.modified_count > 0


class UserPreferencesManager:
    """Manages user preferences in MongoDB"""
    
    def __init__(self, mongo_manager: MongoConnectionManager):
        self.mongo_manager = mongo_manager
        self.collection = mongo_manager.get_collection('user_preferences')
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        self.collection.create_index('user_id', unique=True)
    
    def create_preferences(self, user_id: str, preferences: Dict[str, Any]) -> str:
        """Create user preferences"""
        pref_data = {
            'user_id': user_id,
            'preferences': preferences,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(pref_data)
        logger.info(f"Created user preferences for user: {user_id}")
        return str(result.inserted_id)
    
    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        return self.collection.find_one({'user_id': user_id})
    
    def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        result = self.collection.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'preferences': preferences,
                    'updated_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
    def update_preference_field(self, user_id: str, field: str, value: Any) -> bool:
        """Update a specific preference field"""
        result = self.collection.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    f'preferences.{field}': value,
                    'updated_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
    def delete_preferences(self, user_id: str) -> bool:
        """Delete user preferences"""
        result = self.collection.delete_one({'user_id': user_id})
        return result.deleted_count > 0
    
    def set_learning_preferences(
        self,
        user_id: str,
        preferred_categories: List[str],
        preferred_languages: List[str],
        difficulty_level: str,
        learning_pace: str
    ) -> bool:
        """Set learning preferences"""
        return self.update_preferences(user_id, {
            'learning': {
                'preferred_categories': preferred_categories,
                'preferred_languages': preferred_languages,
                'difficulty_level': difficulty_level,
                'learning_pace': learning_pace
            }
        })
    
    def set_notification_preferences(
        self,
        user_id: str,
        email_notifications: bool,
        push_notifications: bool,
        course_updates: bool,
        promotional: bool
    ) -> bool:
        """Set notification preferences"""
        return self.update_preferences(user_id, {
            'notifications': {
                'email': email_notifications,
                'push': push_notifications,
                'course_updates': course_updates,
                'promotional': promotional
            }
        })
    
    def add_recently_viewed(self, user_id: str, course_id: str) -> bool:
        """Add course to recently viewed list"""
        result = self.collection.update_one(
            {'user_id': user_id},
            {
                '$push': {
                    'preferences.recently_viewed': {
                        '$each': [{'course_id': course_id, 'viewed_at': datetime.utcnow()}],
                        '$slice': -20  # Keep last 20 items
                    }
                },
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
    def add_to_wishlist(self, user_id: str, course_id: str) -> bool:
        """Add course to wishlist"""
        result = self.collection.update_one(
            {'user_id': user_id},
            {
                '$addToSet': {'preferences.wishlist': course_id},
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
    def remove_from_wishlist(self, user_id: str, course_id: str) -> bool:
        """Remove course from wishlist"""
        result = self.collection.update_one(
            {'user_id': user_id},
            {
                '$pull': {'preferences.wishlist': course_id},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0


# Singleton instance
_mongo_manager: Optional[MongoConnectionManager] = None


def get_mongo_manager() -> MongoConnectionManager:
    """Get singleton instance of MongoConnectionManager"""
    global _mongo_manager
    if _mongo_manager is None:
        _mongo_manager = MongoConnectionManager()
    return _mongo_manager


def close_mongo_connection():
    """Close MongoDB connection"""
    global _mongo_manager
    if _mongo_manager:
        _mongo_manager.close_connection()
        _mongo_manager = None
