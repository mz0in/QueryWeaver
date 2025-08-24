"""Demonstration script for schema monitoring functionality."""

import sys
import os

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.loaders.postgres_loader import PostgresLoader


def demonstrate_schema_monitoring():
    """Demonstrate the schema monitoring functionality."""

    print("🔍 Schema Monitoring Demonstration")
    print("=" * 50)

    # Test queries that modify schema
    schema_queries = [
        (
            "CREATE TABLE customers (id SERIAL PRIMARY KEY, name VARCHAR(100),"
            " email VARCHAR(100))"
        ),
        "ALTER TABLE customers ADD COLUMN phone VARCHAR(20)",
        "CREATE INDEX idx_customer_email ON customers(email)",
        "DROP TABLE old_logs",
        "TRUNCATE TABLE temp_data",
        (
            "CREATE VIEW active_customers AS SELECT * FROM customers "
            "WHERE active = true"
        ),
    ]

    # Test queries that don't modify schema
    non_schema_queries = [
        "SELECT * FROM customers",
        "INSERT INTO customers (name, email) VALUES ('John Doe', 'john@example.com')",
        "UPDATE customers SET phone = '555-0123' WHERE id = 1",
        "DELETE FROM customers WHERE id = 999",
    ]

    print("\n📝 Testing Schema-Modifying Queries:")
    print("-" * 40)

    for query in schema_queries:
        is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)

        print(f"\n🔧 Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        print(f"   ✅ Schema Modifying: {is_modifying}")
        print(f"   🏷️  Operation Type: {operation}")
        if is_modifying:
            print(f"   📋 Summary: {operation} operation detected")

    print("\n\n📝 Testing Non-Schema-Modifying Queries:")
    print("-" * 40)

    for query in non_schema_queries:
        is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)

        print(f"\n📊 Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        print(f"   ❌ Schema Modifying: {is_modifying}")
        print(f"   🏷️  Operation Type: {operation if operation else 'N/A'}")

    print("\n\n🎯 Summary:")
    print("-" * 20)
    schema_count = sum(
        1
        for q in schema_queries
        if PostgresLoader.is_schema_modifying_query(q)[0]
    )
    non_schema_count = sum(
        1
        for q in non_schema_queries
        if not PostgresLoader.is_schema_modifying_query(q)[0]
    )

    summary_schema = f"{schema_count}/{len(schema_queries)}"
    summary_non_schema = f"{non_schema_count}/{len(non_schema_queries)}"

    print("✅ Correctly identified", summary_schema, "schema-modifying queries")
    print("✅ Correctly identified", summary_non_schema, "non-schema-modifying queries")

    print("\n🔄 How it works in the text2sql system:")
    print("-" * 40)
    print("1. When a user executes a SQL query through the chat interface")
    print("2. The system checks if the query modifies the database schema")
    print("3. If schema modification is detected:")
    print("   a. The query is executed normally")
    print("   b. The graph schema is automatically refreshed from the database")
    print("   c. A confirmation message is shown to the user")
    print("4. Future queries will use the updated schema information")

    print("\n🚀 Benefits:")
    print("-" * 12)
    print("• Automatic schema synchronization")
    print("• No manual intervention required")
    print("• Real-time graph updates")
    print("• Better query accuracy with up-to-date schema")
    print("• All functionality integrated into existing PostgresLoader class")


if __name__ == "__main__":
    demonstrate_schema_monitoring()
