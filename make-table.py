#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
import xml.etree.ElementTree as etree
import gzip


# List of language FILES
LANG_FILES = os.listdir('lang')
LANG_FILES.pop(LANG_FILES.index('template.xml'))
LANG_FILES.sort()

# List available languages
LANG_AVAIL = [f.removesuffix('.xml') for f in LANG_FILES]


# =======================================
#  Config options class definition
# =======================================

class TableConfig:
	def __init__(self):
		self.theme = 'dark'
		self.large_table = False
		self.colorblind = False
		self.legends = True
		self.show_econfig = False
		self.wiki_links = True

		self._languages = ['en']

	@property
	def multilingual(self):
		return len(self._languages) > 1

	@property
	def languages(self):
		return self._languages

	@languages.setter
	def languages(self, new_values):
		self._languages = []

		for lang in new_values:
			if lang in LANG_AVAIL:
				self._languages.append(lang)
			else:
				print('Language not supported: {}')

		if len(self._languages) == 0:
			print('Error: No supported language(s) were selected. Aborting')
			exit(1)

	def all_languages(self):
		self._languages = LANG_AVAIL


# Init defaults
config = TableConfig()


# =======================================
#  Help functions
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
		'  --large            Generate the 32-column version of the periodic table\n'
		'  --narrow           Generate the 18-column version of the periodic table\n\n'
		'  --legends          Generate the legends\n'
		'  --no-legends       Do not generate the legends\n\n'
		'  --wiki-links       Make element names link to the relevant wikipedia page\n'
		'  --no-wiki-links    Make element names plain text (non-clickable)\n\n'
		'  --econfig          Show the atom\'s electronic configuration (e.g: [Ne] 3s²)\n',
		'  --no-econfig       Do not show the electronic configuration\n\n',
		'  --dark             Use a dark background theme\n'
		'  --light            Use a light background theme\n\n'
		'  --high-contrast    Use a high contrast color scheme\n'
		'  --colorblind       Alias for --high-contrast\n\n'
		'  --lang=*           Include the selected language(s) in the generated file.\n'
		'                       The list needs to be comma-separated (e.g: --lang=en,fr,de).\n'
		'                       To include all languages, use --lang=all.\n'
		'                       To print a list of available languages, use --lang=help.\n\n'
	)

	print(
		'Defaults:\n'
		'  * theme = {theme}\n'
		'  * width = {width}\n'
		'  * languages = {langs}'
		'  * legends = {legends}\n'
		'  * econfig = {econfig}\n'
		'  * wiki-links = {wiki_links}\n'
		'  * high-contrast = {high_contrast}\n'
		.format(
			theme = cfg.theme,
			width = '32 (large)' if cfg.large_table else '18 (narrow)',
			langs = 'all' if cfg.languages == LANG_AVAIL else cfg.languages,
			legends = 'Yes' if cfg.legends else 'No',
			econfig = 'Yes' if cfg.show_econfig else 'No',
			wiki_links = 'Yes' if cfg.wiki_links else 'No',
			high_contrast = 'Yes' if cfg.colorblind else 'No',
		)
	)

def printLanguages():
	buffer = '  '
	for i in range(len(LANG_AVAIL)):
		# Print the value, right aligned on 3 characters
		if len(LANG_AVAIL[i]) == 2:
			buffer += ' ' + LANG_AVAIL[i]
		else: # len == 3
			buffer += LANG_AVAIL[i]

		# Add a comma, unless for the last one
		if i < len(LANG_AVAIL) - 1:
			buffer += ', '

		# Wrap at ~82 columns
		if (i+1) % 18 == 0:
			buffer += '\n  '

	print('Languages:\n' + buffer + '\n')


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
		elif arg == '--narrow':
			config.large_table = False

		if arg == '--no-legends':
			config.legends = False
		elif arg == '--legends':
			config.legends = True

		if arg == '--colorblind' or arg == '--high-contrast':
			config.colorblind = True

		if arg == '--no-econfig':
			config.show_econfig = False
		elif arg == '--econfig':
			config.show_econfig = True

		if arg == '--no-wiki-links':
			config.wiki_links = False
		elif arg == '--wiki-links':
			config.wiki_links = True

		if '--lang' in arg:
			langs = arg.split('=')[1]

			if langs == 'help':
				printLanguages()
				quit()
			elif langs == 'all':
				config.all_languages()
			else:
				config.languages = langs.split(',')


