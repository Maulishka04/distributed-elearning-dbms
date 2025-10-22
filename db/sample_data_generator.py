"""
Sample Data Generator for E-Learning Platform
Inserts test data into the distributed database
"""

import sys
import random
from datetime import datetime, timedelta
from faker import Faker

# Add parent directory to path for imports
sys.path.append('..')

from postgres_scripts.user_crud import UserCRUD
from postgres_scripts.course_crud import CourseCRUD
from postgres_scripts.enrollment_crud import EnrollmentCRUD
from postgres_scripts.payment_crud import PaymentCRUD
from mongo_scripts.connection_manager import get_mongo_manager, CourseContentManager, UserPreferencesManager

fake = Faker()


class SampleDataGenerator:
    """Generate and insert sample data for testing"""
    
    def __init__(self):
        self.user_crud = UserCRUD()
        self.course_crud = CourseCRUD()
        self.enrollment_crud = EnrollmentCRUD()
        self.payment_crud = PaymentCRUD()
        
        # MongoDB managers
        mongo_manager = get_mongo_manager()
        self.content_manager = CourseContentManager(mongo_manager)
        self.preferences_manager = UserPreferencesManager(mongo_manager)
        
        # Storage for generated IDs
        self.student_ids = []
        self.instructor_ids = []
        self.category_ids = []
        self.course_ids = []
        self.regions = ['north_america', 'europe', 'asia']
    
    def generate_users(self, num_students: int = 100, num_instructors: int = 20):
        """Generate sample users (students and instructors)"""
        print(f"\nGenerating {num_students} students and {num_instructors} instructors...")
        
        # Generate students
        for i in range(num_students):
            region = random.choice(self.regions)
            try:
                user_id = self.user_crud.create_user(
                    email=fake.email(),
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type='student',
                    region=region,
                    country=fake.country(),
                    city=fake.city(),
                    phone=fake.phone_number()
                )
                self.student_ids.append((user_id, region))
                
                # Create user preferences in MongoDB
                self.preferences_manager.create_preferences(
                    user_id=user_id,
                    preferences={
                        'learning': {
                            'preferred_categories': random.sample(
                                ['programming', 'data_science', 'business', 'design'],
                                k=random.randint(1, 3)
                            ),
                            'difficulty_level': random.choice(['beginner', 'intermediate', 'advanced']),
                            'learning_pace': random.choice(['slow', 'moderate', 'fast'])
                        },
                        'notifications': {
                            'email': True,
                            'push': random.choice([True, False]),
                            'course_updates': True,
                            'promotional': random.choice([True, False])
                        },
                        'wishlist': [],
                        'recently_viewed': []
                    }
                )
                
                if (i + 1) % 20 == 0:
                    print(f"  Created {i + 1} students...")
            except Exception as e:
                print(f"  Error creating student {i + 1}: {e}")
        
        # Generate instructors
        for i in range(num_instructors):
            region = random.choice(self.regions)
            try:
                user_id = self.user_crud.create_user(
                    email=fake.email(),
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type='instructor',
                    region=region,
                    country=fake.country(),
                    city=fake.city(),
                    phone=fake.phone_number()
                )
                self.instructor_ids.append((user_id, region))
                print(f"  Created instructor {i + 1}")
            except Exception as e:
                print(f"  Error creating instructor {i + 1}: {e}")
        
        print(f"✓ Created {len(self.student_ids)} students and {len(self.instructor_ids)} instructors")
    
    def generate_categories(self):
        """Generate course categories"""
        print("\nGenerating course categories...")
        
        categories = [
            ('Programming', 'Learn to code in various languages'),
            ('Data Science', 'Master data analysis and machine learning'),
            ('Web Development', 'Build modern web applications'),
            ('Mobile Development', 'Create mobile apps for iOS and Android'),
            ('Business', 'Business and entrepreneurship courses'),
            ('Design', 'Graphic design, UX/UI, and more'),
            ('Marketing', 'Digital marketing and growth strategies'),
            ('Personal Development', 'Self-improvement and productivity')
        ]
        
        region = random.choice(self.regions)
        
        for name, description in categories:
            try:
                category_id = self.course_crud.create_category(
                    region=region,
                    category_name=name,
                    description=description
                )
                self.category_ids.append((category_id, region))
                print(f"  Created category: {name}")
            except Exception as e:
                print(f"  Error creating category {name}: {e}")
        
        print(f"✓ Created {len(self.category_ids)} categories")
    
    def generate_courses(self, num_courses: int = 50):
        """Generate sample courses"""
        print(f"\nGenerating {num_courses} courses...")
        
        if not self.instructor_ids or not self.category_ids:
            print("  Error: Must generate instructors and categories first")
            return
        
        course_levels = ['beginner', 'intermediate', 'advanced']
        
        for i in range(num_courses):
            instructor_id, region = random.choice(self.instructor_ids)
            category_id, _ = random.choice(self.category_ids)
            
            try:
                course_id = self.course_crud.create_course(
                    course_code=f"COURSE-{fake.unique.random_number(digits=6)}",
                    title=fake.catch_phrase() + " Masterclass",
                    description=fake.paragraph(nb_sentences=5),
                    instructor_id=instructor_id,
                    region=region,
                    category_id=category_id,
                    level=random.choice(course_levels),
                    price=round(random.uniform(19.99, 199.99), 2),
                    duration_hours=random.randint(5, 40)
                )
                
                # Add modules and lessons
                num_modules = random.randint(3, 8)
                for module_order in range(1, num_modules + 1):
                    module_id = self.course_crud.create_course_module(
                        course_id=course_id,
                        region=region,
                        module_title=f"Module {module_order}: {fake.catch_phrase()}",
                        module_order=module_order,
                        description=fake.sentence()
                    )
                    
                    # Add lessons to module
                    num_lessons = random.randint(3, 7)
                    for lesson_order in range(1, num_lessons + 1):
                        lesson_type = random.choice(['video', 'reading', 'quiz'])
                        content_id = f"content_{fake.uuid4()}"
                        
                        lesson_id = self.course_crud.create_course_lesson(
                            module_id=module_id,
                            region=region,
                            lesson_title=f"Lesson {lesson_order}: {fake.catch_phrase()}",
                            lesson_order=lesson_order,
                            lesson_type=lesson_type,
                            content_id=content_id,
                            duration_minutes=random.randint(5, 30),
                            is_preview=(lesson_order == 1)  # First lesson is preview
                        )
                        
                        # Add content to MongoDB
                        if lesson_type == 'video':
                            self.content_manager.add_video_content(
                                content_id=content_id,
                                course_id=course_id,
                                lesson_id=lesson_id,
                                title=f"Video: {fake.catch_phrase()}",
                                video_url=f"https://videos.example.com/{fake.uuid4()}.mp4",
                                duration_seconds=random.randint(300, 1800),
                                thumbnail_url=f"https://images.example.com/{fake.uuid4()}.jpg"
                            )
                        elif lesson_type == 'reading':
                            self.content_manager.add_document_content(
                                content_id=content_id,
                                course_id=course_id,
                                lesson_id=lesson_id,
                                title=f"Reading: {fake.catch_phrase()}",
                                document_url=f"https://docs.example.com/{fake.uuid4()}.pdf",
                                document_type='pdf',
                                file_size_bytes=random.randint(100000, 5000000),
                                page_count=random.randint(5, 50)
                            )
                
                # Publish the course
                self.course_crud.publish_course(course_id, region)
                
                self.course_ids.append((course_id, region))
                
                if (i + 1) % 10 == 0:
                    print(f"  Created {i + 1} courses...")
            
            except Exception as e:
                print(f"  Error creating course {i + 1}: {e}")
        
        print(f"✓ Created {len(self.course_ids)} courses")
    
    def generate_enrollments(self, num_enrollments: int = 200):
        """Generate sample enrollments"""
        print(f"\nGenerating {num_enrollments} enrollments...")
        
        if not self.student_ids or not self.course_ids:
            print("  Error: Must generate students and courses first")
            return
        
        enrollments_created = 0
        
        for i in range(num_enrollments):
            student_id, student_region = random.choice(self.student_ids)
            course_id, course_region = random.choice(self.course_ids)
            
            try:
                # Use the student's region for sharding
                enrollment_id = self.enrollment_crud.enroll_user(
                    user_id=student_id,
                    course_id=course_id,
                    region=student_region
                )
                
                # Simulate some progress
                if random.random() > 0.3:  # 70% have some progress
                    progress = self.enrollment_crud.get_course_progress(
                        enrollment_id=enrollment_id,
                        region=student_region
                    )
                    
                    # Mark some lessons as complete
                    for lesson in random.sample(progress, k=min(len(progress), random.randint(1, len(progress)))):
                        self.enrollment_crud.mark_lesson_complete(
                            enrollment_id=enrollment_id,
                            lesson_id=lesson['lesson_id'],
                            region=student_region,
                            time_spent=random.randint(5, 30)
                        )
                
                # Add review for some enrollments
                if random.random() > 0.6:  # 40% have reviews
                    self.enrollment_crud.add_course_review(
                        enrollment_id=enrollment_id,
                        region=student_region,
                        rating=random.randint(3, 5),
                        review_text=fake.paragraph(nb_sentences=3)
                    )
                
                enrollments_created += 1
                
                if (i + 1) % 50 == 0:
                    print(f"  Created {i + 1} enrollments...")
            
            except Exception as e:
                # Enrollment might already exist
                pass
        
        print(f"✓ Created {enrollments_created} enrollments")
    
    def generate_transactions(self, num_transactions: int = 150):
        """Generate sample transactions"""
        print(f"\nGenerating {num_transactions} transactions...")
        
        if not self.student_ids or not self.course_ids:
            print("  Error: Must generate students and courses first")
            return
        
        transactions_created = 0
        
        for i in range(num_transactions):
            student_id, region = random.choice(self.student_ids)
            course_id, _ = random.choice(self.course_ids)
            
            try:
                # Create payment method
                payment_method_id = self.payment_crud.add_payment_method(
                    user_id=student_id,
                    region=region,
                    method_type='credit_card',
                    card_last_four=str(random.randint(1000, 9999)),
                    card_brand=random.choice(['Visa', 'Mastercard', 'Amex']),
                    expiry_month=random.randint(1, 12),
                    expiry_year=random.randint(2024, 2029),
                    is_default=True
                )
                
                # Create transaction
                transaction_id = self.payment_crud.create_transaction(
                    user_id=student_id,
                    course_id=course_id,
                    region=region,
                    amount=round(random.uniform(19.99, 199.99), 2),
                    payment_method_id=payment_method_id
                )
                
                # Complete most transactions
                if random.random() > 0.1:  # 90% success rate
                    self.payment_crud.complete_transaction(
                        transaction_id=transaction_id,
                        region=region,
                        gateway_transaction_id=f"stripe_{fake.uuid4()}"
                    )
                else:
                    self.payment_crud.fail_transaction(
                        transaction_id=transaction_id,
                        region=region
                    )
                
                transactions_created += 1
                
                if (i + 1) % 30 == 0:
                    print(f"  Created {i + 1} transactions...")
            
            except Exception as e:
                print(f"  Error creating transaction {i + 1}: {e}")
        
        print(f"✓ Created {transactions_created} transactions")
    
    def run_all(self):
        """Generate all sample data"""
        print("\n" + "="*60)
        print("E-Learning Platform - Sample Data Generator")
        print("="*60)
        
        try:
            self.generate_users(num_students=100, num_instructors=20)
            self.generate_categories()
            self.generate_courses(num_courses=50)
            self.generate_enrollments(num_enrollments=200)
            self.generate_transactions(num_transactions=150)
            
            print("\n" + "="*60)
            print("✓ Sample data generation completed successfully!")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ Error during data generation: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    generator = SampleDataGenerator()
    generator.run_all()
