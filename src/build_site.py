"""Build the AzureAIEngineer site.  Run:  python3 src/build_site.py"""
import html, json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from d12 import LESSONS as L12
from d345 import LESSONS345
import bank_d1, bank_d2, lessons_d1, lessons_d2, mock1, dom3, dom4, dom5, model_guide, tco_page

LESSONS = [l for l in L12 + LESSONS345]
E = html.escape
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">'

def md(s):
    s = E(s)
    s = re.sub(r"`([^`]+)`", r'<span class="k">\1</span>', s)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)

def page(title, rel, body, extra_head="", scripts=""):
    nav = [("Home", "index.html"), ("Study guide", "AI-103/index.html"), ("D1", "D1-Plan-Manage/index.html"), ("D2", "D2-GenAI-Agents/index.html"), ("D3", "D3-Vision/index.html"), ("D4", "D4-Text/index.html"), ("D5", "D5-Extraction/index.html"), ("Choose a model", "Choose-Model/index.html"), ("Agent TCO", "Agent-TCO/index.html"), ("Mock #1", "Mock-Exam-1/index.html")]
    links = "".join(f'<li><a href="{rel}{h}">{t}</a></li>' for t, h in nav)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>{FONTS}<link rel="stylesheet" href="{rel}assets/site.css">{extra_head}</head>
