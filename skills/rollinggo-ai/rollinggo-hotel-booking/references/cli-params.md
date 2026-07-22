# CLI Command Complete Parameter Specifications

## Table of Contents

- [hotel-tags](#hotel-tags) — Get search tags
- [search-hotels](#search-hotels) — Search hotels
- [hotel-detail](#hotel-detail) — Hotel details
- [price-confirm](#price-confirm) — Price confirmation
- [book](#book) — Create order
- [orders](#orders) — Query orders

---

## hotel-tags

Get all available hotel filter tags used to build search conditions.

**Input**: None

**Output**:

| Field | Type | Description |
|------|------|------|
| tags | array | List of tags |
| tags[].name | string | Tag name (used for required-tag) |
| tags[].category | string | Tag category (Core facilities, Services & Dining, Views & Rooms, Special selling points, Transport & Payment, Brand & Rating, Hotel type, Family & Kids, Price related, Service details) |
| tags[].description | string | Tag description |

---

## search-hotels

Search for hotel lists based on location, dates, tags, and other conditions.

**Input**:

| CLI Parameter | Type | Required | Description |
|------|------|------|------|
| --origin-query | string | ✅ | User's original query string |
| --place | string | ✅ | Location name (city, attraction, hotel name, etc.) |
| --place-type | string | ✅ | Location type: city, airport, point_of_interest, train_station, subway_station, hotel, district/county, detailed address |
| --country-code | string | ❌ | Country code (e.g., US) |
| --size | integer | ❌ | Return quantity, default 5, max 20 |
| --check-in-date | string | ❌ | Check-in date YYYY-MM-DD |
| --stay-nights | integer | ❌ | Stay nights, default 1 |
| --adult-count | integer | ❌ | Adult count per room, default 2 |
| --star-ratings | string | ❌ | Star rating range, e.g., "4.5,5.0" |
| --distance-in-meter | integer | ❌ | Distance limit (meters), effective for attraction-type locations, default 5000 |
| --required-tag | string | ❌ | Required tag (hard constraint, filters out non-matching) |
| --max-price-per-night | float | ❌ | Maximum price per night |
| --preferred-brand | string | ❌ | Preferred brand (fuzzy match) |

**Output**:

| Field | Type | Description |
|------|------|------|
| success | boolean | Whether successful |
| message | string | Result message |
| hotelInformationList | array | Hotel list |
| hotelInformationList[].hotelId | integer | Hotel ID (passed to hotel-detail) |
| hotelInformationList[].name | string | Hotel name |
| hotelInformationList[].nameEn | string | Hotel English name |
| hotelInformationList[].brand | string | Hotel brand |
| hotelInformationList[].address | string | Hotel address |
| hotelInformationList[].destinationId | string | Destination ID |
| hotelInformationList[].latitude | float | Latitude |
| hotelInformationList[].longitude | float | Longitude |
| hotelInformationList[].distanceInMeters | integer | Distance to target location (meters) |
| hotelInformationList[].starRating | float | Star rating |
| hotelInformationList[].areaCode | string | Country/Region code |
| hotelInformationList[].price.hasPrice | boolean | Whether it has price |
| hotelInformationList[].price.currency | string | Currency |
| hotelInformationList[].price.lowestPrice | float | Lowest price |
| hotelInformationList[].price.message | string | Price message |
| hotelInformationList[].imageUrl | string | Hotel image URL |
| hotelInformationList[].bookingUrl | string | Booking link |
| hotelInformationList[].description | string | Hotel description (HTML format) |
| hotelInformationList[].hotelAmenities | array[string] | Hotel amenities list |
| hotelInformationList[].tags | array[string] | Hotel tags |

---

## hotel-detail

Query all available room types and real-time prices for a single hotel.

**Input**:

| CLI Parameter | Type | Required | Description |
|------|------|------|------|
| --hotel-id | integer | One of two | Hotel ID (preferred) |
| --name | string | One of two | Hotel name (fuzzy match) |
| --check-in-date | string | ❌ | Check-in date YYYY-MM-DD |
| --check-out-date | string | ❌ | Check-out date YYYY-MM-DD |
| --room-count | integer | ❌ | Room count, default 1 |
| --adult-count | integer | ❌ | Adult count per room, default 2 |
| --child-count | integer | ❌ | Child count per room, default 0 |
| --child-age | string | ❌ | Child ages (comma separated) |
| --country-code | string | ❌ | Country code, default US |
| --currency | string | ❌ | Currency, default USD |

**Output**:

| Field | Type | Description |
|------|------|------|
| success | boolean | Whether successful |
| errorMessage | string | Error message (on failure) |
| hotelId | integer | Hotel ID |
| name | string | Hotel name (including English) |
| nameEn | string | Hotel English name |
| checkIn | string | Check-in date |
| checkOut | string | Check-out date |
| bookingUrl | string | Booking link |
| roomRatePlans | array | Room rate plan list |
| roomRatePlans[].roomTypeId | integer | Room type ID |
| roomRatePlans[].roomName | string | Room type name (English) |
| roomRatePlans[].roomNameCn | string | Room type name (Chinese) |
| roomRatePlans[].ratePlanId | string | Rate plan ID (passed to price-confirm) |
| roomRatePlans[].ratePlanName | string | Rate plan name |
| roomRatePlans[].bedType | integer | Bed type code |
| roomRatePlans[].bedTypeDescription | string | Bed type description (e.g., "1 King", "2 Single") |
| roomRatePlans[].currency | string | Currency |
| roomRatePlans[].totalPrice | float | Total price (including tax) |
| roomRatePlans[].totalSalesRate | float | Average nightly price (can be null) |
| roomRatePlans[].inventoryCount | integer | Remaining inventory (can be null) |
| roomRatePlans[].isOnRequest | boolean | Whether manual confirmation is needed (can be null) |
| roomRatePlans[].cancellationPolicies | array | Cancellation policy list |
| roomRatePlans[].cancellationPolicies[].fromDate | string | Cancellation fee effective time (ISO 8601) |
| roomRatePlans[].cancellationPolicies[].toDate | string | End time (can be null) |
| roomRatePlans[].cancellationPolicies[].amount | float | Cancellation fee amount |
| roomRatePlans[].cancellationPolicies[].percent | integer | Cancellation fee percentage (can be null) |
| roomRatePlans[].cancellationPolicies[].description | string | Cancellation policy description (can be null) |

---

## price-confirm

Lock the real-time price of the selected room type and obtain a booking reference number. referenceNo is valid for about 15-30 minutes, must be re-called if expired.

**Input**:

| CLI Parameter | Type | Required | Description |
|------|------|------|------|
| --hotel-id | integer | ✅ | Hotel ID |
| --rate-plan-id | string | ✅ | Rate plan ID (obtained from hotel-detail) |
| --rooms | integer | ✅ | Room count |
| --check-in-date | string | ✅ | Check-in date YYYY-MM-DD |
| --check-out-date | string | ✅ | Check-out date YYYY-MM-DD |
| --adults | integer | ✅ | Adult count per room |
| --children | integer | ❌ | Child count per room |
| --child-age | string | ❌ | Child ages (comma separated) |
| --nationality | string | ❌ | Nationality code, default US |
| --currency | string | ❌ | Currency, default USD |

**Output**:

| Field | Type | Description |
|------|------|------|
| success | boolean | Whether successful |
| message | string | Result message |
| priceDetailsInfo.referenceNo | string | Booking reference number (passed to book) |
| priceDetailsInfo.checkInDate | string | Check-in date |
| priceDetailsInfo.checkOutDate | string | Check-out date |
| priceDetailsInfo.hotelList | array | Hotel list |
| priceDetailsInfo.hotelList[].hotelName | string | Hotel name |
| priceDetailsInfo.hotelList[].totalPrice | float | Locked total price |
| priceDetailsInfo.hotelList[].ratePlanList | array | Room rate plan list |
| priceDetailsInfo.hotelList[].ratePlanList[].roomName | string | Room type name |
| priceDetailsInfo.hotelList[].ratePlanList[].totalPrice | float | Total price |
| priceDetailsInfo.hotelList[].ratePlanList[].averagePrice | float | Average nightly price |
| priceDetailsInfo.hotelList[].ratePlanList[].priceList | array | Daily price list |
| priceDetailsInfo.hotelList[].cancellationPolicyList | array | Cancellation policy |

---

## book

Create an official order using the referenceNo and return the payment link.

**Input**:

| CLI Parameter | Type | Required | Description |
|------|------|------|------|
| --reference-no | string | ✅ | Booking reference number (from price-confirm) |
| --first-name | string | ✅ | Contact first name (Pinyin or English) |
| --last-name | string | ✅ | Contact last name (Pinyin or English) |
| --guests | string | ❌ | Guest info JSON (usually not needed, defaults to contact info) |

**Output**:

| Field | Type | Description |
|------|------|------|
| success | boolean | Whether successful |
| message | string | Result message (contains reason on failure) |
| bookingResult.orderNo | string | Order number |
| bookingResult.paymentType | string | Payment type (currently fixed to "URL") |
| bookingResult.paymentUrl | string | Payment link |

---

## orders

Query all historical hotel orders for the current user.

**Input**: None

**Output**:

| Field | Type | Description |
|------|------|------|
| message | string | Query result message |
| orderInfoList | array | Order list |
| orderInfoList[].hotelBookingInfo.referenceNo | string | Booking reference number |
| orderInfoList[].hotelBookingInfo.status | string | Order status code ("1"=Pending payment, "3"=Completed/Closed) |
| orderInfoList[].hotelBookingInfo.mainOrderNo | string | Main order number |
| orderInfoList[].hotelBookingInfo.subOrderNo | string | Sub-order number |
| orderInfoList[].hotelBookingInfo.checkInDate | string | Check-in date |
| orderInfoList[].hotelBookingInfo.checkOutDate | string | Check-out date |
| orderInfoList[].hotelBookingInfo.numOfRooms | integer | Room count |
| orderInfoList[].hotelBookingInfo.nights | integer | Stay nights |
| orderInfoList[].hotelBookingInfo.totalPrice | float | Order total price |
| orderInfoList[].hotelBookingInfo.paymentStatus | string | Payment status (CREATED=Pending, REFUNDED=Refunded) |
| orderInfoList[].hotelBookingHotel.hotelName | string | Hotel name |
| orderInfoList[].hotelBookingHotel.hotelAddress | string | Hotel address |
| orderInfoList[].hotelBookingHotel.starRating | string | Star rating |
| orderInfoList[].hotelContact.firstName | string | Contact first name |
| orderInfoList[].hotelContact.lastName | string | Contact last name |
| orderInfoList[].hotelRatePlanInfo.roomName | string | Room type name |
| orderInfoList[].hotelRatePlanInfo.totalPrice | float | Total price |
