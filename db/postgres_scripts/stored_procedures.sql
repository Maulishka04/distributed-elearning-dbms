-- =====================================================
-- STORED PROCEDURES AND FUNCTIONS
-- =====================================================

-- =====================================================
-- USER MANAGEMENT PROCEDURES
-- =====================================================

-- Create new user with profile
CREATE OR REPLACE FUNCTION create_user_with_profile(
    p_email VARCHAR,
    p_password_hash VARCHAR,
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_user_type VARCHAR,
    p_region VARCHAR,
    p_country VARCHAR DEFAULT NULL,
    p_city VARCHAR DEFAULT NULL,
    p_phone VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Insert user
    INSERT INTO users (email, password_hash, first_name, last_name, user_type, region)
    VALUES (p_email, p_password_hash, p_first_name, p_last_name, p_user_type, p_region)
    RETURNING user_id INTO v_user_id;
    
    -- Insert profile
    INSERT INTO user_profiles (user_id, country, city, phone_number)
    VALUES (v_user_id, p_country, p_city, p_phone);
    
    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;

-- Get user by email with profile
CREATE OR REPLACE FUNCTION get_user_by_email(p_email VARCHAR)
RETURNS TABLE (
    user_id UUID,
    email VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    user_type VARCHAR,
    region VARCHAR,
    status VARCHAR,
    country VARCHAR,
    city VARCHAR,
    phone_number VARCHAR,
    profile_picture_url VARCHAR,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.user_id,
        u.email,
        u.first_name,
        u.last_name,
        u.user_type,
        u.region,
        u.status,
        up.country,
        up.city,
        up.phone_number,
        up.profile_picture_url,
        u.created_at
    FROM users u
    LEFT JOIN user_profiles up ON u.user_id = up.user_id
    WHERE u.email = p_email;
END;
$$ LANGUAGE plpgsql;

-- Update user last login
CREATE OR REPLACE FUNCTION update_user_login(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users
    SET last_login = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COURSE MANAGEMENT PROCEDURES
-- =====================================================

-- Create course with modules
CREATE OR REPLACE FUNCTION create_course(
    p_course_code VARCHAR,
    p_title VARCHAR,
    p_description TEXT,
    p_instructor_id UUID,
    p_category_id UUID,
    p_level VARCHAR,
    p_price DECIMAL,
    p_duration_hours INTEGER
)
RETURNS UUID AS $$
DECLARE
    v_course_id UUID;
BEGIN
    INSERT INTO courses (
        course_code, title, description, instructor_id, 
        category_id, level, price, duration_hours
    )
    VALUES (
        p_course_code, p_title, p_description, p_instructor_id,
        p_category_id, p_level, p_price, p_duration_hours
    )
    RETURNING course_id INTO v_course_id;
    
    RETURN v_course_id;
END;
$$ LANGUAGE plpgsql;

-- Get course details with instructor info
CREATE OR REPLACE FUNCTION get_course_details(p_course_id UUID)
RETURNS TABLE (
    course_id UUID,
    course_code VARCHAR,
    title VARCHAR,
    description TEXT,
    instructor_name VARCHAR,
    instructor_email VARCHAR,
    category_name VARCHAR,
    level VARCHAR,
    price DECIMAL,
    duration_hours INTEGER,
    rating DECIMAL,
    total_ratings INTEGER,
    total_enrollments BIGINT,
    status VARCHAR,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.course_id,
        c.course_code,
        c.title,
        c.description,
        CONCAT(u.first_name, ' ', u.last_name) as instructor_name,
        u.email as instructor_email,
        cc.category_name,
        c.level,
        c.price,
        c.duration_hours,
        c.rating,
        c.total_ratings,
        COUNT(e.enrollment_id) as total_enrollments,
        c.status,
        c.created_at
    FROM courses c
    JOIN users u ON c.instructor_id = u.user_id
    LEFT JOIN course_categories cc ON c.category_id = cc.category_id
    LEFT JOIN enrollments e ON c.course_id = e.course_id
    WHERE c.course_id = p_course_id
    GROUP BY c.course_id, u.user_id, cc.category_name;
END;
$$ LANGUAGE plpgsql;

-- Get popular courses
CREATE OR REPLACE FUNCTION get_popular_courses(p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
    course_id UUID,
    title VARCHAR,
    instructor_name VARCHAR,
    rating DECIMAL,
    total_enrollments BIGINT,
    price DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.course_id,
        c.title,
        CONCAT(u.first_name, ' ', u.last_name) as instructor_name,
        c.rating,
        COUNT(e.enrollment_id) as total_enrollments,
        c.price
    FROM courses c
    JOIN users u ON c.instructor_id = u.user_id
    LEFT JOIN enrollments e ON c.course_id = e.course_id
    WHERE c.status = 'published'
    GROUP BY c.course_id, u.user_id
    ORDER BY total_enrollments DESC, c.rating DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Search courses
CREATE OR REPLACE FUNCTION search_courses(
    p_search_term VARCHAR,
    p_category_id UUID DEFAULT NULL,
    p_min_rating DECIMAL DEFAULT 0,
    p_max_price DECIMAL DEFAULT NULL
)
RETURNS TABLE (
    course_id UUID,
    title VARCHAR,
    description TEXT,
    instructor_name VARCHAR,
    category_name VARCHAR,
    rating DECIMAL,
    price DECIMAL,
    total_enrollments BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.course_id,
        c.title,
        c.description,
        CONCAT(u.first_name, ' ', u.last_name) as instructor_name,
        cc.category_name,
        c.rating,
        c.price,
        COUNT(e.enrollment_id) as total_enrollments
    FROM courses c
    JOIN users u ON c.instructor_id = u.user_id
    LEFT JOIN course_categories cc ON c.category_id = cc.category_id
    LEFT JOIN enrollments e ON c.course_id = e.course_id
    WHERE c.status = 'published'
        AND (p_search_term IS NULL OR 
             c.title ILIKE '%' || p_search_term || '%' OR 
             c.description ILIKE '%' || p_search_term || '%')
        AND (p_category_id IS NULL OR c.category_id = p_category_id)
        AND c.rating >= p_min_rating
        AND (p_max_price IS NULL OR c.price <= p_max_price)
    GROUP BY c.course_id, u.user_id, cc.category_name
    ORDER BY c.rating DESC, total_enrollments DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ENROLLMENT PROCEDURES
-- =====================================================

-- Enroll user in course
CREATE OR REPLACE FUNCTION enroll_user(
    p_user_id UUID,
    p_course_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_enrollment_id UUID;
    v_max_enrollments INTEGER;
    v_current_enrollments INTEGER;
BEGIN
    -- Check if course has enrollment limit
    SELECT max_enrollments INTO v_max_enrollments
    FROM courses
    WHERE course_id = p_course_id;
    
    IF v_max_enrollments IS NOT NULL THEN
        -- Check current enrollments
        SELECT COUNT(*) INTO v_current_enrollments
        FROM enrollments
        WHERE course_id = p_course_id AND status = 'active';
        
        IF v_current_enrollments >= v_max_enrollments THEN
            RAISE EXCEPTION 'Course enrollment limit reached';
        END IF;
    END IF;
    
    -- Create enrollment
    INSERT INTO enrollments (user_id, course_id)
    VALUES (p_user_id, p_course_id)
    ON CONFLICT (user_id, course_id) DO NOTHING
    RETURNING enrollment_id INTO v_enrollment_id;
    
    -- Initialize lesson progress
    INSERT INTO lesson_progress (enrollment_id, lesson_id)
    SELECT v_enrollment_id, cl.lesson_id
    FROM course_lessons cl
    JOIN course_modules cm ON cl.module_id = cm.module_id
    WHERE cm.course_id = p_course_id;
    
    RETURN v_enrollment_id;
END;
$$ LANGUAGE plpgsql;

-- Get user enrollments
CREATE OR REPLACE FUNCTION get_user_enrollments(
    p_user_id UUID,
    p_status VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    enrollment_id UUID,
    course_id UUID,
    course_title VARCHAR,
    instructor_name VARCHAR,
    enrollment_date TIMESTAMP,
    progress_percentage DECIMAL,
    status VARCHAR,
    last_accessed TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.enrollment_id,
        c.course_id,
        c.title as course_title,
        CONCAT(u.first_name, ' ', u.last_name) as instructor_name,
        e.enrollment_date,
        e.progress_percentage,
        e.status,
        e.last_accessed
    FROM enrollments e
    JOIN courses c ON e.course_id = c.course_id
    JOIN users u ON c.instructor_id = u.user_id
    WHERE e.user_id = p_user_id
        AND (p_status IS NULL OR e.status = p_status)
    ORDER BY e.enrollment_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Update lesson progress
CREATE OR REPLACE FUNCTION mark_lesson_complete(
    p_enrollment_id UUID,
    p_lesson_id UUID,
    p_time_spent INTEGER DEFAULT 0
)
RETURNS VOID AS $$
BEGIN
    UPDATE lesson_progress
    SET completed = TRUE,
        completion_date = CURRENT_TIMESTAMP,
        time_spent_minutes = time_spent_minutes + p_time_spent
    WHERE enrollment_id = p_enrollment_id
        AND lesson_id = p_lesson_id;
END;
$$ LANGUAGE plpgsql;

-- Get course progress for user
CREATE OR REPLACE FUNCTION get_course_progress(
    p_enrollment_id UUID
)
RETURNS TABLE (
    module_title VARCHAR,
    lesson_title VARCHAR,
    lesson_type VARCHAR,
    completed BOOLEAN,
    completion_date TIMESTAMP,
    time_spent_minutes INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cm.module_title,
        cl.lesson_title,
        cl.lesson_type,
        lp.completed,
        lp.completion_date,
        lp.time_spent_minutes
    FROM lesson_progress lp
    JOIN course_lessons cl ON lp.lesson_id = cl.lesson_id
    JOIN course_modules cm ON cl.module_id = cm.module_id
    WHERE lp.enrollment_id = p_enrollment_id
    ORDER BY cm.module_order, cl.lesson_order;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- PAYMENT PROCEDURES
-- =====================================================

-- Create transaction
CREATE OR REPLACE FUNCTION create_transaction(
    p_user_id UUID,
    p_course_id UUID,
    p_payment_method_id UUID,
    p_amount DECIMAL,
    p_currency VARCHAR DEFAULT 'USD',
    p_payment_gateway VARCHAR DEFAULT 'stripe'
)
RETURNS UUID AS $$
DECLARE
    v_transaction_id UUID;
BEGIN
    INSERT INTO transactions (
        user_id, course_id, payment_method_id, 
        amount, currency, transaction_type, payment_gateway
    )
    VALUES (
        p_user_id, p_course_id, p_payment_method_id,
        p_amount, p_currency, 'purchase', p_payment_gateway
    )
    RETURNING transaction_id INTO v_transaction_id;
    
    RETURN v_transaction_id;
END;
$$ LANGUAGE plpgsql;

-- Complete transaction and generate invoice
CREATE OR REPLACE FUNCTION complete_transaction(
    p_transaction_id UUID,
    p_gateway_transaction_id VARCHAR
)
RETURNS UUID AS $$
DECLARE
    v_invoice_id UUID;
    v_amount DECIMAL;
    v_tax_amount DECIMAL;
    v_invoice_number VARCHAR;
BEGIN
    -- Update transaction
    UPDATE transactions
    SET status = 'completed',
        completed_at = CURRENT_TIMESTAMP,
        gateway_transaction_id = p_gateway_transaction_id
    WHERE transaction_id = p_transaction_id
    RETURNING amount INTO v_amount;
    
    -- Calculate tax (10% for example)
    v_tax_amount := v_amount * 0.10;
    
    -- Generate invoice number
    v_invoice_number := 'INV-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                        LPAD(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::TEXT, 10, '0');
    
    -- Create invoice
    INSERT INTO invoices (
        transaction_id, invoice_number, invoice_date,
        subtotal, tax_amount, total_amount, status
    )
    VALUES (
        p_transaction_id, v_invoice_number, CURRENT_DATE,
        v_amount, v_tax_amount, v_amount + v_tax_amount, 'paid'
    )
    RETURNING invoice_id INTO v_invoice_id;
    
    RETURN v_invoice_id;
END;
$$ LANGUAGE plpgsql;

-- Get user transaction history
CREATE OR REPLACE FUNCTION get_user_transactions(
    p_user_id UUID,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    transaction_id UUID,
    course_title VARCHAR,
    amount DECIMAL,
    currency VARCHAR,
    transaction_type VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.transaction_id,
        c.title as course_title,
        t.amount,
        t.currency,
        t.transaction_type,
        t.status,
        t.created_at,
        t.completed_at
    FROM transactions t
    JOIN courses c ON t.course_id = c.course_id
    WHERE t.user_id = p_user_id
    ORDER BY t.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ANALYTICS PROCEDURES
-- =====================================================

-- Get instructor statistics
CREATE OR REPLACE FUNCTION get_instructor_stats(p_instructor_id UUID)
RETURNS TABLE (
    total_courses BIGINT,
    total_enrollments BIGINT,
    average_rating DECIMAL,
    total_revenue DECIMAL,
    active_students BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT c.course_id) as total_courses,
        COUNT(DISTINCT e.enrollment_id) as total_enrollments,
        AVG(c.rating) as average_rating,
        SUM(t.amount) as total_revenue,
        COUNT(DISTINCT CASE WHEN e.status = 'active' THEN e.user_id END) as active_students
    FROM courses c
    LEFT JOIN enrollments e ON c.course_id = e.course_id
    LEFT JOIN transactions t ON c.course_id = t.course_id AND t.status = 'completed'
    WHERE c.instructor_id = p_instructor_id;
END;
$$ LANGUAGE plpgsql;

-- Get platform statistics
CREATE OR REPLACE FUNCTION get_platform_stats()
RETURNS TABLE (
    total_users BIGINT,
    total_students BIGINT,
    total_instructors BIGINT,
    total_courses BIGINT,
    published_courses BIGINT,
    total_enrollments BIGINT,
    active_enrollments BIGINT,
    total_revenue DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT u.user_id) as total_users,
        COUNT(DISTINCT CASE WHEN u.user_type = 'student' THEN u.user_id END) as total_students,
        COUNT(DISTINCT CASE WHEN u.user_type = 'instructor' THEN u.user_id END) as total_instructors,
        COUNT(DISTINCT c.course_id) as total_courses,
        COUNT(DISTINCT CASE WHEN c.status = 'published' THEN c.course_id END) as published_courses,
        COUNT(DISTINCT e.enrollment_id) as total_enrollments,
        COUNT(DISTINCT CASE WHEN e.status = 'active' THEN e.enrollment_id END) as active_enrollments,
        SUM(t.amount) as total_revenue
    FROM users u
    LEFT JOIN courses c ON u.user_id = c.instructor_id
    LEFT JOIN enrollments e ON c.course_id = e.course_id
    LEFT JOIN transactions t ON c.course_id = t.course_id AND t.status = 'completed';
END;
$$ LANGUAGE plpgsql;
