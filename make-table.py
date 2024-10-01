#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
import xml.etree.ElementTree as etree
import gzip


# =======================================
#  Config options class definition
# =======================================

class TableConfig:
	def __init__(self):
		self.theme = 'dark'
		self.large_table = False
		self.colorblind = False
		self.legends = True

# Init defaults
config = TableConfig()


# =======================================
#  Help functiion
# =======================================

def printUsage(cfg : TableConfig):
	print(
		'Usage: python3 {0} [OPTIONS]\n'
		'Usage: ./{0} [OPTIONS]\n\n'
		.format(os.path.basename(sys.argv[0]))
	)

	print(
		'Options:\n'
		'  --help             Displays this help message and exits\n\n'
		'  --large            Generate a 32-column version of the periodic table\n'
		'  --legends          Generate the legends\n'
		'  --no-legends       Do not generate the legends\n\n'
		'  --dark             Use a dark background theme\n'
		'  --light            Use a light background theme\n\n'
		'  --high-contrast    Use a high contrast color scheme\n'
		'  --colorblind       Alias for --high-contrast\n\n'
	)

	print(
		'Defaults:\n'
		'  * theme = {theme}\n'
		'  * width = {width}\n'
		'  * legends = {legends}\n'
		'  * high-contrast = {high_contrast}\n'
		.format(
			theme = cfg.theme,
			width = '32 (large)' if cfg.large_table else '18 (narrow)',
			legends = 'Yes' if cfg.legends else 'No',
			high_contrast = 'Yes' if cfg.colorblind else 'No',
		)
	)


# =======================================
#  Parse arguments
# =======================================

# Loop in arguments
if len(sys.argv) > 1:
	for arg in sys.argv[1:]:

		if arg == '--help':
			printUsage(config)
			quit()

		if arg == '--light':
			config.theme = 'light'
		elif arg == '--dark':
			config.theme = 'dark'

		if arg == '--large':
			config.large_table = True

		if arg == '--no-legends':
			config.legends = False
		elif arg == '--legends':
			config.legends = True

		if arg == '--colorblind' or arg == '--high-contrast':
			config.colorblind = True


# 32-columns
if config.large_table:
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


# Compute the "element" and "classes" legends positions
CONST_LEG_ELEMS_XPOS = (7*96) + 48  #(7*96) + 72
CONST_LEG_ELEMS_YPOS = 160

CONST_LEG_CLASS_XPOS = 96
CONST_LEG_CLASS_YPOS = (96*CONST_ROW_COUNT) + CONST_LANACT_OFFSET + 35


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
#  Elements
# =======================================

