# Azure AI Engineer · AI-103

Study material for Microsoft exam **AI-103: Developing AI Apps and Agents on Azure** (Azure AI Apps and Agents Developer Associate, the successor to AI-102). Lessons, exam-format practice, timed mock exams and hands-on labs.

## View the live site

GitHub shows `.html` files as source. Open the rendered site on GitHub Pages:

**➡️ https://basantchoudhary.github.io/AzureAIEngineer/**

| Section | Status | Link |
|---|---|---|
| AI-103 study guide: roadmap, services map by exam depth, 19 lessons, 30 questions, glossary | live | [open ›](https://basantchoudhary.github.io/AzureAIEngineer/AI-103/index.html) |
| D1 · Plan and manage (25–30%): lessons | live | [open ›](https://basantchoudhary.github.io/AzureAIEngineer/D1-Plan-Manage/index.html) |
| D1 · Practice bank: 21 items in six exam formats, practice and timed exam modes | live | [open ›](https://basantchoudhary.github.io/AzureAIEngineer/D1-Plan-Manage/practice.html) |
| Lab · Week 1: keyless call to a Foundry model, four break-it exercises | live | [open ›](https://basantchoudhary.github.io/AzureAIEngineer/Labs/week-01-keyless-call.html) |
| D2 · Generative AI and agents (30–35%): 16 teaching cards with CCA-F bridges | live | [open ›](https://basantchoudhary.github.io/AzureAIEngineer/D2-GenAI-Agents/index.html) |
| D2 · Practice bank: 22 items in six exam formats | live | [open ›](https://basantchoudhary.github.io/AzureAIEngineer/D2-GenAI-Agents/practice.html) |
| D3 · Computer vision (10–15%) | coming | |
| D4 · Text analysis (10–15%) | coming | |
| D5 · Information extraction (10–15%) | coming | |
| Mock Exam #1: 50 items, 100 minutes, 2 case studies (Contoso, Fabrikam), D1 14 · D2 16 · D3 6 · D4 7 · D5 7 | live | [Mock-Exam-1](https://basantchoudhary.github.io/AzureAIEngineer/Mock-Exam-1/) |

## Exam blueprint (skills measured as of 16 April 2026)

| Domain | Weight |
|---|:--:|
| Plan and manage an Azure AI solution | 25–30% |
| Implement generative AI and agentic solutions | 30–35% |
| Implement computer vision solutions | 10–15% |
| Implement text analysis solutions | 10–15% |
| Implement information extraction solutions | 10–15% |

Source: [AI-103 study guide on Microsoft Learn](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)

## About the practice questions

Every item is original, written to the exam's style and objectives. None is a real exam question. Items use the exam's formats (choose one, choose two, yes/no statements, build list, code completion, problem/solution series), each with a deliberate runner-up and a four-part explanation. `src/build_site.py` checks that "pick the longest" or "pick the shortest" option scores near chance and that answer positions are balanced.

## Build

```bash
python3 src/build.py        # AI-103 study guide
python3 src/build_site.py   # home, D1 lessons and practice, labs (fails if validation fails)
```

Facts checked against Microsoft Learn on 8 October 2026. Azure AI changes quickly. Not affiliated with Microsoft.
