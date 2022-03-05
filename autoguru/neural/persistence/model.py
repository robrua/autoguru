from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, Union

from pony.orm import Database as PonyDatabase
from pony.orm import db_session, set_sql_debug
from pony.orm.core import Entity as CoreEntity

DB = PonyDatabase()
Entity: CoreEntity = DB.Entity

session = db_session


class Database(Enum):
    SQLITE_MEMORY = auto()
    SQLITE_EMBEDDED = auto()
    POSTGRES = auto()
    MYSQL = auto()
    ORACLE = auto()
    COCKROACH = auto()

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        _INITIALIZERS[self](*args, **kwargs)


def initialize_sqlite_memory(
    thread_safe: bool = True, debug_mode: bool = False
) -> None:
    DB.bind("sqlite", filename=":sharedmemory:" if thread_safe else ":memory:")
    DB.generate_mapping(create_tables=True)
    set_sql_debug(debug_mode)


def initialize_sqlite_embedded(
    db_file: Union[str, Path],
    create_db: bool = True,
    create_tables: bool = True,
    debug_mode: bool = False,
) -> None:
    if isinstance(db_file, Path):
        db_file = str(db_file.resolve())

    DB.bind("sqlite", filename=db_file, create_db=create_db)
    DB.generate_mapping(create_tables=create_tables)
    set_sql_debug(debug_mode)


def initialize_postgres(
    host: str = "localhost",
    port: int = 5432,
    user: str = "autoguru",
    password: str = "autoguru",
    database: str = "autoguru",
    create_tables: bool = True,
    debug_mode: bool = False,
) -> None:
    DB.bind(
        "postgres",
        host=f"{host}:{port}",
        user=user,
        password=password,
        database=database,
    )
    DB.generate_mapping(create_tables=create_tables)
    set_sql_debug(debug_mode)


def initialize_mysql(
    host: str = "localhost",
    port: int = 5432,
    user: str = "autoguru",
    password: str = "autoguru",
    database: str = "autoguru",
    create_tables: bool = True,
    debug_mode: bool = False,
) -> None:
    DB.bind(
        "mysql",
        host=f"{host}:{port}",
        user=user,
        passwd=password,
        db=database,
    )
    DB.generate_mapping(create_tables=create_tables)
    set_sql_debug(debug_mode)


def initialize_oracle(
    dsn: str,
    user: str = "autoguru",
    password: str = "autoguru",
    create_tables: bool = True,
    debug_mode: bool = False,
) -> None:
    DB.bind("oracle", dsn=dsn, user=user, password=password)
    DB.generate_mapping(create_tables=create_tables)
    set_sql_debug(debug_mode)


def initialize_cockroach(
    host: str = "localhost",
    port: int = 5432,
    user: str = "autoguru",
    password: str = "autoguru",
    database: str = "autoguru",
    create_tables: bool = True,
    debug_mode: bool = False,
) -> None:
    DB.bind(
        "cockroach",
        host=f"{host}:{port}",
        user=user,
        password=password,
        database=database,
    )
    DB.generate_mapping(create_tables=create_tables)
    set_sql_debug(debug_mode)


_INITIALIZERS: Dict[Database, Callable[..., None]] = {
    Database.SQLITE_MEMORY: initialize_sqlite_memory,
    Database.SQLITE_EMBEDDED: initialize_sqlite_embedded,
    Database.POSTGRES: initialize_postgres,
    Database.MYSQL: initialize_mysql,
    Database.ORACLE: initialize_oracle,
    Database.COCKROACH: initialize_cockroach,
}
