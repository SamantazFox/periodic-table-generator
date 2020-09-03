Periodic Table Generator
========================

Generates a SVG version of the perdiodic table of elements.

```
Usage: python3 make-table.py [OPTIONS]
Usage: ./make-table.py [OPTIONS]

Options:
  --large            Generate a 32-column version of the periodic table
                      (The default is to generate a 18-column version)

  --embedded-css     Include the contents of periodic.css to the generated SVG,
                      in a <style></style> tag (this is the default)
  --no-embedded-css  Define periodic.css as an XML stylesheet

  --legends          Generate the legends (this is the default)
  --no-legends       Do not generate the legends

  --dark             Use a dark background theme (this is the default)
  --light            Use a light background theme

  --high-contrast    Use a high contrast color scheme
  --colorblind       Alias for --high-contrast
```



Licensing
---------

This repo's content is released under the public domain.

Feel free to copy, modify and redistribute the code.

Read the UNLICENSE file for more infos.
