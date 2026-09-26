# DOM Methods

## Coordinate Guide

- `DOM.getNodeForLocation` and `DOM.getBoxModel` use CDP logical coordinates.
- `Input.emulateTouchFromMouseEvent` is designed to consume the same logical coordinates for the current mode.
- Recommended click flow:
  1. Find the target node with `DOM.querySelector`, `DOM.performSearch`, or `DOM.getDocument`.
  2. Use `DOM.scrollIntoViewIfNeeded` if needed.
  3. Use `DOM.getBoxModel` to compute a target point, usually the center of `model.content` or `model.border`.
  4. Use `DOM.getNodeForLocation` to validate the point.
  5. Pass the same `x/y` to `Input.emulateTouchFromMouseEvent`.
- Do not derive click coordinates from screenshots or apply screenshot pixel scaling to DOM-derived points.
- If a validated point still misses, see [Click Coordinate Troubleshooting](../../troubleshooting/click-coordinates.md).

## Document Operations

- [DOM.enable](DOM.enable.md) - Enable DOM domain events and options
- [DOM.disable](DOM.disable.md) - Disable DOM domain
- [DOM.getDocument](DOM.getDocument.md) - Get document root node
- [DOM.getDocumentWithBoxModel](DOM.getDocumentWithBoxModel.md) - Get document with box model
- [DOM.requestChildNodes](DOM.requestChildNodes.md) - Request child node information

## Node Operations

- [DOM.describeNode](DOM.describeNode.md) - Describe a DOM node
- [DOM.getBoxModel](DOM.getBoxModel.md) - Get element's box model
- [DOM.setAttributesAsText](DOM.setAttributesAsText.md) - Set attributes as text
- [DOM.getNodeForLocation](DOM.getNodeForLocation.md) - Get node by location
- [DOM.pushNodesByBackendIdsToFrontend](DOM.pushNodesByBackendIdsToFrontend.md) - Map backend node IDs to frontend node IDs
- [DOM.focus](DOM.focus.md) - Focus a node

## HTML Operations

- [DOM.getOuterHTML](DOM.getOuterHTML.md) - Get outer HTML

## Selectors

- [DOM.querySelector](DOM.querySelector.md) - CSS selector query
- [DOM.querySelectorAll](DOM.querySelectorAll.md) - CSS selector query all

## Attribute Operations

- [DOM.innerText](DOM.innerText.md) - Get inner text
- [DOM.getAttributes](DOM.getAttributes.md) - Get attributes

## Search Functions

- [DOM.performSearch](DOM.performSearch.md) - Perform search
- [DOM.getSearchResults](DOM.getSearchResults.md) - Get search results
- [DOM.discardSearchResults](DOM.discardSearchResults.md) - Discard search results

## View Operations

- [DOM.scrollIntoViewIfNeeded](DOM.scrollIntoViewIfNeeded.md) - Scroll into view
- [DOM.getOriginalNodeIndex](DOM.getOriginalNodeIndex.md) - Get original node index
