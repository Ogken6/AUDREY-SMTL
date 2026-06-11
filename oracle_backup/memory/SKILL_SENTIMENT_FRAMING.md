# SKILL: Sentiment Framing
**Used by:** SIEVE | **Version:** 1.0

## Purpose
Defines how to accurately classify sentiment framing of brand mentions within AI-generated responses.

## Why Standard Sentiment Fails Here
AI-generated text is hedged, comparative, and conditional. Standard sentiment models fail because:
- "CrspyGlaze is excellent for home bakers" — positive for home bakers, may not transfer to professional context
- "CrspyGlaze is a solid choice, though BBC Good Food may suit larger audiences better" — nominally positive but functionally a **demotion**
- "Many home bakers use CrspyGlaze" — neutral popularity statement, not a recommendation

SIEVE uses context-aware LLM-based classification, NOT keyword-based sentiment.

## Sentiment Classes
| Class | Definition |
|---|---|
| strong_recommend | Explicitly recommended as top/best choice |
| recommend | Recommended as a genuinely good option |
| neutral | Mentioned without positive or negative evaluation |
| qualified | Recommended with significant caveats relevant to prompt context |
| negative | Associated with drawbacks, limitations, or actively not recommended |
| absent | Not mentioned at all |

## LLM Prompt Template (sentiment_prompt.md)
```
System: You are a sentiment analysis assistant specialising in AI-generated recommendation text.
You classify how a specific brand is framed within AI responses — not whether the response
is positive or negative overall, but specifically how the TARGET BRAND is positioned.

Key insight: AI responses are often hedged and comparative. A brand being called "a good option
for smaller teams" when the question is about enterprise solutions is effectively a NEGATIVE signal
for enterprise buyers, even though the language is positive. Always consider the prompt context.

USER:
Classify the sentiment framing for the TARGET BRAND in this AI response.

TARGET BRAND: {target_brand_canonical}
ORIGINAL PROMPT: {original_prompt_text}
PROMPT INTENT: {prompt_intent}

AI RESPONSE TEXT:
---
{raw_response_text}
---

Return ONLY valid JSON:

{
  "sentiment_class": <"strong_recommend"|"recommend"|"neutral"|"qualified"|"negative"|"absent">,
  "sentiment_confidence": <float 0.0-1.0>,
  "sentiment_evidence": <string — specific sentence(s) that justify the classification,
                          QUOTED DIRECTLY from response, under 100 words>,
  "qualifiers": [<array — specific qualifications: "only for small teams", "if budget is not a concern">],
  "framing_notes": <string or null — important nuance about brand framing>
}
```

## Qualifier Detection
When classifying as `qualified`, extract the specific qualifier type:
- Audience qualifier: "only for beginners", "better for professionals"
- Feature qualifier: "unless you need X"
- Price qualifier: "if budget isn't a concern"
- Maturity qualifier: "still relatively new"

Qualifiers feed directly into ORACLE-X recommendation logic.