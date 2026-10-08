"""Mock Exam #1: 50 original items, 100 minutes, domain-weighted, two case studies."""
from mock1_a import A
from mock1_b import B, CASES

main = [q for q in A if q["type"] != "solution"]
sols = [q for q in A if q["type"] == "solution"]
case = [q for q in B if q.get("case")]
rest = [q for q in B if not q.get("case")]
BANK = dict(id="m1", title="Mock Exam #1", minutes=100, mode="practice", v=2, cases=CASES, items=main + rest + case + sols)
