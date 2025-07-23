class AgentGRiskProfiler:
    def run(self, user_profile=None, **kwargs):
        """
        Generate a risk profile based on user input
        
        Args:
            user_profile: Dictionary containing user profile information
            
        Returns:
            Dictionary with risk profile information
        """
        # Default values
        risk_profile = "Moderate"
        score = 0.5
        recommendation = "Consider a balanced portfolio with moderate risk."
        
        if user_profile:
            # Extract risk tolerance from user profile
            risk_tolerance = user_profile.get('risk_tolerance', '').lower()
            
            if risk_tolerance == 'low':
                risk_profile = "Low"
                score = 0.3
                recommendation = "Focus on stable, dividend-paying stocks with lower volatility."
            elif risk_tolerance == 'high':
                risk_profile = "High"
                score = 0.8
                recommendation = "Consider growth stocks with higher potential returns but increased volatility."
            else:  # Default to moderate
                risk_profile = "Moderate"
                score = 0.5
                recommendation = "Balance your portfolio between growth and stability."
                
            # Adjust based on time horizon if available
            time_horizon = user_profile.get('time_horizon', '').lower()
            if time_horizon == 'short':
                # Reduce risk for short-term investments
                score = max(0.2, score - 0.2)
                recommendation = "With a short time horizon, prioritize capital preservation."
            elif time_horizon == 'long':
                # Increase risk tolerance for long-term investments
                score = min(0.9, score + 0.1)
                recommendation += " With a long time horizon, you can withstand short-term volatility."
        
        return {
            "risk_profile": risk_profile,
            "score": score,
            "recommendation": recommendation
        }