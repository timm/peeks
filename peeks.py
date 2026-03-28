#!/usr/bin/env python3 -B
from __future__ import annotations
import os, re, random, sys, bisect, math
from pathlib import Path
from random import random as rand, choices, choice, sample, shuffle
from math import log, log2, exp, sqrt, pi

class obj(dict):
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__
  __repr__ = lambda i : o(i)

the = obj(
  decs=2, seed=1, p=2, few=128, budget=30, K=5, treeWidth=30, check=5,
  file= Path.home() / "gits/moot/optimize/misc/auto93.csv")

#--------------------------------------------------------------------
def Num(txt: str = "", at: int = 0):
  return obj(it=Num, txt=txt, at=at, n=0, mu=0, m2=0, sd=0, heaven=txt[-1:] != "-")

def Sym(txt: str = "", at: int = 0): 
  return obj(it=Sym, txt=txt, at=at, n=0, has={})

def Col(txt: str = "", at: int = 0): 
  return (Num if txt[0].isupper() else Sym)(txt, at) 

def Cols(names: list[str]):
  all = [Col(txt, j) for j, txt in enumerate(names)]
  return obj(it=Cols, names=names, all=all,
             klass = next((c for c in all if c.txt[-1] == "!"), None),
             xs    = [c for c in all if c.txt[-1] not in "+-!X"],
             ys    = [c for c in all if c.txt[-1]     in "+-!"])

def Data(src=None):
  src = iter(src or {})
  return adds(src, obj(it=Data, rows=[], mids=None, cols=Cols(next(src))))

def clone(d,rows=None):
  return Data([d.cols.names] + (rows or []))

#--------------------------------------------------------------------
def adds(src,i=None):
  i = i or Num(); [add(i,v) for v in src]; return i

def add(i: Data|Col, v: Any, w=1) -> Any:
  if v != "?":
    if i.it is Data:
      i.mid = None
      [add(c, v[c.at], w) for c in i.cols.all] 
      i.rows += [v]
    else:
      i.n += w
      if  i.it is Sym: i.has[v] = w + i.has.get(v, 0)
      else:
        delta = v - i.mu
        i.mu += w * delta / i.n
        i.m2 += w * delta * (v - i.mu)
        i.sd  = 0 if i.n < 2 else sqrt(max(0, i.m2) / (i.n - 1))
  return v

#--------------------------------------------------------------------
def mids(d:Data):
  d.mids = d.mids or [mid(c) for c in d.cols.all]
  return d.mids

def mid(i: Num|Sym):
  return max(i.has, key=i.has.get) if i.it is Sym else i.mu

def spread(i: Num|Sym):
  if i.it is Num: return i.sd 
  return -sum(p*log2(p) for v in i.has.values() if (p:=v/i.n) > 0) 

def norm(i, v):
  if v=="?": return v
  z = (v - i.mu) / (i.sd + 1e-32)
  return 1 / (1 + exp(-1.7*max(-3, min(3,z))))

def minkowski(items: Iterable[Qty]) -> float:
  tot, n = 0, 1e-32
  for item in items: tot, n = tot + item**the.p, n + 1
  return (tot/n) ** (1/the.p)

def disty(d: Data, r: Row) -> float:
  return minkowski(abs(norm(c, r[c.at]) - c.heaven) for c in d.cols.ys)

def distx(d: Data, r1: Row, r2: Row) -> float:
  return minkowski(aha(c, r1[c.at], r2[c.at]) for c in d.cols.xs)

def aha(i: Col, u: Any, v: Any) -> float:
  if u == v == "?": return 1
  if i.it is Sym: return u != v
  u, v = norm(i, u), norm(i, v)
  u = u if u != "?" else (0 if v > 0.5 else 1)
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)

