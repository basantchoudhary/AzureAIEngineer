"""Choose the right model: mind map, decision tree, criteria, scenarios, category comparison. Exam skill D1:
'Choose an appropriate model for each task, including LLMs, small language models, multimodal models, and Foundry Tools.'"""
import html
E = html.escape
F = "https://learn.microsoft.com/en-us/azure/foundry/"

# Eight categories: (key, name, colour token, examples, exam cue words)
CATS = [
 ("tool", "Foundry Tools (not a model)", "--d4", "Language · Translator · Speech · Document Intelligence · Content Understanding", "PII, translate a file, invoice, offline"),
 ("flag", "General-purpose LLM", "--d1", "gpt-5 · gpt-4.1 · Claude Sonnet · Llama · Mistral Large", "best quality, complex writing, agents"),
 ("small", "Small model (SLM)", "--good", "gpt-5-mini / nano · gpt-4.1-mini / nano · Phi-4-mini", "high volume, low cost, fast, proven"),
 ("reason", "Reasoning model", "--runner", "o3 · o4-mini · gpt-5 with reasoning_effort · DeepSeek-R1", "multi-step, planning, maths, code"),
 ("multi", "Multimodal (vision) model", "--d3", "gpt-5 · gpt-4.1 · Phi-4-multimodal", "photo, screenshot, chart, describe"),
 ("embed", "Embedding and rerank", "--d5", "text-embedding-3-large / small · Cohere Embed · Cohere Rerank", "vector, similarity, RAG retrieval"),
 ("gen", "Image, video and voice output", "--accent", "gpt-image-2 · sora-2 (preview) · gpt-realtime · gpt-4o-mini-tts", "make an image, mask edit, video, voice"),
 ("router", "Model router", "--azure", "model-router deployment (Balanced, Quality, Cost)", "mixed difficulty, don't pick, cut cost"),
]

def mindmap():
    W, H = 980, 600
    cx, cy = W / 2, H / 2
    bw, bh = 290, 132
    xs = [16, W - 16 - bw]
    ys = [14, 160, 306, 452]
    out = [f'<svg class="mm" viewBox="0 0 {W} {H}" role="img" aria-label="Mind map: eight categories of model choice in Foundry, from Foundry Tools to model router, each with example models and the exam cue words that point to it.">']
    hub_w, hub_h = 250, 92
    for i, (k, name, tok, ex, cue) in enumerate(CATS):
        col, row = i % 2, i // 2
        x, y = xs[col], ys[row]
        ex_x = x + bw if col == 0 else x
        out.append(f'<line x1="{cx + (-hub_w/2 if col == 0 else hub_w/2):.0f}" y1="{cy:.0f}" x2="{ex_x}" y2="{y + bh/2:.0f}" style="stroke:var({tok})" class="mm-edge"/>')
    out.append(f'<rect x="{cx-hub_w/2}" y="{cy-hub_h/2}" width="{hub_w}" height="{hub_h}" rx="14" class="mm-hub"/>')
    out.append(f'<text x="{cx}" y="{cy-8}" text-anchor="middle" class="mm-hubt">Which model?</text>')
    out.append(f'<text x="{cx}" y="{cy+16}" text-anchor="middle" class="mm-sub">8 categories · cue words</text>')
    for i, (k, name, tok, ex, cue) in enumerate(CATS):
        col, row = i % 2, i // 2
        x, y = xs[col], ys[row]
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="10" class="mm-box" style="stroke:var({tok})"/>')
        out.append(f'<rect x="{x}" y="{y}" width="6" height="{bh}" rx="3" style="fill:var({tok})"/>')
        out.append(f'<text x="{x+18}" y="{y+24}" class="mm-t">{i+1} · {E(name)}</text>')
        lines = wrap(ex, 40)[:3]
        for j, ln in enumerate(lines):
            out.append(f'<text x="{x+18}" y="{y+46+j*17}" class="mm-ex">{E(ln)}</text>')
        out.append(f'<text x="{x+18}" y="{y+bh-14}" class="mm-cue">cue: {E(cue)}</text>')
    out.append('</svg>')
    return "".join(out)

def wrap(s, n):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return lines + [cur]

