# sqladaptor

Transferring data, stored as JSON or Pandas, into an SQL database and back again.

## Why?

Building webserver prototypes, one often saves initial data as JSON or Pandas files.
Later, you will want to transition to an SQL database where
updating/inserting data to disk is more efficient. 

SqlAdaptor allows an easy transition for this transition, using a
familiar API consisting of dict lists and pandas dataframes. Table schema 
are treated as Json-Schema.

This is possible
because there is an equivalence between JSON dict lists, Pandas DataFrames
and SQL tables - they are all tabular arrangements of columnar data.

## Installation

```bash
pip install sqladaptor
```

## Basic Usage

Inserting dict lists into an SQLite db

```python
from sqladaptor.sqlite import SqliteAdaptor
import pandas

db = SqliteAdaptor('db.sqlite')
entries = [
    {"description": "this", "value": 1},
    {"description": "that", "value": 2}
]
db.set_from_df('data1', pandas.DataFrame(entries))
```

Read as dict lists or dataframes:
```python
entries = db.read_dicts('data1')
# [
#   {'description': 'this', 'value': 1}, 
#   {'description': 'that', 'value': 2}
# ]
df = db.read_df("data1", {"value": 2})
#   description  value
# 0        this      1
# 1        that      2
```

Get the table schema as Json-schema:
```python
schema = db.read_table_schema("data1")
# {
# │   'type': 'object',
# │   'properties': {
# │   │   'description': {'type': 'string'},
# │   │   'value': {'type': 'integer'}
# │   },
# │   'additionalProperties': False
# }
```

Make an SQL table with Json-schema:
```python
db.create_table(
    "data1",
    {
        "type": "object",
        "properties": {
            "row_id": {"type": "string"},
            "description": {"type": "string"},
            "value": {"type": "integer"},
        },
        "required": ["row_id"],
    },
)
```

Find using dict search:
```python
return_entries = db.read_dicts('data1', {"description": "this"})
# [{'description': 'this', 'value': 1}]
```

CRUD your database:
```python
db.insert("data1", {"value": 3, "description": "inserted"})
entries = db.read_dicts('data1')
# [
# │   {'description': 'this', 'value': 1},
# │   {'description': 'that', 'value': 2},
# │   {'description': 'inserted', 'value': 3}
# ]

db.update(
    "data1",
    {"description": "inserted"},
    {"description": "inserted-then-updated", "value": 77},
)
entries = db.read_dicts('data1')
# [
# │   {'description': 'this', 'value': 1},
# │   {'description': 'that', 'value': 2},
# │   {'description': 'inserted-then-updated', 'value': 77}
# ]

db.delete("data1", {"value": 77})
entries = db.read_dicts('data1')
# [{'description': 'this', 'value': 1}, {'description': 'that', 'value': 2}]
```

