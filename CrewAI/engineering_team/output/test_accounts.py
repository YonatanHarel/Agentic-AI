import unittest
from datetime import datetime
from unittest.mock import patch
import sys
import os

# Import the module to test
from accounts import (
    InsufficientFundsError,
    InsufficientSharesError,
    InvalidTransactionError,
    SUPPORTED_SYMBOLS,
    MIN_TRANSACTION_AMOUNT,
    get_share_price,
    Transaction,
    Holding,
    Account
)


class TestExceptions(unittest.TestCase):
    """Test custom exceptions"""
    
    def test_insufficient_funds_error(self):
        with self.assertRaises(InsufficientFundsError):
            raise InsufficientFundsError("Test error")
    
    def test_insufficient_shares_error(self):
        with self.assertRaises(InsufficientSharesError):
            raise InsufficientSharesError("Test error")
    
    def test_invalid_transaction_error(self):
        with self.assertRaises(InvalidTransactionError):
            raise InvalidTransactionError("Test error")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_get_share_price_valid_symbols(self):
        """Test getting price for valid symbols"""
        self.assertEqual(get_share_price('AAPL'), 150.00)
        self.assertEqual(get_share_price('TSLA'), 200.00)
        self.assertEqual(get_share_price('GOOGL'), 2500.00)
    
    def test_get_share_price_invalid_symbol(self):
        """Test getting price for invalid symbol raises ValueError"""
        with self.assertRaises(ValueError) as context:
            get_share_price('INVALID')
        self.assertIn('Unknown symbol: INVALID', str(context.exception))
    
    def test_supported_symbols_constant(self):
        """Test that SUPPORTED_SYMBOLS contains expected values"""
        expected = ['AAPL', 'TSLA', 'GOOGL']
        self.assertEqual(SUPPORTED_SYMBOLS, expected)
    
    def test_min_transaction_amount_constant(self):
        """Test MIN_TRANSACTION_AMOUNT value"""
        self.assertEqual(MIN_TRANSACTION_AMOUNT, 0.01)


class TestTransaction(unittest.TestCase):
    """Test Transaction class"""
    
    def setUp(self):
        # Reset the class variable for consistent testing
        Transaction._next_id = 1
    
    def test_transaction_creation_deposit(self):
        """Test creating a deposit transaction"""
        tx = Transaction('deposit', 100.0)
        self.assertEqual(tx.transaction_id, 1)
        self.assertEqual(tx.transaction_type, 'deposit')
        self.assertEqual(tx.amount, 100.0)
        self.assertIsNone(tx.symbol)
        self.assertIsNone(tx.quantity)
        self.assertIsNone(tx.price)
        self.assertIsInstance(tx.timestamp, datetime)
    
    def test_transaction_creation_buy(self):
        """Test creating a buy transaction"""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        tx = Transaction('buy', 300.0, 'AAPL', 2, 150.0, timestamp)
        self.assertEqual(tx.transaction_id, 1)
        self.assertEqual(tx.transaction_type, 'buy')
        self.assertEqual(tx.amount, 300.0)
        self.assertEqual(tx.symbol, 'AAPL')
        self.assertEqual(tx.quantity, 2)
        self.assertEqual(tx.price, 150.0)
        self.assertEqual(tx.timestamp, timestamp)
    
    def test_transaction_id_increment(self):
        """Test that transaction IDs increment properly"""
        tx1 = Transaction('deposit', 100.0)
        tx2 = Transaction('withdraw', 50.0)
        self.assertEqual(tx1.transaction_id, 1)
        self.assertEqual(tx2.transaction_id, 2)
    
    def test_transaction_str_deposit(self):
        """Test string representation of deposit transaction"""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        tx = Transaction('deposit', 100.0, timestamp=timestamp)
        expected = "Deposit: $100.00 at 2023-01-01 12:00:00"
        self.assertEqual(str(tx), expected)
    
    def test_transaction_str_withdraw(self):
        """Test string representation of withdraw transaction"""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        tx = Transaction('withdraw', 50.0, timestamp=timestamp)
        expected = "Withdraw: $50.00 at 2023-01-01 12:00:00"
        self.assertEqual(str(tx), expected)
    
    def test_transaction_str_buy(self):
        """Test string representation of buy transaction"""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        tx = Transaction('buy', 300.0, 'AAPL', 2, 150.0, timestamp)
        expected = "Buy: 2 AAPL @ $150.00 ($300.00) at 2023-01-01 12:00:00"
        self.assertEqual(str(tx), expected)
    
    def test_transaction_to_dict(self):
        """Test converting transaction to dictionary"""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        tx = Transaction('buy', 300.0, 'AAPL', 2, 150.0, timestamp)
        result = tx.to_dict()
        expected = {
            'transaction_id': 1,
            'transaction_type': 'buy',
            'amount': 300.0,
            'symbol': 'AAPL',
            'quantity': 2,
            'price': 150.0,
            'timestamp': timestamp
        }
        self.assertEqual(result, expected)


