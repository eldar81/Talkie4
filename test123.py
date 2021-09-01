import re
from datetime import date

from loader import db

matches_table = db.select_all_gen_matches()
print(matches_table)
for user in matches_table:
    print(user[2])
    print(type(user[2]))
