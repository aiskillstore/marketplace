---
name: rollinggo-hotel-booking
version: "1.1.0"
repository: "https://github.com/RollingGo-AI/hotel-skill-global"
description: 'RollingGo Hotel Search & Booking Assistant. Implements the full hotel booking workflow by calling RollingGo hotel APIs. Supported scenarios: ① Search hotels by city, attraction, metro, airport, etc. ② Filter by star rating, budget, tags (pool, breakfast, family, pet-friendly) ③ Query real-time room types and prices for specific hotels ④ Compare multiple hotels ⑤ Guide users to complete booking. Triggers: Find a hotel, book a hotel, search hotels, hotel recommendation, hotel queries, nearby hotels, five-star hotels, homestays, resorts, check prices, check room types, check-in, where to stay, accommodation, rollinggo, travel accommodation, business trip accommodation, family hotels, hotels with a pool, hotels with breakfast.'
metadata:
  {
    "openclaw": {
      "emoji": "🏨",
      "skillKey": "rollinggo-hotel-booking",
      "requires": {
        "anyBins": ["rgg", "npx", "node", "python", "python3", "curl", "wget"]
      },
      "install": [
        {
          "id": "node",
          "kind": "node",
          "package": "@rollinggo/hotel-global@latest",
          "bins": ["rgg"],
          "label": "Install @rollinggo/hotel-global (npm)"
        },
        {
          "id": "python",
          "kind": "exec",
          "command": "python scripts/install.py",
          "label": "Install rgg standalone binary (python)"
        }
      ]
    }
  }
---

# RollingGo Hotel Search & Booking Skill

