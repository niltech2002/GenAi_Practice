#Streamlit app for order and refund status



import os
import operator
from typing import TypedDict, Annotated, Literal

import streamlit as st
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# ──────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Order Support Bot",  layout="centered")

# ──────────────────────────────────────────────────────────────
# 2. ENV SETUP
# ──────────────────────────────────────────────────────────────
load_dotenv(override=True)

LLMGW_API_KEY = os.getenv("LLMGW_API_KEY")
LLMGW_BASE_URL = os.getenv("LLMGW_BASE_URL", "https://llmgw-wp.tekstac.com")

# Optional: define these in your .env for convenience
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=your_password
# MYSQL_DATABASE=support_bot
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Tek@12345")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "support_bot")

if not LLMGW_API_KEY:
    st.error("LLMGW_API_KEY not found. Add it to your .env file.")
    st.stop()

# Anthropic-compatible env vars for LangChain internals
os.environ["ANTHROPIC_API_KEY"] = LLMGW_API_KEY
os.environ["ANTHROPIC_BASE_URL"] = LLMGW_BASE_URL

# ──────────────────────────────────────────────────────────────
# 3. DB HELPERS
# ──────────────────────────────────────────────────────────────
def get_db_connection():
    """Create and return a MySQL connection."""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )


def init_db():
    """Create the orders table if it does not exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id VARCHAR(20) PRIMARY KEY,
                item VARCHAR(255) NOT NULL,
                status VARCHAR(100) NOT NULL,
                expected_delivery VARCHAR(100) NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def seed_sample_data_if_empty():
    """Insert sample rows only when the table is empty."""
    sample_rows = [
        ("ORD123", "Wireless Headphones", "Shipped", "Tomorrow"),
        ("ORD456", "Mechanical Keyboard", "Processing", "Next Tuesday"),
        ("ORD789", "Gaming Mouse", "Delivered", "Yesterday"),
        ("ORD321", "Laptop Stand", "Out for Delivery", "Today"),
        ("ORD654", "Smart Watch", "Cancelled", "N/A"),
        ("ORD999", "Bluetooth Speaker", "Delayed", "In 3 days"),
        ("ORD777", "USB Hub", "Processing", "Next Monday"),
        ("ORD888", "Laptop Bag", "Shipped", "Tomorrow"),
    ]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO orders (order_id, item, status, expected_delivery) VALUES (%s, %s, %s, %s)",
                sample_rows,
            )
            conn.commit()
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def get_all_orders(limit: int = 100):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT order_id, item, status, expected_delivery FROM orders ORDER BY order_id LIMIT %s",
            (limit,),
        )
        rows = cursor.fetchall()
        return rows
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

# ──────────────────────────────────────────────────────────────
# 4. TOOLS
# ──────────────────────────────────────────────────────────────
@tool
def check_order_status(order_id: str) -> str:
    """Check the shipping status and expected delivery for a specific customer order. Provide the order ID such as ORD123."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT order_id, item, status, expected_delivery FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id.upper(),))
        order = cursor.fetchone()

        if order:
            return (
                f"Order {order['order_id']}: {order['item']} is currently '{order['status']}'. "
                f"Expected delivery: {order['expected_delivery']}."
            )
        return f"Order {order_id.upper()} not found in the database. Please verify the order ID."
    except Error as e:
        return f"Database error while checking order {order_id.upper()}: {e}"
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


@tool
def calculate_refund_eligibility(days_since_purchase: int) -> str:
    """Determine refund eligibility based on how many days ago the customer purchased the item."""
    if days_since_purchase <= 30:
        return "Eligible for a full refund."
    elif days_since_purchase <= 60:
        return "Eligible for store credit only."
    else:
        return "Not eligible for a refund. The 60-day return window has expired."



