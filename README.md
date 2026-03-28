![Python 3.14](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white&labelColor=1D4ED8&color=0A2A7A)
![Purpose XAI](https://img.shields.io/badge/Purpose-XAI-orange?logo=openai&logoColor=white&labelColor=FB8C00&color=A85A00)
![Goal Multi-Obj](https://img.shields.io/badge/Goal-Multi--Obj-purple?logo=target&logoColor=white&labelColor=C026D3&color=6D1780)
![Teaching](https://img.shields.io/badge/Teaching-CSC591-red?logo=graduationcap&logoColor=white&labelColor=DC2626&color=7F1D1D)
![Deps 0](https://img.shields.io/badge/Deps-0-green?logo=checkmarx&logoColor=white&labelColor=00C853&color=006B29)
![LOC 300](https://img.shields.io/badge/LOC-300-yellow?logo=codecov&logoColor=white&labelColor=FDE047&color=C3A700)
![License](https://img.shields.io/badge/©_2026-timm-black?logo=github&logoColor=white&labelColor=24292e&color=000000&link=http://timm.fyi)
[![tests](https://github.com/timm/peek/actions/workflows/tests.yml/badge.svg)](https://github.com/timm/peek/tree/26mar)

# peek.py

## The Short Version

Every generation of AI got a new resource and changed accordingly.

- **More memory** → single-solution hill-climbers became genetic algorithms,
  mutating populations of candidates across a wide landscape.
- **More CPU** → local search with random restarts proved surprisingly
  competitive; exhaustive exploration beat clever operators.
- **Better data mining** → surrogate models let optimizers take cheap
  "peeks" at an approximate objective rather than evaluating every
  candidate against the expensive real one.
- **This code** → forget the surrogate. Just read the landscape directly.

## The Idea

Surrogate-based optimization (Bayesian optimization, Gaussian processes,
expected improvement) builds an approximate model of the objective, then
optimizes *that*. But optimizing an approximation of an approximation
compounds errors — especially early, when the surrogate is least reliable.

`peek.py` asks: what if the landscape itself is the model?

**Active learning without Bayes.** Keep a small elite set of the best
labeled examples seen so far. To pick the next example to label, find
the unlabeled point most similar to that elite — weighted by rank, so
the best example pulls hardest. No surrogate. No uncertainty estimate.
Just geometry.

**Decision trees without greedy search.** Instead of scanning all
thresholds to find the best split, sort rows by objective value, divide
into top and bottom halves, and find where the two halves differ. Split
candidates come from the midpoint between each column's central value in
each half. One candidate per column. Fast, stable, noise-resistant.

In both cases the landscape — the shape of the objective over the input
space — does the work that algorithms used to do.

## Why It Works

Real-world optimization landscapes (at least in software engineering)
are not random. Good solutions cluster. That cluster is detectable with
simple Euclidean geometry. Once you've found a few good examples, the
neighborhood around them is a better guide than any model you could fit
to them.

The surprise is not that this works. The surprise is how little geometry
you need.

## Usage

```
./peek.py --run          # active learning on default dataset
./peek.py --tree         # decision tree on default dataset
./peek.py --run path/to/file.csv
```
