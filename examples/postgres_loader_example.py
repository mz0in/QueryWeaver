#!/usr/bin/env python3
"""
Example usage of PostgreSQL Loader

This script demonstrates how to use the PostgreSQL loader to extract
schema information from a PostgreSQL database and load it into a graph.
"""

from api.loaders.postgres_loader import PostgreSQLLoader


def main():
    """
    Example usage of PostgreSQL loader
    """

    # Example connection URLs (modify these with your actual database credentials)
    connection_examples = [
        "postgresql://username:password@localhost:5432/mydatabase",
        "postgresql://user:pass@example.com:5432/production_db",
        "postgresql://postgres:admin@127.0.0.1:5432/testdb",
    ]

    print("PostgreSQL Loader Example")
    print("=" * 40)
    print()
    print("Example connection URL formats:")
    for i, url in enumerate(connection_examples, 1):
        print(f"{i}. {url}")
    print()

    # Get connection URL from user
    connection_url = input("Enter your PostgreSQL connection URL: ").strip()

    if not connection_url:
        print("No connection URL provided. Using example URL...")
        connection_url = "postgresql://postgres:password@localhost:5432/example_db"

    # Get graph ID
    graph_id = input("Enter graph ID (default: 'postgres_schema'): ").strip()
    if not graph_id:
        graph_id = "postgres_schema"

    print(f"\nConnecting to database: {connection_url}")
    print(f"Loading into graph: {graph_id}")
    print()

    # Load the schema
    try:
        success, message = PostgreSQLLoader.load(graph_id, connection_url)

        if success:
            print("✅ Success!")
            print(f"   {message}")
        else:
            print("❌ Failed!")
            print(f"   {message}")

    except (ImportError, AttributeError, ValueError) as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
