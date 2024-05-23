from sqladaptor.sqlite import SqliteAdaptor
import pandas
from rich.pretty import pprint

entries = [
    {"description": "this", "value": 1},
    {"description": "that", "value": 2}
]

db =  SqliteAdaptor('db.sqlite')
db.set_from_df('data1', pandas.DataFrame(entries))

entries = db.get_list_of_dict('data1')
pprint(entries)


entries = db.get_list_of_dict('data1', {"description": "this"})
pprint(entries)
# [{'description': 'this', 'value': 1}]

df = db.get_df("data1", {"value": 2})
pprint(df)
#   description  value
# 0        this      1

db.update("data1", {"value": 2}, {"description": "altered"})
df = db.get_df("data1", {"value": 2})
print(df)