# ALignment of the Afifi and Lakhnawi editions of the Fusus

We have two versions of the Fusus text, obtained in wildly different ways:

* `AF` the Afifi edition, obtained via the OCR pipeline
* `LK` the Lakhnawi edition,
   obtained by reverse engineering a textual PDF with unusual fonts and private use characters.
   
The results of both attempts have been cleaned and enriched by Cornelis van Lit,
through visual inspection and manipulation in Pandas.

In this notebook, we align the results obtained by Cornelis.
The essential result is an alignment table where the words of the `LK` are brought into
correspondence with the words in `AF`.

A candidate tool to perform sequence alignment with is
[Collatex](https://collatex.net) by Ronald Haentjes-Dekker.
We experimented with it, see the [collatexAfLk notebook](collatexAfLk.ipynb),
but it took a very long time to run.

However, the two editions are very similar, with very few transpositions but a lot of OCR errors.

We use Text-Fabric.

The cleaned `LK` and `AF` are present in the TF resources `fususl` and `fususa`.
We then have each word precisely numbered in both version, and we also have a latin
transcription of the words, which eases the visual comparison of similar words.

It is not only that the author of this notebook (Dirk Roorda) is not trained to read Arabic,
it is also that the Arabaic letters change shape depending on their position in the word,
which makes a task like this needlessly complicated.

# Edit distance

We need a measure to estimate how similar words are.
A good measure is the *edit distance*, i.e. the amount of edit operations to change
one word into another.
Since one of the editions is the result of OCR, we expect (many) OCR errors,
and for this the concept of edit distance is useful.

However, we also need the slightly more refined notion of *ratio*, which takes the lengths
of the words into account. It roughly corresponds to proportion of the common part of the words
in relation to the totality of the words.
In other words, and edit distance of 2 between words of length 10 tells you that the words are rather similar,
their *ratio* is high. But the same edit distance between words of length 3 means that the words are very
different, their *ratio* is low.

The concepts *ratio* and *edit distance* can be computed by the
[Levenshtein algorithm](https://en.wikipedia.org/wiki/Levenshtein_distance),
which is implemented in the Python module `Levenshtein`.

You may have to

```
pip3 install python-Levenshtein
```

# The alignment table

The table itself is stored in the list `alignment`.
The elements of this list are tuples with a slot number in LK and a corresponding slot number in
AF and a measure of how well these slots correspond with each other.

Some words cannot be matched with the other source. In those cases the corresponding
member of the tuple is the empty string.

That means that the table becomes longer than each of the editions, and that it is not
trivial to locate a specific slot in the alignment list.

For that reason we maintain two indexes that map slot numbers the editions to 
positions in the alignment list.

# Alignment algorithm

We align the editions by walking through both of them in parallel and performing
comparison actions at each point.

Comparison actions may succeed, in which case we jump in both sources to the first
point after the compared material.

Comparison actions can also fail, in which case we stop the process prematurely
and print the situation around the point of failure.

## Comparison

We do not only compare single words, we also try out short sequences of words at both sides.
We do this because the editions do not always agree on word boundaries.

So, we need to compute whether $n$ consecutive words left are similar to $m$ consecutive words
right.

We set a boundary $C$ on the amount of words that we combine at each source.

We need to try out to al possible combinations, from simplest and shortest to longest and most complex.

Every combination can be characterized by $(n, m)$, where $n$ is the number of words on the left
and $m$ is the number of words on the right. $n$ and $m$ are in the range $1 \ldots C$.

Suppose $C = 3$, then we want to compare combinations in the following order:

combination|x
---|---
$(1, 1)$|--
$(1, 2)$|--
$(2, 1)$|--
$(2, 2)$|--
$(1, 3)$|--
$(3, 1)$|--
$(2, 3)$|--
$(3, 2)$|--
$(3, 3)$|--

In fact, we list all possible combinations and then sort them first by sum of the pair 
and then by decreasing difference of the pair.

We fix a `C` (called `COMBI`) and compute the sequence of combinations up front.

It turns out that 4 is a good value for this source.
3 is definitely too low.
5 is too high, because then the following is likely to happen.

Suppose on the left we have words A, BB, CCC, DDD, EEE and on the right we have BB, CCC, DDD, EEE, X.

The best alignment is to decide that A on the left is not matched with anything on the right, 
X on the left is not matched to anything on the left, and BB, CCC, DDD, EEE will be exact matches.

Buth when comparing combinations of length 5, we get the comparison

ABBCCCDDDEEE versus BBCCCDDDEEEX with distance and ratio:

```
left = "ABBCCCDDDEEE"
right = "BBCCCDDDEEEX"
```

```
distance(left, right)=2
ratio(left, right)=0.9166666666666666
```

whereas when we go no further than 4, we would get:

```
left = "ABBCCCDDD"
right = "BBCCCDDDEEE"
```

```
distance(left, right)=4
ratio(left, right)=0.8
```

The algorithm specifies limits in terms of distance and ratio to determine when a comparison succeeds or fails,
and as you see, the combination of 5 is much more likely to succeed than the combination of 4.

And we want it to fail in this case, because it is a suboptimal match.

## Similarity

We compute the similarity of words, and report if the words are similar with respect
to a given edit distance and ratio.

The two words match if their edit distance is at most the given edit distance
and their ratio is at least the given ratio.

## Comparing

Here we make a local comparison.

First we make a quick 1-1 comparison between the words in both editions at the current positions.
If that fails, we check whether the next word at both sides match.
If that fails, we try out all possible short combinations, using `findCombi` above.

If all fails, None is returned. In case of success, the alignment table is appended to and 
the next positions in both editions are returned.

## Looking up

If comparison fails, even after having tried all possible combinations of words, we are potentially stuck.

But before giving up, we can make a jump if we can match the current word left to a word right that is not far ahead.
Or vice versa.

The following function checks whether there are successful jumps within a specific region and within a given strictness.
Typically, this function is called with different strictnesses for different regions.
For example, first we want to try short jumps with moderate strictness, and if that fails, we try out longer
jumps with higher strictness.

Short jumps are tried out before long jumps, and we try the jumps in the left and right edition alternately.

If a jump is successful, the next position will be returned, and a `catchup` will be done for the
edition in which the jump has been made.
When there is no successful jump, None is returned.

The catchup is a bit complicated, because the comparison that led to the successful jump has already been appended
to the alignment table. So we have to pop that first (it could be multiple entries in case the comparison involved
a combination of words), and then we can do the catchup, and then we can push the comparison entries again.
We also need to update the indexes between slot numbers and the alignment table entries.

# Orchestrating

We can now define how we are going to orchestrate the comparisons that will build the alignment table.

First we define a function that does a single step or a limited number of steps,
starting at given positions in the editions.

This function will then be called from a big loop.

The comparison consists of checking out a number of things under several strictness conditions.
As soon as a check succeeds, we perform the actions associated with that, and continue to the next iteration.

1. First of all: is there a special case defined for this point? If so, follow its instructions.
2. Do left and right compare as equal, give or take an edit distance of 1?
   Comparing involves not only comparing the single words at the current positions,
   but also trying out a number of word combinations at the current point.
3. Do left and right compare as equal, give or take an edit distance of 2?
4. Do left and right compare as equal, give or take an edit distance of 3?
5. Do left and right compare as equal, give or take a similarity ratio of 0.5?
   This is rather lenient for long words.
6. If all comparisons have failed so far, it is time to jump forward:
7. is there a match within 5 words, give or take a similarity ratio of 0.6?
   This is rather coarse, but we stay in the neighbourhood.
8. Is there a match between 6 and 10 words, give or take a similarity ratio of 0.8?
   We are drifting further from home, so we pose stricter requirements to the match.
9. Is there an exact match between and 1000 words?
   When looking so far forward, we do not trust matches that are not 100%.
   
Clearly, there is no guarantee that any of these will be successfull.
When it fails, we have to inspect the failure and see what happens there.
There are basically three solutions to overcome such roadblocks

1. Define a special case. Easy. Until it appears that too many special cases are needed.
2. Tweak the strictness levels in the algorithm. Easy, but risky. Things that went well
   may now go awry. It is not only about preventing the roadblocks, but also maintaining
   the quality of the output alignment table.
3. Change the orchestration: change the order of comparing and jumping, introduce more strictness levels,
   try more or less combinations. Invent new criteria for comparison.
   This is really difficult. The present orchestration is the result of quite some trial and error.

# The diff function

Finally we can write up the `doDiff` function which loops through the editions and produces an alignment table.

But you can also run call it for a specific pair of positions and a limited number of steps.
Handy for debugging and tweaking the decision parameters.

You specify the start positions by means of the slot numbers in the LK and AF.
You can specify the number of steps, or pass -1 in order to continue to the end.

And if you pass `show=True`, the alignment table will be printed after completion.
Only do this if you run a limited number of steps.

# Check the result

We must make sure that the algorithm has not skipped material, duplicated material, or put material in the wrong order.

We examine the alignment list and check that we have all slot numbers of LK in the right order and all slot numbers of AF idem.

# Define the special cases

The special cases below are the result of trial and error.

The keys are the LK slot numbers where the cases must be applied.

The values are the amount of words in LK and in AF that will bee identified.

So `1000: (3, 4)` means that at slot position 1000 in LK we take 3 consecutive words and identify it with
4 consecutive words in AF at the current position there.

When you read the alignment table (by `printDiff` or `printLines`)
you see the information on the basis of which you could define a special case.

# Quality check

How did the alignment perform?
It did complete, but what have we got?
It could be just garbage.

## Sanity

First of all we need to know whether all words of both LF and LK occur left and right, without gaps and duplications
and in the right order. We check that.

## Agreement

We provide information on about the agreement in both sources.
How many words are there for which there is no alignment inb the other edition?

And how close are the words for which an alignment could be established?

Note that there are two reasons for bad agreement results:

1. The editions are really very different
2. The alignment is not optimal and fails to align many words that would have matched under another
   alignment strategy.
   
## Bad stretches

Are there long stretches of poorly matching alignments?
We are going to examine them.

If they contain many cases of a left missing word and many cases of a right missing word,
they are suspect, because they might contain largely the same words, but the algorithm has failed
to spot them.

We show all suspect bad stretches.

The remaining stretches are benign.
We show examples of benign bad strectches (at most three examples per size).