# Decision tree: ask in order, first Yes wins.
TREE = [
 ("Does a Foundry Tool already do this job (PII redaction, translating a document, reading an invoice, transcribing audio, offline extraction)?",
  "tool", "Use the Foundry Tool", "Language PII · Translator · Speech · Document Intelligence", "Deterministic, cheaper, and the exam's 'least effort' answer. An LLM is the runner-up."),
 ("Is the output something other than text: an image, a video, a voice, or vectors?",
  "gen", "Use a generation or embedding model", "gpt-image-2 · sora-2 · gpt-realtime / Voice Live · text-embedding-3-large", "Match the model to the output type; chat models don't make images or vectors."),
 ("Does the input include images, screenshots or charts that the model must read?",
  "multi", "Use a multimodal model", "gpt-5 · gpt-4.1 · Phi-4-multimodal", "For repeatable fields with confidence, Content Understanding beats a chat model."),
 ("Does the task need multi-step reasoning: planning, maths, tricky code, or rules with many conditions?",
  "reason", "Use a reasoning model", "o4-mini · o3 · gpt-5 (reasoning_effort)", "Slower, and reasoning tokens bill as output. No temperature; use reasoning_effort and max_output_tokens."),
 ("Must it run on a device or offline?",
  "small", "Use a small model on the edge", "Phi-4-mini (Foundry Local)", "Small open-weight models fit edge hardware; cloud-only models don't."),
 ("Is the task simple, high-volume, and has a small model been proven accurate enough?",
  "small", "Use a small model", "gpt-5-mini · gpt-5-nano · gpt-4.1-mini", "The cheapest model that passes your evaluation wins."),
 ("Do prompts vary from trivial to hard, and you'd rather not choose per request?",
  "router", "Use model router", "model-router: Balanced (default), Quality, or Cost mode", "Picks a model per prompt. Smallest context window of its models; Global or Data Zone Standard only."),
 ("Has prompting failed to get a consistent style or format, and you have hundreds of good examples?",
  "flag", "Fine-tune a model", "gpt-4.1-mini (SFT, DPO) · o4-mini (RFT)", "Try prompts and RAG first. Fine-tuning teaches style and format, not fresh facts."),
]
FALLBACK = ("flag", "Otherwise: a general-purpose LLM", "gpt-5 · gpt-4.1 · Claude Sonnet", "Start here, evaluate, then move down to a cheaper model if quality holds.")

CRITERIA = [
 ("Task and modality", "What goes in and comes out: text, image, audio, video, vectors.", "Rules out whole categories at once."),
 ("Quality needed", "How hard is the task? Does it need reasoning, or is it classification?", "Proven by evaluation, not guessed."),
 ("Latency", "Is a person waiting? Reasoning and large models are slower.", "Real-time → small or router; batch → anything."),
 ("Cost and volume", "Price per token × requests per day.", "Reasoning tokens bill as output."),
 ("Context length", "How much text per request?", "Model router uses its smallest model's window."),
 ("Availability", "GA, preview, or limited access? Available in your region and deployment type?", "\"GA only\" in a stem rules out preview models."),
 ("Data residency", "Must data stay in a geography?", "That's the deployment type (Data Zone), not the model, but it limits which models you can pick."),
 ("Customisation", "Does it need your style or format, consistently?", "Prompt → RAG → fine-tune, in that order."),
 ("Where it runs", "Cloud, or a device, or offline?", "Offline → small open-weight model or a container."),
]

SCEN = [
 ("Classify 5,000 claim emails an hour into six fixed categories", "Small model", "gpt-5-mini", "Simple and high volume; a small model was proven accurate.", "Reasoning model: slower and dearer for no gain."),
 ("Hide names and card numbers in transcripts", "Foundry Tool", "Language PII detection", "Built for it, returns redacted text.", "An LLM prompted to redact: less reliable, costs tokens."),
 ("Plan a multi-step claims investigation with many rules", "Reasoning model", "o4-mini", "Multi-step logic.", "General LLM: fine for writing, weaker at long chains of rules."),
 ("Describe a damage photo for an adjuster", "Multimodal model", "gpt-4.1", "Reads images and answers in text.", "Image Analysis 4.0: deprecated."),
 ("Extract fields with confidence from varied repair estimates", "Foundry Tool", "Content Understanding analyzer", "Schema, confidence, no training.", "A vision chat model: no confidence scores."),
 ("Retrieve policy clauses by meaning", "Embedding model", "text-embedding-3-large", "Vectors for search.", "A chat model can't produce index vectors."),
 ("Generate a product image with a transparent background", "Image generation", "gpt-image-2", "GA image model.", "DALL-E 3: retired."),
 ("A live phone agent that can be interrupted", "Realtime audio", "gpt-realtime via Voice Live", "Speech to speech in one service.", "STT + LLM + TTS chained: more latency."),
 ("A support chat with mixed easy and hard questions, cut cost", "Model router", "model-router (Cost mode)", "Picks per prompt.", "Model subset limited to small models: blocks hard questions."),
 ("Run on a technician's laptop with no internet", "Small model on the edge", "Phi-4-mini on Foundry Local", "Runs locally.", "Any cloud deployment."),
 ("Replies must match the house style; prompting is inconsistent", "Fine-tuned model", "gpt-4.1-mini (SFT)", "Teaches style from examples.", "Bigger model: costs more and still drifts."),
]

