import pandas
from path import Path
from rich.pretty import pprint

from sqladaptor.sqlite import SqliteAdaptor

entries = [
    {"description": "this", "value": 1},
    {"description": "that", "value": 2}
]

Path('db.sqlite').remove_p()
db = SqliteAdaptor('db.sqlite')

db.set_from_df('data1', pandas.DataFrame(entries))

entries = db.get_dict_list('data1')
pprint(entries)

entries = db.get_dict_list('data1', {"description": "this"})
pprint(entries)

df = db.get_df("data1", {"value": 2})
pprint(df)

db.update("data1", {"value": 2}, {"description": "altered"})
entries = db.get_dict_list('data1', {"value": 2})
pprint(entries)

rows = db.get_rows('data1')
pprint(rows)
