# Run

The pipeline can read Arabic books in the form of page images,
and returns structured data in the form of tab separated files.

# Books

As far as the pipeline is concerned, the input of a book is a directory
of page images. More precisely, it is a directory in which there is 
a subdirectory `in` having the page images.

The books of the Fusus project are in the directory `ur` of this repo.

There you find subdirectories corresponding to

* **Affifi** The Fusus Al Hikam in the Affifi edition.
* **Lakhnawi** The Fusus Al Hikam in the Lakhnawi edition.
  The source is a textual PDF, not in the online repo, from which 
  structured data is derived by means of a specific workflow,
  not the *pipeline*.
* **commentary Xxx** Commentary books

When the pipeline runs, it produces additional directories containing intermediate results and
output.

For details, see `fusus.book`.


## Book in batch

You can run the pipeline on the known works inside the *ur* directory in this repo or
on books that you provide yourself.
See

*   `fusus.convert.tsvFromLakhnawi`
    (not the pipeline, but a reverse engineering effort, see `fusus.lakhnawi`)
*   `fusus.convert.tsvFromAffifi`
*   `fusus.convert.tsvFromCommentary`
*   `fusus.convert.tsvFromBook`