# ──────────────────────────────────────────────────────────────
# 5. LLM + GRAPH SETUP
# ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def build_chatbot():
    chat_model = ChatAnthropic(
        model="global.anthropic.claude-sonnet-4-6",
        temperature=0.3,
        anthropic_api_key=LLMGW_API_KEY,
        base_url=LLMGW_BASE_URL,
    )

    agent_tools = [check_order_status, calculate_refund_eligibility]
    tool_map = {t.name: t for t in agent_tools}
    llm_with_tools = chat_model.bind_tools(agent_tools)

    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage], operator.add]

    def support_agent_node(state: AgentState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def tool_execution_node(state: AgentState):
        last_message = state["messages"][-1]
        results = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_output = tool_map[tool_name].invoke(tool_args)
            results.append(
                ToolMessage(
                    content=str(tool_output),
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": results}

    def route_next_step(state: AgentState) -> Literal["tools", "__end__"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", support_agent_node)
    workflow.add_node("tools", tool_execution_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", route_next_step)
    workflow.add_edge("tools", "agent")

    mem_saver = MemorySaver()
    app = workflow.compile(checkpointer=mem_saver)
    return app



# ──────────────────────────────────────────────────────────────
# 6. STREAMLIT SESSION STATE
# ──────────────────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    # Stable per browser session; change it manually in sidebar if needed
    st.session_state.thread_id = "streamlit-user-001"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I’m your order support bot. You can ask things like:\n\n"
                "- Where is my order ORD123?\n"
                "- Check order ORD456\n"
                "- I bought something 45 days ago, can I get a refund?"
            ),
        }
    ]


# ──────────────────────────────────────────────────────────────
# 7. INITIALIZE APP RESOURCES
# ──────────────────────────────────────────────────────────────
try:
    init_db()
    seed_sample_data_if_empty()
except Error as db_init_error:
    st.error(f"Database initialization failed: {db_init_error}")
    st.stop()

app = build_chatbot()


# ──────────────────────────────────────────────────────────────
# 8. SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    st.caption("Configure memory thread and verify environment/database.")

    thread_id_input = st.text_input("Thread ID", value=st.session_state.thread_id, help="Same thread_id = same conversation memory")
    if thread_id_input != st.session_state.thread_id:
        st.session_state.thread_id = thread_id_input.strip() or "streamlit-user-001"
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Thread changed. This is a fresh visible chat window. Memory for each thread is isolated.",
            }
        ]

    if st.button("Clear visible chat"):
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Visible chat cleared. If you keep the same thread_id, LangGraph memory for that thread still exists in this app process.",
            }
        ]

    st.divider()
    st.subheader("Environment")
    st.write(f"**LLMGW Base URL:** {LLMGW_BASE_URL}")
    st.write(f"**MySQL DB:** {MYSQL_DATABASE}")
    st.write(f"**MySQL Host:** {MYSQL_HOST}:{MYSQL_PORT}")

    try:
        conn = get_db_connection()
        conn.close()
        st.success("MySQL connection successful")
    except Error as e:
        st.error(f"MySQL connection failed: {e}")

    st.divider()
    st.subheader("Orders in DB")
    try:
        rows = get_all_orders(limit=50)
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No orders found in the table.")
    except Error as e:
        st.error(f"Could not load orders: {e}")



# ──────────────────────────────────────────────────────────────
# 9. MAIN UI
# ──────────────────────────────────────────────────────────────
st.title(" Order Support Chatbot")
st.caption("LangGraph + MemorySaver + MySQL + Streamlit")

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ──────────────────────────────────────────────────────────────
# 10. CHAT HANDLER
# ──────────────────────────────────────────────────────────────
if user_prompt := st.chat_input("Ask about an order or refund..."):
    st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    thread_cfg = {"configurable": {"thread_id": st.session_state.thread_id}}

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = app.invoke(
                    {"messages": [HumanMessage(content=user_prompt)]},
                    config=thread_cfg,
                )
                assistant_reply = result["messages"][-1].content
                st.markdown(assistant_reply)

        st.session_state.chat_messages.append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        error_msg = f"Sorry, something went wrong: {e}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})


# ──────────────────────────────────────────────────────────────
# 11. OPTIONAL NOTES FOR RUNNING
# ──────────────────────────────────────────────────────────────
# Run with:
#   streamlit run app.py
#
# Example .env:
#   LLMGW_API_KEY=your_key_here
#   LLMGW_BASE_URL=https://llmgw-wp.tekstac.com
#   MYSQL_HOST=localhost
#   MYSQL_PORT=3306
#   MYSQL_USER=root
#   MYSQL_PASSWORD=your_password
#   MYSQL_DATABASE=support_bot
#
# Example SQL (if database not already created):
#   CREATE DATABASE support_bot;
#   USE support_bot;