# =======================================
#  Constants
# =======================================

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


# The "element" legend positions
CONST_LEG_ELEMS_XPOS = (6*96)
CONST_LEG_ELEMS_YPOS = 160

# The "classes" legend positions
CONST_LEG_CLASS_XPOS = 96
CONST_LEG_CLASS_YPOS = (96*CONST_ROW_COUNT) + CONST_LANACT_OFFSET + 35


# =======================================
#  Utility functions
# =======================================

def elements_range():
	return range(1,119)

def make_xml_id(element):
	return "elem{:03d}".format(int(element['ID']))

def make_text_id(element):
	return "text-" + make_xml_id(element)


def translate_element(cfg, lang, elem_id):
	if cfg.wiki_links:
		return (
			'<a xlink:href="{href}" href="{href}" xlink:show="new" target="_blank">{name}</a>'
			.format(
				href = LANG_DATA[lang]['elements'][elem_id]['wiki'],
				name = LANG_DATA[lang]['elements'][elem_id]['name']
			)
		)
	else:
		return LANG_DATA[lang]['elements'][elem_id]['name']

def number_to_super(number):
	table = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
	return str(number).translate(table)


def format_electron_config(value):
	original = value.split()
	new = []

	for part in original:
		if '^' in part:
			subshell, count = part.split('^')
			part = subshell + number_to_super(count)

		new.append(part)

	return ' '.join(new)


# =======================================
#  Load languages
# =======================================

LANG_DATA = {}

def load_lang_file(lang):
	docroot = etree.parse('lang/' + lang + '.xml').getroot()

	if lang != docroot.get('lang'):
		print("Error: corrupted language file {}.xml".format(lang))

	LANG_DATA[lang] = {
		'elements': [0], # We don't want to use element 0
	}

	# Load element name translations + wiki links
	for elem in docroot.find('elements').findall('element'):
		elem_id = int(elem.get('id'))
		data = {
			'name': elem.findtext('name'),
			'wiki': elem.findtext('wiki')
		}

		LANG_DATA[lang]['elements'].insert(elem_id, data)


# Always load english, as a reference (in case some translations
# are missing in the other files) and as a fallback
load_lang_file('en')

for lang in config.languages:
	# Obviously, don't bother re-loading english
	if lang == 'en': continue
	load_lang_file(lang)


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
		'isRadioactive': (elem.findtext('radioactive') != None),
		'eConfig'  : format_electron_config(elem.findtext('eConfig')),
		'ePerShell': elem.findtext('ePerShell'),
		'eValence' : elem.findtext('eValence'),
	}

	# Sort elements by id in data
	xml_data.insert( int(element['ID']), element )


# =======================================
#  Elements
# =======================================

