# Amazon Scrape API Reference

Scrape Amazon product data: details, search results, category listings, best sellers, and more.

## Endpoint

```
POST https://scrapeapi.pangolinfo.com/api/v1/scrape
```

Note: Amazon uses **v1** endpoint, not v2 (which is used by Google SERP APIs).

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

## Request Body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| url | Yes | string | Amazon page URL |
| format | Yes | string | `"json"`, `"rawHtml"`, or `"markdown"` |
| parserName | Yes | string | Parser type (see below) |
| bizContext | Yes | object | Business context |
| bizContext.zipcode | Yes | string | US zipcode for localized pricing |

## Parser Types

| Parser | Use Case | URL Example |
|--------|----------|-------------|
| `amzProductDetail` | Single product page | `https://www.amazon.com/dp/B0DYTF8L2W` |
| `amzKeyword` | Keyword search results | `https://www.amazon.com/s?k=wireless+mouse` |
| `amzProductOfCategory` | Category listing | Category page URL |
| `amzProductOfSeller` | Seller's products | Seller storefront URL |
| `amzBestSellers` | Best sellers ranking | Best sellers page URL |
| `amzNewReleases` | New releases ranking | New releases page URL |
| `amzFollowSeller` | Variants / other sellers | Product page URL |

## Request Example

```json
{
  "url": "https://www.amazon.com/dp/B0DYTF8L2W",
  "format": "json",
  "parserName": "amzProductDetail",
  "bizContext": {
    "zipcode": "10041"
  }
}
```

## Response

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "json": [
      {
        "asin": "B0DYTF8L2W",
        "title": "Product Title",
        "brand": "Brand Name",
        "price": "$29.99",
        "star": "4.5",
        "rating": "1,234",
        "image": "https://m.media-amazon.com/images/...",
        "images": ["url1", "url2"],
        "inStock": "In Stock",
        "seller": "Seller Name",
        "features": ["Feature 1", "Feature 2"],
        "category_name": "Electronics",
        "bestSellersRank": "#1,234",
        "deliveryTime": "Tomorrow",
        "sales": "10K+ bought in past month"
      }
    ],
    "url": "https://www.amazon.com/dp/B0DYTF8L2W",
    "taskId": "02b3e90810f0450ca6d41244d6009d0f"
  }
}
```

### Product Detail Fields (amzProductDetail)

**Core:**
`asin`, `title`, `brand`, `price`, `strikethroughPrice`, `star`, `rating`, `image`, `images`, `highResolutionImages`

**Inventory & Seller:**
`inStock`, `merchant_id`, `seller`, `shipper`, `has_cart`

**Attributes:**
`color`, `size`, `features`, `badge`, `acBadge` (Amazon's Choice)

**Category & Ranking:**
`category_id`, `category_name`, `bestSellersRank`

**Dimensions:**
`pkg_dims`, `pkg_weight`, `product_dims`, `product_weight`

**Additional:**
`deliveryTime`, `first_date`, `coupon`, `sales`, `ratingDistribution`, `reviews`, `aiReviewsSummary`, `productDescription`, `productOverview`, `attributes`, `otherAsins`

### Keyword Search Fields (amzKeyword)

`asin`, `title`, `price`, `star`, `rating`, `image`, `sales`, `nature_rank`, `sponsored`, `spRank`, `badge`, `delivery`

### Ranking Fields (amzBestSellers / amzNewReleases)

`asin`, `rank`, `title`, `price`, `star`, `rating`, `image`

### Variant Fields (amzFollowSeller)

`options`, `price`, `delivery`, `shipsFrom`, `soldBy`

## Supported Regions

US, UK, Canada, Germany, France, Japan, Italy, Spain, Australia, Mexico, Saudi Arabia, UAE, Brazil. Use the corresponding Amazon domain in the URL.

## Cost

| Format | Credits |
|--------|---------|
| `json` | 1 per request |
| `rawHtml` / `markdown` | 0.75 per request |

Average response time: ~5 seconds.