COMPARE = [
 ("General-purpose LLM", "Writing, broad knowledge, tool use, agents", "Cost at volume; slower than small models", "$$$", "Medium", "gpt-5, gpt-4.1, Claude Sonnet, Llama, Mistral Large"),
 ("Small model (SLM)", "Classification, extraction, routing, high volume", "Hard reasoning, long nuanced writing", "$", "Fast", "gpt-5-mini/nano, gpt-4.1-mini/nano, Phi-4-mini"),
 ("Reasoning model", "Multi-step logic, maths, code, planning", "Latency; reasoning tokens bill as output; no temperature", "$$–$$$$", "Slow", "o3, o4-mini, gpt-5 (reasoning_effort), DeepSeek-R1"),
 ("Multimodal model", "Images in, text out: captions, visual Q&A, charts", "Repeatable fields with confidence (use Content Understanding)", "$$", "Medium", "gpt-5, gpt-4.1, Phi-4-multimodal"),
 ("Embedding / rerank", "Vectors for search, similarity, clustering; reranking", "Doesn't generate text", "¢", "Fast", "text-embedding-3-large/small, Cohere Embed, Cohere Rerank"),
 ("Image / video generation", "Create and edit images; generate and remix video", "Faces in video inputs; real people", "$$ per image / per second", "Seconds to minutes", "gpt-image-2, sora-2 (preview)"),
 ("Realtime audio / speech", "Live voice conversations, transcription, voices", "Content filters don't apply to audio", "$$", "Real-time", "gpt-realtime, gpt-4o-transcribe, gpt-4o-mini-tts"),
 ("Model router", "Mixed difficulty without choosing", "Smallest context window of its models; limited deployment types", "Varies", "Varies", "model-router"),
 ("Foundry Tools", "PII, translation, OCR, forms, speech, offline containers", "Open-ended reasoning", "$", "Fast", "Language, Translator, Speech, Document Intelligence, Content Understanding"),
]