class TestHolding(unittest.TestCase):
    """Test Holding class"""
    
    def test_holding_creation(self):
        """Test creating a holding"""
        holding = Holding('AAPL', 10, 150.0)
        self.assertEqual(holding.symbol, 'AAPL')
        self.assertEqual(holding.quantity, 10)
        self.assertEqual(holding.average_cost, 150.0)
    
    def test_add_shares(self):
        """Test adding shares to holding"""
        holding = Holding('AAPL', 10, 150.0)  # 10 shares at $150
        holding.add_shares(5, 160.0)  # Add 5 shares at $160
        
        self.assertEqual(holding.quantity, 15)
        # Average cost should be (10*150 + 5*160) / 15 = 2300/15 = 153.33...
        expected_avg = (10 * 150.0 + 5 * 160.0) / 15
        self.assertAlmostEqual(holding.average_cost, expected_avg, places=2)
    
    def test_add_shares_invalid_quantity(self):
        """Test adding invalid quantity of shares"""
        holding = Holding('AAPL', 10, 150.0)
        with self.assertRaises(ValueError) as context:
            holding.add_shares(0, 160.0)
        self.assertIn('Quantity must be positive', str(context.exception))
        
        with self.assertRaises(ValueError):
            holding.add_shares(-5, 160.0)
    
    def test_remove_shares(self):
        """Test removing shares from holding"""
        holding = Holding('AAPL', 10, 150.0)
        holding.remove_shares(3)
        self.assertEqual(holding.quantity, 7)
        self.assertEqual(holding.average_cost, 150.0)  # Average cost shouldn't change
    
    def test_remove_shares_invalid_quantity(self):
        """Test removing invalid quantity of shares"""
        holding = Holding('AAPL', 10, 150.0)
        
        with self.assertRaises(ValueError):
            holding.remove_shares(0)
        
        with self.assertRaises(ValueError):
            holding.remove_shares(-5)
    
    def test_remove_shares_insufficient(self):
        """Test removing more shares than available"""
        holding = Holding('AAPL', 10, 150.0)
        with self.assertRaises(InsufficientSharesError) as context:
            holding.remove_shares(15)
        self.assertIn('Cannot remove 15 shares, only have 10', str(context.exception))
    
    def test_get_current_value(self):
        """Test getting current value of holding"""
        holding = Holding('AAPL', 10, 140.0)
        # Current price of AAPL is 150.0
        expected_value = 10 * 150.0
        self.assertEqual(holding.get_current_value(), expected_value)
    
    def test_get_profit_loss(self):
        """Test calculating profit/loss"""
        holding = Holding('AAPL', 10, 140.0)  # Bought at $140
        # Current price is $150, so profit = 10 * (150 - 140) = $100
        expected_profit = 10 * (150.0 - 140.0)
        self.assertEqual(holding.get_profit_loss(), expected_profit)
    
    def test_get_profit_loss_negative(self):
        """Test calculating loss"""
        holding = Holding('AAPL', 10, 160.0)  # Bought at $160
        # Current price is $150, so loss = 10 * (150 - 160) = -$100
        expected_loss = 10 * (150.0 - 160.0)
        self.assertEqual(holding.get_profit_loss(), expected_loss)


