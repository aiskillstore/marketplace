"""
SQL Helper Module
=================

Comprehensive utilities for database operations, schema management,
query building, and performance analysis.

Supports: PostgreSQL, MySQL, SQLite

Usage Examples:
    >>> from sql_helper import DatabaseHelper
    >>> db = DatabaseHelper('postgresql://user:pass@localhost/mydb')
    >>> tables = db.list_tables()
    >>> db.execute_with_timing("SELECT * FROM users LIMIT 10")
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
import time
import json
from contextlib import contextmanager

try:
    from sqlalchemy import (
        create_engine, inspect, text, MetaData, Table,
        Column, Integer, String, DateTime, Boolean, Float
    )
    from sqlalchemy.engine import Engine, Connection
    from sqlalchemy.pool import NullPool
except ImportError:
    raise ImportError(
        "SQLAlchemy is required. Install with: pip install sqlalchemy"
    )


@dataclass
class QueryResult:
    """Container for query execution results with metadata."""
    rows: List[Dict[str, Any]]
    execution_time: float
    row_count: int
    column_names: List[str]

    def __str__(self) -> str:
        return (
            f"QueryResult(rows={self.row_count}, "
            f"time={self.execution_time:.3f}s)"
        )


@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    schema: str
    columns: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    row_count: Optional[int] = None

    def __str__(self) -> str:
        return f"Table({self.schema}.{self.name}, {len(self.columns)} columns)"


@dataclass
class IndexRecommendation:
    """Index recommendation based on query analysis."""
    table: str
    columns: List[str]
    reason: str
    estimated_benefit: str
    create_statement: str


class DatabaseHelper:
    """
    Comprehensive database helper for common operations.

    Examples:
        >>> # Connect to PostgreSQL
        >>> db = DatabaseHelper('postgresql://user:pass@localhost/mydb')
        >>>
        >>> # List all tables
        >>> tables = db.list_tables()
        >>>
        >>> # Get table schema
        >>> schema = db.get_table_schema('users')
        >>>
        >>> # Execute with timing
        >>> result = db.execute_with_timing("SELECT COUNT(*) FROM users")
        >>> print(f"Query took {result.execution_time:.2f}s")
        >>>
        >>> # Analyze indexes
        >>> recommendations = db.analyze_indexes('users')
    """

    def __init__(
        self,
        connection_string: str,
        echo: bool = False,
        pool_size: int = 5
    ):
        """
        Initialize database helper.

        Args:
            connection_string: SQLAlchemy connection string
                Examples:
                    - PostgreSQL: 'postgresql://user:pass@localhost/dbname'
                    - MySQL: 'mysql+pymysql://user:pass@localhost/dbname'
                    - SQLite: 'sqlite:///path/to/database.db'
            echo: If True, log all SQL statements
            pool_size: Connection pool size (ignored for SQLite)
        """
        self.connection_string = connection_string
        self.dialect = self._detect_dialect(connection_string)

        # Configure engine based on dialect
        if self.dialect == 'sqlite':
            self.engine = create_engine(
                connection_string,
                echo=echo,
                poolclass=NullPool
            )
        else:
            self.engine = create_engine(
                connection_string,
                echo=echo,
                pool_size=pool_size,
                max_overflow=10
            )

        self.metadata = MetaData()

    @staticmethod
    def _detect_dialect(connection_string: str) -> str:
        """Detect database dialect from connection string."""
        if connection_string.startswith('postgresql'):
            return 'postgresql'
        elif connection_string.startswith('mysql'):
            return 'mysql'
        elif connection_string.startswith('sqlite'):
            return 'sqlite'
        else:
            raise ValueError(f"Unsupported dialect in: {connection_string}")

    @contextmanager
    def connection(self):
        """
        Context manager for database connections.

        Example:
            >>> with db.connection() as conn:
            ...     result = conn.execute(text("SELECT 1"))
        """
        conn = self.engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_with_timing(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """
        Execute query and return results with timing information.

        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized queries

        Returns:
            QueryResult with rows, timing, and metadata

        Example:
            >>> result = db.execute_with_timing(
            ...     "SELECT * FROM users WHERE age > :min_age",
            ...     {"min_age": 18}
            ... )
            >>> print(f"Found {result.row_count} users in {result.execution_time:.2f}s")
        """
        start_time = time.time()

        with self.connection() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))

            rows = []
            column_names = list(result.keys()) if result.keys() else []

            for row in result:
                rows.append(dict(row._mapping))

        execution_time = time.time() - start_time

        return QueryResult(
            rows=rows,
            execution_time=execution_time,
            row_count=len(rows),
            column_names=column_names
        )

    def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """
        List all tables in the database.

        Args:
            schema: Optional schema name (PostgreSQL/MySQL)

        Returns:
            List of table names

        Example:
            >>> tables = db.list_tables()
            >>> print(f"Database has {len(tables)} tables")
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names(schema=schema)

    def get_table_schema(
        self,
        table_name: str,
        schema: Optional[str] = None
    ) -> TableInfo:
        """
        Get comprehensive information about a table.

        Args:
            table_name: Name of the table
            schema: Optional schema name

        Returns:
            TableInfo object with columns, indexes, and metadata

        Example:
            >>> info = db.get_table_schema('users')
            >>> for col in info.columns:
            ...     print(f"{col['name']}: {col['type']}")
        """
        inspector = inspect(self.engine)

        # Get columns
        columns = []
        for col in inspector.get_columns(table_name, schema=schema):
            columns.append({
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'default': col.get('default'),
                'primary_key': col.get('primary_key', False)
            })

        # Get indexes
        indexes = []
        for idx in inspector.get_indexes(table_name, schema=schema):
            indexes.append({
                'name': idx['name'],
                'columns': idx['column_names'],
                'unique': idx['unique']
            })

        # Get row count
        try:
            result = self.execute_with_timing(
                f"SELECT COUNT(*) as count FROM {table_name}"
            )
            row_count = result.rows[0]['count']
        except Exception:
            row_count = None

        return TableInfo(
            name=table_name,
            schema=schema or 'public',
            columns=columns,
            indexes=indexes,
            row_count=row_count
        )

    def analyze_indexes(
        self,
        table_name: str,
        schema: Optional[str] = None
    ) -> List[IndexRecommendation]:
        """
        Analyze table and recommend indexes based on common patterns.

        Args:
            table_name: Table to analyze
            schema: Optional schema name

        Returns:
            List of index recommendations

        Example:
            >>> recs = db.analyze_indexes('orders')
            >>> for rec in recs:
            ...     print(rec.reason)
            ...     print(rec.create_statement)
        """
        recommendations = []
        table_info = self.get_table_schema(table_name, schema)
        existing_indexes = {
            tuple(idx['columns']) for idx in table_info.indexes
        }

        # Recommend indexes for foreign key columns
        for col in table_info.columns:
            col_name = col['name']

            # Foreign key pattern (ends with _id)
            if col_name.endswith('_id') and (col_name,) not in existing_indexes:
                recommendations.append(IndexRecommendation(
                    table=table_name,
                    columns=[col_name],
                    reason=f"Foreign key column '{col_name}' should have an index",
                    estimated_benefit="High - improves JOIN performance",
                    create_statement=f"CREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name});"
                ))

            # Timestamp columns (often used for filtering)
            if 'timestamp' in col_name.lower() or 'date' in col_name.lower():
                if (col_name,) not in existing_indexes:
                    recommendations.append(IndexRecommendation(
                        table=table_name,
                        columns=[col_name],
                        reason=f"Timestamp column '{col_name}' frequently used in WHERE/ORDER BY",
                        estimated_benefit="Medium - improves time-range queries",
                        create_statement=f"CREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name});"
                    ))

        return recommendations

    def explain_query(self, query: str) -> Dict[str, Any]:
        """
        Get query execution plan.

        Args:
            query: SQL query to analyze

        Returns:
            Dictionary with execution plan details

        Example:
            >>> plan = db.explain_query("SELECT * FROM users WHERE age > 18")
            >>> print(json.dumps(plan, indent=2))
        """
        explain_query = f"EXPLAIN {query}"

        if self.dialect == 'postgresql':
            explain_query = f"EXPLAIN (FORMAT JSON) {query}"
            result = self.execute_with_timing(explain_query)
            return result.rows[0] if result.rows else {}
        else:
            result = self.execute_with_timing(explain_query)
            return {'plan': result.rows}

    def bulk_insert(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> int:
        """
        Bulk insert records efficiently.

        Args:
            table_name: Target table
            records: List of record dictionaries
            batch_size: Number of records per batch

        Returns:
            Number of records inserted

        Example:
            >>> records = [
            ...     {'name': 'Alice', 'age': 30},
            ...     {'name': 'Bob', 'age': 25}
            ... ]
            >>> count = db.bulk_insert('users', records)
            >>> print(f"Inserted {count} records")
        """
        if not records:
            return 0

        total_inserted = 0

        with self.connection() as conn:
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]

                # Build bulk insert query
                columns = list(batch[0].keys())
                placeholders = ', '.join([
                    f":{col}" for col in columns
                ])

                query = f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({placeholders})
                """

                conn.execute(text(query), batch)
                total_inserted += len(batch)

        return total_inserted

    def create_table_from_dict(
        self,
        table_name: str,
        sample_data: Dict[str, Any],
        primary_key: str = 'id'
    ) -> str:
        """
        Generate CREATE TABLE statement from sample data.

        Args:
            table_name: Name for the new table
            sample_data: Dictionary representing a sample row
            primary_key: Column name for primary key

        Returns:
            CREATE TABLE SQL statement

        Example:
            >>> sample = {'name': 'Alice', 'age': 30, 'active': True}
            >>> sql = db.create_table_from_dict('users', sample)
            >>> print(sql)
        """
        type_mapping = {
            str: 'VARCHAR(255)',
            int: 'INTEGER',
            float: 'FLOAT',
            bool: 'BOOLEAN',
            datetime: 'TIMESTAMP'
        }

        columns = []

        # Add primary key if not in sample data
        if primary_key not in sample_data:
            if self.dialect == 'postgresql':
                columns.append(f"{primary_key} SERIAL PRIMARY KEY")
            elif self.dialect == 'mysql':
                columns.append(f"{primary_key} INT AUTO_INCREMENT PRIMARY KEY")
            else:  # sqlite
                columns.append(f"{primary_key} INTEGER PRIMARY KEY AUTOINCREMENT")

        # Add data columns
        for key, value in sample_data.items():
            col_type = type_mapping.get(type(value), 'TEXT')
            nullable = "NULL" if value is None else "NOT NULL"

            if key == primary_key:
                columns.append(f"{key} {col_type} PRIMARY KEY")
            else:
                columns.append(f"{key} {col_type} {nullable}")

        columns_str = ',\n    '.join(columns)
        create_statement = f"""
