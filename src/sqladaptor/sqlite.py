import logging
import sqlite3

import pandas
from pydash import py_

__doc__ = """
Interface to an SQLite3 database for storage, with accessor methods to both ingest
and generate pandas dataframes
"""

logger = logging.getLogger(__name__)


class SqliteAdaptor:
    def __init__(self, db_fname):
        self.db_fname = db_fname
        self.conn = self.make_conn()
        self.cursor = self.conn.cursor()

    def make_conn(self):
        return sqlite3.connect(self.db_fname)

    def execute(self, *args):
        return self.cursor.execute(*args)

    def execute_to_df(self, sql: str, params=None):
        return pandas.read_sql_query(sql, self.conn, params=params)

    def commit(self):
        self.conn.commit()

    def set_from_df(self, table: str, df: pandas.DataFrame, index=False, if_exists="append"):
        """
        :param df: pandas.Dataframe
        :param if_exists: ["fail", "append", "replace"]
        """
        df.to_sql(con=self.conn, name=table, index=index, if_exists=if_exists)
        self.commit()

    def replace_table_with_df(self, table: str, df: pandas.DataFrame, index=False):
        self.set_from_df(table, df, index=index, if_exists="replace")

    def add_column(self, table: str, name: str, col_type: str):
        self.execute(f"ALTER TABLE {table} ADD COLUMN '{name}' '{col_type}';")
        self.commit()

    def get_columns(self, table: str):
        queries = self.execute(f"PRAGMA table_info('{table}');").fetchall()
        return [r[1] for r in queries]

    def close(self):
        self.conn.close()

    def get_tables(self):
        rows = self.execute("SELECT name FROM sqlite_master;").fetchall()
        return [r[0] for r in rows]

    def get_select_sql_and_params(self, table: str, where: dict[str, [None, str, int, float]]):
        sql = f"SELECT * FROM {table} "
        params = []
        if where:
            for i, [k, v] in enumerate(where.items()):
                sql += ("WHERE " if i == 0 else "AND ") + f"{k} = ? "
                params.append(str(v))
        return sql, params

    def get_rows(self, table, where=None) -> [tuple]:
        sql, params = self.get_select_sql_and_params(table, where)
        return list(self.execute(sql, params))

    def get_one_row(self, table, where=None) -> tuple:
        sql, params = self.get_select_sql_and_params(table, where)
        return self.execute(sql, params).fetchone()

    def get_df(self, table, where=None) -> pandas.DataFrame:
        sql, params = self.get_select_sql_and_params(table, where)
        return pandas.read_sql_query(sql, self.conn, params=params)

    def get_dict_list(self, table, where=None) -> [dict]:
        return self.get_df(table, where).to_dict(orient="records")

    def get_csv(self, table) -> str:
        return self.get_df(table).to_csv(index=False)

    def insert(self, table, vals):
        """
        :param vals:
            <k>: <v>
        """
        keys = ",".join(vals.keys())
        questions = ",".join(["?" for _ in range(len(vals))])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({questions});"
        self.execute(sql, list(vals.values()))
        self.commit()
        return self.cursor.lastrowid

    def update(self, table, where, vals):
        """
        :param vals:
            <k>: <v>
        """
        sql = f"UPDATE {table} "
        params = []
        for i, [k, v] in enumerate(vals.items()):
            sql += ("SET " if i == 0 else ", ") + f"{k} = ? "
            params.append(v)
        for i, [k, v] in enumerate(where.items()):
            sql += ("WHERE " if i == 0 else "AND ") + f"{k} = ? "
            params.append(str(v))
        self.execute(sql, params)
        self.commit()

    def delete(self, table, where):
        """
        :param vals:
            <k>: <v>
        """
        sql = f"DELETE FROM {table} "
        params = []
        for i, [k, v] in enumerate(where.items()):
            sql += ("WHERE " if i == 0 else "AND ") + f"{k} = ? "
            params.append(str(v))
        self.execute(sql, params)
        self.commit()

    def drop_table(self, table):
        if table in self.get_tables():
            self.execute(f"DROP TABLE {table}")
            self.commit()

    def rename_table(self, table, new_table):
        if table in self.get_tables():
            new_table = py_.snake_case(new_table)
            self.execute(f"ALTER TABLE {table} RENAME to {new_table};")
            self.commit()