class TestAccount(unittest.TestCase):
    """Test Account class"""
    
    def setUp(self):
        # Reset transaction ID counter
        Transaction._next_id = 1
    
    def test_account_creation_no_initial_balance(self):
        """Test creating account with no initial balance"""
        account = Account('ACC001')
        self.assertEqual(account.account_id, 'ACC001')
        self.assertEqual(account.cash_balance, 0.0)
        self.assertEqual(account.initial_deposit, 0.0)
        self.assertEqual(len(account.holdings), 0)
        self.assertEqual(len(account.transactions), 0)
        self.assertIsInstance(account.created_at, datetime)
    
    def test_account_creation_with_initial_balance(self):
        """Test creating account with initial balance"""
        account = Account('ACC001', 1000.0)
        self.assertEqual(account.cash_balance, 1000.0)
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0].transaction_type, 'deposit')
        self.assertEqual(account.transactions[0].amount, 1000.0)
    
    def test_deposit_valid(self):
        """Test valid deposit"""
        account = Account('ACC001')
        result = account.deposit(500.0)
        self.assertTrue(result)
        self.assertEqual(account.cash_balance, 500.0)
        self.assertEqual(account.initial_deposit, 500.0)
        self.assertEqual(len(account.transactions), 1)
    
    def test_deposit_invalid_amount(self):
        """Test deposit with invalid amount"""
        account = Account('ACC001')
        with self.assertRaises(InvalidTransactionError) as context:
            account.deposit(0.005)  # Less than MIN_TRANSACTION_AMOUNT
        self.assertIn('Deposit amount must be at least', str(context.exception))
    
    def test_withdraw_valid(self):
        """Test valid withdrawal"""
        account = Account('ACC001', 1000.0)
        result = account.withdraw(300.0)
        self.assertTrue(result)
        self.assertEqual(account.cash_balance, 700.0)
        self.assertEqual(len(account.transactions), 2)  # Initial deposit + withdrawal
    
    def test_withdraw_insufficient_funds(self):
        """Test withdrawal with insufficient funds"""
        account = Account('ACC001', 100.0)
        with self.assertRaises(InsufficientFundsError) as context:
            account.withdraw(200.0)
        self.assertIn('Insufficient funds', str(context.exception))
    
    def test_withdraw_invalid_amount(self):
        """Test withdrawal with invalid amount"""
        account = Account('ACC001', 1000.0)
        with self.assertRaises(InvalidTransactionError):
            account.withdraw(0.005)
    
    def test_buy_shares_valid(self):
        """Test valid share purchase"""
        account = Account('ACC001', 1000.0)
        result = account.buy_shares('AAPL', 2)
        self.assertTrue(result)
        self.assertEqual(account.cash_balance, 700.0)  # 1000 - (2 * 150)
        self.assertIn('AAPL', account.holdings)
        self.assertEqual(account.holdings['AAPL'].quantity, 2)
        self.assertEqual(account.holdings['AAPL'].average_cost, 150.0)
    
    def test_buy_shares_multiple_purchases(self):
        """Test multiple purchases of same stock"""
        account = Account('ACC001', 2000.0)
        account.buy_shares('AAPL', 2)  # 2 at $150
        account.buy_shares('AAPL', 1)  # 1 more at $150
        
        self.assertEqual(account.holdings['AAPL'].quantity, 3)
        self.assertEqual(account.holdings['AAPL'].average_cost, 150.0)
        self.assertEqual(account.cash_balance, 1550.0)  # 2000 - (3 * 150)
    
    def test_buy_shares_insufficient_funds(self):
        """Test buying shares with insufficient funds"""
        account = Account('ACC001', 100.0)
        with self.assertRaises(InsufficientFundsError) as context:
            account.buy_shares('AAPL', 2)  # 2 * 150 = 300, but only have 100
        self.assertIn('Insufficient funds to buy', str(context.exception))
    
    def test_buy_shares_invalid_quantity(self):
        """Test buying shares with invalid quantity"""
        account = Account('ACC001', 1000.0)
        with self.assertRaises(InvalidTransactionError):
            account.buy_shares('AAPL', 0)
        
        with self.assertRaises(InvalidTransactionError):
            account.buy_shares('AAPL', -1)
    
    def test_sell_shares_valid(self):
        """Test valid share sale"""
        account = Account('ACC001', 1000.0)
        account.buy_shares('AAPL', 4)  # Buy 4 shares
        
        result = account.sell_shares('AAPL', 2)  # Sell 2 shares
        self.assertTrue(result)
        self.assertEqual(account.holdings['AAPL'].quantity, 2)
        # Cash should be: 1000 - (4*150) + (2*150) = 1000 - 600 + 300 = 700
        self.assertEqual(account.cash_balance, 700.0)
    
    def test_sell_all_shares(self):
        """Test selling all shares removes holding"""
        account = Account('ACC001', 1000.0)
        account.buy_shares('AAPL', 2)