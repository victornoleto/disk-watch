from flask import Flask, render_template, request
from dotenv import load_dotenv
import database
import datetime
import json
import os

load_dotenv()

# Flask constructor 
app = Flask(__name__)

def get_chart_config(disks, start_date, end_date):

	colors = [
		'blue', 'red', 'green', 'purple', 'orange', 'yellow', 'pink', 'brown', 'cyan', 'magenta',
		'black', 'gray', 'darkblue', 'darkred', 'darkgreen', 'darkpurple', 'darkorange', 'darkyellow',
		'darkpink', 'darkbrown', 'darkcyan', 'darkmagenta', 'darkblack', 'darkgray',
	]

	query = "SELECT * FROM history WHERE id > 0"

	query += ' AND mounted_on in ("' + '","'.join(disks) + '")'

	if start_date and end_date:
		query += f' and created_at BETWEEN "{start_date}" AND "{end_date}"'
	elif start_date:
		query += f' and created_at >= "{start_date}"'
	elif end_date:
		query += f' and created_at <= "{end_date}"'

	query += ' ORDER BY filesystem, created_at'

	rows = database.exec_select(query)

	datasets = {}
	i = 0

	for row in rows:

		alias = row['mounted_on']

		if alias not in datasets:
			datasets[alias] = {
				'label': alias,
				'borderColor': colors[i],
				'data': []
			}
			i += 1

		datasets[alias]['data'].append({
			'x': row['created_at'],
			'y': row['percent']
		})

	chart_config = {
		'type': 'line',
		'data': {
			'datasets': list(datasets.values())
		},
		'options': {
			'scales': {
				'x': {
					'type': 'time',
					'time': {
						'unit': 'minute',
						'stepSize': 15,
						'round': False,
						'displayFormats': {
							'minute': 'dd/MM HH:mm'
						}
					},
					'title': {
						'display': True,
						'text': 'Date'
					}
				},
				'y': {
					'title': {
						'display': True,
						'text': 'Use %'
					}
				}
			}
		}
	}

	return chart_config

def get_disks():
	query = "SELECT DISTINCT mounted_on FROM history WHERE created_at >= datetime('now', '-7 days')"
	rows = database.exec_select(query)
	return [row['mounted_on'] for row in rows]

# Root endpoint 
@app.route('/')
def homepage():

	disks = get_disks()

	selected_disks = request.args.getlist('disks[]')
	chart_config = None

	start_date = request.args.get('start_date')
	end_date = request.args.get('end_date')

	if not start_date and not end_date:
		# sub 7 days
		start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

	if len(selected_disks) == 0:
		selected_disks = disks
		
	chart_config = get_chart_config(selected_disks, start_date, end_date)

	# Return the components to the HTML template 
	return render_template(
		template_name_or_list='index.html',
		disks=disks,
		start_date=start_date,
		end_date=end_date,
		selected_disks=selected_disks,
		chart_config=chart_config
	)

if __name__ == '__main__':
	host = os.getenv('APP_HOST', '0.0.0.0')
	port = os.getenv('APP_PORT', 5000)
	debug = os.getenv('APP_DEBUG', True)
	app.run(debug=True, host=host, port=port)
