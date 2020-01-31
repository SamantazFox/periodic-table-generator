#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
import xml.etree.ElementTree as etree


# =======================================
#  Help functiion
# =======================================

def printUsage():
	print(
		'Usage: python3 {0} [OPTIONS]\n'
		'Usage: ./{0} [OPTIONS]\n\n'
		'Options:\n'
		'  --help             Displays this help message and exits\n'
		'  --large            Generate a 32-column version of the periodic table\n'
		'                      (The default is to generate a 18-column version)\n'
		'  --embedded-css     Include the contents of periodic.css to the generated SVG,\n'
		'                      in a <style></style> tag (this is the default)\n'
		'  --no-embedded-css  Define periodic.css as an XML stylesheet\n'
		'  --high-contrast    Use a high contrast color scheme\n'
		'  --colorblind       Same as --high-contrast\n'
		.format(os.path.basename(sys.argv[0]))
	)

# =======================================
#  Parse arguments
# =======================================

# Init
largeTable = False
colorblind = False
embed_css = True

# Loop in arguments
if len(sys.argv) > 1:
	for arg in sys.argv[1:]:

		if arg == '--help':
			printUsage()
			quit()

		if arg == '--large':
			largeTable = True

		if arg == '--colorblind' or arg == '--high-contrast':
			colorblind = True

		if arg == '--no-embedded-css':
			embed_css = False
		elif arg == '--embedded-css':
			embed_css = True


# 32-columns
if largeTable:
	CONST_GROUP4_OFFSET = 0
	CONST_LANACT_OFFSET = 0

	CONST_COL_COUNT = 33
	CONST_ROW_COUNT =  8

# 18-columns
else:
	CONST_GROUP4_OFFSET = 20
	CONST_LANACT_OFFSET = 20

	CONST_COL_COUNT = 19
	CONST_ROW_COUNT = 10


# Colorblind/high-contrast mode
colorblind_tag = " colorblind" if colorblind else ""


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
		'Name'  : elem.findtext('name'),
		'isRadioactive': (elem.findtext('radioactive') != None)
	}

	# Sort elements by id in data
	xml_data.insert( int(element['ID']), element )


# =======================================
#  function definition
# =======================================

def elementDataToSVG(indent, element, xoff, yoff):
	strbuffer = (
		'{tabs}<g transform="translate({x} {y})" class="element"\n'
		'{tabs}  width="80" height="80" x="8" y="8">\n'
		'{tabs}\t<rect class="background {css}" width="80" height="80"\n'
		'{tabs}\t  x="8" y="8" rx="4" ry="4"/>\n'
		.format(
			tabs = (indent * '\t'),
			x = xoff, y = yoff,
			css = element['Class']
		)
	)

	if element['isRadioactive']:
		strbuffer += (
			'{tabs}\t<use xlink:href="#radioactive-logo" />\n'
			.format(tabs = (indent * '\t'))
		)

	strbuffer += (
		'{tabs}\t<text class="number" fill="black" x="12.5" y="20">{id}</text>\n'
		'{tabs}\t<text class="symbol" fill="black" x="48" y="50">{sym}</text>\n'
		'{tabs}\t<text class="name"   fill="black" x="48" y="70">{name}</text>\n'
		'{tabs}\t<text class="weight" fill="black" x="48" y="81.5">{weight}</text>\n'
		'{tabs}</g>\n'
		.format(
			tabs = (indent * '\t'),
			id = element['ID'],
			sym = element['Symbol'],
			name = element['Name'],
			weight = element['Weight'],
		)
	)

	return strbuffer


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
#  Main parts of the SVG file
# =======================================

