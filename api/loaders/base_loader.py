"""Base loader module providing abstract base class for data loaders."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Any, Tuple, TYPE_CHECKING
from api.config import Config


class BaseLoader(ABC):
    """Abstract base class for data loaders."""

    # DDL operations that modify database schema (common to both MySQL and PostgreSQL)
    SCHEMA_MODIFYING_OPERATIONS = {
        'CREATE', 'ALTER', 'DROP', 'RENAME', 'TRUNCATE'
    }

    # More specific patterns for schema-affecting operations (common patterns)
    SCHEMA_PATTERNS = [
        r'^\s*CREATE\s+TABLE',
        r'^\s*CREATE\s+INDEX',
        r'^\s*CREATE\s+UNIQUE\s+INDEX',
        r'^\s*ALTER\s+TABLE',
        r'^\s*DROP\s+TABLE',
        r'^\s*DROP\s+INDEX',
        r'^\s*RENAME\s+TABLE',
        r'^\s*TRUNCATE\s+TABLE',
        r'^\s*CREATE\s+VIEW',
        r'^\s*DROP\s+VIEW',
        r'^\s*CREATE\s+SCHEMA',
        r'^\s*DROP\s+SCHEMA',
    ]

    @staticmethod
    @abstractmethod
    async def load(_graph_id: str, _data) -> AsyncGenerator[tuple[bool, str], None]:
        """
        Load the graph data into the database.
        This method must be implemented by any subclass.
        """
        # This method is intended to be implemented by subclasses as an
        # async generator (using `yield`). Including a `yield` inside a
        # `if TYPE_CHECKING` block makes the function an async generator
        # for static type checkers (mypy) while having no runtime effect.
        if TYPE_CHECKING:  # pragma: no cover - only for type checking
            yield True, ""

    @staticmethod
    @abstractmethod
    def _execute_count_query(cursor, table_name: str, col_name: str) -> Tuple[int, int]:
        """
        Execute query to get total count and distinct count for a column.

        Args:
            cursor: Database cursor
            table_name: Name of the table
            col_name: Name of the column

        Returns:
            Tuple of (total_count, distinct_count)
        """

    @staticmethod
    @abstractmethod
    def _execute_distinct_query(cursor, table_name: str, col_name: str) -> List[Any]:
        """
        Execute query to get distinct values for a column.

        Args:
            cursor: Database cursor
            table_name: Name of the table
            col_name: Name of the column

        Returns:
            List of distinct values
        """

    @classmethod
    def extract_distinct_values_for_column(
        cls, cursor, table_name: str, col_name: str
    ) -> List[str]:
        """
        Extract distinct values for a column if it meets the criteria for inclusion.

        Args:
            cursor: Database cursor
            table_name: Name of the table
            col_name: Name of the column

        Returns:
            List of formatted distinct values to add to description, or empty list
        """
        # Get row counts using database-specific implementation
        rows_count, distinct_count = cls._execute_count_query(
            cursor, table_name, col_name
        )

        max_distinct = Config.DB_MAX_DISTINCT
        uniqueness_threshold = Config.DB_UNIQUENESS_THRESHOLD

        if 0 < distinct_count < max_distinct and distinct_count < (
            uniqueness_threshold * rows_count
        ):
            # Get distinct values using database-specific implementation
            distinct_values = cls._execute_distinct_query(cursor, table_name, col_name)

            if distinct_values:
                # Check first value type to avoid objects like dict/bytes
                first_val = distinct_values[0]
                if isinstance(first_val, (str, int)):
                    return [
                        f"(Optional values: {', '.join(f'({str(v)})' for v in distinct_values)})"
                    ]

        return []
