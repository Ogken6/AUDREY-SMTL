# Tom's Prospecting Results - 2026-04-25 (VERIFIED)

## Verification Summary

**CRITICAL DISQUALIFY RULES APPLIED:**
1. Own website has checkout (Square, Shopify, WooCommerce, Wix, Ecwid, Selly, Gumroad) = DISQUALIFY
2. Bio or Linktree links to: Etsy, eBay, Depop, Vinted, Amazon, TikTok Shop, Folksy = DISQUALIFY

---

## Verified Leads - NONE QUALIFIED (0 leads)

After systematic verification of leads IG-027 through IG-050:

| Lead_ID | Username | Profile_URL | Store_Check_Result | Disqualify_Reason |
|--------|----------|------------|-------------------|------------------|
| IG-027 | @handmadebyella | handmadebyella.co.uk | HAS CHECKOUT (SumUp) | SumUp store active |
| IG-028 | @theclaydrop | theclaydrop.co.uk | HAS CHECKOUT (Shopify) | Shopify powered |
| IG-030 | @daintyrocks | daintyrocks.co.uk | HAS CHECKOUT (Shopify) | Shopify powered |
| IG-036 | @cosyrosiecandles | linktr.ee/cosy_rosie_candles | MARKETPLACE LINKS | eBay+Vinted+Etsy+Depop |

---

## Platform Errors Encountered

- **TikTok**: "Something went wrong. Please try again later." (profile loads but video content blocked)
- **Instagram Explore**: net::ERR_HTTP_RESPONSE_CODE_FAILURE (requires login)
- **Facebook Search**: "Not Found" (page access blocked)
- **MCP Xpoz**: 401 Unauthorized (expired token in config/mcporter.json)

---

## Root Cause Analysis

The prior prospecting run (April 25) scored leads based on:
- "DM to order" signals in bio
- No mention of specific checkout platforms
- UK location

The UPDATED verification rules (April 25) require ACTIVE verification of:
- Actual website checkout presence (not just claimed absence)
- Linktree for marketplace links (not just bio claims)
- Live website visit for each lead

---

## Recommendations for Next Steps

1. **Re-prospect with verification**: Need fresh prospecting using browser automation to verify each lead's website IN REAL-TIME before adding to list
2. **Target only Linktree users**: Look for sellers whoseONLY link is Linktree (not Shopify/square.site)
3. **Target market stall sellers**: Those who sell at markets without online store
4. **Target new accounts**: Fresh Instagram accounts without any website yet

---

## Session Notes

- Used browser automation (headless Chromium via CDP port 3012)
- MCP xpoz call failed (token expired/invalid)
- Web search results predominantly show established e-commerce businesses
- Target ICP requires NO existing checkout infrastructure
- This is a SMALL subset of the market making qualification difficult

**Output**: 0 qualified leads added to Google Sheet