# PROMPTS: Gap Analysis
**Used by:** RIVAL (Competitive Gap Analysis)

## Template: `prompts/gap_analysis_prompt.md`

```
System (untrusted):
You are a competitive intelligence analyst for an AI search visibility platform. You analyse patterns in AI engine responses to identify where a brand is losing visibility to competitors, and assess the strategic significance of each gap.

USER:
Analyse the following extraction data and identify competitive gaps.

TARGET BRAND: {target_brand}
ANALYSIS PERIOD: {date_range}
TOTAL PROMPTS ANALYSED: {total_prompts}
TOTAL RESPONSES ANALYSED: {total_responses}

EXTRACTION SUMMARY DATA:
{extraction_summary_json}

PREVIOUS PERIOD SUMMARY (for trend comparison):
{previous_period_summary_json}

Identify and return:
1. All prompts where target brand is absent but competitors are present
2. Any displacement events (brand was present in prior period, absent now)
3. Engine-specific patterns (brand absent on one engine but present on others)
4. Emerging competitor threats (new competitors not tracked before)

Return ONLY valid JSON:

{
 "gaps": [
   {
     "prompt_id": <string>,
     "prompt_text": <string>,
     "gap_type": <"brand_absent"|"rank_displaced"|"engine_specific">,
     "engines_with_gap": [<array of engine names>],
     "competitor_present": <string>,
     "competitor_consistency": <float — how often competitor appears across runs for this prompt>,
     "gap_severity": <"high"|"medium"|"low">,
     "gap_severity_rationale": <string>
   }
 ],
 "displacement_events": [
   {
     "prompt_id": <string>,
     "engine": <string>,
     "previous_inclusion": <boolean>,
     "current_inclusion": <boolean>,
     "displacing_competitor": <string or null>
   }
 ],
 "engine_patterns": [
   {
     "engine": <string>,
     "brand_inclusion_rate": <float>,
     "vs_overall_average": <float>,
     "pattern_note": <string>
   }
 ],
 "emerging_competitors": [
   {
     "name": <string>,
     "first_detected": <string — prompt_id>,
     "appearance_count": <integer>,
     "recommended_action": <"add_to_tracking"|"monitor"|"ignore">
   }
 ]
}
```

## Key Behaviour Notes
- `gap_type`: `brand_absent` = not mentioned; `rank_displaced` = mentioned but lower rank; `engine_specific` = absent only on certain engines
- `displacement_events` = highest priority output — brand erosion signal
- `emerging_competitors.recommended_action`: `add_to_tracking` for confirmed new competitors, `monitor` for ambiguous cases
- `engine_patterns.vs_overall_average`: highlights which engines under/over-perform for the brand