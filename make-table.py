#!/usr/bin/python

import csv

# List of rows
periods = ['1','2','3','4','5','6','7','L','A']


# =======================================
#  Load list of elements
# =======================================

csv_fd = open("elements.csv", 'rb')
csv_reader = csv.DictReader(csv_fd)
csv_data = [row for row in csv_reader]
csv_fd.close()


# =======================================
#  Write to SVG file
# =======================================

fd = open("periodic.svg", 'w')

# Header
fd.write(
	'<?xml version="1.0" encoding="UTF-8"?>\n'
	'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\n'
	'  width="100%" height="100%" viewBox="0 0 1824 960">\n\n'
)


# Embedded CSS
fd.write('\t<style>\n')
with open("style.css", 'r') as style_fd:
	[fd.write('\t\t' + l) for l in style_fd]
fd.write('\t</style>\n\n')


# Image title
fd.write('\t<title>Periodic table</title>\n\n')


# Create elements
for i in range(len(periods)):

	# Compute period position
	yoff = i * 96

	# Treat Lanthanides and Actinides as separate "periods" (i.e rows)
	if periods[i] == 'L':
		fd.write('\n\n\t<!-- Lanthanides -->\n\n')
		yoff += 20

	elif periods[i] == 'A':
		fd.write('\n\n\t<!-- Actinides -->\n\n')
		yoff += 20

	else:
		fd.write('\n\n\t<!-- Period {} -->\n\n'.format(periods[i]))


	# TODO: Period Indicator

	# Elements for this "period"
	col_num = 0

	for element in csv_data:
		# Skip elements not on this row
		if element['Period'] != periods[i]:
			continue

		# Properly align groups
		if element['Group'] == 'L':
			column = 3 + int(element['ID']) - 57
		elif element['Group'] == 'A':
			column = 3 + int(element['ID']) - 89
		else:
			column = int(element['Group'])

		# Add offset if group is >= 4
		xoff = column * 96
		if column >= 4: xoff += 20


		# Determine CSS class for background
		# TODO: put CSS class in CSV
		if   element['Subtype'] == "Alkali metals":         css_class = "alkali"
		elif element['Subtype'] == "Alkaline earth metals": css_class = "alkalineEM"
		elif element['Subtype'] == "Lanthanides":           css_class = "lanthanide"
		elif element['Subtype'] == "Actinides":             css_class = "actinide"
		elif element['Subtype'] == "Transition metals":     css_class = "transitionM"
		elif element['Subtype'] == "Post-transition metal": css_class = "post-transM"
		elif element['Subtype'] == "Metalloids":            css_class = "metalloid"
		elif element['Subtype'] == "Reactive nonmetals":    css_class = "reactiveNM"
		elif element['Subtype'] == "Noble gases":           css_class = "noble-gas"
		elif element['Subtype'] == "Unknown chemical properties": css_class = "unknown"


		# Write element's data
		fd.write(
			'\t<g transform="translate({x} {y})" class="element"\n'
			'\t  width="80" height="80" x="8" y="8">\n'
			'\t\t<rect class="background {css}" width="80" height="80"\n'
			'\t\t  x="8" y="8" rx="4" ry="4"/>\n'
			'\t\t<text class="number" fill="black" x="12.5" y="20">{id}</text>\n'
			'\t\t<text class="symbol" fill="black" x="48" y="56">{sym}</text>\n'
			'\t\t<text class="name"   fill="black" x="48" y="70">{name}</text>\n'
			'\t\t<text class="weight" fill="black" x="48" y="81.5">{weight}</text>\n'
			'\t</g>\n'
			.format(
				x = xoff, y = yoff,
				id = element['ID'],
				sym = element['Symbol'],
				name = element['Name'],
				weight = element['Atomic weight'],
				css = css_class
			)
		)


# End of file (closing tag)
fd.write('</svg>\n')
fd.close()
