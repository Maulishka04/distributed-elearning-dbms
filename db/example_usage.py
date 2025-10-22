"""
Example Usage of the Distributed Database Layer
Demonstrates common operations and best practices
"""

import sys
from datetime import datetime

# Add parent directory to path
sys.path.append('..')

from db.postgres_scripts.user_crud import UserCRUD
from db.postgres_scripts.course_crud import CourseCRUD
from db.postgres_scripts.enrollment_crud import EnrollmentCRUD
from db.postgres_scripts.payment_crud import PaymentCRUD
from db.mongo_scripts.connection_manager import (
    get_mongo_manager,
    CourseContentManager,
    UserPreferencesManager
)


def example_user_operations():
    """Demonstrate user management operations"""
    print("\n" + "="*60)
    print("EXAMPLE 1: User Management")
    print("="*60)
    
    user_crud = UserCRUD()
    
    # Create a new student
    print("\n1. Creating a new student...")
    student_id = user_crud.create_user(
        email="alice.smith@example.com",
        password="securepassword123",
        first_name="Alice",
        last_name="Smith",
        user_type="student",
        region="north_america",
        country="United States",
        city="San Francisco",
        phone="+1-415-555-0100"
    )
    print(f"✓ Created student with ID: {student_id}")
    
    # Retrieve user details
    print("\n2. Retrieving user details...")
    user = user_crud.get_user_by_email("alice.smith@example.com", "north_america")
    print(f"✓ Found user: {user['first_name']} {user['last_name']}")
    print(f"  Email: {user['email']}")
    print(f"  Type: {user['user_type']}")
    print(f"  Region: {user['region']}")
    
    # Update user profile
    print("\n3. Updating user profile...")
    user_crud.update_user_profile(
        user_id=student_id,
        region="north_america",
        profile_data={
            "bio": "Passionate about learning data science and machine learning",
            "timezone": "America/Los_Angeles",
            "language_preference": "en"
        }
    )
    print("✓ Profile updated")
    
    # Set user preferences in MongoDB
    print("\n4. Setting user preferences in MongoDB...")
    mongo_manager = get_mongo_manager()
    prefs_manager = UserPreferencesManager(mongo_manager)
    
    prefs_manager.set_learning_preferences(
        user_id=student_id,
        preferred_categories=["data_science", "programming", "machine_learning"],
        preferred_languages=["English"],
        difficulty_level="intermediate",
        learning_pace="moderate"
    )
    print("✓ Preferences saved to MongoDB")
    
    return student_id


