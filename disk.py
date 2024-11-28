import subprocess
import datetime

def get_data():

	command = 'df'
	command_output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	lines = command_output.stdout.decode().split('\n')
	data = []

	keys = [
		'filesystem',
		'size',
		'used',
		'avail',
		'percent',
		'mounted_on'
	]

	now = datetime.datetime.now()

	for line in lines:

		if line and not line.startswith('Filesystem'):

			values = line.split()
			row = dict(zip(keys, values))

			if row['mounted_on'].startswith('/snap'):
				continue

			row['percent'] = float(row['percent'].replace('%', '')) / 100
			row['created_at'] = now
			
			data.append(row)

	return data
