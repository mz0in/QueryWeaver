#!/usr/bin/env python3
"""
Test script for the ResponseFormatterAgent to ensure it works correctly.
"""

import os
import sys

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from agents import ResponseFormatterAgent

def test_response_agent():
    """Test the ResponseFormatterAgent with sample data."""

    # Initialize the agent
    agent = ResponseFormatterAgent()

    # Test case 1: Simple count query
    user_query1 = "How many customers do we have?"
    sql_query1 = "SELECT COUNT(*) as customer_count FROM customers"
    query_results1 = [{"customer_count": 150}]
    db_description1 = "A customer management database containing customer information."

    print("Test 1: Simple count query")
    print(f"User Query: {user_query1}")
    print(f"SQL Query: {sql_query1}")
    print(f"Results: {query_results1}")
    print("AI Response:")

    try:
        response1 = agent.format_response(user_query1, sql_query1, query_results1, db_description1)
        print(response1)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This might fail without proper API credentials")
        print("\n" + "="*80 + "\n")

    # Test case 2: List query with multiple results
    user_query2 = "What are the top 5 products by sales?"
    sql_query2 = (
        "SELECT product_name, sales_amount FROM products "
        "ORDER BY sales_amount DESC LIMIT 5"
    )
    query_results2 = [
        {"product_name": "Laptop Pro", "sales_amount": 50000},
        {"product_name": "Wireless Mouse", "sales_amount": 35000},
        {"product_name": "USB-C Cable", "sales_amount": 28000},
        {"product_name": "Bluetooth Speaker", "sales_amount": 22000},
        {"product_name": "Phone Case", "sales_amount": 18000}
    ]
    db_description2 = "An e-commerce database containing product and sales information."

    print("Test 2: Top products query")
    print(f"User Query: {user_query2}")
    print(f"SQL Query: {sql_query2}")
    print(f"Results: {query_results2}")
    print("AI Response:")

    try:
        response2 = agent.format_response(user_query2, sql_query2, query_results2, db_description2)
        print(response2)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This might fail without proper API credentials")
        print("\n" + "="*80 + "\n")

    # Test case 3: INSERT query result
    user_query3 = "Add a new user with name Guy and email gg@gg.com"
    sql_query3 = "INSERT INTO users (id, name, email) VALUES (12345, 'Guy', 'gg@gg.com')"
    query_results3 = [{"operation": "INSERT", "affected_rows": 1, "status": "success"}]
    db_description3 = "A user management database."

    print("Test 3: INSERT query result")
    print(f"User Query: {user_query3}")
    print(f"SQL Query: {sql_query3}")
    print(f"Results: {query_results3}")
    print("AI Response:")

    try:
        response3 = agent.format_response(user_query3, sql_query3, query_results3, db_description3)
        print(response3)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This might fail without proper API credentials")
        print("\n" + "="*80 + "\n")

    # Test case 4: Destructive operation detection (simulation)
    print("Test 4: Destructive operation detection (simulation)")
    print("This would be detected as destructive and require confirmation:")

    user_query4 = "Delete the user with email test@example.com"
    sql_query4 = "DELETE FROM users WHERE email = 'test@example.com'"
    print(f"User Query: {user_query4}")
    print(f"SQL Query: {sql_query4}")
    print("🛡️ This would trigger the destructive operation confirmation dialog")
    print("User would need to type 'CONFIRM' to proceed")
    print("\n" + "="*80 + "\n")

    # Test case 5: Empty results
    user_query5 = "How many orders were placed yesterday?"
    sql_query5 = "SELECT COUNT(*) as order_count FROM orders WHERE order_date = '2024-01-20'"
    query_results5 = []
    db_description5 = "An order management database."

    print("Test 5: Empty results query")
    print(f"User Query: {user_query5}")
    print(f"SQL Query: {sql_query5}")
    print(f"Results: {query_results5}")
    print("AI Response:")

    try:
        response5 = agent.format_response(user_query5, sql_query5, query_results5, db_description5)
        print(response5)
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This might fail without proper API credentials")

if __name__ == "__main__":
    print("Testing ResponseFormatterAgent...")
    print("="*80)
    test_response_agent()
    print("="*80)
    print("Test completed!")
