# Install and update

*code and documentation* `fusus.about.install`

* get code
* update docs
* update code

# Run 

*Straight from the command line* `fusus.convert`

* run the OCR pipeline from the command line
* run the PDF extraction from the command line
* convert TSV to TF

# Contribute more sources

*From "no comments" to "more comments"* `fusus.works`

* add commentaries as works

# Explore

*Page by page in a notebook*

* [do](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/do.ipynb)
  Run the pipeline in a notebook;
* [inspect](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/inspect.ipynb)
  Inspect intermediate results in a notebook.
* [ocr](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/ocr.ipynb)
  Read the proofs of Kraken-OCR.
* [notebooks on nbviewer](https://nbviewer.jupyter.org/github/among/fusus/tree/master/notebooks/).
  All notebooks.


# Tweak

*Sickness and cure by parameters*

* [tweak](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/tweak.ipynb)
  Basic parameter tweaking;
* `fusus.parameters`
  All parameters.
* [comma](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/comma.ipynb)
  A ministudy in cleaning: tweak mark templates and parameters to wipe commas.
* [lines](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/lines.ipynb)
  Follow the line detection algorithm in a wide variety of cases.
* [piece](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/piece.ipynb)
  What to do if you have an image that is a small fragment of a page.


# Engineer

*Change the flow*

* `fusus.lakhnawi` 
  PDF reverse engineering.

  * [pages](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/pages.ipynb)
    Work with pages, follow line division, extract text and save to disk.
  * [characters](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/characters.ipynb)
    See which characters are in the PDF and how they are converted.
  * [final](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/final.ipynb)
    See in the effect of final characters on spacing.
* [border](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/border.ipynb)
  See how black borders get removed from a page.
  See also `fusus.lib.cropBorders` and `fusus.lib.removeBorders`.


# Work

*Do data science with the results*

* [useTsv](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/useTsv.ipynb)
  Use the TSV output of the pipeline.
* [useTf](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/useTf.ipynb)
  Use the Text-Fabric output of the pipeline.
* [boxes](https://nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/boxes.ipynb)
  Work with bounding boxes in the Text-Fabric data of the Lakhnawi.