CREATE TABLE {table_name} (
    {columns_str}
);
        """.strip()

        return create_statement


class QueryBuilder:
    """
    Fluent query builder with parameterization support.

    Example:
        >>> qb = QueryBuilder('users')
        >>> query, params = qb.select(['name', 'email']) \
        ...                     .where('age > :min_age') \
        ...                     .order_by('created_at DESC') \
        ...                     .limit(10) \
        ...                     .build(min_age=18)
        >>> print(query)
    """

    def __init__(self, table: str):
        """Initialize query builder for a table."""
        self.table = table
        self._select_columns: List[str] = ['*']
        self._where_clauses: List[str] = []
        self._joins: List[str] = []
        self._order_by: Optional[str] = None
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._group_by: Optional[str] = None

    def select(self, columns: List[str]) -> 'QueryBuilder':
        """Specify columns to select."""
        self._select_columns = columns
        return self

    def where(self, condition: str) -> 'QueryBuilder':
        """Add WHERE condition."""
        self._where_clauses.append(condition)
        return self

    def join(
        self,
        table: str,
        on: str,
        join_type: str = 'INNER'
    ) -> 'QueryBuilder':
        """Add JOIN clause."""
        self._joins.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def order_by(self, order: str) -> 'QueryBuilder':
        """Add ORDER BY clause."""
        self._order_by = order
        return self

    def group_by(self, columns: str) -> 'QueryBuilder':
        """Add GROUP BY clause."""
        self._group_by = columns
        return self

    def limit(self, limit: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self._offset = offset
        return self

    def build(self, **params) -> Tuple[str, Dict[str, Any]]:
        """
        Build the final query.

        Args:
            **params: Parameters for parameterized queries

        Returns:
            Tuple of (query_string, parameters_dict)
        """
        query_parts = [
            f"SELECT {', '.join(self._select_columns)}",
            f"FROM {self.table}"
        ]

        if self._joins:
            query_parts.extend(self._joins)

        if self._where_clauses:
            query_parts.append(f"WHERE {' AND '.join(self._where_clauses)}")

        if self._group_by:
            query_parts.append(f"GROUP BY {self._group_by}")

        if self._order_by:
            query_parts.append(f"ORDER BY {self._order_by}")

        if self._limit:
            query_parts.append(f"LIMIT {self._limit}")

        if self._offset:
            query_parts.append(f"OFFSET {self._offset}")

        query = '\n'.join(query_parts)
        return query, params


class SampleDataGenerator:
    """
    Generate sample data for testing.

    Example:
        >>> gen = SampleDataGenerator()
        >>> users = gen.generate_users(100)
        >>> orders = gen.generate_orders(500, user_ids=[u['id'] for u in users])
    """

    @staticmethod
    def generate_users(count: int) -> List[Dict[str, Any]]:
        """
        Generate sample user records.

        Args:
            count: Number of users to generate

        Returns:
            List of user dictionaries
        """
        import random
        from datetime import timedelta

        first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']

        users = []
        base_date = datetime.now()

        for i in range(count):
            users.append({
                'id': i + 1,
                'username': f"user{i + 1}",
                'email': f"user{i + 1}@example.com",
                'first_name': random.choice(first_names),
                'last_name': random.choice(last_names),
                'age': random.randint(18, 80),
                'active': random.choice([True, False]),
                'created_at': base_date - timedelta(days=random.randint(0, 365))
            })

        return users

    @staticmethod
    def generate_orders(
        count: int,
        user_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Generate sample order records.

        Args:
            count: Number of orders to generate
            user_ids: List of valid user IDs

        Returns:
            List of order dictionaries
        """
        import random
        from datetime import timedelta

        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        orders = []
        base_date = datetime.now()

        for i in range(count):
            orders.append({
                'id': i + 1,
                'user_id': random.choice(user_ids),
                'total_amount': round(random.uniform(10.0, 500.0), 2),
                'status': random.choice(statuses),
                'created_at': base_date - timedelta(days=random.randint(0, 90))
            })

        return orders


