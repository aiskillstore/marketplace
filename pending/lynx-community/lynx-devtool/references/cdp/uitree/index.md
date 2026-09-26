# UITree Methods

The `UITree` domain exposes the rendered native UI tree with metadata such as tag names, node indices, props, and labels. Available metadata differs by platform: Android and Darwin expose `tagName`, `nodeIndex`, `props`, and `label`; Harmony exposes the basic `name`, `id`, `frame`, and `children` fields.

## Methods

- [UITree.enable](UITree.enable.md) - Enable the UITree domain
- [UITree.getLynxUITree](UITree.getLynxUITree.md) - Get the rendered Lynx UI tree
- [UITree.getUIInfoForNode](UITree.getUIInfoForNode.md) - Get detailed platform UI information for one node
