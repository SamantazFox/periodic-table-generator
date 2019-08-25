#!/usr/bin/python

import xml.etree.ElementTree as etree

# List of rows
periods = ['1','2','3','4','5','6','7','L','A']

# Some constants
CONST_GROUP4_OFFSET = 20
CONST_LANACT_OFFSET = 20


# =======================================
#  Load list of elements
# =======================================

docroot = etree.parse('elements.xml').getroot()
treelist = docroot.findall('element')

xml_data = [0]

for elem in treelist:
	element = {
		'ID'    : elem.get('id'),
		'Symbol': elem.get('symbol'),
		'Period': elem.get('period'),
		'Group' : elem.get('group'),
		'Weight': elem.findtext('weight'),
		'Class' : elem.findtext('class'),
		'Name'  : elem.findtext('name')
	}

	# Sort elements by id in data
	xml_data.insert( int(element['ID']), element )


# =======================================
#  Write to SVG file
# =======================================

fd = open("periodic.svg", 'w')

# Header
fd.write(
	'<?xml version="1.0" encoding="UTF-8"?>\n'
	'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\n'
	'  width="100%" height="100%" viewBox="0 0 1824 1000"\n'
	'  class="dark" id="periodic-table"\n'
	'>\n\n'
)


# Embedded CSS
fd.write('\t<style>\n')
with open("style.css", 'r') as style_fd:
	[fd.write('\t\t' + l) for l in style_fd]
fd.write('\t</style>\n\n')


# Image title
fd.write('\t<title>Periodic table</title>\n\n')


# Create the periods & groups headers
fd.write('\t<g class="headers-text">\n')
fd.write('\t\t<!-- Groups header -->\n')

for i in range(1,19):
	# Add a space between group 3/4
	xpos = (i*96 + 48)
	if i >= 4: xpos += CONST_GROUP4_OFFSET

	fd.write(
		'\t\t<text width="96" x="{x}" y="{y}">{grp}</text>\n'
		.format(x = xpos, y = 64, grp = i)
	)

fd.write('\t\t<!-- Periods header -->\n')

for i in range(1,8):
	fd.write(
		'\t\t<text width="96" x="{x}" y="{y}">{per}</text>\n'
		.format(x = 48, y =(i*96 + 58), per = i)
	)

fd.write('\t</g>\n\n')


# Create elements
for i in range(len(periods)):

	# Compute period position
	yoff = (i+1) * 96

	# Treat Lanthanides and Actinides as separate "periods" (i.e rows)
	if periods[i] == 'L':
		fd.write('\n\n\t<!-- Lanthanides -->\n\n')
		yoff += CONST_LANACT_OFFSET

	elif periods[i] == 'A':
		fd.write('\n\n\t<!-- Actinides -->\n\n')
		yoff += CONST_LANACT_OFFSET

	else:
		fd.write('\n\n\t<!-- Period {} -->\n\n'.format(periods[i]))


	# TODO: Period Indicator

	# Elements for this "period"
	col_num = 0

	for element in xml_data[1:]:
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
		if column >= 4: xoff += CONST_GROUP4_OFFSET


		# Write element's data
		fd.write(
			'\t<g transform="translate({x} {y})" class="element"\n'
			'\t  width="80" height="80" x="8" y="8">\n'
			'\t\t<rect class="background {css}" width="80" height="80"\n'
			'\t\t  x="8" y="8" rx="4" ry="4"/>\n'
			'\t\t<text class="number" fill="black" x="12.5" y="20">{id}</text>\n'
			'\t\t<text class="symbol" fill="black" x="48" y="50">{sym}</text>\n'
			'\t\t<text class="name"   fill="black" x="48" y="70">{name}</text>\n'
			'\t\t<text class="weight" fill="black" x="48" y="81.5">{weight}</text>\n'
			'\t</g>\n'
			.format(
				x = xoff, y = yoff,
				id = element['ID'],
				sym = element['Symbol'],
				name = element['Name'],
				weight = element['Weight'],
				css = element['Class']
			)
		)


# End of file (closing tag)
fd.write('</svg>\n')
fd.close()
