import gradio as gr
from accounts import Account, InsufficientFundsError, InsufficientSharesError, InvalidTransactionError, get_share_price
from typing import Dict, Any
import pandas as pd

# Global account instance for single user demo
account = None

def create_account(initial_balance: float) -> str:
    global account
    try:
        if initial_balance < 0:
            return "Error: Initial balance cannot be negative"
        account = Account("demo_user", initial_balance)
        return f"Account created successfully with initial balance: ${initial_balance:.2f}"
    except Exception as e:
        return f"Error creating account: {str(e)}"

def deposit_funds(amount: float) -> str:
    global account
    if account is None:
        return "Error: Please create an account first"
    try:
        account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}. New balance: ${account.get_cash_balance():.2f}"
    except (InsufficientFundsError, InvalidTransactionError) as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def withdraw_funds(amount: float) -> str:
    global account
    if account is None:
        return "Error: Please create an account first"
    try:
        account.withdraw(amount)
        return f"Successfully withdrew ${amount:.2f}. New balance: ${account.get_cash_balance():.2f}"
    except (InsufficientFundsError, InvalidTransactionError) as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def buy_shares(symbol: str, quantity: int) -> str:
    global account
    if account is None:
        return "Error: Please create an account first"
    try:
        price = get_share_price(symbol)
        account.buy_shares(symbol, quantity)
        total_cost = quantity * price
        return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} each. Total cost: ${total_cost:.2f}"
    except (InsufficientFundsError, InvalidTransactionError) as e:
        return f"Error: {str(e)}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def sell_shares(symbol: str, quantity: int) -> str:
    global account
    if account is None:
        return "Error: Please create an account first"
    try:
        price = get_share_price(symbol)
        account.sell_shares(symbol, quantity)
        total_proceeds = quantity * price
        return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} each. Total proceeds: ${total_proceeds:.2f}"
    except (InsufficientSharesError, InvalidTransactionError) as e:
        return f"Error: {str(e)}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def get_account_status() -> str:
    global account
    if account is None:
        return "No account created yet"
    
    cash_balance = account.get_cash_balance()
    portfolio_value = account.get_portfolio_value()
    profit_loss = account.get_profit_loss()
    
    status = f"""
Account Status:
- Cash Balance: ${cash_balance:.2f}
- Total Portfolio Value: ${portfolio_value:.2f}
- Profit/Loss: ${profit_loss:.2f}
"""
    return status

def get_holdings_info() -> str:
    global account
    if account is None:
        return "No account created yet"
    
    holdings = account.get_holdings()
    if not holdings:
        return "No holdings"
    
    holdings_text = "Current Holdings:\n"
    for symbol, info in holdings.items():
        holdings_text += f"- {symbol}: {info['quantity']} shares, "
        holdings_text += f"Avg Cost: ${info['average_cost']:.2f}, "
        holdings_text += f"Current Price: ${info['current_price']:.2f}, "
        holdings_text += f"Value: ${info['current_value']:.2f}, "
        holdings_text += f"P&L: ${info['profit_loss']:.2f}\n"
    
    return holdings_text

def get_transactions_history() -> str:
    global account
    if account is None:
        return "No account created yet"
    
    transactions = account.get_transactions()
    if not transactions:
        return "No transactions"
    
    history = "Transaction History:\n"
    for transaction in transactions[-10:]:  # Show last 10 transactions
        history += f"- {str(transaction)}\n"
    
    return history

def get_current_prices() -> str:
    prices = []
    symbols = ['AAPL', 'TSLA', 'GOOGL']
    for symbol in symbols:
        price = get_share_price(symbol)
        prices.append(f"{symbol}: ${price:.2f}")
    
    return "Current Market Prices:\n" + "\n".join(prices)

# Create Gradio interface
with gr.Blocks(title="Trading Simulation Account Manager") as demo:
    gr.Markdown("# Trading Simulation Account Manager")
    gr.Markdown("A simple demo for managing a trading account. Create an account first, then deposit/withdraw funds and trade shares.")
    
    with gr.Tab("Account Management"):
        gr.Markdown("### Create Account")
        initial_balance = gr.Number(value=10000.0, label="Initial Balance ($)")
        create_btn = gr.Button("Create Account")
        create_output = gr.Textbox(label="Result", interactive=False)
        create_btn.click(create_account, inputs=[initial_balance], outputs=[create_output])
        
        gr.Markdown("### Deposit/Withdraw Funds")
        with gr.Row():
            with gr.Column():
                deposit_amount = gr.Number(value=1000.0, label="Deposit Amount ($)")
                deposit_btn = gr.Button("Deposit")
                deposit_output = gr.Textbox(label="Deposit Result", interactive=False)
                deposit_btn.click(deposit_funds, inputs=[deposit_amount], outputs=[deposit_output])
            
            with gr.Column():
                withdraw_amount = gr.Number(value=500.0, label="Withdraw Amount ($)")
                withdraw_btn = gr.Button("Withdraw")
                withdraw_output = gr.Textbox(label="Withdraw Result", interactive=False)
                withdraw_btn.click(withdraw_funds, inputs=[withdraw_amount], outputs=[withdraw_output])
    
    with gr.Tab("Trading"):
        gr.Markdown("### Buy/Sell Shares")
        
        # Current prices display
        prices_display = gr.Textbox(label="Current Market Prices", value=get_current_prices(), interactive=False)
        refresh_prices_btn = gr.Button("Refresh Prices")
        refresh_prices_btn.click(lambda: get_current_prices(), outputs=[prices_display])
        
        with gr.Row():
            with gr.Column():
                buy_symbol = gr.Dropdown(choices=['AAPL', 'TSLA', 'GOOGL'], value='AAPL', label="Symbol to Buy")
                buy_quantity = gr.Number(value=10, label="Quantity", precision=0)
                buy_btn = gr.Button("Buy Shares")
                buy_output = gr.Textbox(label="Buy Result", interactive=False)
                buy_btn.click(buy_shares, inputs=[buy_symbol, buy_quantity], outputs=[buy_output])
            
            with gr.Column():
                sell_symbol = gr.Dropdown(choices=['AAPL', 'TSLA', 'GOOGL'], value='AAPL', label="Symbol to Sell")
                sell_quantity = gr.Number(value=5, label="Quantity", precision=0)
                sell_btn = gr.Button("Sell Shares")
                sell_output = gr.Textbox(label="Sell Result", interactive=False)
                sell_btn.click(sell_shares, inputs=[sell_symbol, sell_quantity], outputs=[sell_output])
    
    with gr.Tab("Portfolio Status"):
        gr.Markdown("### Account Overview")
        
        status_output = gr.Textbox(label="Account Status", interactive=False)
        holdings_output = gr.Textbox(label="Holdings", interactive=False)
        transactions_output = gr.Textbox(label="Recent Transactions", interactive=False)
        
        refresh_btn = gr.Button("Refresh Portfolio Status")
        
        def refresh_all():
            return get_account_status(), get_holdings_info(), get_transactions_history()
        
        refresh_btn.click(refresh_all, outputs=[status_output, holdings_output, transactions_output])

if __name__ == "__main__":
    demo.launch()