from flask import Blueprint, jsonify, request
from agents.stock_agent import EnhancedDatabaseManager
from api.portfolio_update import update_portfolio_current_prices
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

portfolio_routes = Blueprint('portfolio_routes', __name__)

@portfolio_routes.route('/api/users/initialize', methods=['POST'])
def initialize_user():
    """
    Endpoint to initialize a new user with default values
    """
    try:
        data = request.json
        user_id = data.get('userId', 'demo_user')
        
        # Initialize database manager
        db_manager = EnhancedDatabaseManager()
        
        # Check if user already exists
        user_profile = db_manager.get_user_profile(user_id)
        if user_profile:
            return jsonify({
                'success': True,
                'message': 'User already exists',
                'user_id': user_id
            }), 200
        
        # Create a new user profile
        with db_manager.get_connection() as conn:
            conn.execute('''
                INSERT INTO users (
                    user_id, name, email, risk_tolerance, investment_goal,
                    portfolio_value, cash_balance, preferred_sectors, blacklisted_stocks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 'New User', f'{user_id}@example.com', 'medium', 'growth',
                10000.0, 10000.0, '[]', '[]'
            ))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'User initialized successfully',
            'user_id': user_id
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error initializing user: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """
    Endpoint to fetch user's portfolio
    Returns a JSON object with portfolio data
    """
    try:
        user_id = request.args.get('user_id', 'demo_user')
        
        # Initialize database manager
        db_manager = EnhancedDatabaseManager()
        
        # Get user profile
        user_profile = db_manager.get_user_profile(user_id)
        if not user_profile:
            # Create a new user profile if it doesn't exist
            with db_manager.get_connection() as conn:
                conn.execute('''
                    INSERT INTO users (
                        user_id, name, email, risk_tolerance, investment_goal,
                        portfolio_value, cash_balance, preferred_sectors, blacklisted_stocks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, 'Demo User', 'demo@example.com', 'medium', 'growth',
                    10000.0, 10000.0, '[]', '[]'
                ))
                conn.commit()
            user_profile = db_manager.get_user_profile(user_id)
        
        # Update current prices before fetching portfolio
        update_portfolio_current_prices(user_id)
        
        # Get user investments
        investments = []
        with db_manager.get_connection() as conn:
            results = conn.execute('''
                SELECT * FROM investments WHERE user_id = ?
            ''', (user_id,)).fetchall()
            
            if results:
                for row in results:
                    investments.append({
                        'id': row['id'],
                        'user_id': row['user_id'],
                        'stockSymbol': row['stock_symbol'],
                        'companyName': row['company_name'],
                        'quantity': row['quantity'],
                        'purchasePrice': row['purchase_price'],
                        'currentPrice': row['current_price'],
                        'purchase_date': row['purchase_date'],
                        'sector': row['sector'],
                        'status': row['status']
                    })
        
        # Calculate portfolio metrics
        total_invested = sum(inv['purchasePrice'] * inv['quantity'] for inv in investments)
        total_value = sum(inv['currentPrice'] * inv['quantity'] for inv in investments) + user_profile.cash_balance
        total_returns = total_value - total_invested - user_profile.cash_balance
        return_percentage = (total_returns / total_invested) * 100 if total_invested > 0 else 0
        
        # Calculate sector allocation
        sector_allocation = {}
        for inv in investments:
            value = inv['currentPrice'] * inv['quantity']
            sector = inv['sector']
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += value
        
        allocation = []
        for sector, value in sector_allocation.items():
            percentage = (value / (total_value - user_profile.cash_balance)) * 100 if total_value > user_profile.cash_balance else 0
            allocation.append({
                'sector': sector,
                'value': value,
                'percentage': percentage,
                'color': f'#{hash(sector) % 0xFFFFFF:06x}'  # Generate a color based on sector name
            })
        
        return jsonify({
            'totalValue': total_value,
            'totalInvested': total_invested,
            'totalReturns': total_returns,
            'returnPercentage': return_percentage,
            'cashBalance': user_profile.cash_balance,
            'investments': investments,
            'allocation': allocation
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching portfolio data: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/investments', methods=['POST'])
def add_investment():
    """
    Endpoint to add a new investment to the portfolio
    """
    try:
        data = request.json
        user_id = data.get('userId', 'demo_user')
        stock_symbol = data.get('stockSymbol')
        amount = data.get('amount', 0)
        
        if not stock_symbol or amount <= 0:
            return jsonify({
                'success': False,
                'message': 'Invalid investment data'
            }), 400
        
        # Initialize database manager
        db_manager = EnhancedDatabaseManager()
        
        # Get user profile
        user_profile = db_manager.get_user_profile(user_id)
        if not user_profile:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check if user has enough cash
        if user_profile.cash_balance < amount:
            return jsonify({
                'success': False,
                'message': 'Insufficient funds'
            }), 400
        
        # Get stock data
        stock_data = None
        with db_manager.get_connection() as conn:
            result = conn.execute('''
                SELECT * FROM stock_data WHERE code = ? ORDER BY timestamp DESC LIMIT 1
            ''', (stock_symbol,)).fetchone()
            
            if result:
                stock_data = {
                    'code': result['code'],
                    'name': result['name'],
                    'sector': result['sector'],
                    'price': result['close_price']
                }
        
        if not stock_data:
            return jsonify({
                'success': False,
                'message': f'Stock {stock_symbol} not found'
            }), 404
        
        # Calculate quantity based on amount and current price
        quantity = int(amount / stock_data['price'])
        if quantity <= 0:
            return jsonify({
                'success': False,
                'message': 'Amount too small to purchase any shares'
            }), 400
        
        # Check if user already owns this stock
        existing_investment = None
        with db_manager.get_connection() as conn:
            result = conn.execute('''
                SELECT * FROM investments 
                WHERE user_id = ? AND stock_symbol = ? AND status = 'active'
            ''', (user_id, stock_symbol)).fetchone()
            
            if result:
                existing_investment = {
                    'id': result['id'],
                    'quantity': result['quantity'],
                    'purchase_price': result['purchase_price']
                }
        
        # Add investment to database
        with db_manager.get_connection() as conn:
            if existing_investment:
                # Calculate new average purchase price
                total_shares = existing_investment['quantity'] + quantity
                total_cost = (existing_investment['purchase_price'] * existing_investment['quantity']) + (stock_data['price'] * quantity)
                avg_price = total_cost / total_shares
                
                # Update existing investment
                conn.execute('''
                    UPDATE investments 
                    SET quantity = ?, purchase_price = ?, current_price = ?
                    WHERE id = ?
                ''', (
                    total_shares, 
                    avg_price, 
                    stock_data['price'],
                    existing_investment['id']
                ))
            else:
                # Create new investment
                conn.execute('''
                    INSERT INTO investments (
                        user_id, stock_symbol, company_name, quantity, purchase_price,
                        current_price, purchase_date, sector, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, stock_symbol, stock_data['name'], quantity, stock_data['price'],
                    stock_data['price'], datetime.now().isoformat(), stock_data['sector'], 'active'
                ))
            
            # Update user's cash balance
            conn.execute('''
                UPDATE users SET cash_balance = cash_balance - ? WHERE user_id = ?
            ''', (amount, user_id))
            
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully purchased {quantity} shares of {stock_symbol}',
            'investment': {
                'stock_symbol': stock_symbol,
                'company_name': stock_data['name'],
                'quantity': quantity,
                'purchase_price': stock_data['price'],
                'total_cost': amount
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding investment: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/refresh-prices', methods=['POST'])
def refresh_portfolio_prices():
    """
    Endpoint to refresh the current prices of stocks in a portfolio
    """
    try:
        data = request.json
        user_id = data.get('userId', 'demo_user')
        
        # Update current prices
        success = update_portfolio_current_prices(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Portfolio prices updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update portfolio prices'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error refreshing portfolio prices: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/update-value', methods=['POST'])
def update_portfolio_value():
    """
    Endpoint to update the total value of a portfolio
    """
    try:
        data = request.json
        user_id = data.get('userId', 'demo_user')
        total_value = data.get('totalValue')
        
        logger.info(f"Updating portfolio value for {user_id} to {total_value}")
        
        if total_value is None:
            return jsonify({
                'success': False,
                'message': 'Total value is required'
            }), 400
        
        # Initialize database manager
        db_manager = EnhancedDatabaseManager()
        
        # Get user profile
        user_profile = db_manager.get_user_profile(user_id)
        if not user_profile:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Update current prices before calculating
        update_portfolio_current_prices(user_id)
        
        # Get user investments
        investments = []
        with db_manager.get_connection() as conn:
            results = conn.execute('''
                SELECT * FROM investments WHERE user_id = ?
            ''', (user_id,)).fetchall()
            
            if results:
                for row in results:
                    investments.append({
                        'quantity': row['quantity'],
                        'current_price': row['current_price']
                    })
        
        # Calculate investments value
        investments_value = sum(inv['current_price'] * inv['quantity'] for inv in investments)
        
        # Calculate new cash balance
        new_cash_balance = total_value - investments_value
        if new_cash_balance < 0:
            new_cash_balance = 0
        
        logger.info(f"Investments value: {investments_value}, New cash balance: {new_cash_balance}")
        
        # Update user's cash balance
        with db_manager.get_connection() as conn:
            conn.execute('''
                UPDATE users SET cash_balance = ? WHERE user_id = ?
            ''', (new_cash_balance, user_id))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio value updated successfully',
            'totalValue': total_value,
            'cashBalance': new_cash_balance
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating portfolio value: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating portfolio value: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/investments/<investment_id>', methods=['POST'])
def sell_investment(investment_id):
    """
    Endpoint to sell an investment
    """
    try:
        data = request.json
        user_id = data.get('userId', 'demo_user')
        quantity = data.get('quantity', 0)
        
        if quantity <= 0:
            return jsonify({
                'success': False,
                'message': 'Invalid quantity'
            }), 400
        
        # Initialize database manager
        db_manager = EnhancedDatabaseManager()
        
        # Update current prices before selling
        update_portfolio_current_prices(user_id)
        
        # Get investment
        investment = None
        with db_manager.get_connection() as conn:
            result = conn.execute('''
                SELECT * FROM investments WHERE id = ? AND user_id = ?
            ''', (investment_id, user_id)).fetchone()
            
            if result:
                investment = {
                    'id': result['id'],
                    'user_id': result['user_id'],
                    'stock_symbol': result['stock_symbol'],
                    'company_name': result['company_name'],
                    'quantity': result['quantity'],
                    'purchase_price': result['purchase_price'],
                    'current_price': result['current_price'],
                    'purchase_date': result['purchase_date'],
                    'sector': result['sector'],
                    'status': result['status']
                }
        
        if not investment:
            return jsonify({
                'success': False,
                'message': 'Investment not found'
            }), 404
        
        if investment['quantity'] < quantity:
            return jsonify({
                'success': False,
                'message': f'You only have {investment["quantity"]} shares to sell'
            }), 400
        
        # Calculate sale amount
        sale_amount = quantity * investment['current_price']
        
        # Update investment in database
        with db_manager.get_connection() as conn:
            if investment['quantity'] == quantity:
                # Remove investment if selling all shares
                conn.execute('''
                    DELETE FROM investments WHERE id = ?
                ''', (investment_id,))
            else:
                # Update quantity if selling partial shares
                conn.execute('''
                    UPDATE investments SET quantity = quantity - ? WHERE id = ?
                ''', (quantity, investment_id))
            
            # Update user's cash balance
            conn.execute('''
                UPDATE users SET cash_balance = cash_balance + ? WHERE user_id = ?
            ''', (sale_amount, user_id))
            
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully sold {quantity} shares of {investment["stock_symbol"]}',
            'sale': {
                'stock_symbol': investment['stock_symbol'],
                'quantity': quantity,
                'sale_price': investment['current_price'],
                'total_amount': sale_amount
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error selling investment: {str(e)}'
        }), 500