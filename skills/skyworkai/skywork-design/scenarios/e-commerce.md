# E-commerce Product Images

## Triggers

amazon, product listing, product photo, e-commerce, shopify, product shot, packshot, white background product, marketplace image

## Defaults

- **Aspect ratio**: `1:1`
- **Resolution**: `4K` (Amazon requires min 1600px on longest side for zoom; recommend 2000px+)

## Image Set

A complete Amazon listing supports up to 7 images. Images are split into **required** (always generate) and **optional** (generate only when the user requests, or when the product clearly benefits from it).

Ask the user for product details, key selling points, and target audience before starting. By default, generate the 3 required images only.

### Required Images (always generate)

#### Image 1: Main Image (Hero Shot)

The most critical image — determines click-through rate in search results.

- **Pure white background** (RGB 255,255,255) — no gradients, no shadows on background, no off-white
- **Product only** — absolutely no text, logos, badges, watermarks, props, or accessories not included in the sale
- **Fill 85%+ of the frame** — the product should feel large and dominant, with minimal white border
- **Single, clean angle** — front-facing or 3/4 angle that best shows the product's shape and identity
- **Studio-quality lighting** — soft, even lighting with subtle shadow beneath the product for grounding. No harsh reflections or dark spots
- **No mannequins** — for apparel, show on a human model or as a clean flat-lay. Ghost mannequin (invisible mannequin) effect is acceptable

#### Image 2: Lifestyle / In-Use Image

- Product shown in a realistic usage context — a person using it, or the product in its natural environment
- Environment should match the target customer's aspirational setting (modern kitchen, outdoor adventure, minimalist desk, etc.)
- Warm, natural lighting. The scene should feel authentic, not stock-photo-generic
- Product must remain the clear focal point — the scene supports but never overwhelms

#### Image 3: Feature Callout Infographic

- Annotated diagram highlighting 4-6 key selling points with callout lines/icons
- Clean layout: product centered, callout text arranged around it with clear pointers
- Use short, benefit-driven phrases (not feature specs). E.g., "Keeps drinks cold 24 hrs" not "Double-wall vacuum insulation"
- Consistent icon style (all outline or all filled, same line weight)
- Background: solid white or very light neutral. No busy patterns

### Optional Images (generate when user requests or product needs it)

#### Image 4: Alternate Angle / Back View

- Show the product from a different perspective (back, side, top-down, or 3/4 from the opposite side)
- Same pure white background and lighting as the main image
- Reveals details not visible in the hero shot (back panel, ports, closure, label)
- **When to suggest**: products with functional back/side elements (electronics, bags, furniture)

#### Image 5: Detail / Close-Up Shots

- Macro-level close-ups of materials, textures, stitching, hardware, buttons, or key components
- Can be a collage of 2-3 close-ups in a grid layout, or a single dramatic close-up
- Demonstrates build quality and craftsmanship — this image builds trust
- Same lighting temperature as other images for visual consistency
- **When to suggest**: products where material quality is a selling point (leather goods, jewelry, textiles, premium hardware)

#### Image 6: Scale / Dimensions Reference

- Show the product next to a common reference object (hand, phone, pen, coin) or with explicit dimension annotations
- For apparel/wearables: a size chart with clear measurements table
- For multi-size products: side-by-side comparison of available sizes
- **When to suggest**: products where size is frequently misjudged (furniture, bags, small accessories, apparel)

#### Image 7: Package Contents / What's in the Box

- Flat-lay or arranged display of everything included: the product, accessories, cables, manuals, packaging
- Clean white or light background, each item clearly separated and identifiable
- Optional: small text labels identifying each component
- **When to suggest**: products that ship with multiple accessories (electronics kits, tool sets, gift boxes)

## Design Thinking

1. **Understand the purchase decision** — What hesitation stops a buyer? Design each image to remove a specific objection (Is it well-made? Will it fit? What's included? How does it look in real life?)
2. **Design for the search grid first** — The main image competes in a grid of 20+ products at thumbnail size. It must be instantly recognizable, well-lit, and product-dominant. Overly clever compositions fail at thumbnail scale
3. **Tell a visual story** — The required 3 images cover the core narrative: attract (main) → desire (lifestyle) → understand (features). Optional images deepen the story when needed: explore (angles) → trust (details) → confirm (size) → commit (contents)
4. **Consistency is professionalism** — All 7 images must feel like they belong to the same listing. Same color temperature, same quality level, same visual language. Mixed styles signal amateur sellers
5. **Benefit over feature** — Every image should communicate why the customer's life improves, not just what the product is. A lifestyle shot sells the dream; a feature callout sells the solution

## Aesthetics Guidelines

- **Lighting consistency**: Use the same soft, diffused studio lighting across all white-background shots (images 1, 2, 5, 7). Lifestyle shots (image 3) can use warmer natural light but should not clash in color temperature
- **Color accuracy**: Product colors must look accurate — what the customer sees should match what arrives. Avoid over-saturated or heavily graded images. Describe the exact product color in the prompt
- **Composition for square format**: Every image will be viewed in 1:1. Center the product with even margins. For infographic images, maintain a clear central anchor with callouts radiating outward
- **Typography in secondary images**: Use clean, sans-serif fonts. Maximum 2 font sizes (heading + body). Text must be readable at mobile phone size — if a callout requires squinting, it's too small or too wordy
- **Visual hierarchy in infographics**: The product image dominates; text callouts are secondary. Never let annotations overwhelm the product. Use thin callout lines, not thick arrows
- **Professional restraint**: No starburst badges, no "BEST SELLER" stamps, no red/yellow sale graphics, no clip-art icons. These signal cheap quality. Let the product photography speak

## Prompt Rules

- Main image: specify "pure white background RGB 255,255,255, studio photography, product centered, soft even lighting, subtle ground shadow"
- All images should default to photorealistic style ("professional product photography") unless the user or platform context calls for a different approach (e.g., illustrated style for Xiaohongshu)
- Put all text content in double quotes for accurate rendering
- Maintain consistent lighting and color temperature across the set — reference the main image with `--input-image` for subsequent shots
- Describe the product material, color, and finish explicitly (e.g., "brushed stainless steel with matte black silicone grip") — do not leave surface details to chance
