---
name: unreal-engine-developer
description: Expert Unreal Engine 5 developer and technical artist for complete game development via agentic coding. Enables AI-driven control of Unreal Editor through MCP, Python scripting, Blueprints, and C++ for level design, asset management, gameplay programming, and visual development.
---

# Unreal Engine Developer & Technical Artist

## Overview

This skill enables complete game development in Unreal Engine 5 through agentic coding. It provides expertise in:

- **MCP Integration** - Control Unreal Editor via Model Context Protocol
- **Python Automation** - Editor scripting and pipeline automation
- **Blueprint Development** - Visual scripting and node graph manipulation
- **C++ Programming** - Engine extension and gameplay systems
- **Technical Art** - Materials, shaders, VFX, and procedural content
- **Level Design** - World building, lighting, and environment art

## MCP Server Setup

### Option 1: runreal/unreal-mcp (Recommended - No Plugin Required)

Uses Unreal's built-in Python Remote Execution. Supports full Unreal Python API.

**Prerequisites:**
- Unreal Engine 5.4+
- Node.js with npx

**Unreal Editor Setup:**
1. Edit → Plugins → Enable "Python Editor Script Plugin"
2. Edit → Project Settings → Search "Python" → Enable "Remote Execution"
3. Restart Editor

**MCP Client Config:**
```json
{
  "mcpServers": {
    "unreal": {
      "command": "npx",
      "args": ["-y", "@runreal/unreal-mcp"]
    }
  }
}
```

**Available Tools:**
| Tool | Description |
|------|-------------|
| `editor_run_python` | Execute any Python within Unreal Editor |
| `editor_list_assets` | List all Unreal assets |
| `editor_export_asset` | Export asset to text |
| `editor_get_asset_info` | Get asset info including LOD levels |
| `editor_search_assets` | Search assets by name/path/class |
| `editor_get_world_outliner` | Get all actors with properties |
| `editor_create_object` | Create new actor in world |
| `editor_update_object` | Update existing actor |
| `editor_delete_object` | Delete actor from world |
| `editor_console_command` | Run console command |
| `editor_take_screenshot` | Capture viewport screenshot |
| `editor_move_camera` | Position viewport camera |

### Option 2: chongdashu/unreal-mcp (Plugin-Based)

Provides deeper Blueprint and node graph control via C++ plugin.

**Prerequisites:**
- Unreal Engine 5.5+
- Python 3.12+
- uv package manager

**Installation:**
1. Copy `MCPGameProject/Plugins/UnrealMCP` to your project's Plugins folder
2. Generate Visual Studio project files
3. Build project with plugin

**MCP Client Config:**
```json
{
  "mcpServers": {
    "unrealMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "<path/to/Python>",
        "run",
        "unreal_mcp_server.py"
      ]
    }
  }
}
```

**Additional Capabilities:**
- Create Blueprint classes with custom components
- Add and configure components (mesh, camera, light)
- Manipulate Blueprint node graphs
- Add event nodes (BeginPlay, Tick)
- Create function call nodes and connect them
- Add variables with types and defaults

---

## Python Scripting Reference

### Enable Python in Unreal

1. Edit → Plugins → Enable "Python Editor Script Plugin"
2. Edit → Plugins → Enable "Editor Scripting Utilities"
3. Restart Editor

Unreal embeds Python 3.11.8 - no separate installation needed.

### Core API Patterns

```python
import unreal

# Asset Registry
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_assets_by_path('/Game/MyFolder', recursive=True)

# Editor Utility
editor_util = unreal.EditorUtilityLibrary()
selected_assets = editor_util.get_selected_assets()

# Actor Operations
world = unreal.EditorLevelLibrary.get_editor_world()
actors = unreal.EditorLevelLibrary.get_all_level_actors()

# Spawn Actor
location = unreal.Vector(0, 0, 100)
rotation = unreal.Rotator(0, 0, 0)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, location, rotation
)

# Set Properties
actor.set_actor_label('MyActor')
actor.set_actor_location(unreal.Vector(100, 200, 300), False, False)
actor.set_actor_rotation(unreal.Rotator(0, 45, 0), False)

# Static Mesh Component
mesh_component = actor.static_mesh_component
mesh_component.set_static_mesh(
    unreal.load_asset('/Game/Meshes/MyMesh')
)

# Material Assignment
material = unreal.load_asset('/Game/Materials/MyMaterial')
mesh_component.set_material(0, material)
```

### Asset Management

```python
# Create Asset
factory = unreal.MaterialFactoryNew()
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
new_material = asset_tools.create_asset(
    'M_NewMaterial',
    '/Game/Materials',
    unreal.Material,
    factory
)

# Import Asset
import_task = unreal.AssetImportTask()
import_task.filename = 'C:/path/to/texture.png'
import_task.destination_path = '/Game/Textures'
import_task.automated = True
import_task.save = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])

# Generate LODs for Static Mesh
mesh = unreal.load_asset('/Game/Meshes/MyMesh')
options = unreal.EditorStaticMeshLibrary.generate_lod(mesh, 3)

# Save All
unreal.EditorAssetLibrary.save_loaded_assets([new_material])
```

### Level Operations

