import streamlit as st
from stock_agent import StockAnalysisAgent
from dataclasses import asdict
import pandas as pd

st.set_page_config(page_title="PSX AI Stock Chatbot", page_icon="📈", layout="centered")
st.title("📈 PSX AI Stock Chatbot")

if "agent" not in st.session_state:
    st.session_state.agent = StockAnalysisAgent()
agent = st.session_state.agent

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "history" not in st.session_state:
    st.session_state.history = []

# --- User Login ---
st.markdown("### User Login")
user_id_input = st.text_input("Enter your user ID (or type 'new' to create a new user)", value=st.session_state.user_id or "")
if user_id_input.lower() == "new":
    name = st.text_input("Enter your name to register as a new user", value=st.session_state.user_name or "")
    if name:
        user_id = agent.db_manager.create_user(name)
        st.session_state.user_id = user_id
        st.session_state.user_name = name
        st.success(f"New user created! Your user ID is: {user_id}")
else:
    # Check if user exists
    if user_id_input:
        profile = agent.db_manager.get_user_profile(user_id_input)
        if profile:
            st.session_state.user_id = user_id_input
            st.session_state.user_name = profile.name
            st.success(f"Welcome back, {profile.name}!")
        elif user_id_input:
            st.warning("User not found. Please enter a valid user ID or type 'new'.")

user_id = st.session_state.user_id
user_name = st.session_state.user_name

if user_id:
    st.markdown(f"**Logged in as:** {user_name} ({user_id})")
    st.divider()
    st.markdown("### Menu")
    menu = st.selectbox(
        "Choose an action:",
        ["Chat (Ask anything)", "View Portfolio", "View Signals", "Add Stock to Portfolio", "User Management", "Performance Report", "Update Data"],
        key="menu_option"
    )
    if menu == "View Portfolio":
        perf = agent.db_manager.get_portfolio_performance(user_id)
        holdings = agent.db_manager.get_user_portfolio(user_id)
        st.write(f"**Portfolio Value:** ${perf['total_value']:.2f}")
        st.write(f"**Total P/L:** ${perf['total_pl']:.2f} ({perf['total_pl_percent']:.2f}%)")
        if holdings:
            df = pd.DataFrame(holdings)
            st.dataframe(df)
            # Bar chart: current value per stock
            if "stock_code" in df and "current_price" in df and "quantity" in df:
                df["current_value"] = df["current_price"] * df["quantity"]
                st.bar_chart(df.set_index("stock_code")["current_value"])
            # Pie chart: sector allocation
            if "sector" in df and "current_value" in df:
                sector_df = df.groupby("sector")["current_value"].sum()
                st.write("### Sector Allocation")
                st.pyplot(sector_df.plot.pie(autopct='%1.1f%%', ylabel='').get_figure())
    elif menu == "View Signals":
        signals = agent.signal_generator.generate_intelligent_signals(user_id)
        if not signals:
            st.info("No strong signals at the moment.")
        else:
            st.dataframe([asdict(s) for s in signals])
    elif menu == "Add Stock to Portfolio":
        stock_code = st.text_input("Stock code (e.g., AAPL)", key="add_stock_code")
        quantity = st.number_input("Quantity", min_value=1, step=1, key="add_stock_qty")
        if st.button("Add Stock"):
            result = agent._execute_buy(user_id, stock_code.upper(), int(quantity))
            st.success(result)
    elif menu == "User Management":
        st.write("User management features coming soon. For now, you can view your profile below:")
        profile = agent.db_manager.get_user_profile(user_id)
        st.json(asdict(profile))
    elif menu == "Performance Report":
        report = agent.performance_tracker.generate_performance_report(user_id)
        st.write("**Portfolio Performance:**")
        st.json(report["portfolio_performance"])
        st.write("**Monthly Performance:**")
        st.json(report["monthly"])
        st.write("**Weekly Performance:**")
        st.json(report["weekly"])
        st.write("**Yearly Performance:**")
        st.json(report["yearly"])
    elif menu == "Update Data":
        with st.spinner("Updating data (running fin.py)..."):
            agent._daily_data_update()
        st.success("Data update complete.")
    elif menu == "Chat (Ask anything)":
        st.markdown("#### Chat with the AI Agent")
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and "data" in msg and msg["data"]:
                    if "holdings" in msg["data"] and msg["data"]["holdings"]:
                        st.dataframe(msg["data"]["holdings"])
                    if "recommendations" in msg["data"] and msg["data"]["recommendations"]:
                        st.dataframe(msg["data"]["recommendations"])
                    if "signals" in msg["data"] and msg["data"]["signals"]:
                        st.dataframe(msg["data"]["signals"])
        prompt = st.chat_input("Type your question and press Enter...")
        if prompt:
            st.session_state.history.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                response = agent.handle_prompt(user_id, prompt)
                st.markdown(response["text"])
                if "holdings" in response["data"] and response["data"]["holdings"]:
                    st.dataframe(response["data"]["holdings"])
                if "recommendations" in response["data"] and response["data"]["recommendations"]:
                    st.dataframe(response["data"]["recommendations"])
                if "signals" in response["data"] and response["data"]["signals"]:
                    st.dataframe(response["data"]["signals"])
                if "chart_data" in response and response["chart_data"]:
                    df = pd.DataFrame({
                        "Date": response["chart_data"]["dates"],
                        "Price": response["chart_data"]["prices"]
                    })
                    st.line_chart(df.set_index("Date"))
            st.session_state.history.append({"role": "assistant", "content": response["text"], "data": response["data"]})
else:
    st.info("Please log in with your user ID or create a new user to continue.")