def generateSVGHeader(file):
	# XML/encoding declaration
	strbuffer = '<?xml version="1.0" encoding="UTF-8"?>\n'

	# Include a stylesheet, the XML way
	if not embed_css:
		strbuffer += '<?xml-stylesheet type="text/css" href="periodic.css"?>\n'

	# Open SVG tag
	strbuffer += (
		'<svg class="dark{cbtag}" id="periodic-table"\n'
		'  width="100%" height="100%" viewBox="0 0 {w} {h}"\n'
		'  xmlns="http://www.w3.org/2000/svg"\n'
		'  xmlns:xlink="http://www.w3.org/1999/xlink"\n'
		'>\n\n'
		.format(
			w = (CONST_COL_COUNT * 96) + CONST_GROUP4_OFFSET + 10,
			h = (CONST_ROW_COUNT * 96) + CONST_LANACT_OFFSET + 10,
			cbtag = colorblind_tag
		)
	)

	# Write to file
	file.write(strbuffer)


def generateDocTitle(file):
	file.write('\t<title>Periodic table</title>\n\n')


def generateDefs(file):
	# For the radioactive logo:
	#   * scale(0.16) => border:   0
	#   * scale(0.13) => border:  8x8
	#   * scale(0.12) => border: 12x12
	#
	file.write(
		'\t<defs>\n'
		'\t\t<svg id="radioactive-logo" width="96" height="96">\n'
		'\t\t\t<g transform="translate(12 12) scale(0.12)">\n'
		'\t\t\t\t<circle cx="300" cy="300" r="50"  opacity="0.15" />\n'
		'\t\t\t\t<path stroke="#000" stroke-width="175" fill="none" opacity="0.15"\n'
		'\t\t\t\t  stroke-dasharray="171.74" d="M382,158a164,164 0 1,1-164,0" />\n'
		'\t\t\t</g>\n'
		'\t\t</svg>\n'
		'\t</defs>\n\n'
	)


def generateEmbeddedCSS(file):
	strbuffer = '\t<style>\n'

	# Copy/Past lines, with added indentation
	with open("periodic.css", 'r') as style_fd:
		for line in style_fd:
			strbuffer += '\t\t' + line

	file.write(strbuffer + '\t</style>\n\n')


# =======================================
#  Write to SVG file
# =======================================

fd = open("periodic.svg", 'w')

# Header
generateSVGHeader(fd)
generateDocTitle(fd)
generateDefs(fd)

if embed_css:
	generateEmbeddedCSS(fd)


# Create the periods & groups headers
fd.write('\t<!-- Groups header -->\n\n' '\t<g>\n')

for i in range(1,19):
	# Add a space between group 3/4
	xpos = (i*96 + 48)
	if i >= 4:
		xpos += CONST_GROUP4_OFFSET
		if largeTable: xpos += 14 * 96

	fd.write(
		'\t\t<text class="headers-text" x="{x}" y="{y}">{grp}</text>\n'
		.format(x = xpos, y = 64, grp = i)
	)

fd.write('\t</g>\n')


# Create elements
for i in range(1, 8):

	# Compute period position
	yoff = (i * 96)

	fd.write(
		'\n\n\t<!-- Period {per} -->\n\n'
		'\t<text class="headers-text" x="{x}" y="{y}">{per}</text>\n\n'
		.format(x = 48, y = (yoff + 58), per = i)
	)

	for element in xml_data[1:]:
		# Skip elements not on this row
		if element['Period'] != str(i):
			continue

		# Properly align groups
		column = int(element['Group'])
		xoff = (column * 96)

		if column >= 4:
			xoff += CONST_GROUP4_OFFSET
			if largeTable: xoff += 14*96

		# Write element's data
		fd.write( elementDataToSVG(1, element, xoff, yoff) )


# Lanthanides and Actinides
if largeTable:
	# Generate inline with period 6 & 7
	generateLanthanides (fd, 6)
	generateActinides   (fd, 7)
else:
	# Put lanthanides and actinides on sparate rows (8 & 9, respectively)
	generateLanthanides (fd, 8)
	generateActinides   (fd, 9)


# End of file (closing tag)
fd.write('</svg>\n')
fd.close()


# Compress the SVG file when we're done
os.system('gzip -c periodic.svg > periodic.svgz')
