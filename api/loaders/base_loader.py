"""Base loader module providing abstract base class for data loaders."""

from abc import ABC
from typing import Tuple, List
from api.config import Config


class BaseLoader(ABC):
    """Abstract base class for data loaders."""

    @staticmethod
    def load(_graph_id: str, _data) -> Tuple[bool, str]:
        """
        Load the graph data into the database.
        This method must be implemented by any subclass.
        """
        return False, "Not implemented"

    @staticmethod
    def extract_distinct_values_for_column(cursor, table_name: str, col_name: str) -> List[str]:
        """
        Extract distinct values for a column if it meets the criteria for inclusion.
        
        Args:
            cursor: Database cursor
            table_name: Name of the table
            col_name: Name of the column
            
        Returns:
            List of formatted distinct values to add to description, or empty list
        """
        # Count rows and distinct values for the column
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total_count,
                   COUNT(DISTINCT {col_name}) AS distinct_count
            FROM {table_name};
            """
        )
        output = cursor.fetchall()
        
        # Auto-detect result format by checking the first result
        first_result = output[0]
        if isinstance(first_result, dict):
            # MySQL/dictionary-style results
            rows_count, distinct_count = first_result['total_count'], first_result['distinct_count']
        else:
            # PostgreSQL/tuple-style results
            rows_count, distinct_count = first_result

        max_rows = Config.DB_MAX_ROWS
        max_distinct = Config.DB_MAX_DISTINCT
        uniqueness_threshold = Config.DB_UNIQUENESS_THRESHOLD

        if 0 < rows_count < max_rows and distinct_count < max_distinct:
            uniqueness_value = distinct_count / rows_count
            if uniqueness_value < uniqueness_threshold:
                cursor.execute(
                    f"SELECT DISTINCT {col_name} FROM {table_name};"
                )
                
                distinct_results = cursor.fetchall()
                if distinct_results and isinstance(distinct_results[0], dict):
                    # MySQL/dictionary-style results
                    distinct_values = [row[col_name] for row in distinct_results if row[col_name] is not None]
                else:
                    # PostgreSQL/tuple-style results
                    distinct_values = [row[0] for row in distinct_results if row[0] is not None]
                
                if distinct_values:
                    # Check first value type to avoid objects like dict/bytes
                    first_val = distinct_values[0]
                    if isinstance(first_val, (str, int, float)):
                        return [f"(Optional values: {', '.join(f'({str(v)})' for v in distinct_values)})"]
        
        return []
