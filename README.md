# sqladaptor

Transferring data, stored as JSON or Pandas, into an SQL database and back again.

## Why?

If you often build prototypes, then to start with,
you will probably save your data in JSON files or Pandas parquet files.
At some point, you will want to transition to a database where 
updating/inserting data to disk would more efficient.

SqlAdaptor allows an easy transition to get started on such a database.
This includes convenience functions to search the data using dicts, and 
methods to return database rows in dicts for web-servers.

## Installation

```bash
pip install sqladaptor
```

## Basic Usage

```python
from sqladaptor.sqlite import SqliteAdaptor
import pandas

entries = [
    {"description": "this", "value": 1},
    {"description": "that", "value": 2}
]

db =  SqliteAdaptor('db.sqlite')
db.set_from_df('data1', pandas.DataFrame(entries))

entries = db.get_list_of_dict('data1')
# [{'description': 'this', 'value': 1}, {'description': 'that', 'value': 2}]

entries = db.get_list_of_dict('data1', {"description": "this"})
# [{'description': 'this', 'value': 1}]

df = db.get_df("data1", {"value": 2})
#   description  value
# 0        that      2

db.update("data1", {"value": 2}, {"description": "altered"})
df = db.get_df("data1", {"value": 2})
#   description  value
# 0     altered      2
```