import re

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


def _is_mysql(engine: Engine) -> bool:
    return engine.dialect.name == "mysql"


def _is_bigint(column_type: object) -> bool:
    return "BIGINT" in str(column_type).upper()


def _modify_column_if_needed(
    engine: Engine,
    table_name: str,
    column_name: str,
    column_sql: str,
) -> bool:
    inspector = inspect(engine)
    columns = {column["name"]: column for column in inspector.get_columns(table_name)}
    existing = columns.get(column_name)
    if existing is None:
        return False

    if _is_bigint(existing["type"]):
        return False

    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE `{table_name}` MODIFY COLUMN {column_sql}"))
    return True


def _add_index_if_missing(engine: Engine, table_name: str, index_name: str, columns_sql: str) -> bool:
    inspector = inspect(engine)
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name in existing_indexes:
        return False

    with engine.begin() as connection:
        connection.execute(text(f"CREATE INDEX `{index_name}` ON `{table_name}` ({columns_sql})"))
    return True


def _apply_mysql_capacity_migrations(engine: Engine) -> None:
    if not _is_mysql(engine):
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    bigint_columns = [
        ("quality_records", "id", "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT"),
        ("users", "id", "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT"),
        ("action_plans", "id", "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT"),
        ("non_conformities", "id", "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT"),
        ("quality_records", "qte_ok", "qte_ok BIGINT UNSIGNED NOT NULL DEFAULT 0"),
        ("quality_records", "qte_nok", "qte_nok BIGINT UNSIGNED NOT NULL DEFAULT 0"),
        ("quality_records", "qte_nok_defaut", "qte_nok_defaut BIGINT UNSIGNED NOT NULL DEFAULT 0"),
        ("quality_records", "qte_nok_moulage", "qte_nok_moulage BIGINT UNSIGNED NOT NULL DEFAULT 0"),
        ("quality_records", "qte_nok_zone", "qte_nok_zone BIGINT UNSIGNED NOT NULL DEFAULT 0"),
        ("quality_records", "qte_scrap", "qte_scrap BIGINT UNSIGNED NOT NULL DEFAULT 0"),
        ("quality_records", "qte_rework", "qte_rework BIGINT UNSIGNED NOT NULL DEFAULT 0"),
        ("non_conformities", "numero", "numero BIGINT UNSIGNED NOT NULL"),
        ("non_conformities", "qte_nok", "qte_nok BIGINT UNSIGNED NOT NULL"),
        ("action_plans", "numero", "numero BIGINT UNSIGNED NOT NULL"),
        ("action_plans", "cv", "cv BIGINT UNSIGNED NOT NULL DEFAULT 0"),
    ]

    for table_name, column_name, column_sql in bigint_columns:
        if table_name not in table_names:
            continue
        _modify_column_if_needed(engine, table_name, column_name, column_sql)

    index_specs = [
        ("quality_records", "ix_quality_records_date", "`date`"),
        ("quality_records", "ix_quality_records_semaine", "`semaine`"),
        ("quality_records", "ix_quality_records_mois", "`mois`"),
        ("quality_records", "ix_quality_records_projet", "`projet`"),
        ("quality_records", "ix_quality_records_shift", "`shift`"),
        ("quality_records", "ix_quality_records_poste", "`poste`"),
        ("quality_records", "ix_quality_records_parts_origin", "`parts_origin`"),
        ("quality_records", "ix_quality_records_zone", "`zone`"),
        ("quality_records", "ix_quality_records_created_at", "`created_at`"),
        ("quality_records", "ix_quality_records_date_project_shift", "`date`, `projet`, `shift`"),
        ("quality_records", "ix_quality_records_created_at_id", "`created_at`, `id`"),
    ]

    for table_name, index_name, columns_sql in index_specs:
        if table_name not in table_names:
            continue
        _add_index_if_missing(engine, table_name, index_name, columns_sql)


def _is_sqlite(engine: Engine) -> bool:
    return engine.dialect.name == "sqlite"


