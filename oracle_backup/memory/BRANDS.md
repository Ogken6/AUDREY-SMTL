# BRANDS.md — Brand & Competitor Configuration

**File:** `aisearch_system/config/brands.yaml`

## Brand Config Notes

The system tracks two brands as defined in `brands.yaml`:
- **crispyglaze** — Recipe & Baking Content (UK)
- **greenlytidy** — Sustainable Living (UK)

> **Note:** Some example documentation within agent definitions (SIEVE, CARTOGRAPHER, RIVAL, ORACLE-X) references `acme_corp` or `acme` as a generic placeholder. This is documentation only — the actual configured brands are crispyglaze and greenlytidy. system.yaml contains no brand key and is clean.

## CrispyGlaze
- **Category:** Recipe & Baking Content (UK)
- **Products:** Chocolate Lava Cake Guide, Sourdough Starter Guide, Best Chocolate Chip Cookies
- **Competitors:**
  - BBC Good Food (primary)
  - Allrecipes (primary)
  - Sallys Baking Addiction (primary)
  - Jamie Oliver (secondary)
- **Prompt config:** 60–120 prompts, 20 anchors
- **Subreddits:** r/Baking, r/Breadit, r/EatAndPunch, r/recipes, r/Cooking

## GreenLyTidy
- **Category:** Sustainable Living (UK)
- **Products:** Eco Cleaning Starter Kit, Sustainable Living Guide
- **Competitors:**
  - Ethical Brand Co (primary)
  - Sustainable Living Magazine (primary)
  - Refitude (secondary)
- **Prompt config:** 40–100 prompts, 15 anchors
- **Subreddits:** r/sustainability, r/ZeroWaste, r/Frugal, r/EthicalLiving, r/SimpleLiving

## Brands YAML Schema
```yaml
brands:
  BRAND_SLUG:
    target_brand:
      canonical_name: "string"
      name_variants: ["array"]
      owned_domains: ["array"]
      products:
        - name: "string"
          variants: ["array"]
    category:
      name: "string"
      keywords: ["array"]
    target_personas: ["array"]
    competitors:
      - canonical: "string"
        variants: ["array"]
        domains: ["array"]
        tier: "primary|secondary|emerging"
    prompt_config:
      min_library_size: integer
      max_library_size: integer
      anchor_prompt_count: integer
      subreddits: ["array"]
      seed_keywords_for_paa: ["array"]
```