def example_course_operations():
    """Demonstrate course management operations"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Course Management")
    print("="*60)
    
    course_crud = CourseCRUD()
    user_crud = UserCRUD()
    
    # Create instructor
    print("\n1. Creating instructor account...")
    instructor_id = user_crud.create_user(
        email="prof.johnson@example.com",
        password="instructor123",
        first_name="Robert",
        last_name="Johnson",
        user_type="instructor",
        region="north_america",
        country="United States",
        city="Boston"
    )
    print(f"✓ Created instructor with ID: {instructor_id}")
    
    # Create category
    print("\n2. Creating course category...")
    category_id = course_crud.create_category(
        region="north_america",
        category_name="Data Science & Analytics",
        description="Master data analysis, visualization, and machine learning"
    )
    print(f"✓ Created category with ID: {category_id}")
    
    # Create course
    print("\n3. Creating a new course...")
    course_id = course_crud.create_course(
        course_code="DS-101",
        title="Data Science Fundamentals",
        description="Learn the foundations of data science including Python, statistics, and machine learning",
        instructor_id=instructor_id,
        region="north_america",
        category_id=category_id,
        level="beginner",
        price=79.99,
        duration_hours=25
    )
    print(f"✓ Created course with ID: {course_id}")
    
    # Add course modules and lessons
    print("\n4. Adding course curriculum...")
    
    # Module 1
    module1_id = course_crud.create_course_module(
        course_id=course_id,
        region="north_america",
        module_title="Introduction to Data Science",
        module_order=1,
        description="Get started with data science concepts and tools"
    )
    
    lesson1_id = course_crud.create_course_lesson(
        module_id=module1_id,
        region="north_america",
        lesson_title="What is Data Science?",
        lesson_order=1,
        lesson_type="video",
        content_id="content_ds101_001",
        duration_minutes=15,
        is_preview=True
    )
    
    lesson2_id = course_crud.create_course_lesson(
        module_id=module1_id,
        region="north_america",
        lesson_title="Setting Up Your Environment",
        lesson_order=2,
        lesson_type="video",
        content_id="content_ds101_002",
        duration_minutes=20
    )
    
    # Module 2
    module2_id = course_crud.create_course_module(
        course_id=course_id,
        region="north_america",
        module_title="Python for Data Science",
        module_order=2,
        description="Learn Python programming essentials"
    )
    
    lesson3_id = course_crud.create_course_lesson(
        module_id=module2_id,
        region="north_america",
        lesson_title="Python Basics",
        lesson_order=1,
        lesson_type="video",
        content_id="content_ds101_003",
        duration_minutes=25
    )
    
    print("✓ Added 2 modules with 3 lessons")
    
    # Add course content to MongoDB
    print("\n5. Adding course content to MongoDB...")
    content_manager = CourseContentManager(get_mongo_manager())
    
    content_manager.add_video_content(
        content_id="content_ds101_001",
        course_id=course_id,
        lesson_id=lesson1_id,
        title="What is Data Science? - Introduction",
        video_url="https://videos.elearning.com/ds101/intro.mp4",
        duration_seconds=900,
        thumbnail_url="https://images.elearning.com/ds101/intro_thumb.jpg",
        quality_options=[
            {"quality": "1080p", "url": "https://videos.elearning.com/ds101/intro_1080.mp4"},
            {"quality": "720p", "url": "https://videos.elearning.com/ds101/intro_720.mp4"}
        ]
    )
    
    content_manager.add_video_content(
        content_id="content_ds101_002",
        course_id=course_id,
        lesson_id=lesson2_id,
        title="Setting Up Your Environment",
        video_url="https://videos.elearning.com/ds101/setup.mp4",
        duration_seconds=1200,
        thumbnail_url="https://images.elearning.com/ds101/setup_thumb.jpg"
    )
    
    print("✓ Course content stored in MongoDB")
    
    # Publish course
    print("\n6. Publishing course...")
    course_crud.publish_course(course_id, "north_america")
    print("✓ Course published and available to students")
    
    # Get course details
    print("\n7. Retrieving course details...")
    course_details = course_crud.get_course_by_id(course_id, "north_america")
    print(f"✓ Course: {course_details['title']}")
    print(f"  Code: {course_details['course_code']}")
    print(f"  Instructor: {course_details['instructor_name']}")
    print(f"  Price: ${course_details['price']}")
    print(f"  Duration: {course_details['duration_hours']} hours")
    
    return course_id, instructor_id


def example_enrollment_operations(student_id, course_id):
    """Demonstrate enrollment and progress tracking"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Enrollment & Progress Tracking")
    print("="*60)
    
    enrollment_crud = EnrollmentCRUD()
    
    # Enroll student in course
    print("\n1. Enrolling student in course...")
    enrollment_id = enrollment_crud.enroll_user(
        user_id=student_id,
        course_id=course_id,
        region="north_america"
    )
    print(f"✓ Student enrolled with enrollment ID: {enrollment_id}")
    
    # Get course progress
    print("\n2. Checking initial course progress...")
    progress = enrollment_crud.get_course_progress(
        enrollment_id=enrollment_id,
        region="north_america"
    )
    print(f"✓ Found {len(progress)} lessons to complete")
    
    # Mark some lessons as complete
    print("\n3. Marking lessons as complete...")
    if len(progress) > 0:
        # Complete first lesson
        enrollment_crud.mark_lesson_complete(
            enrollment_id=enrollment_id,
            lesson_id=progress[0]['lesson_id'],
            region="north_america",
            time_spent=15
        )
        print(f"  ✓ Completed: {progress[0]['lesson_title']}")
        
        if len(progress) > 1:
            # Complete second lesson
            enrollment_crud.mark_lesson_complete(
                enrollment_id=enrollment_id,
                lesson_id=progress[1]['lesson_id'],
                region="north_america",
                time_spent=20
            )
            print(f"  ✓ Completed: {progress[1]['lesson_title']}")
    
    # Check enrollment status
    print("\n4. Checking enrollment status...")
    enrollment_details = enrollment_crud.get_enrollment_by_id(
        enrollment_id=enrollment_id,
        region="north_america"
    )
    print(f"✓ Enrollment Status:")
    print(f"  Course: {enrollment_details['course_title']}")
    print(f"  Progress: {enrollment_details['progress_percentage']:.2f}%")
    print(f"  Status: {enrollment_details['status']}")
    
    # Add course review
    print("\n5. Adding course review...")
    enrollment_crud.add_course_review(
        enrollment_id=enrollment_id,
        region="north_america",
        rating=5,
        review_text="Excellent course! The instructor explains concepts clearly and the hands-on exercises are very helpful."
    )
    print("✓ Review added")
    
    return enrollment_id


