import json, random, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from d12 import LESSONS as L12, QUESTIONS as Q12
from d345 import LESSONS345, QUESTIONS345

LESSONS = L12 + LESSONS345
QUESTIONS = Q12 + QUESTIONS345

# deterministic shuffle of options; remap answer and runner-up
def positions(seed):
    r = random.Random(seed); c = [0]*4
    for q in QUESTIONS:
        idx = list(range(4)); r.shuffle(idx); c[idx.index(q["answer"])] += 1
    return max(c) - min(c)
SEED = min(range(1, 400), key=positions)
rng = random.Random(SEED)
for q in QUESTIONS:
    idx = list(range(4)); rng.shuffle(idx)
    q["options"] = [q["options"][i] for i in idx]
    q["answer"] = idx.index(q["answer"]); q["runner"] = idx.index(q["runner"])

# ---- baselines: mechanical strategies must sit near chance (25%) ----
def rate(pick):
    return sum(1 for q in QUESTIONS if pick(q) == q["answer"]) / len(QUESTIONS)
longest = rate(lambda q: max(range(4), key=lambda k: (len(q["options"][k]), -k)))
shortest = rate(lambda q: min(range(4), key=lambda k: (len(q["options"][k]), k)))
pos = [sum(1 for q in QUESTIONS if q["answer"] == k) for k in range(4)]
def echo(q):
    stem = set(w.lower().strip(".,?'") for w in q["stem"].split() if len(w) > 3)
    return max(range(4), key=lambda k: len(stem & set(w.lower().strip(".,?'") for w in q["options"][k].split())))
echo_r = rate(echo)
spread = [max(len(o) for o in q["options"]) - min(len(o) for o in q["options"]) for q in QUESTIONS]
print(f"questions={len(QUESTIONS)} lessons={len(LESSONS)}")
print(f"pick-longest={longest:.0%} pick-shortest={shortest:.0%} most-stem-echo={echo_r:.0%} answer positions={pos} max length spread={max(spread)} chars")
fail = []
if longest > 0.35: fail.append("pick-longest too high")
if shortest > 0.35: fail.append("pick-shortest too high")
if max(pos) > len(QUESTIONS) * 0.4: fail.append("answer position skew")
EXEMPT = {"q11"}  # "always"/"never" are the literal require_approval values, present in two options
for q in QUESTIONS:
    if q["id"] in EXEMPT: continue
    for w in ("always", "never", "only", "which ensures"):
        o = q["options"][q["answer"]].lower()
        if f" {w} " in f" {o} " and not any(f" {w} " in f" {x.lower()} " for k, x in enumerate(q["options"]) if k != q["answer"]):
            fail.append(f"{q['id']}: tell word '{w}' only in the correct option")
print("VALIDATION:", "PASS" if not fail else fail)

tpl = open(os.path.join(os.path.dirname(__file__), "template.html")).read()
content = open(os.path.join(os.path.dirname(__file__), "content.html")).read()
data = "var LESSONS=" + json.dumps(LESSONS, ensure_ascii=False) + ";\nvar QUESTIONS=" + json.dumps(QUESTIONS, ensure_ascii=False) + ";"
out = tpl.replace("<!--CONTENT-->", content).replace("/*DATA*/", data).replace(" 🔒", " · locked")
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AI-103", "index.html"), "w").write(out)
print("written", len(out), "bytes")
