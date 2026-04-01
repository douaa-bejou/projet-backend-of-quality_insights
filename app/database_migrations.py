from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def _add_column_if_missing(engine: Engine, table_name: str, column_name: str, column_sql: str) -> bool:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in columns:
        return False

    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}"))
    return True


def apply_runtime_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    if "quality_records" not in inspector.get_table_names():
        return

    added_columns: list[str] = []
    columns_to_add = [
        ("qte_nok_defaut", "qte_nok_defaut INTEGER NOT NULL DEFAULT 0"),
        ("qte_nok_moulage", "qte_nok_moulage INTEGER NOT NULL DEFAULT 0"),
        ("qte_nok_zone", "qte_nok_zone INTEGER NOT NULL DEFAULT 0"),
    ]

    for column_name, column_sql in columns_to_add:
        added = _add_column_if_missing(engine, "quality_records", column_name, column_sql)
        if added:
            added_columns.append(column_name)

    # Backfill only when the column has just been created, to preserve current values on next runs.
    if not added_columns:
        return

    with engine.begin() as connection:
        for column_name in added_columns:
            connection.execute(
                text(
                    f"""
                    UPDATE quality_records
                    SET {column_name} = qte_nok
                    WHERE qte_nok > 0
                    """
                )
            )