def example_payment_operations(student_id, course_id):
    """Demonstrate payment processing"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Payment Processing")
    print("="*60)
    
    payment_crud = PaymentCRUD()
    
    # Add payment method
    print("\n1. Adding payment method...")
    payment_method_id = payment_crud.add_payment_method(
        user_id=student_id,
        region="north_america",
        method_type="credit_card",
        card_last_four="4242",
        card_brand="Visa",
        expiry_month=12,
        expiry_year=2027,
        billing_address="123 Main St, San Francisco, CA 94102",
        is_default=True
    )
    print(f"✓ Payment method added: Visa ending in 4242")
    
    # Create transaction
    print("\n2. Creating payment transaction...")
    transaction_id = payment_crud.create_transaction(
        user_id=student_id,
        course_id=course_id,
        region="north_america",
        amount=79.99,
        payment_method_id=payment_method_id,
        currency="USD",
        payment_gateway="stripe"
    )
    print(f"✓ Transaction created: {transaction_id}")
    
    # Complete transaction
    print("\n3. Processing payment...")
    invoice_id = payment_crud.complete_transaction(
        transaction_id=transaction_id,
        region="north_america",
        gateway_transaction_id="ch_1234567890_stripe"
    )
    print(f"✓ Payment completed successfully")
    print(f"✓ Invoice generated: {invoice_id}")
    
    # Get invoice details
    print("\n4. Retrieving invoice...")
    invoice = payment_crud.get_invoice_by_transaction(
        transaction_id=transaction_id,
        region="north_america"
    )
    print(f"✓ Invoice Details:")
    print(f"  Invoice Number: {invoice['invoice_number']}")
    print(f"  Subtotal: ${invoice['subtotal']:.2f}")
    print(f"  Tax: ${invoice['tax_amount']:.2f}")
    print(f"  Total: ${invoice['total_amount']:.2f}")
    print(f"  Status: {invoice['status']}")
    
    # Get transaction history
    print("\n5. Getting transaction history...")
    transactions = payment_crud.get_user_transactions(
        user_id=student_id,
        region="north_america",
        limit=5
    )
    print(f"✓ Found {len(transactions)} transaction(s):")
    for txn in transactions:
        print(f"  - {txn['course_title']}: ${txn['amount']:.2f} ({txn['status']})")


def example_search_operations():
    """Demonstrate search functionality"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Search & Discovery")
    print("="*60)
    
    course_crud = CourseCRUD()
    
    # Search courses
    print("\n1. Searching for Data Science courses...")
    results = course_crud.search_courses(
        region="north_america",
        search_term="Data",
        min_rating=0.0
    )
    print(f"✓ Found {len(results)} course(s):")
    for course in results[:5]:  # Show first 5
        print(f"  - {course['title']} (Rating: {course['rating']:.1f}, ${course['price']:.2f})")
    
    # Get popular courses
    print("\n2. Getting popular courses...")
    popular = course_crud.get_popular_courses(
        region="north_america",
        limit=5
    )
    print(f"✓ Top {len(popular)} popular course(s):")
    for course in popular:
        print(f"  - {course['title']} ({course['total_enrollments']} enrollments)")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("DISTRIBUTED DATABASE LAYER - USAGE EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates common operations with the")
    print("distributed database layer for the e-learning platform.")
    
    try:
        # Example 1: User Management
        student_id = example_user_operations()
        
        # Example 2: Course Management
        course_id, instructor_id = example_course_operations()
        
        # Example 3: Enrollment & Progress
        enrollment_id = example_enrollment_operations(student_id, course_id)
        
        # Example 4: Payment Processing
        example_payment_operations(student_id, course_id)
        
        # Example 5: Search Operations
        example_search_operations()
        
        # Summary
        print("\n" + "="*60)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nKey Takeaways:")
        print("1. User data is sharded by geographic region")
        print("2. Course content is stored in MongoDB")
        print("3. Progress tracking happens automatically via triggers")
        print("4. All operations use connection pooling")
        print("5. Transactions are properly managed")
        print("\nRefer to DATABASE_GUIDE.md for more details!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