# Convenience functions
def connect(connection_string: str, **kwargs) -> DatabaseHelper:
    """
    Create a database helper instance.

    Args:
        connection_string: Database connection string
        **kwargs: Additional arguments for DatabaseHelper

    Returns:
        DatabaseHelper instance

    Example:
        >>> db = connect('postgresql://user:pass@localhost/mydb')
        >>> tables = db.list_tables()
    """
    return DatabaseHelper(connection_string, **kwargs)


if __name__ == '__main__':
    # Example usage
    print("SQL Helper Module - Example Usage")
    print("=" * 50)

    # SQLite example (no external dependencies)
    db = DatabaseHelper('sqlite:///example.db')

    print("\n1. Creating sample table...")
    sample_data = {
        'name': 'Alice',
        'age': 30,
        'email': 'alice@example.com'
    }
    create_sql = db.create_table_from_dict('users', sample_data)
    print(create_sql)

    print("\n2. Generating sample data...")
    gen = SampleDataGenerator()
    users = gen.generate_users(5)
    for user in users:
        print(f"  {user['username']}: {user['email']}")

    print("\n3. Building a query...")
    qb = QueryBuilder('users')
    query, params = qb.select(['name', 'email']) \
                       .where('age > :min_age') \
                       .order_by('name') \
                       .limit(10) \
                       .build(min_age=18)
    print(query)
    print(f"Parameters: {params}")
