# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Use TSV data
#
# We show how to work with the TSV data from the Lakhnawi PDF.
#
# Fusus has a function to import TSV data that is coming out of the OCR pipeline and out of the text extraction pipeline.
#
# These have slightly different columns.
# When unpacking the TSV data, the function will cast the appropriate columns to integer.
#
# Reference: [convert](https://among.github.io/fusus/fusus/convert.html).

# %load_ext autoreload
# %autoreload 2

from fusus.convert import loadTsv

# For a known work, such as the Lakhnawi edition of the Fusus,
# we can use a keyword, see [works](https://among.github.io/fusus/fusus/works.html).

# # Lakhnawi
#
# ## By acronym

(headers, words) = loadTsv(source="fususl")

# We get the header fields and the words:

print(headers)

len(words)

print(words[40000])

# ## By path
#
# Alternatively, we could have gotten it as follows:

(headers, words) = loadTsv(source="~/github/among/fusus/ur/Lakhnawi/allpages.tsv", ocred=False)

print(headers)
print(len(words))
print(words[40000])

# # Afifi
#
# ## By acronym

(headers, words) = loadTsv(source="fususa")

# We get the header fields and the words:

print(headers)

len(words)

print(words[40000])

# ## By path
#
# Alternatively, we could have gotten it as follows:

(headers, words) = loadTsv(source="~/github/among/fusus/ur/Afifi/allpages.tsv", ocred=True)

print(headers)
print(len(words))
print(words[40000])