def elementDataToSVG(indent, element, xoff, yoff, element_id = None):
	# Unique identifier for the element (useful in Inkscape e.g)
	# This is also used as a prefix for sub-nodes (like text)
	if element_id is None:
		element_id = "elem{:03d}".format(int(element['ID']))

	strbuffer = (
		'{tabs}<g transform="translate({x} {y})" class="element" id="{id}"\n'
		'{tabs}  width="80" height="80" x="8" y="8">\n'
		'{tabs}\t<rect class="background {css}" id="{id}_bg" width="80" height="80"\n'
		'{tabs}\t  x="8" y="8" rx="4" ry="4"/>\n'
		.format(
			tabs = (indent * '\t'),
			id = element_id,
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
		'{tabs}\t<text class="number" id="{id}_txt-num" x="12.5" y="20">{number}</text>\n'
		'{tabs}\t<text class="symbol" id="{id}_txt-sym" x="48" y="50">{sym}</text>\n'
		'{tabs}\t<text class="name"   id="{id}_txt-lbl" x="48" y="70">{name}</text>\n'
		'{tabs}\t<text class="weight" id="{id}_txt-saw" x="48" y="81.5">{weight}</text>\n'
		'{tabs}</g>\n'
		.format(
			tabs = (indent * '\t'),
			id = element_id,
			number = element['ID'],
			sym = element['Symbol'],
			name = element['Name'],
			weight = element['Weight'],
		)
	)

	return strbuffer


def generateLanthanides(file, row):
	file.write('\n\n\t<!-- Lanthanides -->\n\n')
	file.write('\t<g id="lanthanides">\n')
	yoff = (row * 96) + CONST_LANACT_OFFSET

	for element in xml_data[1:]:
		# Skip elements not on this row
		if element['Period'] != 'L': continue

		# Properly align groups
		column = 3 + int(element['ID']) - 57
		xoff = column * 96 + CONST_GROUP4_OFFSET

		# Write element's data
		file.write( elementDataToSVG(1, element, xoff, yoff) )

	file.write('\t</g>\n')

def generateActinides(file, row):
	file.write('\n\n\t<!-- Actinides -->\n\n')
	file.write('\t<g id="actinides">\n')
	yoff = (row * 96) + CONST_LANACT_OFFSET

	for element in xml_data[1:]:
		# Skip elements not on this row
		if element['Period'] != 'A': continue

		# Properly align groups
		column = 3 + int(element['ID']) - 89
		xoff = column * 96 + CONST_GROUP4_OFFSET

		# Write element's data
		file.write( elementDataToSVG(1, element, xoff, yoff) )

	file.write('\t</g>\n')


# =======================================
#  Legends
# =======================================

def generateLegendElement(file):
	# Based on Oxygen (aka element 8)
	strbuffer = (
		'\t<g transform="translate({x} {y}) scale(1.2)" id="legend_elem">\n'
		'\t\t<rect fill="#ADADAD" stroke="#424242" stroke-width="1.2"\n'
		'\t\t  width="340" height="116" x="0" y="0" rx="4" ry="4"/>\n'
		'\t\t<g transform="translate(30 0)">\n'
		'{element}'
		.format(
			x = CONST_LEG_ELEMS_XPOS,
			y = CONST_LEG_ELEMS_YPOS,
			element = elementDataToSVG(3, xml_data[8], 110, 10, "elem_example")
		)
	)

	strbuffer += (
		'\t\t\t<text x="110" y="30" text-anchor="end">Atomic number</text>\n'
		'\t\t\t<path stroke="#000" d="M113 27 l8 0"/>\n'
		'\t\t\t<text x="110" y="91" text-anchor="end">Atomic standard weight</text>\n'
		'\t\t\t<path stroke="#000" d="M113 88.5 l20 0"/>\n'
		'\t\t\t<text x="205" y="52" text-anchor="start">Symbol</text>\n'
		'\t\t\t<path stroke="#000" d="M202 48.8 l-29 0"/>\n'
		'\t\t\t<text x="205" y="80" text-anchor="start">Element name</text>\n'
		'\t\t\t<path stroke="#000" d="M202 76.6 l-21 0"/>\n'
	)

	# End of group & write to file
	strbuffer += '\t\t</g>\n'
	strbuffer += '\t</g>\n'
	file.write(strbuffer)


def generateLegendClasses(file):
	# List of classes, and their corresponding display text
	classes_list = [
		("alkali",      "Alkali|metal"                ),
		("alkalineEM",  "Alkaline|earth|metal"        ),
		("lanthanide",  "Lanthanide"                  ),
		("actinide",    "Actinide"                    ),
		("transitionM", "Transition|metal"            ),
		("post-transM", "Post-|transition|metal"      ),
		("metalloid",   "Metalloid"                   ),
		("reactiveNM",  "Reactive|nonmetal"           ),
		("noble-gas",   "Noble gas"                   ),
		("unknown",     "Unknown|chemical|properties" )
	]

	# Group start
	# NB: Position of this legend depends on the "large table" option
	strbuffer = (
		'\t<g transform="translate({x} {y})" class="legend-class" id="legend_classes">\n'
		'\t\t<rect fill="#ADADAD" stroke="#424242" stroke-width="1.2"\n'
		'\t\t  width="915" height="110" x="0" y="0" rx="4" ry="4"/>\n'
		.format(x = CONST_LEG_CLASS_XPOS, y = CONST_LEG_CLASS_YPOS)
	)

	# Main class: metals
	strbuffer += (
		'\t\t<g class="super-class" id="legend_superclass_Metals" transform="translate(10 10)">\n'
		'\t\t\t<rect width="540" height="90" x="0" y="0"/>\n'
		'\t\t\t<text x="270" y="13.5">Metals</text>\n'
		'\t\t\t<path d="M5 18 L535 18"/>\n'
		'\t\t</g>\n'
	)

	# Main class: nonmetals
	strbuffer += (
		'\t\t<g class="super-class" id="legend_superclass_Nonmetals" transform="translate(640 10)">\n'
		'\t\t\t<rect width="180" height="90" x="0" y="0"/>\n'
		'\t\t\t<text x="90" y="13.5">Nonmetals</text>\n'
		'\t\t\t<path d="M5 18 L175 18"/>\n'
		'\t\t</g>\n'
	)


	# Display each class, with it's associated background
	for i in range(0,len(classes_list)):

		# Split the text as needed
		text_lines = classes_list[i][1].split('|')
		line_count = len(text_lines)

		# Use one "<tspan>" per line
		if line_count == 1:
			outText = text_lines[0]
		elif line_count == 2:
			outText  = '<tspan x="40" dy="-0.5em">' + text_lines[0] + '</tspan>'
			outText += '<tspan x="40" dy="1.1em">' + text_lines[1] + '</tspan>'
		elif line_count == 3:
			outText  = '<tspan x="40" dy="-1.1em">' + text_lines[0] + '</tspan>'
			outText += '<tspan x="40" y="35">' + text_lines[1] + '</tspan>'
			outText += '<tspan x="40" dy="1.1em">' + text_lines[2] + '</tspan>'

		# Append formatted data to buffer
		strbuffer += (
			'\t\t<g class="sub-class" transform="translate({pos_X} {pos_Y})">\n'
			'\t\t\t<rect id="legend_class_{css}" class="{css}" width="80" height="60" x="0" y="0"/>\n'
			'\t\t\t<text x="40" y="35">{text}</text>\n'
			'\t\t</g>\n'
			.format(
				pos_X = (i*90) + 15, pos_Y = 35,
				css = classes_list[i][0],
				text = outText
			)
		)

	# End of group & write to file
	strbuffer += '\t</g>\n'
	file.write(strbuffer)


# =======================================
#  Main sections of the SVG file
# =======================================

def generateSVGHeader(cfg : TableConfig, file):
	# XML/encoding declaration
	strbuffer = '<?xml version="1.0" encoding="UTF-8"?>\n'

	# Take into account the legends in the viewbox
	legend_H = 150 if cfg.legends else 0

	# CSS classes
	classes = cfg.theme
	if cfg.colorblind: classes += " colorblind"

	# Open SVG tag
	strbuffer += (
		'<svg class="{classes}" id="periodic-table"\n'
		'  width="100%" height="100%" viewBox="0 0 {w} {h}"\n'
		'  xmlns="http://www.w3.org/2000/svg"\n'
		'  xmlns:xlink="http://www.w3.org/1999/xlink"\n'
		'>\n\n'
		.format(
			w = (CONST_COL_COUNT * 96) + CONST_GROUP4_OFFSET + 10,
			h = (CONST_ROW_COUNT * 96) + CONST_LANACT_OFFSET + 10 + legend_H,
			classes = classes,
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

	# We have to remove comments, as Inkscape doesn't seem to like them.
	comment_flag = False

	# Copy/Past lines, with added indentation
	with open("periodic.css", 'r') as style_fd:
		for line in style_fd:
			# Detect start of comment
			if "/*" in line: comment_flag = True

			# Copy line (except for comments and empty lines)
			if not (comment_flag or line == "\n" or line == "\r\n"):
				strbuffer += '\t\t' + line

			# Detect end of comment
			# Done after everything to easily skip one-liners
			if "*/" in line: comment_flag = False

	file.write(strbuffer + '\t</style>\n\n')


# =======================================
#  Write to SVG file
# =======================================

fd = open("periodic.svg", 'w')

# Header
generateSVGHeader(config, fd)
generateDocTitle(fd)
generateDefs(fd)

generateEmbeddedCSS(fd)


# Legends
if config.legends:
	fd.write('\t<!-- Legends -->\n\n')
	generateLegendClasses(fd)
	generateLegendElement(fd)
	fd.write('\n\n')


# Create the groups headers
fd.write(
	'\t<!-- Groups header -->\n\n'
	'\t<g id="groups_header">\n'
)

for i in range(1,19):
	# Add a space between group 3/4
	xpos = (i*96 + 48)
	if i >= 4:
		xpos += CONST_GROUP4_OFFSET
		if config.large_table: xpos += 14 * 96

	fd.write(
		'\t\t<text class="headers-text" id="group{grp:02d}_header" x="{x}" y="{y}">{grp}</text>\n'
		.format(x = xpos, y = 64, grp = i)
	)

fd.write('\t</g>\n')


# Create the periods header
fd.write(
	'\t<!-- Periods header -->\n\n'
	'\t<g id="periods_header">\n'
)

for i in range(1, 8):
	fd.write(
		'\t<text class="headers-text" id="period{per}_header" x="{x}" y="{y}">{per}</text>\n\n'
		.format(x = 48, y = (i*96 + 58), per = i)
	)

fd.write('\t</g>\n')


# Create elements
for i in range(1, 8):

	# Compute period position
	yoff = (i * 96)

	fd.write(
		'\n\n\t<!-- Period {per} -->\n\n'
		'\t<g id="period{per}">\n'
		.format(per = i)
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
			if config.large_table: xoff += 14*96

		# Write element's data
		fd.write( elementDataToSVG(2, element, xoff, yoff) )

	fd.write('\t</g>\n')


# Lanthanides and Actinides
if config.large_table:
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


# =======================================
#  Compress SVG to SVGZ
# =======================================

with gzip.open("periodic.svgz", 'wb') as f_out:
	with  open("periodic.svg",  'rb') as f_in:
		compressed_data = gzip.compress(f_in.read())
		f_out.write(compressed_data)
