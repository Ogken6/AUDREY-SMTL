# ANCHOR_PROMPTS.md — 30 Anchor Prompts for CrispyGlaze

**Brand:** CrispyGlaze | **Keywords:** "simple comfort food recipes" + "easy comfort food recipes"
**Run mode:** Every pipeline cycle. Never retire without explicit human approval.

## "Simple" Keyword Anchors — 15 Prompts (S01–S15)

| ID | Prompt Text | Intent | Stage |
|---|---|---|---|
| S01 | What are the best simple comfort food recipes for busy weeknights? | recommendation | awareness |
| S02 | What simple comfort food can I make in 30 minutes for my family? | tool_discovery | consideration |
| S03 | Where can I find simple comfort food recipes online? | tool_discovery | awareness |
| S04 | What is the best website for simple comfort food recipes? | recommendation | consideration |
| S05 | What simple comfort food can I make with pantry ingredients? | problem_framing | consideration |
| S06 | What are simple global comfort food recipes for home cooks? | tool_discovery | awareness |
| S07 | What are simple comfort food recipes that beginners can actually make? | recommendation | awareness |
| S08 | What simple comfort food recipes work for gluten-free diets? | validation | consideration |
| S09 | What are simple homemade bread recipes for first-time bakers? | tool_discovery | awareness |
| S10 | What simple comfort food breakfast ideas are filling and fast? | recommendation | awareness |
| S11 | What are simple soup recipes that feel like comfort food? | recommendation | consideration |
| S12 | What are simple comfort food desserts I can make tonight? | recommendation | consideration |
| S13 | What are simple Thai comfort food recipes I can make at home? | tool_discovery | consideration |
| S14 | What simple comfort food dishes can I meal prep on Sundays? | validation | decision |
| S15 | What simple comfort food recipes are popular in Canada? | tool_discovery | awareness |

## "Easy" Keyword Anchors — 15 Prompts (E01–E15)

| ID | Prompt Text | Intent | Stage |
|---|---|---|---|
| E01 | What are the best easy comfort food recipes for busy families? | recommendation | awareness |
| E02 | What easy comfort food can I cook tonight in under 30 minutes? | tool_discovery | consideration |
| E03 | What is the best food blog for easy comfort food recipes? | recommendation | consideration |
| E04 | Where do I find easy comfort food recipes that actually taste great? | tool_discovery | awareness |
| E05 | What easy comfort food can I make without a lot of ingredients? | problem_framing | consideration |
| E06 | What are easy comfort food recipes from different cultures? | tool_discovery | awareness |
| E07 | What easy comfort food recipes can a beginner cook successfully? | recommendation | awareness |
| E08 | What easy gluten-free comfort food recipes can the whole family enjoy? | validation | consideration |
| E09 | What are easy homemade bread recipes that don't require experience? | tool_discovery | awareness |
| E10 | What easy comfort food breakfast recipes are worth waking up for? | recommendation | awareness |
| E11 | What easy soup and chowder recipes are best for cold nights? | recommendation | consideration |
| E12 | What are easy comfort food desserts I can make from scratch? | recommendation | consideration |
| E13 | What easy Korean comfort food recipes can I make at home? | tool_discovery | consideration |
| E14 | What easy comfort food dishes are good for weekly meal prep? | validation | decision |
| E15 | What are the best easy comfort food recipes for Canadian home cooks? | tool_discovery | awareness |

## Intent Distribution
- `recommendation`: S01, S04, S07, S10, S11, S12, E01, E03, E07, E10, E11, E12 — 12 prompts
- `tool_discovery`: S02, S03, S06, S09, S13, S15, E02, E04, E06, E09, E13, E15 — 12 prompts
- `problem_framing`: S05, E05 — 2 prompts
- `validation`: S08, S14, E08, E14 — 4 prompts

## Full JSON (for direct loading into prompt_library.json)
```json
[
  {"id": "S01", "text": "What are the best simple comfort food recipes for busy weeknights?", "intent": "recommendation", "funnel_stage": "awareness", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S02", "text": "What simple comfort food can I make in 30 minutes for my family?", "intent": "tool_discovery", "funnel_stage": "consideration", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S03", "text": "Where can I find simple comfort food recipes online?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S04", "text": "What is the best website for simple comfort food recipes?", "intent": "recommendation", "funnel_stage": "consideration", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S05", "text": "What simple comfort food can I make with pantry ingredients?", "intent": "problem_framing", "funnel_stage": "consideration", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S06", "text": "What are simple global comfort food recipes for home cooks?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S07", "text": "What are simple comfort food recipes that beginners can actually make?", "intent": "recommendation", "funnel_stage": "awareness", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S08", "text": "What simple comfort food recipes work for gluten-free diets?", "intent": "validation", "funnel_stage": "consideration", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S09", "text": "What are simple homemade bread recipes for first-time bakers?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S10", "text": "What simple comfort food breakfast ideas are filling and fast?", "intent": "recommendation", "funnel_stage": "awareness", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S11", "text": "What are simple soup recipes that feel like comfort food?", "intent": "recommendation", "funnel_stage": "consideration", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S12", "text": "What are simple comfort food desserts I can make tonight?", "intent": "recommendation", "funnel_stage": "consideration", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S13", "text": "What are simple Thai comfort food recipes I can make at home?", "intent": "tool_discovery", "funnel_stage": "consideration", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S14", "text": "What simple comfort food dishes can I meal prep on Sundays?", "intent": "validation", "funnel_stage": "decision", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "S15", "text": "What simple comfort food recipes are popular in Canada?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "simple comfort food recipes"},
  {"id": "E01", "text": "What are the best easy comfort food recipes for busy families?", "intent": "recommendation", "funnel_stage": "awareness", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E02", "text": "What easy comfort food can I cook tonight in under 30 minutes?", "intent": "tool_discovery", "funnel_stage": "consideration", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E03", "text": "What is the best food blog for easy comfort food recipes?", "intent": "recommendation", "funnel_stage": "consideration", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E04", "text": "Where do I find easy comfort food recipes that actually taste great?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E05", "text": "What easy comfort food can I make without a lot of ingredients?", "intent": "problem_framing", "funnel_stage": "consideration", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E06", "text": "What are easy comfort food recipes from different cultures?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E07", "text": "What easy comfort food recipes can a beginner cook successfully?", "intent": "recommendation", "funnel_stage": "awareness", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E08", "text": "What easy gluten-free comfort food recipes can the whole family enjoy?", "intent": "validation", "funnel_stage": "consideration", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E09", "text": "What are easy homemade bread recipes that don't require experience?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E10", "text": "What easy comfort food breakfast recipes are worth waking up for?", "intent": "recommendation", "funnel_stage": "awareness", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E11", "text": "What easy soup and chowder recipes are best for cold nights?", "intent": "recommendation", "funnel_stage": "consideration", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E12", "text": "What are easy comfort food desserts I can make from scratch?", "intent": "recommendation", "funnel_stage": "consideration", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E13", "text": "What easy Korean comfort food recipes can I make at home?", "intent": "tool_discovery", "funnel_stage": "consideration", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E14", "text": "What easy comfort food dishes are good for weekly meal prep?", "intent": "validation", "funnel_stage": "decision", "anchor": true, "keyword": "easy comfort food recipes"},
  {"id": "E15", "text": "What are the best easy comfort food recipes for Canadian home cooks?", "intent": "tool_discovery", "funnel_stage": "awareness", "anchor": true, "keyword": "easy comfort food recipes"}
]
```