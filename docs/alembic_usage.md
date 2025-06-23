# Using Alembic for Database Migrations in Librium

This document provides instructions for using Alembic to manage database schema changes in the Librium project.

## Prerequisites

Ensure you have Alembic installed:

```bash
pipenv install alembic
```

## Basic Commands

### Applying Migrations

To apply all pending migrations:

```bash
alembic upgrade head
```

To apply migrations up to a specific revision:

```bash
alembic upgrade <revision_id>
```

### Creating New Migrations

#### Automatic Migration Generation

Alembic can automatically generate migrations based on changes to your SQLAlchemy models:

1. Make changes to your model definitions in `librium/database/sqlalchemy/db.py`
2. Run the following command to generate a migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

3. Review the generated migration script in `alembic/versions/` to ensure it correctly captures your changes

#### Manual Migration Creation

For more complex changes, you can create a migration manually:

```bash
alembic revision -m "Description of changes"
```

This will create a new migration script in `alembic/versions/` that you can edit to implement your changes.

### Reverting Migrations

To revert the most recent migration:

```bash
alembic downgrade -1
```

To revert to a specific revision:

```bash
alembic downgrade <revision_id>
```

To revert all migrations:

```bash
alembic downgrade base
```

### Checking Migration Status

To see the current migration status:

```bash
alembic current
```

To see the history of migrations:

```bash
alembic history
```

## Best Practices

1. **Always review auto-generated migrations**: Alembic's auto-generation is not perfect and may miss some changes or generate incorrect SQL. Always review the generated migration scripts before applying them.

2. **Test migrations before applying to production**: Always test migrations in a development environment before applying them to production.

3. **Include both upgrade and downgrade paths**: Ensure that each migration includes both upgrade and downgrade functions to allow for rollbacks if needed.

4. **Use meaningful migration names**: Use descriptive names for your migrations to make it easier to understand what each migration does.

5. **Keep migrations small and focused**: Each migration should make a small, focused change to the database schema. This makes it easier to understand, test, and revert if necessary.

6. **Commit migrations to version control**: Always commit migration scripts to version control along with the model changes that they implement.

7. **Don't modify existing migrations**: Once a migration has been applied and committed, don't modify it. Instead, create a new migration to make additional changes.

## Troubleshooting

### Migration Conflicts

If you encounter conflicts between migrations, you may need to manually resolve them by editing the migration scripts or creating a new migration that fixes the issues.

### Database Out of Sync

If your database schema gets out of sync with your migrations, you can use the following steps to reset it:

1. Back up your data if needed
2. Drop all tables in the database
3. Run `alembic upgrade head` to recreate the schema from scratch

## Integration with SQLAlchemy

The Alembic configuration in this project is set up to work directly with SQLAlchemy. The `env.py` file includes code to use SQLAlchemy metadata, which Alembic uses to detect schema changes.

When you make changes to your SQLAlchemy models, Alembic will detect those changes and generate appropriate migration scripts.