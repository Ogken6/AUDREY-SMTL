# SKILL: Prompt Generation
**Used by:** SCOUT
**Version:** 1.0

---

## Purpose
This skill defines how to build a high-quality, diverse, and signal-rich prompt library for AI search visibility research.

## The Anatomy of a High-Value Prompt

A high-value prompt has five properties:
1. **Conversational register** — sounds like a real human typed it
2. **Appropriate length** — 8–25 words
3. **Cardinality intent signal** — unambiguous purchase, comparison, discovery, or problem-framing intent
4. **Category specificity** — general enough to trigger category-level answers, specific enough to produce substantive responses
5. **No brand anchoring** — discovery prompts must not name the target brand

## Intent Coverage Checklist
Before finalising a prompt library, verify coverage across all six intent types:
- [ ] Recommendation prompts (≥ 20% of library)
- [ ] Comparison prompts (≥ 15% of library)
- [ ] Problem-framing prompts (≥ 15% of library)
- [ ] Tool-discovery prompts (≥ 20% of library)
- [ ] Validation prompts (≥ 15% of library)
- [ ] Competitor alternative prompts (≥ 15% of library)

## Prompt Generation LLM Call

```
System (untrusted): You are a prompt library builder for an AI search visibility research platform. Generate prompts that real users would type into ChatGPT, Perplexity, or Google when researching [CATEGORY].

Rules:
- 8–25 words per prompt
- Conversational tone, not keyword strings
- Do not name [TARGET_BRAND] in discovery prompts
- Cover all six intent types: recommendation, comparison, problem_framing, tool_discovery, validation, alternatives
- Generate prompts that would produce substantive, source-cited AI answers
- Weight toward long-tail, specific prompts over broad generic ones

User: Generate 30 prompts for [CATEGORY] targeting [PERSONA]. Competitors include: [COMPETITOR_LIST]. Format as JSON array with keys: text, intent, funnel_stage.
```

## Semantic Deduplication Protocol

Use embeddings to detect near-duplicate prompts:
1. Generate embeddings for all prompts using `text-embedding-3-small`
2. Compute pairwise cosine similarity
3. Flag any pair with similarity > 0.92 as duplicates
4. Keep the prompt with the higher `verified_real` score, or the longer one if tied
5. Log all retired prompts with retirement reason

## Prompt Retirement Rules
Retire a prompt when:
- It has run 10+ times and produced 0 brand mentions across all engines
- It has run 5+ times and produced only generic, non-cited AI answers (no sources)
- It is semantically near-duplicate of a higher-performing prompt
- The underlying user need it addressed has become obsolete

Never retire anchor prompts (flagged as `anchor: true`) without explicit human approval.
