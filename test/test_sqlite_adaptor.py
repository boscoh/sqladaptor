from copy import deepcopy

import pandas
import pytest
from path import Path
from pydash import py_

from sqladaptor.sqlite import SqliteAdaptor, var_name_regex

schema = {
    "type": "object",
    "properties": {
        "row_id": {"type": "integer"},
        "description": {"type": "string"},
        "amount": {"type": "number"},
        "category": {"type": "string"},
    },
    "required": ["row_id"],
}


@pytest.fixture(scope="function")
def test_db():
    db_fname = Path(__file__).parent / "test.sqlite3"
    db_fname.remove_p()

    db = SqliteAdaptor(db_fname)
    db.create_table("test_table", schema)
    db.commit()

    yield db

    db.close()
    db_fname.remove_p()


def test_get_schema(test_db):
    this_schema = deepcopy(schema)
    del this_schema["required"]
    return_schmea = test_db.get_table_schema("test_table")
    assert return_schmea == this_schema


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


def test_get_dicts(test_db):
    entries = [
        dict(description="haha", amount=2),
        dict(description="dodo", amount=3),
    ]
    test_db.set_from_df("test_table", pandas.DataFrame(entries))
    return_entries = test_db.get_dicts("test_table")
    for entry in return_entries:
        assert py_.find(return_entries, entry)


def test_get_one_dict(test_db):
    entries = [
        dict(description="haha", amount=2),
        dict(description="dodo", amount=3),
    ]
    test_db.set_from_df("test_table", pandas.DataFrame(entries))
    return_entry = test_db.get_one_dict("test_table")
    is_found = False
    for entry in entries:
        if entry.items() < return_entry.items():
            is_found = True
    assert is_found


def test_var_names():
    assert var_name_regex.fullmatch("__ha__")
    assert not var_name_regex.fullmatch("1__ha__")
    assert not var_name_regex.fullmatch("__ ha__")
    assert not var_name_regex.fullmatch("var#")
    assert not var_name_regex.fullmatch("v;ar")
