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

entries = db.read_dicts("data1")
pprint(entries)

df = db.read_df("data1")
pprint(df)

schema = db.read_table_schema("data1")
pprint(schema)
validator = fastjsonschema.compile(schema)
for entry in entries:
    print("validate: ", end="")
    pprint(validator(entry))

db.insert("data1", {"value": 3, "description": "inserted"})
entries = db.read_dicts("data1")
pprint(entries)
# [{'description': 'altered', 'value': 2}]

db.update(
    "data1",
    {"description": "inserted"},
    {"description": "inserted & updated", "value": 77},
)
entries = db.read_dicts("data1")
pprint(entries)
# [{'description': 'altered', 'value': 2}]

db.delete("data1", {"value": 77})
entries = db.read_dicts("data1")
pprint(entries)
# [{'description': 'altered', 'value': 2}]


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
entries = db.read_dicts("data1", {"description": "this"})
pprint(entries)

df = db.read_df("data1", {"value": 2})
pprint(df)

db.update("data1", {"value": 2}, {"description": "altered"})
entries = db.read_dicts("data1", {"value": 2})
pprint(entries)

rows = db.read_rows("data1")
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
