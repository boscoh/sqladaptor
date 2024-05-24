import fastjsonschema
import pandas
from path import Path
from rich.pretty import pprint

from sqladaptor.sqlite import SqliteAdaptor, var_name_regex

Path("db.sqlite").remove_p()
db = SqliteAdaptor("db.sqlite")

entries = [
    {"description": "this", "value": 1},
    {"description": "that", "value": 2},
]
db.set_from_df("data1", pandas.DataFrame(entries))

entries = db.get_dicts("data1")
pprint(entries)

schema = db.get_table_schema("test_table")
validator = fastjsonschema.compile(schema)
for entry in entries:
    print("validate: ", end="")
    pprint(validator(entry))

entries = db.get_dicts("data1", {"description": "this"})
pprint(entries)

df = db.get_df("data1", {"value": 2})
pprint(df)

db.update("data1", {"value": 2}, {"description": "altered"})
entries = db.get_dicts("data1", {"value": 2})
pprint(entries)

rows = db.get_rows("data1")
pprint(rows)

schema = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "value": {"type": "integer"},
    },
    "required": ["description"],
}

db.create_table("data2", schema)


print(var_name_regex.match("__ha__"))
print(var_name_regex.match("1__ha__"))