def _sqlite_rebuild_bigint_primary_key_table(engine: Engine, table_name: str) -> bool:
    # SQLite autoincrement behavior only works with INTEGER primary keys.
    with engine.begin() as connection:
        row = connection.execute(
            text("SELECT sql FROM sqlite_master WHERE type='table' AND name=:name"),
            {"name": table_name},
        ).fetchone()
        if not row or not row[0]:
            return False

        create_sql = str(row[0])
        if not re.search(r"\bid\s+BIGINT\b", create_sql, flags=re.IGNORECASE):
            return False

        index_rows = connection.execute(
            text(
                """
                SELECT sql
                FROM sqlite_master
                WHERE type='index'
                  AND tbl_name=:name
                  AND sql IS NOT NULL
                """
            ),
            {"name": table_name},
        ).fetchall()
        index_sql_statements = [str(index_row[0]) for index_row in index_rows if index_row and index_row[0]]

        temp_table_name = f"{table_name}__pkfix"
        connection.execute(text(f'DROP TABLE IF EXISTS "{temp_table_name}"'))

        temp_create_sql = re.sub(
            rf'CREATE TABLE\s+"?{re.escape(table_name)}"?',
            f'CREATE TABLE "{temp_table_name}"',
            create_sql,
            count=1,
            flags=re.IGNORECASE,
        )
        temp_create_sql = re.sub(
            r"\bid\s+BIGINT\s+NOT\s+NULL\b",
            "id INTEGER NOT NULL",
            temp_create_sql,
            count=1,
            flags=re.IGNORECASE,
        )
        if re.search(r"\bid\s+BIGINT\b", temp_create_sql, flags=re.IGNORECASE):
            temp_create_sql = re.sub(
                r"\bid\s+BIGINT\b",
                "id INTEGER",
                temp_create_sql,
                count=1,
                flags=re.IGNORECASE,
            )

        connection.execute(text(temp_create_sql))

        column_rows = connection.execute(text(f'PRAGMA table_info("{table_name}")')).fetchall()
        column_names = [str(column_row[1]) for column_row in column_rows]
        if column_names:
            columns_sql = ", ".join(f'"{column_name}"' for column_name in column_names)
            connection.execute(
                text(
                    f"""
                    INSERT INTO "{temp_table_name}" ({columns_sql})
                    SELECT {columns_sql}
                    FROM "{table_name}"
                    """
                )
            )

        connection.execute(text(f'DROP TABLE "{table_name}"'))
        connection.execute(text(f'ALTER TABLE "{temp_table_name}" RENAME TO "{table_name}"'))

        for index_sql in index_sql_statements:
            connection.execute(text(index_sql))

    return True


def _apply_sqlite_primary_key_migrations(engine: Engine) -> None:
    if not _is_sqlite(engine):
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    for table_name in ("users", "action_plans", "non_conformities", "quality_records"):
        if table_name in table_names:
            _sqlite_rebuild_bigint_primary_key_table(engine, table_name)


def apply_runtime_migrations(engine: Engine) -> None:
    _apply_sqlite_primary_key_migrations(engine)

    inspector = inspect(engine)
    if "quality_records" not in inspector.get_table_names():
        return

    added_columns: list[str] = []
    columns_to_add = [
        ("qte_nok_defaut", "qte_nok_defaut INTEGER NOT NULL DEFAULT 0"),
        ("qte_nok_moulage", "qte_nok_moulage INTEGER NOT NULL DEFAULT 0"),
        ("qte_nok_zone", "qte_nok_zone INTEGER NOT NULL DEFAULT 0"),
        ("photo_url", "photo_url TEXT NULL"),
    ]

    for column_name, column_sql in columns_to_add:
        added = _add_column_if_missing(engine, "quality_records", column_name, column_sql)
        if added:
            added_columns.append(column_name)

    # Backfill only quantity columns when they are newly created.
    backfill_columns = [column_name for column_name in added_columns if column_name.startswith("qte_nok_")]
    if backfill_columns:
        with engine.begin() as connection:
            for column_name in backfill_columns:
                connection.execute(
                    text(
                        f"""
                        UPDATE quality_records
                        SET {column_name} = qte_nok
                        WHERE qte_nok > 0
                        """
                    )
                )

    _apply_mysql_capacity_migrations(engine)
