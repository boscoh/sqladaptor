import pandas
import pytest
from path import Path
from pydash import py_

from sqladaptor.sqlite import SqliteAdaptor


@pytest.fixture(scope="function")
def test_db():
    db_fname = Path(__file__).parent / "test.sqlite3"
    db_fname.remove_p()

    db = SqliteAdaptor(db_fname)
    db.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            row_id INTEGER PRIMARY KEY, 
            description text, 
            amount FLOAT,
            category text
        );
    """)
    db.commit()

    yield db

    db.close()
    db_fname.remove_p()


def test_insert_row(test_db):
    entry = dict(description="haha", amount=2)
    test_db.insert("test_table", entry)
    saved_entries = test_db.get_df("test_table").to_dict(orient="records")
    assert py_.find(saved_entries, entry)


def test_update_row(test_db):
    test_db.insert("test_table", dict(description="haha", amount=2))

    entries = test_db.get_df("test_table").to_dict(orient="records")
    where = {"row_id": entries[0]["row_id"]}

    vals = {"category": "X"}
    test_db.update("test_table", where, vals)

    entries = test_db.get_df("test_table").to_dict(orient="records")
    assert py_.find(entries, {**vals, **where})


def test_delete_row(test_db):
    test_db.insert("test_table", dict(description="haha", amount=2))
    entries = test_db.get_df("test_table").to_dict(orient="records")
    where = {"row_id": entries[0]["row_id"]}
    test_db.delete("test_table", where)
    entries = test_db.get_df("test_table").to_dict(orient="records")
    assert not py_.find(entries, where)


def test_get_rows(test_db):
    entry = dict(description="haha", amount=2)
    test_db.insert("test_table", entry)
    rows = test_db.get_rows("test_table")
    assert len(rows) == 1
    row = rows[0]
    for val in entry.values():
        assert val in row


def test_get_one_row(test_db):
    entry = dict(description="haha", amount=2)
    test_db.insert("test_table", entry)
    row = test_db.get_one_row("test_table")
    for val in entry.values():
        assert val in row


def test_get_list_of_dict(test_db):
    entries = [
        dict(description="haha", amount=2),
        dict(description="dodo", amount=3),
    ]
    test_db.set_from_df("test_table", pandas.DataFrame(entries))
    return_entries = test_db.get_dict_list("test_table")
    for entry in return_entries:
        assert py_.find(return_entries, entry)
