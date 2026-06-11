# SKILL: Prompt Generation
**Used by:** SCOUT | **Version:** 1.0

## Purpose
Defines how to build a high-quality, diverse, signal-rich prompt library for AI search visibility research.

## Anatomy of a High-Value Prompt (5 properties)
1. Conversational register — sounds like a real human typed it
2. Appropriate length — 8–25 words
3. Clear intent signal — unambiguous purchase, comparison, discovery, or problem-framing intent
4. Category specificity — general enough for category-level answers, specific enough for substantive responses
5. No brand anchoring — discovery prompts must not name the target brand

## Intent Coverage Checklist
- [ ] Recommendation prompts ≥ 20%
- [ ] Comparison prompts ≥ 15%
- [ ] Problem-framing prompts ≥ 15%
- [ ] Tool-discovery prompts ≥ 20%
- [ ] Validation prompts ≥ 15%
- [ ] Competitor alternative prompts ≥ 15%

## Prompt Generation LLM Call
```
System: You are a prompt library builder for an AI search visibility research platform.
Generate prompts that real users would type into ChatGPT, Perplexity, or Google when researching [CATEGORY].
Rules:
- 8–25 words per prompt
- Conversational tone, not keyword strings
- Do not name [TARGET_BRAND] in discovery prompts
- Cover all six intent types: recommendation, comparison, problem_framing, tool_discovery, validation, alternatives
- Generate prompts that produce substantive, source-cited AI answers
- Weight toward long-tail, specific prompts over broad generic ones

User: Generate 30 prompts for [CATEGORY] targeting [PERSONA]. Competitors include: [COMPETITOR_LIST].
Format as JSON array with keys: text, intent, funnel_stage.
```

## Semantic Deduplication Protocol
1. Generate embeddings for all prompts using `text-embedding-3-small`
2. Compute pairwise cosine similarity
3. Flag any pair with similarity > 0.92 as duplicates
4. Keep the prompt with higher `verified_real` score, or longer if tied
5. Log all retired prompts with retirement reason

## Prompt Retirement Rules
Retire when:
- Run 10+ times with 0 brand mentions across all engines
- Run 5+ times with only generic, non-cited AI answers (no sources)
- Semantically near-duplicate of higher-performing prompt
- Underlying user need has become obsolete

Never retire anchor prompts (`anchor: true`) without explicit human approval.

## Intent Types
| Type | Example | Why It Matters |
|---|---|---|
| recommendation | "What's the best X for Y?" | Highest purchase intent |
| comparison | "X vs Y — which is better?" | Competitor displacement |
| problem_framing | "How do I solve [pain point]?" | Category entry point |
| tool_discovery | "What tools do teams use for X?" | Brand discovery |
| validation | "Is X good for enterprise?" | Late-stage buyer research |
| alternatives | "Alternatives to [competitor]" | Acquisition from rivals |