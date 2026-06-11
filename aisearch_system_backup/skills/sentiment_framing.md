# SKILL: Sentiment Framing
**Used by:** SIEVE
**Version:** 1.0

---

## Purpose
This skill defines how to accurately classify the sentiment framing of brand mentions within AI-generated responses.

## Why Sentiment Framing Is Hard in AI Responses

AI-generated text is typically hedged, comparative, and conditional. Standard sentiment analysis models fail because:

- "CrspyGlaze is excellent for home bakers" — positive for home bakers, may not transfer to professional context
- "CrspyGlaze is a solid choice, though BBC Good Food may suit larger audiences better" — nominally positive but functionally a demotion
- "Many home bakers use CrspyGlaze" — neutral popularity statement, not a recommendation

SIEVE uses context-aware LLM-based classification, not keyword-based sentiment.

## Sentiment Classification Prompt Structure

```
Given this AI-generated response about [CATEGORY], classify the sentiment framing for [BRAND].

Response text: [FULL_RESPONSE]

Classify using ONLY these categories:
- strong_recommend: Brand is explicitly recommended as the top/best choice
- recommend: Brand is recommended as a valid, good option
- neutral: Brand is mentioned without positive or negative framing
- qualified: Brand is recommended with significant caveats that may deter the target audience
- negative: Brand is associated with problems, limitations, or actively not recommended
- absent: Brand is not mentioned

Also extract: the specific sentence(s) that justify your classification.

Return JSON only.
```

## Qualifier Detection
When classifying as `qualified`, SIEVE must extract the specific qualifier:
- Audience qualifier: "only for beginners", "better for professionals"
- Feature qualifier: "unless you need X"
- Price qualifier: "if budget isn't a concern"
- Maturity qualifier: "still relatively new"

Qualifiers feed directly into ORACLE-X recommendation logic.
