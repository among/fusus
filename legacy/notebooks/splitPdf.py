# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python3.8
#     language: python
#     name: python3.8
# ---

# %load_ext autoreload
# %autoreload 2
# !cd `pwd`

from fusus.pdf import pdf2png

name = "Afifi1"
source = f"../_local/source/{name}/{name.lower()}.pdf"
dest = f"../ur/{name}/in"

pdf2png(source, dest, silent=False)