def elementDataToSVG(cfg : TableConfig, indent, element, xoff, yoff, xml_id = None):
	# Unique identifier for the element (useful in Inkscape e.g)
	# This is also used as a prefix for sub-nodes (like text)
	if xml_id is None: xml_id = make_xml_id(element)

	# Reference to the translated element name
	# It must remain the same, even if a custom xml_id is provided
	text_id = make_text_id(element)

	strbuffer = (
		'{tabs}<g transform="translate({x} {y})" class="element" id="{xml_id}"\n'
		'{tabs}  width="80" height="80" x="8" y="8">\n'
		'{tabs}\t<rect class="background {Class}" id="{xml_id}_bg" width="80" height="80"\n'
		'{tabs}\t  x="8" y="8" rx="4" ry="4"/>\n'
	)

	if element['isRadioactive']:
		strbuffer += '{tabs}\t<use xlink:href="#radioactive-logo" />\n'

	if cfg.show_econfig:
		strbuffer += (
			'{tabs}\t<text class="number"    id="{xml_id}_txt-num" x="12.5" y="20">{ID}</text>\n'
			'{tabs}\t<text class="symbol sm" id="{xml_id}_txt-sym" x="48" y="46">{Symbol}</text>\n'
			'{tabs}\t<use  class="name"      xlink:href="#{text_id}" x="48" y="63" />\n'
			'{tabs}\t<text class="weight"    id="{xml_id}_txt-saw" x="48" y="73">{Weight}</text>\n'
			'{tabs}\t<text class="econf"     id="{xml_id}_txt-ecf" x="48" y="84">{eConfig}</text>\n'
		)

	else:
		strbuffer += (
			'{tabs}\t<text class="number" id="{xml_id}_txt-num" x="12.5" y="20">{ID}</text>\n'
			'{tabs}\t<text class="symbol" id="{xml_id}_txt-sym" x="48" y="50">{Symbol}</text>\n'
			'{tabs}\t<use  class="name"   xlink:href="#{text_id}" x="48" y="70" />\n'
			'{tabs}\t<text class="weight" id="{xml_id}_txt-saw" x="48" y="81.5">{Weight}</text>\n'
		)

	strbuffer += '{tabs}</g>\n'

	return strbuffer.format(
		tabs = (indent * '\t'),
		xml_id = xml_id, text_id = text_id,
		x = xoff, y = yoff,
		**element, # Use element fields directly
	)


def generateLanthanides(cfg : TableConfig, file, row):
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
		file.write( elementDataToSVG(cfg, 2, element, xoff, yoff) )

	file.write('\t</g>\n')

def generateActinides(cfg : TableConfig, file, row):
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
		file.write( elementDataToSVG(cfg, 2, element, xoff, yoff) )

	file.write('\t</g>\n')


# =======================================
#  Legends
# =======================================

