# Database Indexing in Librium

This document explains the database indexing strategy implemented in Librium to improve query performance.

## Overview

Indexes are database structures that improve the speed of data retrieval operations at the cost of additional writes and storage space. In Librium, we've added indexes to frequently queried fields to optimise the most common database operations.

## Implemented Indexes

### Book Table

| Index Name          | Fields     | Purpose                                                        |
|---------------------|------------|----------------------------------------------------------------|
| idx_book_title      | title      | Improves performance of title searches and sorting by title    |
| idx_book_isbn       | isbn       | Speeds up book lookups by ISBN                                 |
| idx_book_read       | read       | Optimizes filtering books by read status                       |
| idx_book_released   | released   | Improves performance when filtering or sorting by release year |
| idx_book_created_at | created_at | Speeds up queries that sort by creation date                   |

### Author Table

| Index Name            | Fields     | Purpose                                     |
|-----------------------|------------|---------------------------------------------|
| idx_author_first_name | first_name | Improves author searches by first name      |
| idx_author_last_name  | last_name  | Improves author searches by last name       |
| idx_author_name       | name       | Speeds up searches for authors by full name |

### Publisher Table

| Index Name         | Fields | Purpose                            |
|--------------------|--------|------------------------------------|
| idx_publisher_name | name   | Improves publisher lookups by name |

### Format Table

| Index Name      | Fields | Purpose                          |
|-----------------|--------|----------------------------------|
| idx_format_name | name   | Speeds up format lookups by name |

### Language Table

| Index Name        | Fields | Purpose                           |
|-------------------|--------|-----------------------------------|
| idx_language_name | name   | Improves language lookups by name |

### Genre Table

| Index Name     | Fields | Purpose                         |
|----------------|--------|---------------------------------|
| idx_genre_name | name   | Speeds up genre lookups by name |

### Series Table

| Index Name      | Fields | Purpose                                             |
|-----------------|--------|-----------------------------------------------------|
| idx_series_name | name   | Improves series lookups by name (unique constraint) |

## Performance Impact

These indexes significantly improve the performance of the following common operations:

1. **Book searches**: Searching for books by title, ISBN, or release year is now faster
2. **Filtering**: Filtering books by read status or other attributes is more efficient
3. **Author lookups**: Finding authors by name is optimised
4. **Metadata filtering**: Filtering by publisher, format, language, genre, or series is improved
5. **Sorting**: Sorting books by title, release year, or creation date is faster

## Trade-offs

While indexes improve read performance, they come with some trade-offs:

1. **Write performance**: Each index needs to be updated when the indexed data changes, which can slow down write operations
2. **Storage space**: Indexes require additional storage space
3. **Maintenance**: Indexes need to be maintained and potentially rebuilt over time

For Librium, these trade-offs are acceptable because:

1. Read operations are much more frequent than write operations
2. The additional storage space is minimal compared to the performance benefits
3. SQLite handles index maintenance automatically in most cases

## Future Considerations

As the application evolves, we should:

1. **Monitor query performance**: Use database profiling to identify slow queries that might benefit from additional indexes
2. **Review index usage**: Periodically check which indexes are being used and consider removing unused ones
3. **Consider composite indexes**: For queries that filter on multiple columns simultaneously, composite indexes might provide better performance

## Implementation

These indexes were added using Alembic migrations. To apply these indexes to your database, run:

```bash
alembic upgrade head
```

If you need to revert these changes, you can run:

```bash
alembic downgrade initial
```