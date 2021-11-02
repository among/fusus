# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python3.9
#     language: python
#     name: python3
# ---

import re

WORD_RE = re.compile(r"""
      ([x-z]+)
      |
      ([a-d]+)
""", re.X)

string = "ccxzaayzbbzz"

x = WORD_RE.findall(string)
x

CHUNK_RE = re.compile(fr"[{nonLetterRange}]")

string = "..aa"

match = CHUNK_RE.match(string)
match

# +
PART = r"""!"\#\$%\&\'\(\)\*\+,\-\./:;<=>\?@\[\]\{\}«»ʰʱʲʳʴʵʶʷʸʹʺʻʼʽʾʿˀˁ˂˃˄˅ˆˇˈˉˊˋˌˍˎˏːˑ˒˓˔˕˖˗˘˙˚˛˜˝˞˟ˠˡˢˣˤ˥˦˧˨˩˪˫ˬ˭ˮ˯˰˱˲˳˴˵˶˷˸˹˺˻˼˽˾˿̀́̂̃̄،؛\u061c\u061d؞؟‐‑‒–—―‖‗‘’‚‛“”„‟†‡•‣․ ‥…‧\u2028\u2029‹›⁅⁆⁌⁍﴾﴿"""

WORD_RE = re.compile(f"""
(
[^{PART}]+
)
|
(
[{PART}]+
)
""", re.X)
# -

string = 'إِلىٰأَكْثَرَ،إِلىٰ' 

# +
parts = []
first = True

for (letters, nonLetters) in WORD_RE.findall(string):
    print(f"PART {letters=} {nonLetters=}")
    if first:
        parts.append([nonLetters, letters, ""])
        first = False
    elif letters:
        parts.append(["", letters, ""])
    else:
        parts[-1][-1] += nonLetters
    if parts:
        parts[-1][-1] += " "

# -

for part in parts:
    print("PART")
    print(f"\t{part[0]=}")
    print(f"\t{part[1]=}")
    print(f"\t{part[2]=}")


