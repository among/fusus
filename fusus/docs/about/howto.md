# Run the pipeline

Put a collection of page images in a subdirectory `in` of an arbitrary directory.

Optionally, tweak some settings of `fusus.parameters.SETTINGS` in a file *parameters.yaml*,
at the top level of the book directory.

Put a program of notebook in the top level directory that has code to run the pipeline.
The run it.

As an example, see 
[Affifi](https://nbviewer.jupyter.org/github/among/fusus/blob/master/ur/Affifi/do.ipynb)
and inspect its
[directory](https://github.com/among/fusus/tree/master/ur/Affifi).

What you see is:

*   `parameters.yaml` parameter settings specific for this book, overriding
    the default parameter settings as defined in `fusus.parameters.SETTINGS`.
*   `do.ipynb` A notebook that lets you run the pipeline in various manners,
    see there for further instructions and explanations;
*   `allPages.tsv` A tab-separated file with the outcome of the pipeline.
    Each row specifies a word, including its unicdoe text,
    page and line numbers, layout details and bounding boxes.
    *   `in` The input file: scanned page images in tiff;
    *   `inter`: intermediate processing stages of each page; 
    *   `out`: output data in tsv format, a word on each line, for each page individually;
    *   `proof`: formatted files that help to proof the results of the OCR, containing:
        *   *ppp*`.html`: rendering of OCR result as boxed words in fixed positions on the page
            colored on the basis of the OCR confidences,
        *   *ppp*`-char.html`: same as above but now at character level,
        *   *ppp*`.tif` page images, used as a background for the `.html` files,
        *   *ppp*`-char.tsv`: output data in tsv format, a character on each line,
        *   *ppp*`-line.tsv`: the boundary boxes of all lines of the page

For more ways to interact with the pipeline, see `fusus.book`.

# Update documentation

The documentation of this project resides in

* the docstrings in the Python code of the *fusus* package;
* the markdown files in the *docs* directory and its subdirectories.

The documentation is generated as a set of static html pages by means of 
[pdoc3](https://pdoc3.github.io/pdoc/), to be published by means of GitHub pages.

If you need to do that yourself, consult `fusus.about.install`.