def body():
    tok = {k: t for k, _, t, _, _ in CATS}
    tree = []
    for i, (q, k, choose, ex, why) in enumerate(TREE, 1):
        tree.append(f'''<li class="mg-step"><div class="mg-q"><span class="mg-n">{i}</span><p>{E(q)}</p></div>
<div class="mg-yes" style="--c:var({tok[k]})"><span class="mg-lab">Yes →</span><b>{E(choose)}</b><span class="mg-ex">{E(ex)}</span><span class="mg-why">{E(why)}</span></div></li>''')
    k, choose, ex, why = FALLBACK
    tree.append(f'<li class="mg-step mg-last"><div class="mg-q"><span class="mg-n">✓</span><p>No to everything?</p></div><div class="mg-yes" style="--c:var({tok[k]})"><span class="mg-lab">Then →</span><b>{E(choose)}</b><span class="mg-ex">{E(ex)}</span><span class="mg-why">{E(why)}</span></div></li>')
    crit = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in CRITERIA)
    scen = "".join(f"<tr><td>{E(a)}</td><td><b>{E(b)}</b></td><td><span class=\"k\">{E(c)}</span></td><td>{E(d)}</td><td class=\"mg-trap\">{E(e)}</td></tr>" for a, b, c, d, e in SCEN)
    comp = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td class=\"num\">{E(d)}</td><td>{E(e)}</td><td>{E(f)}</td></tr>" for a, b, c, d, e, f in COMPARE)
    return f'''<div class="eyebrow"><b>Domain 1 · Plan and manage</b>Choose the right model</div>
<h1>Choose the right <span>model</span></h1>
<p class="lede">The exam skill: choose an appropriate model for each task, including LLMs, small models, multimodal models and Foundry Tools. <em>Exam questions test the category; model names are examples.</em></p>
<div class="frame"><b>From CCA-F:</b> the same idea as choosing Haiku, Sonnet or Opus: the cheapest model that passes your evaluation wins. Azure adds three things: a catalogue with many vendors, Foundry Tools that aren't LLMs at all, and a model router that chooses for you.</div>

<h2>1 · The mind map: eight categories</h2>
<p class="note">Each branch is a category, with example models and the words in a question stem that point to it.</p>
<figure class="mg-fig"><div class="mg-scroll">{mindmap()}</div>
<figcaption>Every model choice in Foundry falls into one of eight categories. Learn the cue words; they're how a question tells you which branch it wants.</figcaption></figure>

<h2>2 · The decision tree</h2>
<p class="note">Ask the questions in order. <b>The first Yes wins.</b> The order matters: a Foundry Tool beats any model, and a cheaper model beats a bigger one once it passes evaluation.</p>
<ol class="mg-tree">{"".join(tree)}</ol>

<h2>3 · The criteria to weigh</h2>
<div class="tbl"><table><thead><tr><th>Criterion</th><th>Ask</th><th>Exam angle</th></tr></thead><tbody>{crit}</tbody></table></div>

<h2>4 · In this scenario, choose this</h2>
<div class="tbl"><table><thead><tr><th>Scenario</th><th>Choose</th><th>Example</th><th>Why</th><th>Runner-up trap</th></tr></thead><tbody>{scen}</tbody></table></div>

<h2>5 · Categories compared</h2>
<div class="tbl"><table><thead><tr><th>Category</th><th>Best at</th><th>Weak at</th><th>Cost</th><th>Speed</th><th>Examples</th></tr></thead><tbody>{comp}</tbody></table></div>
<p class="note">Costs are relative per request, not prices. Model names change fast; check the <a href="{F}concepts/foundry-models-overview" target="_blank" rel="noopener">Foundry Models catalogue</a> (open during the exam) for current names, regions and GA status.</p>

<h2>6 · Model choice isn't deployment choice</h2>
<div class="frame">Picking the <b>model</b> answers "what can do this job?". Picking the <b>deployment type</b> answers "where is it processed, and how do I pay?" (Global, Data Zone, Standard, Provisioned, Batch). A stem about residency or throughput is asking about the deployment, not the model. See D1.</div>
<div class="tiles"><a class="tile" href="../D1-Plan-Manage/practice.html"><span class="lv">Practice</span><b>D1 practice bank →</b><p>Includes model-choice questions with runner-ups.</p></a>
<a class="tile" href="../Mock-Exam-1/index.html"><span class="lv">Mock</span><b>Mock Exam #1 →</b><p>Q1 and Q17 test model choice.</p></a></div>'''

CSS = """
.mg-fig{margin:0;display:grid;gap:8px}.mg-fig figcaption{font-size:14px;color:var(--muted)}
.mg-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:14px;background:var(--surface);padding:8px}
.mm{display:block;width:100%;min-width:760px;height:auto;color:var(--ink)}
.mm-edge{stroke-width:2;fill:none;opacity:.7}
.mm-hub{fill:var(--ink)}.mm-hubt{fill:var(--surface);font:700 20px var(--display)}.mm-sub{fill:var(--surface);font:500 12.5px var(--sans);opacity:.85}
.mm-box{fill:var(--surface);stroke-width:1.5}
.mm-t{fill:var(--ink);font:700 14px var(--display)}.mm-ex{fill:var(--ink);font:400 12.5px var(--sans)}.mm-cue{fill:var(--muted);font:italic 400 12px var(--sans)}
.mg-tree{list-style:none;margin:0;padding:0;display:grid;gap:0}
.mg-step{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:12px;align-items:stretch;padding-bottom:22px;position:relative}
.mg-step:not(.mg-last)::after{content:"No ↓";position:absolute;left:18px;bottom:2px;font:600 12px var(--mono);color:var(--muted)}
.mg-q{display:flex;gap:10px;align-items:flex-start;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.mg-q p{margin:0}
.mg-n{flex:none;width:26px;height:26px;border-radius:50%;background:var(--ink);color:var(--surface);display:grid;place-items:center;font:700 13px var(--mono)}
.mg-yes{display:grid;gap:3px;border:1px solid var(--line);border-left:5px solid var(--c);border-radius:12px;padding:10px 14px;background:color-mix(in srgb,var(--c) 7%,var(--surface))}
.mg-lab{font:600 12px var(--mono);color:var(--c)}.mg-ex{font:500 13px var(--mono);overflow-wrap:anywhere}.mg-why{font-size:14px;color:var(--muted)}
.mg-trap{color:var(--runner)}
@media (max-width:700px){.mg-step{grid-template-columns:1fr;gap:6px}}
"""