#--------------------------------------------------------------------
def Tree(oracle, rows, stop=4):
  def splitter(c, top, bot):
    a, b = mid(top.cols.all[c.at]), mid(bot.cols.all[c.at])
    return (a + b) / 2 if c.it is Num else a

  def partition(c, v, rows):
    left, right, yl, yr = [], [], Num(), Num()
    for r in rows:
      if   r[c.at] == "?": right.append(r)
      elif (r[c.at] <= v if c.it is Num else r[c.at] == v):
        left.append(r);  add(yl, disty(oracle, r))
      else:
        right.append(r); add(yr, disty(oracle, r))
    sl = f"{c.txt} <= {o(v)}" if c.it is Num else f"{c.txt} == {o(v)}"
    sr = f"{c.txt} >  {o(v)}" if c.it is Num else f"{c.txt} != {o(v)}"
    return left, right, yl, yr, sl, sr

  def grow(here, pre=""):
    here.pre  = pre
    here.kids = []
    if len(here.rows) > stop*2:
      rs = sorted(here.rows, key=lambda r: disty(oracle, r))
      best, bv, bl, br, sl, sr = None, 1e32, None, None, None, None
      for c in oracle.cols.xs:
        v= splitter(c, clone(oracle, rs[:len(rs)//2]),
                       clone(oracle, rs[len(rs)//2:]))
        l,r,yl,yr,s1,s2 = partition(c, v, here.rows)
        if l and r:
          w = spread(yl)*yl.n + spread(yr)*yr.n
          if w < bv: best,bv,bl,br,sl,sr = (c,v),w,l,r,s1,s2
      if best:
        here.cut  = best
        here.kids = [grow(clone(oracle,bl), sl),
                     grow(clone(oracle,br), sr)]
    return here
  return grow(clone(oracle, rows))

def treeLeaf(t, row):
  if not t.kids: return t
  c, v = t.cut
  here = row[c.at]
  ok   = here != "?" and (here <= v if c.it is Num else here == v)
  return treeLeaf(t.kids[0 if ok else 1], row)

def treeShow(oracle, t, lvl=0):
  label = '|  '*(lvl-1) + t.pre
  if not t.kids:
    mu = adds(disty(oracle,r) for r in t.rows).mu
    print(f"{label:<{the.treeWidth}} n={len(t.rows):3d}  y={mu:.2f}")
  else:
    print(f"{label}")
  for k in t.kids: treeShow(oracle, k, lvl+1)
 
#--------------------------------------------------------------------
def run(oracle,rows, K=5, budget=30, 
        label=lambda d,r: r):
  def Y(r):     return disty(oracle, label(oracle,r))
  def score(u): return sum(distx(model,unlab[u],model.rows[i])/(i+1)
                           for i in range(K))
  random.shuffle(rows)
  unlab = rows[K:][:the.few]
  model = clone(oracle, rows[:K])
  model.rows.sort(key=Y)
  for j in range(budget-K-the.check):
    if not unlab: break
    add(model, unlab.pop(min(range(len(unlab)), key=score)))
    model.rows = sorted(model.rows, key=Y)[:budget]
  return model
   
#--------------------------------------------------------------------
def o(it: Any) -> str:
  of = isinstance
  if callable(it): return it.__name__
  if of(it,float): return f"{it:.{the.decs}f}"
  if of(it,dict): return "{"+ ", ".join(f"{k}={o(v)}" for k,v in it.items())+"}"
  if of(it,list): return "{"+", ".join(map(o, it))+"}"
  return str(it)

def cli() -> None:
  args = [thing(x) for x in sys.argv[1:]]
  while args:
    random.seed(the.seed)
    k = re.sub(r"^-+", "", args.pop(0))
    if fn := globals().get(f"test_{k}"): 
      fn(*[args.pop(0) for _ in fn.__annotations__ if args])
    elif k in the: 
      the[k] = args.pop(0)

def thing(txt: str) -> Atom:
  txt = txt.strip()
  b = lambda s: {"true": 1, "false": 0}.get(s.lower(), s)
  for f in [int, float, b]:
    try: return f(txt)
    except ValueError: pass

def clean(s): return  s.partition("#")[0].split(",")

def csv(f: str, clean=clean):
  with open(f, encoding="utf-8") as file:
    for s in file:
      r = clean(s)
      if any(x.strip() for x in r): 
        yield [thing(x) for x in r]     

#--------------------------------------------------------------------
def test_the(): print(o(the))

def test_csv(file=the.file):
  for row in list(csv(file))[::30]: print(row)

def test_data(file=the.file):
  d = Data(csv(file))
  [print("x",x) for x in d.cols.xs]
  [print("y",y) for y in d.cols.ys]

def wins(d):
  d.rows.sort(key=lambda r: disty(d,r))
  lo = disty(d, d.rows[0])
  md = disty(d, d.rows[len(d.rows)//2])
  return lambda r: int(100*(1 - (disty(d,r) - lo) / (md - lo + 1e-32)))

def test_run(file: str = the.file):
  d   = Data(csv(file))
  W   = wins(d)
  best = [run(d, d.rows, K=the.K, budget=the.budget).rows[0]
          for _ in range(20)]
  stats = adds(W(r) for r in best)
  print(int(stats.mu), int(stats.sd))

def test_guess(file: str = the.file):
  d    = Data(csv(file))
  W    = wins(d)
  stats = Num()
  for _ in range(20):
    random.shuffle(d.rows)
    n = len(d.rows) // 2
    t = Tree(d, d.rows[:n])
    add(stats, W(max(sorted(d.rows[n:],
                key=lambda r: W(treeLeaf(t,r).rows[0]),
                reverse=True)[:the.check], key=W))) 
  print(int(stats.mu))
 
#--------------------------------------------------------------------
if __name__ == "__main__": cli()
