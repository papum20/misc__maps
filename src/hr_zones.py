# add src to python path
#import sys
#sys.path.append('src')

from datetime import datetime
import csv
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import numpy as np

import extract_hr


HR_MAX = 178

ZONE_THRESHOLDS = {
	0: 0.0,	# default value, just to cover all of them (in case of errors)
	1: 0.5,
	2: 0.6,
	3: 0.7,
	4: 0.8,
	5: 0.9
}


def extract_hr_zones(gpx):

	for time, latitude, longitude, elevation, hr in extract_hr.extract_hr_points(gpx):

		hr_percentage = int(hr) / HR_MAX
		# get the last threshold below the hr_percentage
		hr_zone = list(filter( lambda threshold: hr_percentage > threshold[1], ZONE_THRESHOLDS.items() ))[-1][0]

		# convert time from 'YYYY-MM-DD HH:MM:SS+00:00' to 'HH:MM:SS'
		new_time = datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S+00:00')
		new_time = time.strftime('%H:%M:%S')

		yield new_time, latitude, longitude, elevation, hr, hr_zone


def group_data_by_bins(times, elevations, hr_zones, num_bins=20):
	"""
	Groups the data into bins and calculates the mean for each bin
	(only if the number of bins is less than the actual data size).

	Args:
		times (list): List of time values.
		elevations (list): List of elevation values.
		hr_zones (list): List of HR zone values.
		num_bins (int): Number of bins to divide the data into.

	Returns:
		tuple: Binned times, mean elevations, and mean HR zones.
	"""
	num_bins = min(num_bins, len(times) - 1)

	# Convert times to numerical indices for easier binning
	indices = np.linspace(0, len(times) - 1, num_bins + 1).astype(int)

	binned_times = []
	mean_elevations = []
	mean_hr_zones = []

	for i in range(len(indices) - 1):
		start, end = indices[i], indices[i + 1]

		# Get the slice of data for this bin
		bin_times = times[start:end]
		bin_elevations = elevations[start:end]
		bin_hr_zones = hr_zones[start:end]

		# Append the midpoint of the bin for times
		binned_times.append(bin_times[len(bin_times) // 2])

		# Append the mean values for elevations and HR zones
		mean_elevations.append(np.mean(bin_elevations))
		mean_hr_zones.append(np.mean(bin_hr_zones))

	return binned_times, mean_elevations, mean_hr_zones


def export_hr_zones_to_csv(gpx, filename, csv_separator=','):

	with open(filename, 'w', newline='') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=csv_separator, quotechar='|', quoting=csv.QUOTE_MINIMAL)

		# print header
		csvwriter.writerow(['Time', 'Latitude', 'Longitude', 'Elevation', 'HR', 'HR Zone'])

		for time, latitude, longitude, elevation, hr, hr_zone in extract_hr_zones(gpx):
			csvwriter.writerow([time, latitude, longitude, elevation, hr, hr_zone])


# plot zones + elevation and wite to file
def plot_hr_zones(gpx, filename, num_bins=2000, num_xticks=30):

	# get hr zones
	data = list(extract_hr_zones(gpx))

	elevations	= [elevation	for time, latitude, longitude, elevation, hr, hr_zone in data]
	hr_zones	= [hr_zone		for time, latitude, longitude, elevation, hr, hr_zone in data]
	times		= [time for time, latitude, longitude, elevation, hr, hr_zone in data]

	binned_times, mean_elevations, mean_hr_zones = group_data_by_bins(times, elevations, hr_zones, num_bins)

	# plot, using as x times, as y both elevations and hr_zones
	fig, ax1 = plt.subplots(figsize=(16, 8))

	color = 'tab:red'
	ax1.set_xlabel('Time')
	ax1.set_ylabel('Elevation', color=color)
	ax1.plot(binned_times, mean_elevations, color=color, label='Elevation')
	ax1.fill_between(binned_times, mean_elevations, color=color, alpha=0.3)
	ax1.tick_params(axis='y', labelcolor=color)
	ax1.grid(True)
	ax1.set_xticks(binned_times[::len(binned_times) // num_xticks])
	plt.xticks(rotation=60)

	ax2 = ax1.twinx()
	color = 'tab:blue'
	ax2.set_ylabel('HR Zone', color=color)
	ax2.plot(binned_times, mean_hr_zones, color=color, label='HR Zone')
	ax2.tick_params(axis='y', labelcolor=color)
	ax2.grid(True, axis='both')
	ax2.set_yticks([1, 2, 3, 4, 5])

	#ax2.fill_between(binned_times, mean_hr_zones, color=color, alpha=0.3)

	# Fill different colors for different HR zones

	# horizontal
	colors = ['#FFDDC1', '#FFABAB', '#FFC3A0', '#FF677D', '#D4A5A5']
	alphas = np.linspace(0.1, 0.85, 5)
	#for i in range(1, 6):
	#	ax2.fill_between(binned_times, i-1, np.maximum( np.minimum(i, mean_hr_zones), i-1), color=color, alpha=alphas[i-1])

	# vertical
	for i in range(1, 6):
		ax2.fill_between(binned_times, 0, mean_hr_zones, where=np.array(mean_hr_zones) == i, color=color, alpha=alphas[i-1])
		#ax2.fill_between(binned_times, 0, mean_hr_zones, where=np.array(mean_hr_zones) == i, color=colors[i-1], alpha=0.3)


	plt.tight_layout()
	plt.savefig(filename)
	plt.close()



if __name__ == '__main__':

	file_csv = 'hr-zones.csv'

	file_gpx = open('samples/gpx/mtb-ride.gpx', 'r')
	gpx = gpxpy.parse(file_gpx)

	export_hr_zones_to_csv(gpx, file_csv)
	plot_hr_zones(gpx, 'out/mtb-ride_hr-zones.png')
