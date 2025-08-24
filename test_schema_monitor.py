"""Test script for schema monitoring functionality."""

import unittest
import sys
import os

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.loaders.postgres_loader import PostgresLoader


class TestSchemaMonitor(unittest.TestCase):
    """Test cases for PostgresLoader schema monitoring functionality."""

    def test_create_table_detection(self):
        """Test detection of CREATE TABLE statements."""
        queries = [
            "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50))",
            "create table products (id serial primary key, name text)",
            "CREATE TABLE IF NOT EXISTS orders (id INT, user_id INT)",
        ]

        for query in queries:
            is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)
            self.assertTrue(is_modifying, f"Should detect CREATE TABLE: {query}")
            self.assertEqual(operation, "CREATE")

    def test_alter_table_detection(self):
        """Test detection of ALTER TABLE statements."""
        queries = [
            "ALTER TABLE users ADD COLUMN email VARCHAR(100)",
            "alter table products drop column description",
            "ALTER TABLE orders MODIFY COLUMN total DECIMAL(10,2)",
        ]

        for query in queries:
            is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)
            self.assertTrue(is_modifying, f"Should detect ALTER TABLE: {query}")
            self.assertEqual(operation, "ALTER")

    def test_drop_table_detection(self):
        """Test detection of DROP TABLE statements."""
        queries = [
            "DROP TABLE users",
            "drop table if exists products",
            "DROP TABLE orders CASCADE",
        ]

        for query in queries:
            is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)
            self.assertTrue(is_modifying, f"Should detect DROP TABLE: {query}")
            self.assertEqual(operation, "DROP")

    def test_index_operations_detection(self):
        """Test detection of index-related operations."""
        queries = [
            "CREATE INDEX idx_user_email ON users(email)",
            "CREATE UNIQUE INDEX idx_product_sku ON products(sku)",
            "DROP INDEX idx_user_email",
        ]

        for query in queries:
            is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)
            self.assertTrue(is_modifying, f"Should detect index operation: {query}")
            self.assertIn(operation, ["CREATE", "DROP"])

    def test_non_schema_queries(self):
        """Test that non-schema-modifying queries are not detected."""
        queries = [
            "SELECT * FROM users",
            "INSERT INTO users (name) VALUES ('John')",
            "UPDATE users SET name = 'Jane' WHERE id = 1",
            "DELETE FROM users WHERE id = 1",
        ]

        for query in queries:
            is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)
            self.assertFalse(is_modifying, f"Should not detect as schema-modifying: {query}")

    def test_empty_and_invalid_queries(self):
        """Test handling of empty and invalid queries."""
        invalid_queries = [
            "",
            "   ",
            None,
            "INVALID SQL STATEMENT",
        ]

        for query in invalid_queries:
            is_modifying, operation = PostgresLoader.is_schema_modifying_query(query)
            self.assertFalse(is_modifying, f"Should not detect empty/invalid query: {query}")
            self.assertEqual(operation, "")


if __name__ == "__main__":
    print("Running Schema Monitor Tests...")
    unittest.main(verbosity=2)
