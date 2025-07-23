class AgentHUserHistory:
    def run(self, user_id=None, **kwargs):
        """
        Get user investment history from database
        
        Args:
            user_id: User ID to get history for
            
        Returns:
            Dictionary with user history information
        """
        if not user_id:
            return {
                "history_summary": "No user history available.",
                "preferred_sectors": [],
                "recent_trades": []
            }
            
        # Get user history from database
        from agents.stock_agent import EnhancedDatabaseManager
        db_manager = EnhancedDatabaseManager()
        
        # Get user investments
        investments = []
        with db_manager.get_connection() as conn:
            # Get recent trades
            results = conn.execute('''
                SELECT * FROM investments 
                WHERE user_id = ? 
                ORDER BY purchase_date DESC
                LIMIT 10
            ''', (user_id,)).fetchall()
            
            if results:
                for row in results:
                    investments.append({
                        "stock_code": row['stock_symbol'],
                        "action": "buy",  # We only track buys for now
                        "quantity": row['quantity'],
                        "price": row['purchase_price'],
                        "date": row['purchase_date'],
                        "sector": row['sector']
                    })
        
        # Calculate preferred sectors based on investment value
        sector_values = {}
        for inv in investments:
            sector = inv.get('sector', 'Unknown')
            if sector not in sector_values:
                sector_values[sector] = 0
            sector_values[sector] += inv.get('quantity', 0) * inv.get('price', 0)
        
        # Sort sectors by investment value
        preferred_sectors = sorted(
            sector_values.keys(), 
            key=lambda s: sector_values.get(s, 0), 
            reverse=True
        )
        
        # Generate summary
        if preferred_sectors:
            top_sectors = preferred_sectors[:2]
            history_summary = f"User prefers {' and '.join(top_sectors)} sectors."
        else:
            history_summary = "No investment history available."
            
        return {
            "history_summary": history_summary,
            "preferred_sectors": preferred_sectors,
            "recent_trades": investments[:5]  # Return only the 5 most recent trades
        }
        
    def get_extended_context(self, user_id):
        """Get extended user context based on history"""
        if not user_id:
            return {
                "risk_tolerance": "moderate",
                "investment_horizon": "medium",
                "preferred_sectors": []
            }
            
        # Get user preferences from database
        from agents.stock_agent import EnhancedDatabaseManager
        db_manager = EnhancedDatabaseManager()
        
        user_prefs = {
            "risk_tolerance": "moderate",
            "investment_horizon": "medium",
            "preferred_sectors": []
        }
        
        with db_manager.get_connection() as conn:
            # Get user preferences
            result = conn.execute('''
                SELECT * FROM user_preferences 
                WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if result:
                user_prefs["risk_tolerance"] = result['risk_appetite']
                user_prefs["investment_horizon"] = result['time_horizon']
                user_prefs["preferred_sectors"] = [result['sector']] if result['sector'] else []
                
        # If no preferred sectors in preferences, get from investments
        if not user_prefs["preferred_sectors"]:
            history = self.run(user_id)
            user_prefs["preferred_sectors"] = history.get("preferred_sectors", [])
            
        return user_prefs
        
    def update_from_feedback(self, user_id, feedback, recommendations):
        """Update user history based on feedback"""
        if not user_id or not feedback or not recommendations:
            return False
            
        # Extract sectors from recommendations
        sectors = []
        for rec in recommendations:
            if isinstance(rec, dict) and 'company' in rec:
                # Extract sector if available
                if 'analysis_highlights' in rec and 'sector' in rec['analysis_highlights']:
                    sectors.append(rec['analysis_highlights']['sector'])
        
        # Update user preferences in database if we have sectors
        if sectors:
            from agents.stock_agent import EnhancedDatabaseManager
            db_manager = EnhancedDatabaseManager()
            
            with db_manager.get_connection() as conn:
                # Get existing preferences
                result = conn.execute('''
                    SELECT * FROM user_preferences 
                    WHERE user_id = ?
                ''', (user_id,)).fetchone()
                
                if result:
                    # Update sector preference based on feedback
                    if feedback.lower() == 'positive':
                        # Use the first sector from recommendations
                        conn.execute('''
                            UPDATE user_preferences 
                            SET sector = ? 
                            WHERE user_id = ?
                        ''', (sectors[0], user_id))
                        conn.commit()
                
        return True