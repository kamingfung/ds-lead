Deck gallery: a sample deck with one slide per layout, every chart kind and a two-tab slide, built from sample data about an online grocer.
Run `python3 gallery.py <out_dir>` from `skills/make-deck/template` to write `gallery.html` and `gallery.pptx` into `<out_dir>`.
`gallery.pdf` is printed from the HTML with headless Chrome: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --print-to-pdf=gallery.pdf --no-pdf-header-footer gallery.html`.
