# accounts.py - Account Management System for Trading Simulation Platform

from datetime import datetime
from typing import Dict, List, Optional


# Custom Exceptions
class InsufficientFundsError(Exception):
    pass


class InsufficientSharesError(Exception):
    pass


class InvalidTransactionError(Exception):
    pass


# Module Constants
SUPPORTED_SYMBOLS = ['AAPL', 'TSLA', 'GOOGL']
MIN_TRANSACTION_AMOUNT = 0.01


# Utility Functions
def get_share_price(symbol: str) -> float:
    prices = {
        'AAPL': 150.00,
        'TSLA': 200.00,
        'GOOGL': 2500.00
    }
    
    if symbol not in prices:
        raise ValueError(f"Unknown symbol: {symbol}")
    
    return prices[symbol]


class Transaction:
    _next_id = 1
    
    def __init__(self, transaction_type: str, amount: float, symbol: str = None, 
                 quantity: int = None, price: float = None, timestamp: datetime = None):
        self.transaction_id = Transaction._next_id
        Transaction._next_id += 1
        self.transaction_type = transaction_type
        self.amount = amount
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp or datetime.now()
    
    def __str__(self) -> str:
        if self.transaction_type in ['deposit', 'withdraw']:
            return f"{self.transaction_type.capitalize()}: ${self.amount:.2f} at {self.timestamp}"
        else:
            return f"{self.transaction_type.capitalize()}: {self.quantity} {self.symbol} @ ${self.price:.2f} (${self.amount:.2f}) at {self.timestamp}"
    
    def to_dict(self) -> Dict:
        return {
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp
        }


class Holding:
    def __init__(self, symbol: str, quantity: int, average_cost: float):
        self.symbol = symbol
        self.quantity = quantity
        self.average_cost = average_cost
    
    def add_shares(self, quantity: int, price: float) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        total_cost = (self.quantity * self.average_cost) + (quantity * price)
        self.quantity += quantity
        self.average_cost = total_cost / self.quantity
    
    def remove_shares(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.quantity:
            raise InsufficientSharesError(f"Cannot remove {quantity} shares, only have {self.quantity}")
        
        self.quantity -= quantity
    
    def get_current_value(self) -> float:
        return self.quantity * get_share_price(self.symbol)
    
    def get_profit_loss(self) -> float:
        current_value = self.get_current_value()
        cost_basis = self.quantity * self.average_cost
        return current_value - cost_basis


class Account:
    def __init__(self, account_id: str, initial_balance: float = 0.0):
        self.account_id = account_id
        self.cash_balance = initial_balance
        self.initial_deposit = initial_balance
        self.holdings: Dict[str, Holding] = {}
        self.transactions: List[Transaction] = []
        self.created_at = datetime.now()
        
        if initial_balance > 0:
            self.transactions.append(Transaction('deposit', initial_balance))
    
    def deposit(self, amount: float) -> bool:
        if amount < MIN_TRANSACTION_AMOUNT:
            raise InvalidTransactionError(f"Deposit amount must be at least ${MIN_TRANSACTION_AMOUNT}")
        
        self.cash_balance += amount
        self.initial_deposit += amount
        self.transactions.append(Transaction('deposit', amount))
        return True
    
    def withdraw(self, amount: float) -> bool:
        if amount < MIN_TRANSACTION_AMOUNT:
            raise InvalidTransactionError(f"Withdrawal amount must be at least ${MIN_TRANSACTION_AMOUNT}")
        
        if not self._validate_sufficient_cash(amount):
            raise InsufficientFundsError(f"Insufficient funds. Available: ${self.cash_balance:.2f}, Requested: ${amount:.2f}")
        
        self.cash_balance -= amount
        self.transactions.append(Transaction('withdraw', amount))
        return True
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        if quantity <= 0:
            raise InvalidTransactionError("Quantity must be positive")
        
        price = get_share_price(symbol)
        total_cost = quantity * price
        
        if not self._validate_sufficient_cash(total_cost):
            raise InsufficientFundsError(f"Insufficient funds to buy {quantity} {symbol}. Cost: ${total_cost:.2f}, Available: ${self.cash_balance:.2f}")
        
        if symbol in self.holdings:
            self.holdings[symbol].add_shares(quantity, price)
        else:
            self.holdings[symbol] = Holding(symbol, quantity, price)
        
        self.cash_balance -= total_cost
        self.transactions.append(Transaction('buy', total_cost, symbol, quantity, price))
        return True
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        if quantity <= 0:
            raise InvalidTransactionError("Quantity must be positive")
        
        if not self._validate_sufficient_shares(symbol, quantity):
            owned = self.holdings.get(symbol, Holding(symbol, 0, 0)).quantity
            raise InsufficientSharesError(f"Insufficient shares to sell {quantity} {symbol}. Owned: {owned}")
        
        price = get_share_price(symbol)
        total_proceeds = quantity * price
        
        self.holdings[symbol].remove_shares(quantity)
        if self.holdings[symbol].quantity == 0:
            del self.holdings[symbol]
        
        self.cash_balance += total_proceeds
        self.transactions.append(Transaction('sell', total_proceeds, symbol, quantity, price))
        return True
    
    def get_portfolio_value(self) -> float:
        holdings_value = sum(holding.get_current_value() for holding in self.holdings.values())
        return self.cash_balance + holdings_value
    
    def get_profit_loss(self) -> float:
        total_withdrawals = sum(t.amount for t in self.transactions if t.transaction_type == 'withdraw')
        current_portfolio_value = self.get_portfolio_value()
        return current_portfolio_value - self.initial_deposit + total_withdrawals
    
    def get_holdings(self) -> Dict[str, Dict]:
        holdings_info = {}
        for symbol, holding in self.holdings.items():
            current_price = get_share_price(symbol)
            holdings_info[symbol] = {
                'quantity': holding.quantity,
                'average_cost': holding.average_cost,
                'current_price': current_price,
                'current_value': holding.get_current_value(),
                'profit_loss': holding.get_profit_loss()
            }
        return holdings_info
    
    def get_transactions(self) -> List[Transaction]:
        return sorted(self.transactions, key=lambda t: t.timestamp)
    
    def get_cash_balance(self) -> float:
        return self.cash_balance
    
    def _validate_sufficient_cash(self, amount: float) -> bool:
        return self.cash_balance >= amount
    
    def _validate_sufficient_shares(self, symbol: str, quantity: int) -> bool:
        if symbol not in self.holdings:
            return False
        return self.holdings[symbol].quantity >= quantity