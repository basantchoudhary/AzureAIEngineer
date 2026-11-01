"""Mock Exam #2: 50 original items, 100 minutes, domain-weighted, two new case studies."""
from mock2_a import A
from mock2_b import B, CASES

main = [q for q in A if q["type"] != "solution"]
sols = [q for q in A if q["type"] == "solution"]
case = [q for q in B if q.get("case")]
rest = [q for q in B if not q.get("case")]
BANK = dict(id="m2", title="Mock Exam #2", minutes=100, mode="practice", v=1, cases=CASES, items=main + rest + case + sols)
