from pony.orm import *

db = Database()

db.bind(
    provider='sqlite',
    filename='database.sqlite',
    create_db=True
)

class Food(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    calories = Required(int)
    date = Required(str)

db.generate_mapping(create_tables=True)