<body><div class="bar"><div class="bar-in"><a class="brand" href="{rel}index.html">Azure AI Engineer · AI-103</a><ul class="nav">{links}</ul></div></div>
<main>{body}</main>
<footer>Original study material for Microsoft exam AI-103. Not affiliated with Microsoft. Practice items are original and are not real exam questions. Facts checked against Microsoft Learn on 8 October 2026.</footer>
{scripts}</body></html>"""

# ---------- validation ----------
def best_seed(bank):
    """Pick the shuffle seed that balances answer positions and keeps length strategies near chance."""
    import copy
    def score(seed):
        b = copy.deepcopy(bank); r = random.Random(seed); sg = []
        for q in b["items"]:
            if q["type"] in ("single", "multi"):
                idx = list(range(len(q["options"]))); r.shuffle(idx); q["options"] = [q["options"][i] for i in idx]
                if q["type"] == "single": q["answer"] = idx.index(q["answer"]); sg.append(q)
        pos = [sum(q["answer"] == k for q in sg) for k in range(4)]
        lo = sum(max(range(4), key=lambda k: (len(q["options"][k]), -k)) == q["answer"] for q in sg)
        sh = sum(min(range(4), key=lambda k: (len(q["options"][k]), k)) == q["answer"] for q in sg)
        return (max(pos) - min(pos)) * 3 + max(lo, sh)
    return min(range(1, 600), key=score)

def validate(bank):
    rng = random.Random(best_seed(bank)); fail = []
    singles = [q for q in bank["items"] if q["type"] == "single"]
    for q in bank["items"]:
        if q["type"] in ("single", "multi"):
            idx = list(range(len(q["options"]))); rng.shuffle(idx)
            q["options"] = [q["options"][i] for i in idx]
            if q["type"] == "single": q["answer"] = idx.index(q["answer"])
            else: q["answer"] = sorted(idx.index(a) for a in q["answer"])
            if q.get("runner") is not None: q["runner"] = idx.index(q["runner"])
    def rate(pick): return sum(pick(q) == q["answer"] for q in singles) / max(1, len(singles))
    longest = rate(lambda q: max(range(4), key=lambda k: (len(q["options"][k]), -k)))
    shortest = rate(lambda q: min(range(4), key=lambda k: (len(q["options"][k]), k)))
    pos = [sum(q["answer"] == k for q in singles) for k in range(4)]
    if max(pos) - min(pos) > max(2, len(singles) // 4): fail.append(f"answer positions skewed {pos}")
    if longest > .35: fail.append(f"pick-longest {longest:.0%}")
    if shortest > .35: fail.append(f"pick-shortest {shortest:.0%}")
    for q in bank["items"]:
        if q["type"] == "multi":
            right = [len(q["options"][a]) for a in q["answer"]]; wrong = [len(o) for k, o in enumerate(q["options"]) if k not in q["answer"]]
            if min(right) > max(wrong): fail.append(f"{q['id']}: correct options are the longest")
        if q["type"] == "yesno":
            ys = sum(s["answer"] for s in q["statements"])
            if ys in (0, len(q["statements"])): fail.append(f"{q['id']}: all statements share one answer")
    sol = [q["answer"] for q in bank["items"] if q["type"] == "solution"]
    if sol and (all(sol) or not any(sol)): fail.append("solution series all one answer")
    kinds = {}
    for q in bank["items"]: kinds[q["type"]] = kinds.get(q["type"], 0) + 1
    print(f"{bank['id']}: {len(bank['items'])} items {kinds} · singles pick-longest={longest:.0%} pick-shortest={shortest:.0%} positions={pos}")
    print("  VALIDATION:", "PASS" if not fail else fail)
    return not fail

# ---------- pages ----------
def lessons_html(d):
    out = []
    for l in [x for x in LESSONS if str(x["d"]) == str(d)]:
        facts = "".join(f"<li>{md(f)}</li>" for f in l["facts"])
        traps = "".join(f"<li>{md(f)}</li>" for f in l.get("traps", []))
        code = f'<div class="box"><h4>In code</h4><pre class="code">{E(l["code"])}</pre></div>' if l.get("code") else ""
        src = " · ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(u.replace("https://learn.microsoft.com/en-us/", "learn: "))}</a>' for u in l.get("src", []))
        out.append(f'''<details class="tile" id="L-{l["id"]}"><summary><b>{md(l["title"])}</b> <span class="note">· {md(l["skill"])}</span></summary>
<div style="display:grid;gap:10px;margin-top:10px"><p class="lede" style="font-size:16.5px">{md(l["plain"])}</p>
<div class="tiles"><div class="box"><h4>Key facts</h4><ul>{facts}</ul></div>{code}</div>
{f'<div class="box" style="border-color:var(--bad)"><h4 style="color:var(--bad)">Exam traps</h4><ul>{traps}</ul></div>' if traps else ''}
{f'<div class="frame"><b>Hands-on:</b> {md(l["lab"])}</div>' if l.get("lab") else ''}
<p class="note">Source: {src}</p></div></details>''')
    return "\n".join(out)

def build():
    ok = validate(bank_d1.BANK)
    os.makedirs(os.path.join(ROOT, "D1-Plan-Manage"), exist_ok=True)
    open(os.path.join(ROOT, "D1-Plan-Manage", "bank.js"), "w").write("window.BANK=" + json.dumps(bank_d1.BANK, ensure_ascii=False) + ";")
    practice = page("D1 practice · AI-103", "../", f'''<div class="eyebrow"><b>Domain 1 · 25–30%</b>Plan and manage an Azure AI solution</div>
<h1>D1 practice <span>bank</span></h1>
<p class="lede">{len(bank_d1.BANK["items"])} original items in the exam's formats: choose one, choose two, yes/no statements, put in order, complete the code, and a problem/solution series. <em>Practice mode explains each answer; exam mode is timed and scores at the end.</em></p>
<p class="note">In the real exam, problem/solution items can't be revisited once answered; exam mode here locks them the same way. Microsoft Learn is open during the real exam, so each explanation links the page where the answer lives.</p>
<div id="bank"></div>''', scripts='<script src="bank.js"></script><script src="../assets/practice.js"></script>')
    open(os.path.join(ROOT, "D1-Plan-Manage", "practice.html"), "w").write(practice)
    hub = page("D1 lessons · AI-103", "../", f'''<div class="eyebrow"><b>Domain 1 · 25–30%</b>Plan and manage an Azure AI solution</div>
<h1>Plan and <span>manage</span></h1>
<p class="lede">Choosing models and services, setting up Foundry, managing and securing it, and responsible AI. <em>Read a lesson, then test it in the practice bank.</em></p>
<div class="tiles"><a class="tile" href="practice.html"><span class="lv">Practice</span><b>D1 practice bank →</b><p>{len(bank_d1.BANK["items"])} items, all formats, practice or timed exam mode.</p></a>
<a class="tile" href="../Labs/week-01-keyless-call.html"><span class="lv">Lab</span><b>Week 1 lab →</b><p>Keyless call to a Foundry model, with a break-it exercise.</p></a></div>
{cards_html(lessons_d1, "d1")}
<h2>All D1 lessons</h2>
<div style="display:grid;gap:10px">{lessons_html(1)}</div>''')
    open(os.path.join(ROOT, "D1-Plan-Manage", "index.html"), "w").write(hub)
    return ok

def cards_html(mod, prefix):
    out = []
    for cid, cname in mod.CLUSTERS:
        cards = [c for c in mod.CARDS if c["c"] == cid]
        items = []
        for c in cards:
            steps = "".join(f"<li>{md(x)}</li>" for x in c["steps"])
            facts = "".join(f"<li>{md(x)}</li>" for x in c["facts"])
            traps = "".join(f"<li>{md(x)}</li>" for x in c["traps"])
            checks = " · ".join(f'<a href="practice.html#Q-{q}">{q}</a>' for q in c["checks"])
            t = c.get("table")
            table = ('<div class="tbl"><table><thead><tr>' + "".join(f"<th>{E(h)}</th>" for h in t["head"]) + '</tr></thead><tbody>' +
                     "".join("<tr>" + "".join(f"<td>{md(x)}</td>" for x in r) + "</tr>" for r in t["rows"]) + '</tbody></table></div>') if t else ""
            items.append(f'''<article class="card" id="C-{c["id"]}"><header><span class="cid">{c["id"]}</span><h3>{md(c["title"])}</h3></header>
<p class="one">{md(c["one"])}</p>
<div class="bridge"><b>From CCA-F:</b> {md(c["bridge"])}</div>
<div class="cgrid"><div class="box"><h4>How it works</h4><ol>{steps}</ol></div><div class="box"><h4>Must know</h4><ul>{facts}</ul></div></div>
{table}<div class="box trapbox"><h4>Traps</h4><ul>{traps}</ul></div>
<p class="note">Check yourself: {checks} · <a href="{E(c["src"])}" target="_blank" rel="noopener">Microsoft Learn</a></p></article>''')
        out.append(f'<section class="cluster"><h2><span class="cl">{cid}</span>{E(cname)}</h2>{"".join(items)}</section>')
    return "\n".join(out)

def build_domain2():
    validate(bank_d2.BANK)
    d = os.path.join(ROOT, "D2-GenAI-Agents"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "bank.js"), "w").write("window.BANK=" + json.dumps(bank_d2.BANK, ensure_ascii=False) + ";")
    n = len(bank_d2.BANK["items"])
    open(os.path.join(d, "practice.html"), "w").write(page("D2 practice · AI-103", "../", f'''<div class="eyebrow"><b>Domain 2 · 30–35%</b>Implement generative AI and agentic solutions</div>
<h1>D2 practice <span>bank</span></h1>
<p class="lede">{n} original items in the exam's formats. <em>Practice mode explains each answer; exam mode is timed and scores at the end.</em></p>
<p class="note">Problem/solution items lock once answered in exam mode, as in the real exam. Each explanation links the Microsoft Learn page where the answer lives.</p>
<div id="bank"></div>''', scripts='<script src="bank.js"></script><script src="../assets/practice.js"></script>'))
    open(os.path.join(d, "index.html"), "w").write(page("D2 lessons · AI-103", "../", f'''<div class="eyebrow"><b>Domain 2 · 30–35%</b>Implement generative AI and agentic solutions</div>
<h1>Generative AI <span>and agents</span></h1>
<p class="lede">The biggest domain, and the one closest to CCA-F. <em>Each card says what you already know from CCA-F, then the Azure detail the exam tests.</em></p>
<div class="frame"><b>How the exam asks:</b> about 80% of questions are Azure-specific (which service, setting, role, SDK call, or GA vs preview) and about 20% are concept-led. CCA-F gives you the why; these cards give you Azure's names, defaults, limits and traps.</div>
<div class="tiles"><a class="tile" href="practice.html"><span class="lv">Practice</span><b>D2 practice bank →</b><p>{n} items, all formats, practice or timed exam mode.</p></a></div>
{cards_html(lessons_d2, "d2")}'''))

def build_lab():
    code = open(os.path.join(ROOT, "skeletons", "01-keyless-call", "main.py")).read()
    def brk(n, title, do, see, why, q):
        return f'<div class="box"><h4>Break it {n} · {title}</h4><p><b>Do:</b> {do}</p><p><b>You will see:</b> {see}</p><p><b>Why it matters for the exam:</b> {why}</p><p class="note">Practice: <a href="../D1-Plan-Manage/practice.html#Q-{q}">{q}</a></p></div>'
    body = f'''<div class="eyebrow"><b>Lab · Week 1</b>Plan and manage · Foundry foundations</div>
<h1>A keyless call to a <span>Foundry model</span></h1>
<p class="lede">Create a project, deploy a small model, and call it from Python with no API key. <em>Then break it four ways, the ways the exam asks about.</em></p>
<div class="tiles">
<div class="tile"><span class="lv">Time</span><b>45 minutes</b><p>Portal setup, one Python script, four break-it exercises.</p></div>
<div class="tile"><span class="lv">Cost</span><b>A few cents</b><p>Pay-per-token on a small model. Delete the resource group afterwards.</p></div>
<div class="tile"><span class="lv">Subscription</span><b>Pay-as-you-go needed</b><p>Free-trial subscriptions have zero model quota. Upgrading to pay-as-you-go unlocks it and keeps the free credit.</p></div>
<div class="tile"><span class="lv">No subscription?</span><b>Read along</b><p>Every step shows the expected result, so you can follow without running it.</p></div>
</div>
<h2>Steps</h2>
<div class="box"><ul>
<li><b>1.</b> In the Foundry portal (ai.azure.com), create a project. This creates a Foundry resource with the project inside it.</li>
<li><b>2.</b> Deploy <span class="k">gpt-5-mini</span> with the <b>Global Standard</b> deployment type.</li>
<li><b>3.</b> In the project's Access control (IAM), assign yourself <b>Foundry User</b>. Note the least-privilege choice: not Owner, not Azure AI Developer.</li>
<li><b>4.</b> Copy the project endpoint: <span class="k">https://&lt;resource&gt;.services.ai.azure.com/api/projects/&lt;project&gt;</span>.</li>
<li><b>5.</b> On your machine: <span class="k">pip install "azure-ai-projects&gt;=2.3" azure-identity openai</span>, then <span class="k">az login</span>, then set <span class="k">PROJECT_ENDPOINT</span> and <span class="k">MODEL_DEPLOYMENT</span>.</li>
<li><b>6.</b> Run the script below.</li></ul></div>
<pre class="code">{E(code)}</pre>
<div class="box"><h4>Expected output (illustrative; wording varies run to run)</h4><pre class="code">Rear-end collision in Pune on 6 Oct; no injuries; bumper and tail light damaged.
Third party admitted fault; photos are on file.

[tokens] input=74 output=152</pre><p class="note">Output tokens include the model's reasoning tokens, which are billed as output.</p></div>
<h2>Break it on purpose</h2>
<div class="tiles">
{brk(1, "Remove your role", "In IAM, remove your Foundry User assignment and run again (role changes can take a few minutes).", "an HTTP 403 permission error for your identity.", "keyless access is only as good as the role behind it; Foundry User is the least privilege for building.", "d1-q1")}
{brk(2, "Use the old length parameter", "Replace max_output_tokens=300 with max_tokens=300.", "an HTTP 400 error: the parameter isn't supported for this model.", "reasoning models reject max_tokens and temperature; the Responses API uses max_output_tokens.", "d1-c1")}
{brk(3, "Use an API key instead", "Create the client with the resource key instead of DefaultAzureCredential, then try to create an agent or run an evaluation.", "model calls may work, but agents and evaluations fail: they require Entra ID.", "keys grant full access with no role scoping, and Foundry's agent and evaluation features don't accept them.", "d1-y2")}
{brk(4, "Hit the rate limit", "Lower the deployment's TPM to the minimum and send 30 requests in parallel.", "some requests return HTTP 429 with a Retry-After value.", "a 429 means wait and back off; then check quota per model and deployment type.", "d1-o1")}
</div>
<h2>Clean up</h2>
<div class="frame">Delete the resource group that holds the Foundry resource. Deployments and quota are released with it.</div>'''
    os.makedirs(os.path.join(ROOT, "Labs"), exist_ok=True)
    open(os.path.join(ROOT, "Labs", "week-01-keyless-call.html"), "w").write(page("Week 1 lab · AI-103", "../", body))

def build_mock1():
    b = mock1.BANK; ok = validate(b)
    stems = [len(q["stem"].split()) for q in b["items"] if not q.get("case") and q["type"] not in ("yesno", "solution")]
    case_words = {k: len(" ".join(x for t in c["tabs"] for x in t["items"]).split()) for k, c in b["cases"].items()}
    lvl = sum(stems) / len(stems) >= 40 and min(stems) >= 35 and min(case_words.values()) >= 700
    print(f"  EXAM LEVEL: stem mean {sum(stems)/len(stems):.0f} min {min(stems)} · case words {case_words} →", "PASS" if lvl else "FAIL")
    ok = ok and lvl
    d = os.path.join(ROOT, "Mock-Exam-1"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "bank.js"), "w").write("window.BANK=" + json.dumps(b, ensure_ascii=False) + ";")
    dom = {}
    for q in b["items"]: k = q["skill"].split(" ·")[0]; dom[k] = dom.get(k, 0) + 1
    rows = "".join(f"<tr><td><b>{k}</b></td><td>{v}</td></tr>" for k, v in sorted(dom.items()))
    open(os.path.join(d, "index.html"), "w").write(page("Mock Exam #1 · AI-103", "../", f'''<div class="eyebrow"><b>Mock exam</b>AI-103 · full length</div>
<h1>Mock Exam <span>#1</span></h1>
<p class="lede">{len(b["items"])} original items in 100 minutes, weighted like the real exam, with two case studies and a problem/solution series. <em>It opens in practice mode: each answer and its explanation show as soon as you answer. For a real timed run, switch to exam mode, which hides answers until you finish.</em></p>
<div class="tbl"><table><thead><tr><th>Domain</th><th>Items</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">As in the real exam: problem/solution items lock once answered, and each correct selection in a yes/no or code item is worth one point. Scores are scaled to 1000; 700 passes. Switch to practice mode for explanations as you go. These are original questions, not real exam content.</p>
<div id="bank"></div>''', scripts='<script src="bank.js"></script><script src="../assets/practice.js"></script>'))
    return ok

DOMS = [(dom3, "D3-Vision", 3, "10–15%", "Implement computer vision solutions", "Computer <span>vision</span>",
         "Generate and edit images and video, understand images with vision models and Content Understanding, and keep it safe. <em>CCA-F overlap is small here (about 20%): most cards are marked New for you.</em>"),
        (dom4, "D4-Text", 4, "10–15%", "Implement text analysis solutions", "Text <span>analysis</span>",
         "Structured outputs, Azure Language, Translator and Speech. <em>The traps are retirement dates and look-alike names (custom speech vs custom voice).</em>"),
        (dom5, "D5-Extraction", 5, "10–15%", "Implement information extraction solutions", "Information <span>extraction</span>",
         "Azure AI Search pipelines and queries, knowledge bases for agents, and document extraction. <em>Closest to CCA-F RAG, with Azure's names for every stage.</em>")]

def build_dom(mod, folder, n, w, full, h1, lede):
    ok = validate(mod.BANK)
    d = os.path.join(ROOT, folder); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "bank.js"), "w").write("window.BANK=" + json.dumps(mod.BANK, ensure_ascii=False) + ";")
    k = len(mod.BANK["items"]); ey = f'<div class="eyebrow"><b>Domain {n} · {w}</b>{full}</div>'
    open(os.path.join(d, "practice.html"), "w").write(page(f"D{n} practice · AI-103", "../", f'''{ey}
<h1>D{n} practice <span>bank</span></h1>
<p class="lede">{k} original items in the exam's formats. <em>Practice mode explains each answer; exam mode is timed and scores at the end.</em></p>
<p class="note">Problem/solution items lock once answered in exam mode, as in the real exam. Each explanation links the Microsoft Learn page where the answer lives.</p>
<div id="bank"></div>''', scripts='<script src="bank.js"></script><script src="../assets/practice.js"></script>'))
    open(os.path.join(d, "index.html"), "w").write(page(f"D{n} lessons · AI-103", "../", f'''{ey}
<h1>{h1}</h1>
<p class="lede">{lede}</p>
<div class="tiles"><a class="tile" href="practice.html"><span class="lv">Practice</span><b>D{n} practice bank →</b><p>{k} items, all formats, practice or timed exam mode.</p></a></div>
{cards_html(mod, f"d{n}")}'''))
    return ok

def build_model_guide():
    d = os.path.join(ROOT, "Choose-Model"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page("Choose a model · AI-103", "../", model_guide.body(), extra_head="<style>" + model_guide.CSS + "</style>"))

def build_tco():
    d = os.path.join(ROOT, "Agent-TCO"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page("Agent TCO · AI-103", "../", tco_page.BODY, extra_head="<style>" + tco_page.CSS + "</style>", scripts="<script>" + tco_page.JS + "</script>"))

def build_home():
    n = len(bank_d1.BANK["items"])
    def t(href, lv, title, desc, live=True):
        tag = '' if live else ' <span class="chip">coming</span>'
        return (f'<a class="tile" href="{href}">' if live else '<div class="tile" style="opacity:.6">') + f'<span class="lv">{lv}</span><b>{title}{tag}</b><p>{desc}</p>' + ('</a>' if live else '</div>')
    body = f'''<div class="eyebrow"><b>Azure AI Engineer</b>Microsoft exam AI-103</div>
<h1>Pass <span>AI-103</span>, and know Azure AI for real</h1>
<p class="lede">Study material for <b>AI-103: Developing AI Apps and Agents on Azure</b>. <em>Lessons, exam-format practice, timed mocks and hands-on labs.</em></p>
<div class="tbl"><table><thead><tr><th>The exam</th><th></th></tr></thead><tbody>
<tr><td><b>Certification</b></td><td>Azure AI Apps and Agents Developer Associate (replaced AI-102, retired 30 June 2026)</td></tr>
<tr><td><b>Format</b></td><td>Typically 40–60 questions, 100 minutes; pass mark 700; Python</td></tr>
<tr><td><b>Question types</b></td><td>Multiple choice, multiple response, drag and drop, hot area, build list, case studies, problem/solution sets (no going back)</td></tr>
<tr><td><b>Open book</b></td><td>Microsoft Learn is available during the exam (not Q&amp;A or practice assessments); the clock keeps running</td></tr>
<tr><td><b>Renewal</b></td><td>Yearly, with a free online assessment</td></tr></tbody></table></div>
<h2>Start here</h2>
<div class="tiles">
{t("AI-103/index.html", "Study guide", "AI-103 study guide", "Roadmap, exam weights, the services map by exam depth, all 19 lessons, 30 practice questions, glossary of renames.")}
{t("Choose-Model/index.html", "Decision guide", "Choose the right model", "Mind map of eight model categories, a decision tree, criteria, scenario table and category comparison.")}
{t("Agent-TCO/index.html", "Cost calculator", "What does an agent cost to run?", "Interactive TCO: users, turns and tokens in; an itemised daily bill, one-time costs and what moves the total out.")}
{t("Labs/week-01-keyless-call.html", "Lab · Week 1", "Keyless call to a Foundry model", "Setup, expected output, four break-it exercises.")}
</div>
<h2>Domains</h2>
<div class="tiles">
{t("D1-Plan-Manage/index.html", "D1 · 25–30%", "Plan and manage", f"Lessons and a {n}-item practice bank in every exam format.")}
{t("D2-GenAI-Agents/index.html", "D2 · 30–35%", "Generative AI and agents", f"16 teaching cards with CCA-F bridges, and a {len(bank_d2.BANK['items'])}-item practice bank.")}
{t("D3-Vision/index.html", "D3 · 10–15%", "Computer vision", f"{len(dom3.CARDS)} teaching cards and a {len(dom3.BANK['items'])}-item practice bank.")}
{t("D4-Text/index.html", "D4 · 10–15%", "Text analysis", f"{len(dom4.CARDS)} teaching cards and a {len(dom4.BANK['items'])}-item practice bank.")}
{t("D5-Extraction/index.html", "D5 · 10–15%", "Information extraction", f"{len(dom5.CARDS)} teaching cards and a {len(dom5.BANK['items'])}-item practice bank.")}
{t("Mock-Exam-1/index.html", "Mock · 100 min", "Mock Exam #1", f"{len(mock1.BANK['items'])} items, all formats, two long case studies, exam-level stems.")}
</div>
<div class="frame"><b>About the questions:</b> every practice item is original, written to the exam's style and objectives. None is a real exam question. Each has a deliberate runner-up and a plain-language explanation, and the build checks that mechanical strategies like "pick the longest option" score near chance.</div>'''
    open(os.path.join(ROOT, "index.html"), "w").write(page("Azure AI Engineer · AI-103", "", body))

if __name__ == "__main__":
    ok = build(); build_domain2(); ok = build_mock1() and ok
    for m in DOMS: ok = build_dom(*m) and ok
    build_model_guide(); build_tco(); build_lab(); build_home()
    sys.exit(0 if ok else 1)
