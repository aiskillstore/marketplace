---
name: 3d-model-generation
description: Generate 3D models using each::sense AI. Create 3D assets from text or images for games, products, architecture, characters, vehicles, and more with PBR textures.
metadata:
  author: eachlabs
  version: "2.0"
---

# 3D Model Generation

Generate production-ready 3D models using each::sense. This skill creates 3D assets from text descriptions or reference images, suitable for games, e-commerce, architecture, product visualization, and more.

## Features

- **Text-to-3D**: Generate 3D models from natural language descriptions
- **Image-to-3D**: Convert 2D images into 3D models
- **Character Models**: Create humanoid and creature 3D characters
- **Product Models**: E-commerce ready product 3D assets
- **Environment/Scene**: Generate 3D environments and landscapes
- **Game Assets**: Low-poly and stylized game-ready models
- **Furniture**: Interior design and home decor 3D models
- **Vehicles**: Cars, aircraft, and transportation 3D assets
- **Architecture**: Buildings, structures, and architectural elements
- **PBR Textures**: Generate physically-based rendering textures for 3D models

## Quick Start

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D model of a medieval treasure chest with gold trim and iron locks"}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

## Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| GLB | .glb | Universal format, web/AR/VR, Unity, Unreal |
| GLTF | .gltf | Web applications, three.js |
| OBJ | .obj | Legacy support, 3D printing |
| FBX | .fbx | Animation, game engines |
| USDZ | .usdz | Apple AR Quick Look |

## Use Case Examples

### 1. Text-to-3D Model Generation

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D model of a futuristic sci-fi helmet with glowing blue visor and matte black finish. High detail, suitable for game assets."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 2. Image-to-3D Conversion

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Convert this product image into a 3D model. Maintain accurate proportions and surface details for e-commerce use."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max",
    "image_urls": ["https://example.com/product-image.jpg"]
  }'
```

### 3. Character 3D Model

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D character model of a fantasy warrior elf with ornate silver armor, long pointed ears, and a flowing cape. T-pose, game-ready topology."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 4. Product 3D Model

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Generate a 3D model of a premium wireless headphone. Matte black with rose gold accents, leather ear cushions. High detail for product visualization and AR try-on."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 5. Environment/Scene 3D

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D environment scene of a Japanese zen garden with a stone pathway, bamboo fence, koi pond, and cherry blossom trees. Stylized low-poly aesthetic for mobile games."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 6. Game Asset 3D Model

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a low-poly 3D game asset pack: a wooden crate, barrel, torch, and treasure chest. Stylized textures, optimized for real-time rendering, under 5000 triangles each."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "eco"
  }'
```

### 7. Furniture 3D Model

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Generate a 3D model of a mid-century modern armchair. Walnut wood frame with teal velvet upholstery. Realistic materials for interior design visualization and AR placement."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 8. Vehicle 3D Model

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D model of a vintage 1960s muscle car. Cherry red metallic paint, chrome details, whitewall tires. High detail exterior suitable for automotive visualization."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 9. Architecture 3D Model

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Generate a 3D architectural model of a modern minimalist house. Two stories, large glass windows, flat roof, concrete and wood exterior. Include surrounding landscape."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 10. PBR Texture Generation for 3D

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Generate PBR texture maps for weathered bronze metal. Include albedo, normal, roughness, metallic, and ambient occlusion maps. 2K resolution, tileable."}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

## Best Practices

### Model Quality
- **Be specific**: Include material types (metal, wood, fabric), surface finish (matte, glossy), and style (realistic, stylized, low-poly)
- **Specify use case**: Mention if it's for games (optimized), AR/VR, 3D printing, or visualization
- **Include scale reference**: Describe size when relevant for proper proportions

### Topology Guidelines
- **Game-ready**: Request optimized polygon count and clean topology
- **Animation-ready**: Specify T-pose for characters, request proper edge loops
- **3D printing**: Ask for watertight meshes and manifold geometry

### Texture Quality
- **PBR materials**: Request specific texture maps (albedo, normal, roughness, metallic, AO)
- **Resolution**: Specify texture resolution (1K, 2K, 4K) based on use case
- **Tileable**: Request seamless/tileable textures for repeating surfaces

## Prompt Tips for 3D Generation

When creating 3D models, include these details in your prompt:

1. **Object description**: What is the object? Be specific about type and style
2. **Materials**: What materials make up the object? (metal, wood, plastic, fabric)
3. **Surface finish**: Matte, glossy, brushed, weathered, etc.
4. **Style**: Realistic, stylized, low-poly, cartoon, photorealistic
5. **Use case**: Game asset, product visualization, AR, 3D printing
6. **Technical specs**: Polygon count, texture resolution if needed

### Example Prompt Structure

```
"Create a 3D model of [object description] with [materials/colors].
Style: [realistic/stylized/low-poly].
Use case: [game/AR/visualization/printing].
[Additional requirements like texture maps, polygon count, etc.]"
```

## Mode Selection

Ask your users before generating:

**"Do you want fast & cheap, or high quality?"**

| Mode | Best For | Speed | Quality |
|------|----------|-------|---------|
| `max` | Final production assets, hero models, product shots | Slower | Highest |
| `eco` | Quick prototypes, concept exploration, bulk generation | Faster | Good |

## Multi-Turn 3D Model Iteration

Use `session_id` to iterate on 3D models:

```bash
# Initial model
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D model of a fantasy sword with dragon motifs"}],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "sword-project-001"
  }'

# Iterate based on feedback
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Add more intricate engravings on the blade and make the dragon head on the hilt more prominent"}],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "sword-project-001"
  }'

# Request variations
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create 2 more variations: one with ice theme and one with fire theme"}],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "sword-project-001"
  }'
```

## Batch Asset Generation

Generate multiple 3D assets for a project:

```bash
# Asset 1 - Props
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D model of a medieval wooden tavern table with benches"}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "eco",
    "session_id": "medieval-tavern-pack"
  }'

# Asset 2 - Environment piece
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create a 3D model of a stone fireplace with crackling fire effect placeholder"}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "eco",
    "session_id": "medieval-tavern-pack"
  }'

# Asset 3 - Decorative
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "Create 3D models of tavern decorations: hanging lantern, wall-mounted deer head, and wooden mug"}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "eco",
    "session_id": "medieval-tavern-pack"
  }'
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Failed to create prediction: HTTP 422` | Insufficient balance | Top up at eachlabs.ai |
| Content policy violation | Prohibited content | Adjust prompt to comply with content policies |
| Timeout | Complex generation | Set client timeout to minimum 10 minutes |
| Invalid image URL | Unreachable image | Ensure image URL is publicly accessible |

## Related Skills

- `each-sense` - Core API documentation
- `product-photo-generation` - Product photography and visualization
- `image-generation` - 2D image generation for reference images