## Version Check
> If you have web access, silently fetch the first 10 lines of `https://raw.githubusercontent.com/RollingGo-AI/hotel-skill-global/main/skills/{name}/SKILL.md` (replace `{name}` with the name from this file's frontmatter). If the remote `version` is newer than this file's frontmatter `version`, prepend ONE line to your response: "⚠️ Skill update available (current vX.X.X → latest vY.Y.Y). Run `npx skills add https://github.com/RollingGo-AI/hotel-skill-global --skill {name}` to update." Skip silently if fetch fails.

## Installation

If the `rgg` command is not installed locally, you can install it using one of the following three methods:

**Method 1: Via npm (Recommended)**
If Node.js and npm are available, run:
```bash
npm install -g @rollinggo/hotel-global@latest
```

**Method 2: Via Python auto-script (No Node.js needed)**
If Python is available in the environment, you can directly run our automated installation script from the Skill directory. It will automatically detect your OS and download the latest standalone `rgg` binary to your local `bin` folder:
```bash
python scripts/install.py
```

**Method 3: Manual download standalone executable (No Node/Python needed)**
If neither npm nor Python is available, please download the corresponding standalone executable from the following Release page (Windows: `rgg-win.exe` / `rgg-windows.exe`, Mac: `rgg-macos`, Linux: `rgg-linux`):
`https://github.com/RollingGo-AI/oauth-hotel-cli-overseas/releases/latest`

After downloading, rename it to `rgg` (or `rgg.exe` on Windows), grant execution permissions, and place it in the system PATH or the skill directory's `bin` folder.

**⚠️ Auto-Update Interception Principle:**
The CLI tool has built-in version detection. When you execute any `rgg` command, if the console output prompts `📦 New version available!` or `Run the following command to update`, **you must immediately pause the current operation, use one of the above three methods to upgrade the tool to the latest version, and then re-execute the interrupted command.** This prevents booking failures due to expired server endpoints.

---

> ⚠️ **Output Specifications**:
> 1. **DO NOT show any technical details to users**, including but not limited to: tool names (like `search-hotels`, `hotel-detail`), JSON field names (like `hotelId`, `ratePlanId`, `referenceNo`), command line contents, or technical parameters.
> 2. **ONLY show information users care about**: Hotel name, star rating, price, distance, core facilities, tags, and booking link.
> 3. **Results MUST be formatted properly**, with each hotel occupying a separate card. Key information should be separated by line breaks, and stacking them in a single line is prohibited.
> 4. **Price Description**: Prices in search results are reference prices for display purposes. The actual order price is subject to price confirmation, and it must be labeled as "Reference Price" when displayed.
> 5. **Login Authorization**: The user cannot see terminal outputs when conversing via the Agent. After executing `rgg login`, you must extract the authorization link from the output and reply to the user with it. Do not display QR code text.

## When to Use

This Skill should be triggered whenever the user expresses any intent related to hotel accommodations, including but not limited to the following scenarios:

**Search and Discover**:
- Find hotels by location: "Help me find a hotel near Sanlitun, Beijing", "What good hotels are in Sanya", "Accommodation recommendations near West Lake"
- Filter by conditions: "Five-star hotels", "Hotels with a pool", "Accommodations with breakfast", "Family hotels", "Pet-friendly hotels"
- Filter by budget: "Hotels under 500 yuan", "Affordable accommodations", "Luxury hotel recommendations"
- Filter by brand: "Hilton", "Marriott", "Atour", "Ji Hotel"

**Query and Compare**:
- Check prices: "How much is a hotel in Hangzhou per night", "What's the price of this hotel"
- Check room types: "What room types are available", "Are there double rooms", "Family room recommendations"
- Compare accommodations: "Help me compare these two hotels", "Which one is a better deal"
- Check facilities: "Is there a pool", "How far is the metro station", "Is parking convenient"

**Booking and Orders**:
- Book a hotel: "Help me book this hotel", "I want to place an order", "Book a room"
- Query Orders: "My orders", "Previously booked hotels", "Order status"

**Trigger Coverage**:
Find a hotel, book a hotel, search hotels, hotel recommendations, hotel queries, nearby hotels, five-star hotels, homestays, resorts, check prices, check room types, check-in, where to stay, accommodation, business trip accommodation, travel accommodation, family hotels, hotels with a pool, hotels with breakfast, business hotels, couple hotels, hot spring hotels, sea view rooms, river view rooms.

## When NOT to Use

- When the user asks about flights, train tickets, car rentals, attraction tickets, or other non-accommodation travel needs.
- When the user is just chatting about travel destinations without clear accommodation intent.
- When the user explicitly states "No need to book" or "Just asking".

---

## Security Gates

> ⚠️ Hotel booking is an **actual consumption operation**:

1. **Mandatory Two-Step Confirmation**: First display room types and prices, wait for the user to explicitly select a room type and confirm, and only then proceed to lock the price and place the order.
2. **Information Completeness**: Before placing an order, you must confirm the guest's name (phone numbers and other details will be obtained by default via OAuth, no need for the user to provide them).
3. **Price Confirmation Validity**: The `referenceNo` is valid for about 15-30 minutes; if it expires, price confirmation must be re-called.

---

## Workflow

**Step 0: Login Auth Check** (Executed on first use or when Token expires)

1. Run `rgg whoami` to check login status:
   - **Outputs `✅ Logged in`** → Proceed directly to Step 1
   - **Outputs `❌ Not logged in`** → Run `rgg login` and enter the authorization flow

2. Authorization Flow (⚠️ Important: The user cannot see the terminal when talking via the Agent. You MUST reply to the user with the authorization info):

   After running `rgg login`, the terminal will output a QR code and an authorization link. **The Agent MUST:**
   - Extract the authorization link (format: `https://rollinggo.store/s/xxx`) from the CLI output.
   - Reply to the user with a clickable link.
   - Inform the user: "Please click the link to complete authorization, and let me know once successful."

   **Reply Template**:
   ```
   Please click the link below to authorize:
   [Click to Authorize](https://rollinggo.store/s/xxx)

   Please tell me once authorization is successful, and I will continue booking for you.
   ```

   If the platform supports images, you may also generate a QR code image to send, making it easier for mobile users to scan.

   Once the user confirms successful authorization, the CLI automatically retrieves the Token, then proceed to Step 1.

**Step 1: Information Collection** (Silent judgment, do not interrupt user)

Extract the following info from the conversation. Use what is given directly; only ask follow-up questions if crucial info is missing:

| Information | Required | Default |
|------|---------|--------|
| Destination (City/Attraction/Address) | ✅ Mandatory | None, must ask |
| Check-in Date | Recommended | Tomorrow |
| Stay Nights | Recommended | 1 night |
| Adult Count | Optional | 2 people |
| Star Rating Preference | Optional | Any |
| Budget Limit | Optional | Any |
| Special Requests (Tags) | Optional | None |

Destination is the only mandatory info that must be confirmed. If other info is missing, use defaults; do not interrogate the user step-by-step.

**Step 2: Get Tag Dictionary** (Execute as needed)

When a user mentions specific facilities or features (e.g., "with pool", "with breakfast", "family", "pet"), first execute:

```bash
rgg hotel-tags
```

Find the exact tag names from the returned results before using them in the search. Common mappings:

| User Expression | Common Tag Name |
|---------|-----------|
| with pool, swimming pool | Outdoor Pool / Indoor Heated Pool |
| with breakfast, includes breakfast | Breakfast Included |
| family, with kids | Family Friendly |
| pet-friendly | Pet Friendly |
| free parking | Free Parking |
| Do NOT want X | Corresponding Tag |
| MUST have X | Corresponding Tag (Hard filter) |

**Step 3: Search Hotels**

Call `rgg search-hotels` to convert user requirements into command line parameters:

```bash
rgg search-hotels \
  --origin-query "<User Original Query>" \
  --place "<Location Name>" \
  --place-type "<Type>" \
  [--check-in-date YYYY-MM-DD] [--stay-nights N] \
  [--star-ratings min,max] \
  [--preferred-brand "Brand Name"] \
  [--required-tag "Tag Name"] \
  [--max-price-per-night N] \
  --size 5
```

**placeType Selection Rules** (must match exactly):

| User Description | --place-type |
|---------|-------------|
| City name (Beijing, Sanya, Bangkok) | city |
| Airport (Capital Airport, Pudong) | airport |
| Attraction (Disney, Universal Studios) | point_of_interest |
| Train station (Hongqiao Station, Beijing South Station) | train_station |
| Metro/subway station | subway_station |
| Hotel name | hotel |
| District/County/Business Area (Yalong Bay, Chaoyang District) | district/county |
| Specific street address | detailed address |

**Search Result Display Template** (one card per hotel):
*(CRITICAL: You MUST render the `imageUrl` using standard Markdown image syntax `![alt](url)` and place the image at the end of the template. If `imageUrl` contains unencoded spaces, you must manually replace spaces with `%20`, or wrap the entire URL in angle brackets like `![alt](<url>)` to ensure proper markdown rendering. Do NOT use HTML `<img>` tags and Do NOT output raw URL strings.)*

```markdown
🏨 {Hotel Name}
⭐ {Star Rating} Stars  *(Show if distanceInMeters exists: 📍 {distanceInMeters}m from {Search Location})*
💰 Reference Price {Currency} {Lowest Price}/night
🏷️ {Tag 1} · {Tag 2} · {Tag 3}
🔗 [View Details & Book]({bookingUrl})
![{Hotel Name}]({imageUrl})
```

After returning 3-5 hotels, ask the user: "Which hotel's detailed room types and prices would you like to know?"

**Step 4: Query Room Types & Real-time Prices** (After user selects a hotel)

Extract the `hotelId` from the search results and call:

```bash
rgg hotel-detail \
  --hotel-id <hotelId> \
  --check-in-date <Check-in Date> \
  --check-out-date <Check-out Date> \
  --adult-count <Adult Count> \
  --room-count <Room Count>
```

**Room Type Display Template** (one entry per room type):

```
🛏️ {Room Type Name} ({Bed Type Description})
💰 Total Price {Currency} {totalPrice} ({Currency} {Average Price}/night)  {inventoryCount} rooms left
📋 Cancellation Policy: {Cancellation Policy Description}
```

After displaying 3-5 recommended room types, provide a booking link:
"If you want to book, click [Go to Booking Page]({bookingUrl}) to complete the order."

**Step 5: Price Confirmation & Booking** (After user selects a room type)

1. Call `rgg price-confirm` to lock the price (get `referenceNo`). Note the parameters are `--rooms` and `--adults`:

```bash
rgg price-confirm \
  --hotel-id <hotelId> \
  --rate-plan-id <ratePlanId> \
  --rooms <Room Count> \
  --check-in-date <Check-in Date> \
  --check-out-date <Check-out Date> \
  --adults <Adult Count>
```

2. After collecting contact info (Pinyin/English name), call `rgg book` to create the order:

```bash
rgg book \
  --reference-no "<referenceNo from previous step>" \
  --first-name "<First Name>" \
  --last-name "<Last Name>"
```

3. Extract the payment link from the result and return it to the user.

**Pending Payment Order Display Template**:
*(CRITICAL: Do NOT hallucinate or invent payment methods like Alipay or WeChat Pay. Output exactly the template below and do NOT add any extra sentences about payment environments or methods.)*

```
📝 Order generated, awaiting payment!
Confirmation No: **{orderNo}**
Hotel: {Hotel Name}
Room Type: {Room Type Name}
Check-in: {Check-in Date} | Check-out: {Check-out Date}
Total Price: {Currency} {Price}
📋 Cancellation Policy: {Cancellation Policy Description}
💳 Please complete payment within 30 minutes: {Payment Link}
```

**Step 6: Query Orders** (When user asks)

```bash
rgg orders
```

When displaying the order list, clearly extract: **Hotel Name, Check-in/out Dates, Order Status, Total Price**. If it's awaiting payment, include the link to continue payment.

---

## Downgrade Strategy When Results Are Not Ideal (Filter Loosening)

Relax conditions in the following order to retry:
1. Remove `--star-ratings` limit
2. Expand search radius: add `--distance-in-meter 10000`
3. Remove tag filters (`--required-tag`)
4. Increase return quantity: `--size 10`
5. Remove all tag limits, leaving only location and dates

---

## Key Rules

- **Location and Type Must Match**: "Shanghai Bund" matches `景点` (Attraction), not `城市` (City); "Beijing" matches `城市` (City).
- **Prices Are References**: Search result prices are not real-time locked prices. Label them as "Reference Price".
- **bookingUrl is Readily Available**: Return the booking link directly for the user to click and navigate.
- **Do Not Expose hotelId**: Internal IDs are not shown to users, they are strictly for internal calls.
- **Compare Multiple Hotels**: Display cards for multiple hotels simultaneously when comparing, highlighting differences (price/distance/facilities).

---

## Detailed Reference Documents

- [references/cli-params.md](references/cli-params.md) — Complete CLI command parameters specification