```python
# Load Level
unreal.EditorLevelLibrary.load_level('/Game/Maps/MyLevel')

# Save Current Level
unreal.EditorLevelLibrary.save_current_level()

# Get Level Actors by Class
lights = unreal.EditorFilterLibrary.by_class(
    unreal.EditorLevelLibrary.get_all_level_actors(),
    unreal.PointLight
)

# Duplicate Actors
duplicates = unreal.EditorLevelLibrary.duplicate_actors(
    [actor1, actor2],
    to_level_duplicate=False
)

# Delete Actors
unreal.EditorLevelLibrary.destroy_actors([actor])
```

### Blueprint Creation via Python

```python
# Create Blueprint
factory = unreal.BlueprintFactory()
factory.set_editor_property('parent_class', unreal.Actor)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
blueprint = asset_tools.create_asset(
    'BP_MyActor',
    '/Game/Blueprints',
    unreal.Blueprint,
    factory
)

# Add Component
unreal.BlueprintEditorLibrary.add_component(
    blueprint,
    unreal.StaticMeshComponent
)

# Compile Blueprint
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)

# Spawn Blueprint Actor
bp_class = unreal.load_class(None, '/Game/Blueprints/BP_MyActor.BP_MyActor_C')
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    bp_class, unreal.Vector(0,0,0), unreal.Rotator(0,0,0)
)
```

---

## Editor Utility Widgets

Create custom Editor tools with Python + Blueprints:

```python
# Execute Python from Editor Utility Widget
# Use "Execute Python Command" node in Blueprint

# Example: Batch rename selected assets
import unreal

assets = unreal.EditorUtilityLibrary.get_selected_assets()
for asset in assets:
    old_name = asset.get_name()
    new_name = 'SM_' + old_name  # Add prefix
    unreal.EditorAssetLibrary.rename_asset(
        asset.get_path_name(),
        asset.get_path_name().replace(old_name, new_name)
    )
```

---

## Coordinate System & Units

| Axis | Direction | Notes |
|------|-----------|-------|
| X | Forward (Red) | Positive = Forward |
| Y | Right (Green) | Positive = Right |
| Z | Up (Blue) | Positive = Up |

**Units:** 1 Unreal Unit = 1 centimeter

**Rotation:** Pitch (Y), Yaw (Z), Roll (X) in degrees

---

## Common Workflows

### 1. Procedural Level Generation

```python
import unreal
import random

def spawn_grid(mesh_path, rows, cols, spacing):
    mesh = unreal.load_asset(mesh_path)
    for x in range(rows):
        for y in range(cols):
            loc = unreal.Vector(x * spacing, y * spacing, 0)
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor, loc, unreal.Rotator(0,0,0)
            )
            actor.static_mesh_component.set_static_mesh(mesh)
            # Random rotation
            actor.set_actor_rotation(
                unreal.Rotator(0, random.uniform(0, 360), 0), False
            )
```

### 2. Batch Material Assignment

```python
import unreal

def assign_material_to_selection(material_path):
    material = unreal.load_asset(material_path)
    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    
    for actor in actors:
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
        for comp in components:
            for i in range(comp.get_num_materials()):
                comp.set_material(i, material)
```

### 3. Export Level Data

```python
import unreal
import json

def export_level_to_json(output_path):
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    data = []
    
    for actor in actors:
        actor_data = {
            'name': actor.get_actor_label(),
            'class': actor.get_class().get_name(),
            'location': [
                actor.get_actor_location().x,
                actor.get_actor_location().y,
                actor.get_actor_location().z
            ],
            'rotation': [
                actor.get_actor_rotation().pitch,
                actor.get_actor_rotation().yaw,
                actor.get_actor_rotation().roll
            ]
        }
        data.append(actor_data)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
```

---

## Verification Checklist

Before completing any task:

- [ ] Python scripts execute without errors in Unreal Console
- [ ] Assets are saved after creation/modification
- [ ] Blueprint compiles successfully if modified
- [ ] Level saves after actor changes
- [ ] MCP connection verified if using remote execution
- [ ] Screenshots captured for visual verification when relevant

---

## Troubleshooting

### MCP Connection Issues

1. Verify Python Editor Script Plugin is enabled
2. Verify Remote Execution is enabled in Project Settings
3. Try bind address `0.0.0.0` instead of `127.0.0.1`
4. Restart Unreal Editor completely
5. Kill any zombie Node.js processes

### Python Script Errors

1. Check Output Log for Python exceptions
2. Verify asset paths use `/Game/` prefix
3. Ensure assets are loaded before access
4. Use `unreal.load_asset()` or `unreal.load_class()` as needed

### Blueprint Compilation Failures

1. Check Message Log for BP errors
2. Verify parent class compatibility
3. Ensure all required pins are connected
4. Save and recompile after node changes

---

## Resources

- [Unreal Python API Docs](https://docs.unrealengine.com/5.0/en-US/PythonAPI/)
- [Editor Scripting with Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)
- [runreal/unreal-mcp GitHub](https://github.com/runreal/unreal-mcp)
- [chongdashu/unreal-mcp GitHub](https://github.com/chongdashu/unreal-mcp)
- [Editor Utility Widgets](https://dev.epicgames.com/documentation/en-us/unreal-engine/editor-utility-widgets-in-unreal-engine)
