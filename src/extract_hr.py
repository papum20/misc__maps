from datetime import datetime
import csv
import gpxpy
import gpxpy.gpx



# How to extract hr:
# https://stackoverflow.com/a/70405658/20607105
# From the source:
# .extensions[0] renders a child list that you can either iterate over or query using .find().
# ...it uses the schema http://www.garmin.com/xmlschemas/TrackPointExtension/v1
# For garmin hr:
# .extensions[0].tag = {http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr
# .extensions[0].text = hr value

def extract_hr_points(gpx):

	for track in gpx.tracks:
		for segment in track.segments:
			for point in segment.points:
				hr = point.extensions[0][0].text
				yield point.time, point.latitude, point.longitude, point.elevation, hr


def export_hr_to_txt(gpx, filename, do_print=False):

	with open(filename, 'w', newline='') as outfile:
		for time, latitude, longitude, elevation, hr in extract_hr_points(gpx):

			# convert time from 'YYYY-MM-DD HH:MM:SS+00:00' to 'HH:MM:SS'
			new_time = datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S+00:00')
			new_time = time.strftime('%H:%M:%S')

			line = f'{new_time},{latitude},{longitude},{elevation},{hr}'
			if do_print:
				print(f'{line}')
			outfile.write(f'{line}\n')


def export_hr_to_csv(gpx, filename, csv_separator=','):

	with open(filename, 'w', newline='') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=csv_separator, quotechar='|', quoting=csv.QUOTE_MINIMAL)

		# print header
		csvwriter.writerow(['Time', 'Latitude', 'Longitude', 'Elevation', 'HR'])

		for time, latitude, longitude, elevation, hr in extract_hr_points(gpx):

			# convert time from 'YYYY-MM-DD HH:MM:SS+00:00' to 'HH:MM:SS'
			new_time = datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S+00:00')
			new_time = time.strftime('%H:%M:%S')

			csvwriter.writerow([new_time, latitude, longitude, elevation, hr])



if __name__ == '__main__':

	file_basename = 'mtb-ride'

	gpx_file = open(f'samples/gpx/{file_basename}.gpx', 'r')
	gpx = gpxpy.parse(gpx_file)

	export_hr_to_txt(gpx, f'out/{file_basename}_hr.txt')
	export_hr_to_csv(gpx, f'out/{file_basename}_hr.csv')
