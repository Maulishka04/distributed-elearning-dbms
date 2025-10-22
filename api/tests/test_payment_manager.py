"""
Unit tests for PaymentManager business logic
"""
import pytest
from api.services.payment_manager import PaymentManager

class DummyPaymentCrud:
    payments = {}
    @staticmethod
    def create_payment(user_id, enrollment_id, amount, status, method):
        pid = len(DummyPaymentCrud.payments) + 1
        DummyPaymentCrud.payments[pid] = {"id": pid, "user_id": user_id, "enrollment_id": enrollment_id, "amount": amount, "status": status, "method": method}
        return pid
    @staticmethod
    def get_payment_by_id(payment_id):
        return DummyPaymentCrud.payments.get(payment_id)
    @staticmethod
    def update_payment(payment_id, status, method):
        payment = DummyPaymentCrud.payments.get(payment_id)
        if payment:
            if status: payment["status"] = status
            if method: payment["method"] = method
        return payment
    @staticmethod
    def delete_payment(payment_id):
        DummyPaymentCrud.payments.pop(payment_id, None)
    @staticmethod
    def list_payments():
        return list(DummyPaymentCrud.payments.values())

PaymentManager.process_payment = DummyPaymentCrud.create_payment
PaymentManager.get_payment = DummyPaymentCrud.get_payment_by_id
PaymentManager.update_payment = DummyPaymentCrud.update_payment
PaymentManager.delete_payment = DummyPaymentCrud.delete_payment
PaymentManager.list_all_payments = DummyPaymentCrud.list_payments

def test_process_and_get_payment():
    pid = PaymentManager.process_payment(1, 1, 100.0, "card", "pending")
    payment = PaymentManager.get_payment(pid)
    assert payment["amount"] == 100.0
    assert payment["method"] == "card"

def test_update_payment():
    pid = PaymentManager.process_payment(2, 2, 200.0, "paypal", "pending")
    PaymentManager.update_payment(pid, "completed", "paypal")
    payment = PaymentManager.get_payment(pid)
    assert payment["status"] == "completed"
    assert payment["method"] == "paypal"

def test_delete_payment():
    pid = PaymentManager.process_payment(3, 3, 300.0, "card", "pending")
    PaymentManager.delete_payment(pid)
    payment = PaymentManager.get_payment(pid)
    assert payment is None

def test_list_all_payments():
    PaymentManager.process_payment(4, 4, 400.0, "card", "completed")
    PaymentManager.process_payment(5, 5, 500.0, "paypal", "completed")
    payments = PaymentManager.list_all_payments()
    assert len(payments) >= 2