def generateLegendElement(cfg : TableConfig, file):
	# Based on Oxygen (aka element 8)
	strbuffer = (
		'\t<g transform="translate({x} {y}) scale(1.2)" id="legend_elem">\n'
		'\t\t<rect fill="#ADADAD" stroke="#424242" stroke-width="1.2"\n'
		'\t\t  width="380" height="116" x="0" y="0" rx="4" ry="4"/>\n'
		'\t\t<g transform="translate(30 0)">\n'
		'{element}'
		.format(
			x = CONST_LEG_ELEMS_XPOS,
			y = CONST_LEG_ELEMS_YPOS,
			element = elementDataToSVG(cfg, 3, xml_data[8], 110, 10, "elem_example")
		)
	)

	# The atomic number never moves
	strbuffer += (
		'\t\t\t<text class="legend-elem left" x="110" y="27">Atomic number</text>\n'
		'\t\t\t<path stroke="#000" d="M113 27 l8 0"/>\n'
	)

	if cfg.show_econfig:
		strbuffer += (
			'\t\t\t<text class="legend-elem right" x="205" y="45">Symbol</text>\n'
			'\t\t\t<path stroke="#000" d="M202 45 l-29 0"/>\n'
			'\t\t\t<text class="legend-elem left" x="110" y="80">Atomic standard weight</text>\n'
			'\t\t\t<path stroke="#000" d="M113 80 l26 0"/>\n'
			'\t\t\t<text class="legend-elem right" x="205" y="70">Element name</text>\n'
			'\t\t\t<path stroke="#000" d="M202 70 l-21 0"/>\n'
			'\t\t\t<text class="legend-elem right" x="205" y="92">Electronic configuration</text>\n'
			'\t\t\t<path stroke="#000" d="M202 92 l-22 0"/>\n'
		)
	else:
			strbuffer += (
			'\t\t\t<text class="legend-elem right" x="205" y="48.8">Symbol</text>\n'
			'\t\t\t<path stroke="#000" d="M202 48.8 l-29 0"/>\n'
			'\t\t\t<text class="legend-elem left" x="110" y="88.5">Atomic standard weight</text>\n'
			'\t\t\t<path stroke="#000" d="M113 88.5 l26 0"/>\n'
			'\t\t\t<text class="legend-elem right" x="205" y="76.6">Element name</text>\n'
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


def generateDefs(cfg : TableConfig, elements_list, lang_data):
	strbuffer = (
		'\t<defs>\n'
		'\t\t<!-- Graphics -->\n'
	)

	# For the radioactive logo:
	#   * scale(0.16) => border:   0
	#   * scale(0.13) => border:  8x8
	#   * scale(0.12) => border: 12x12
	#
	strbuffer += (
		'\t\t<svg id="radioactive-logo" width="96" height="96">\n'
		'\t\t\t<g transform="translate(12 12) scale(0.12)">\n'
		'\t\t\t\t<circle cx="300" cy="300" r="50"  opacity="0.15" />\n'
		'\t\t\t\t<path stroke="#000" stroke-width="175" fill="none" opacity="0.15"\n'
		'\t\t\t\t  stroke-dasharray="171.74" d="M382,158a164,164 0 1,1-164,0" />\n'
		'\t\t\t</g>\n'
		'\t\t</svg>\n\n'
	)

	strbuffer += (
		'\t\t<!-- Element names -->\n'
		'\t\t<g>\n'
	)

	if cfg.multilingual:
		for i in elements_range():
			# Start of switch element
			text_id = make_text_id(elements_list[i])
			strbuffer += '\t\t\t<switch id="{}">\n'.format(text_id)

			# <text><a {link}>{name}</a></text> for every language
			for lang in cfg.languages:
				strbuffer += (
					'\t\t\t\t<text class="name" systemLanguage="{lang}">{text}</text>\n'
					.format(lang = lang, text = translate_element(cfg, lang, i))
				)

			# End of switch element
			strbuffer += '\t\t\t</switch>\n'

	else:
		for i in elements_range():
			strbuffer += (
				'\t\t\t<text class="name" id="{text_id}">{text}</text>\n'
				.format(
					text_id = make_text_id(elements_list[i]),
					text = translate_element(cfg, cfg.languages[0], i)
				)
			)

	# End group
	strbuffer += '\t\t</g>\n'

	# Closing tag, then return data
	strbuffer += '\t</defs>\n\n'
	return strbuffer


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

	file.write(strbuffer + '\t</style>\n')


# =======================================
#  Write to SVG file
# =======================================

fd = open("periodic.svg", 'w')

# Header
generateSVGHeader(config, fd)
generateDocTitle(fd)
fd.write( generateDefs(config, xml_data, LANG_DATA) )

generateEmbeddedCSS(fd)


# Legends
if config.legends:
	fd.write('\n\n\t<!-- Legends -->\n\n')
	generateLegendClasses(fd)
	generateLegendElement(config, fd)


# Create the groups headers
fd.write(
	'\n\n\t<!-- Groups header -->\n\n'
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
	'\n\n\t<!-- Periods header -->\n\n'
	'\t<g id="periods_header">\n'
)

for i in range(1, 8):
	fd.write(
		'\t\t<text class="headers-text" id="period{per}_header" x="{x}" y="{y}">{per}</text>\n'
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
		fd.write( elementDataToSVG(config, 2, element, xoff, yoff) )

	fd.write('\t</g>\n')


# Lanthanides and Actinides
if config.large_table:
	# Generate inline with period 6 & 7
	generateLanthanides (config, fd, 6)
	generateActinides   (config, fd, 7)
else:
	# Put lanthanides and actinides on sparate rows (8 & 9, respectively)
	generateLanthanides (config, fd, 8)
	generateActinides   (config, fd, 9)


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
