#!/usr/bin/python

import xml.etree.ElementTree as etree


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
#  function definition
# =======================================

def elementDataToSVG(indent, element, xoff, yoff):
	return (
		'{tabs}<g transform="translate({x} {y})" class="element"\n'
		'{tabs}  width="80" height="80" x="8" y="8">\n'
		'{tabs}\t<rect class="background {css}" width="80" height="80"\n'
		'{tabs}\t  x="8" y="8" rx="4" ry="4"/>\n'
		'{tabs}\t<text class="number" fill="black" x="12.5" y="20">{id}</text>\n'
		'{tabs}\t<text class="symbol" fill="black" x="48" y="50">{sym}</text>\n'
		'{tabs}\t<text class="name"   fill="black" x="48" y="70">{name}</text>\n'
		'{tabs}\t<text class="weight" fill="black" x="48" y="81.5">{weight}</text>\n'
		'{tabs}</g>\n'
		.format(
			tabs = (indent * '\t'),
			x = xoff, y = yoff,
			id = element['ID'],
			sym = element['Symbol'],
			name = element['Name'],
			weight = element['Weight'],
			css = element['Class']
		)
	)


def generateLanthanides(file, row):
	file.write('\n\n\t<!-- Lanthanides -->\n\n')
	yoff = (row * 96) + CONST_LANACT_OFFSET

	for element in xml_data[1:]:
		# Skip elements not on this row
		if element['Period'] != 'L': continue

		# Properly align groups
		column = 3 + int(element['ID']) - 57
		xoff = column * 96 + CONST_GROUP4_OFFSET

		# Write element's data
		file.write( elementDataToSVG(1, element, xoff, yoff) )


def generateActinides(file, row):
	file.write('\n\n\t<!-- Actinides -->\n\n')
	yoff = (row * 96) + CONST_LANACT_OFFSET

	for element in xml_data[1:]:
		# Skip elements not on this row
		if element['Period'] != 'A': continue

		# Properly align groups
		column = 3 + int(element['ID']) - 89
		xoff = column * 96 + CONST_GROUP4_OFFSET

		# Write element's data
		file.write( elementDataToSVG(1, element, xoff, yoff) )


# =======================================
#  Write to SVG file
# =======================================

fd = open("periodic.svg", 'w')

# Header
fd.write(
	'<?xml version="1.0" encoding="UTF-8"?>\n'
	'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\n'
	'  width="100%" height="100%" viewBox="0 0 {w} {h}"\n'
	'  class="dark" id="periodic-table"\n'
	'>\n\n'
	.format(
		w = (19*96) + CONST_GROUP4_OFFSET + 10,
		h = (10*96) + CONST_LANACT_OFFSET + 10
	)
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
for i in range(1-7):

	# Compute period position
	yoff = (i+1) * 96

	fd.write('\n\n\t<!-- Period {} -->\n\n'.format(periods[i]))


	# TODO: Period Indicator

	for element in xml_data[1:]:
		# Skip elements not on this row
		if element['Period'] != periods[i]:
			continue

		# Properly align groups
		column = int(element['Group'])

		# Add offset if group is >= 4
		xoff = column * 96
		if column >= 4: xoff += CONST_GROUP4_OFFSET

		# Write element's data
		fd.write( elementDataToSVG(1, element, xoff, yoff) )


# Put Lanthanides on row 8 and actinides on row 9 (with some offset)
generateLanthanides (fd, 8)
generateActinides   (fd, 9)


# End of file (closing tag)
fd.write('</svg>\n')
fd.close()
