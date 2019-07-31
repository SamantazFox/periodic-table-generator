#!/usr/bin/python

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
fd.write(
	'\t<g class="element" width="80" height="80" x="8" y="8">\n'
	'\t\t<rect class="background noble-gas" width="80" height="80"\n'
	'\t\t  x="8" y="8" rx="4" ry="4"/>\n'
	'\t\t<text class="number" fill="black" x="12.5" y="20">18</text>\n'
	'\t\t<text class="symbol" fill="black" x="48" y="56">Ar</text>\n'
	'\t\t<text class="name"   fill="black" x="48" y="70">Argon</text>\n'
	'\t\t<text class="weight" fill="black" x="48" y="81.5">[39.792, 39.963]</text>\n'
	'\t</g>\n'
)

# End of file (closing tag)
fd.write('</svg>\n')
fd.close()
