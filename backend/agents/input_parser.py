import re

REQUIRED_FIELDS = ["budget", "sector_preference", "risk_tolerance", "time_horizon", "target_profit"]

def parse_hybrid_input(user_input: dict, chat_message: str = "") -> dict:
    # Start with form input
    parsed = {k: v for k, v in user_input.items() if v}
    # Try to extract from chat if missing
    if chat_message:
        # Budget
        if "budget" not in parsed:
            match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)(?:k)?\s*PKR', chat_message, re.I)
            if match:
                val = match.group(1).replace(',', '')
                parsed["budget"] = str(int(val) * 1000 if 'k' in chat_message.lower() else int(val)) + " PKR"
        # Sector
        if "sector_preference" not in parsed:
            for sector in ["banking", "tech", "energy", "cement"]:
                if sector in chat_message.lower():
                    parsed["sector_preference"] = sector.capitalize()
        # Risk
        if "risk_tolerance" not in parsed:
            for risk in ["low", "medium", "high"]:
                if risk in chat_message.lower():
                    parsed["risk_tolerance"] = risk.capitalize()
        # Time horizon
        if "time_horizon" not in parsed:
            match = re.search(r'(\d+)\s*(day|week|month|year)', chat_message, re.I)
            if match:
                parsed["time_horizon"] = f"{match.group(1)} {match.group(2)}s"
        # Target profit
        if "target_profit" not in parsed:
            match = re.search(r'(\d+)%\s*(profit|return)', chat_message, re.I)
            if match:
                parsed["target_profit"] = match.group(1) + "%"

    # Identify missing fields
    missing = [f for f in REQUIRED_FIELDS if f not in parsed]
    return parsed, missing
