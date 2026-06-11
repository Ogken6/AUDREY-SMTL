# `prompts/gap_analysis_prompt.md`
## RIVAL Gap Analysis Prompt

System:
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
1. All prompts where the target brand is absent but competitors are present
2. Any displacement events (brand was present in prior period, absent now)
3. Engine-specific patterns (brand consistently absent on one engine but present on others)
4. Emerging competitor threats (new competitors appearing that weren't tracked before)

Return ONLY valid JSON:

{
  "gaps": [
    {
      "prompt_id": <string>,
      "prompt_text": <string>,
      "gap_type": <"brand_absent"|"rank_displaced"|"engine_specific">,
      "engines_with_gap": [<array of engine names>],
      "competitor_present": <string — which competitor is capturing this space>,
      "competitor_consistency": <float — how often competitor appears across runs for this prompt>,
      "gap_severity": <"high"|"medium"|"low">,
      "gap_severity_rationale": <string — why this severity>
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
      "vs_overall_average": <float — difference from average across all engines>,
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
