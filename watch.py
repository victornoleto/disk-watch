import database
import disk

database.init()

data = disk.get_data()

for row in data:
	database.insert('history', row)