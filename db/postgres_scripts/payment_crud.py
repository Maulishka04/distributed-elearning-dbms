"""
CRUD Operations for Payment and Transaction Management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from .connection_manager import get_postgres_manager


class PaymentCRUD:
    """CRUD operations for payments and transactions"""
    
    def __init__(self):
        self.pg_manager = get_postgres_manager()
    
    def add_payment_method(
        self,
        user_id: str,
        region: str,
        method_type: str,
        card_last_four: Optional[str] = None,
        card_brand: Optional[str] = None,
        expiry_month: Optional[int] = None,
        expiry_year: Optional[int] = None,
        billing_address: Optional[str] = None,
        is_default: bool = False
    ) -> str:
        """Add a payment method for a user"""
        query = """
            INSERT INTO payment_methods 
            (user_id, method_type, card_last_four, card_brand, 
             expiry_month, expiry_year, billing_address, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING payment_method_id
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(user_id, method_type, card_last_four, card_brand,
                   expiry_month, expiry_year, billing_address, is_default),
            read_only=False,
            fetch_one=True
        )
        
        return str(result['payment_method_id']) if result else None
    
    def get_user_payment_methods(
        self,
        user_id: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """Get all payment methods for a user"""
        query = """
            SELECT 
                payment_method_id, method_type, card_last_four,
                card_brand, expiry_month, expiry_year,
                is_default, created_at
            FROM payment_methods
            WHERE user_id = %s
            ORDER BY is_default DESC, created_at DESC
        """
        
        results = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(user_id,),
            read_only=True
        )
        
        return results or []
    
    def create_transaction(
        self,
        user_id: str,
        course_id: str,
        region: str,
        amount: float,
        payment_method_id: Optional[str] = None,
        currency: str = 'USD',
        payment_gateway: str = 'stripe'
    ) -> str:
        """Create a new transaction"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='create_transaction',
            params=(user_id, course_id, payment_method_id, amount, currency, payment_gateway),
            read_only=False
        )
        
        if result and len(result) > 0:
            return str(result[0]['create_transaction'])
        
        raise Exception("Failed to create transaction")
    
    def complete_transaction(
        self,
        transaction_id: str,
        region: str,
        gateway_transaction_id: str
    ) -> str:
        """Complete a transaction and generate invoice"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='complete_transaction',
            params=(transaction_id, gateway_transaction_id),
            read_only=False
        )
        
        if result and len(result) > 0:
            return str(result[0]['complete_transaction'])
        
        raise Exception("Failed to complete transaction")
    
    def fail_transaction(
        self,
        transaction_id: str,
        region: str
    ) -> bool:
        """Mark transaction as failed"""
        query = """
            UPDATE transactions
            SET status = 'failed'
            WHERE transaction_id = %s
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(transaction_id,),
            read_only=False
        )
        
        return True
    
    def refund_transaction(
        self,
        transaction_id: str,
        region: str
    ) -> str:
        """Process a refund for a transaction"""
        # Get original transaction
        query_get = """
            SELECT user_id, course_id, amount, currency, payment_method_id
            FROM transactions
            WHERE transaction_id = %s AND status = 'completed'
        """
        
        original = self.pg_manager.execute_query(
            region=region,
            query=query_get,
            params=(transaction_id,),
            read_only=True,
            fetch_one=True
        )
        
        if not original:
            raise Exception("Original transaction not found or not completed")
        
        # Create refund transaction
        query_refund = """
            INSERT INTO transactions 
            (user_id, course_id, payment_method_id, amount, currency, 
             transaction_type, status, payment_gateway)
            VALUES (%s, %s, %s, %s, %s, 'refund', 'completed', 'stripe')
            RETURNING transaction_id
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query_refund,
            params=(original['user_id'], original['course_id'], 
                   original['payment_method_id'], original['amount'], 
                   original['currency']),
            read_only=False,
            fetch_one=True
        )
        
        # Update original transaction
        query_update = """
            UPDATE transactions
            SET status = 'refunded'
            WHERE transaction_id = %s
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query_update,
            params=(transaction_id,),
            read_only=False
        )
        
        return str(result['transaction_id']) if result else None
    
    def get_transaction_by_id(
        self,
        transaction_id: str,
        region: str
    ) -> Optional[Dict[str, Any]]:
        """Get transaction details"""
        query = """
            SELECT 
                t.transaction_id, t.user_id, t.course_id,
                t.amount, t.currency, t.transaction_type,
                t.status, t.payment_gateway, t.gateway_transaction_id,
                t.created_at, t.completed_at,
                c.title as course_title,
                u.email as user_email
            FROM transactions t
            JOIN courses c ON t.course_id = c.course_id
            JOIN users u ON t.user_id = u.user_id
            WHERE t.transaction_id = %s
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(transaction_id,),
            read_only=True,
            fetch_one=True
        )
        
        return result
    
    def get_user_transactions(
        self,
        user_id: str,
        region: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user transaction history"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='get_user_transactions',
            params=(user_id, limit),
            read_only=True
        )
        
        return result or []
    
    def get_invoice_by_transaction(
        self,
        transaction_id: str,
        region: str
    ) -> Optional[Dict[str, Any]]:
        """Get invoice for a transaction"""
        query = """
            SELECT 
                i.invoice_id, i.invoice_number, i.invoice_date,
                i.due_date, i.subtotal, i.tax_amount,
                i.discount_amount, i.total_amount, i.status,
                t.transaction_id, t.amount as transaction_amount,
                c.title as course_title,
                u.email as user_email,
                u.first_name, u.last_name
            FROM invoices i
            JOIN transactions t ON i.transaction_id = t.transaction_id
            JOIN courses c ON t.course_id = c.course_id
            JOIN users u ON t.user_id = u.user_id
            WHERE i.transaction_id = %s
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(transaction_id,),
            read_only=True,
            fetch_one=True
        )
        
        return result
    
    def get_revenue_statistics(
        self,
        region: str,
        instructor_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get revenue statistics"""
        query = """
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) as total_revenue,
                SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END) as total_refunds,
                AVG(CASE WHEN status = 'completed' THEN amount ELSE NULL END) as average_transaction,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
            FROM transactions t
            JOIN courses c ON t.course_id = c.course_id
            WHERE t.transaction_type = 'purchase'
        """
        
        params = []
        
        if instructor_id:
            query += " AND c.instructor_id = %s"
            params.append(instructor_id)
        
        if start_date:
            query += " AND t.created_at >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND t.created_at <= %s"
            params.append(end_date)
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=tuple(params) if params else None,
            read_only=True,
            fetch_one=True
        )
        
        return result or {}
