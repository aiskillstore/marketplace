# Unreal Engine Developer - Quick Reference

## Python API Classes

### Core Systems
| Class | Purpose |
|-------|---------|
| `unreal.EditorLevelLibrary` | Level/actor operations |
| `unreal.EditorAssetLibrary` | Asset CRUD operations |
| `unreal.EditorUtilityLibrary` | Selection and utility |
| `unreal.AssetToolsHelpers` | Asset creation/import |
| `unreal.BlueprintEditorLibrary` | Blueprint manipulation |

### Common Actor Classes
| Class | Use Case |
|-------|----------|
| `unreal.StaticMeshActor` | Static geometry |
| `unreal.SkeletalMeshActor` | Animated meshes |
| `unreal.PointLight` | Point lights |
| `unreal.SpotLight` | Spot lights |
| `unreal.DirectionalLight` | Sun/directional |
| `unreal.CameraActor` | Cameras |
| `unreal.PlayerStart` | Player spawn |
| `unreal.TriggerBox` | Collision triggers |
| `unreal.BlockingVolume` | Invisible collision |

### Component Classes
| Class | Purpose |
|-------|---------|
| `unreal.StaticMeshComponent` | Static mesh rendering |
| `unreal.SkeletalMeshComponent` | Skeletal mesh |
| `unreal.CameraComponent` | Camera view |
| `unreal.SceneComponent` | Transform hierarchy |
| `unreal.BoxComponent` | Box collision |
| `unreal.SphereComponent` | Sphere collision |
| `unreal.AudioComponent` | Sound playback |
| `unreal.ParticleSystemComponent` | VFX |

## MCP Tool Quick Reference

### runreal/unreal-mcp Tools
```
editor_run_python         - Execute Python code
editor_list_assets        - List assets in path
editor_search_assets      - Search by name/class
editor_get_asset_info     - Asset details + LODs
editor_export_asset       - Export to text
editor_get_world_outliner - All actors + properties
editor_create_object      - Spawn new actor
editor_update_object      - Modify actor
editor_delete_object      - Remove actor
editor_console_command    - UE console command
editor_take_screenshot    - Viewport capture
editor_move_camera        - Position viewport
```

### chongdashu/unreal-mcp Additional
```
Actor Management:
- create_actor, delete_actor
- set_actor_transform
- query_actor_properties
- find_actors_by_name
- list_all_actors

Blueprint Development:
- create_blueprint_class
- add_component_to_blueprint
- set_component_properties
- compile_blueprint
- spawn_blueprint_actor
- create_input_mapping

Blueprint Node Graph:
- add_event_node
- create_function_call_node
- connect_nodes
- add_variable
- create_component_reference
- find_nodes

Editor Control:
- focus_viewport
- set_camera_orientation
```

## Asset Path Conventions

```
/Game/                    - Project content root
/Game/Maps/               - Level files
/Game/Meshes/             - Static meshes
/Game/Characters/         - Character assets
/Game/Materials/          - Materials
/Game/Textures/           - Textures
/Game/Blueprints/         - Blueprint classes
/Game/VFX/                - Particle systems
/Game/Audio/              - Sound assets
/Engine/                  - Engine content
/Engine/BasicShapes/      - Primitive meshes
```

## Console Commands

### Rendering
```
r.SetRes 1920x1080       - Set resolution
HighResShot 2            - High-res screenshot (2x)
ShowFlag.Lighting 0      - Toggle lighting
ShowFlag.PostProcessing 0 - Toggle post process
```

### Performance
```
stat fps                 - Show FPS
stat unit               - Frame time breakdown
stat gpu                - GPU stats
profilegpu              - GPU profiler
```

### Level
```
open MapName            - Load level
restartlevel            - Restart current
```

## Blueprint Event Nodes

| Event | Fires When |
|-------|------------|
| `BeginPlay` | Actor spawns/level starts |
| `Tick` | Every frame |
| `EndPlay` | Actor destroyed |
| `ActorBeginOverlap` | Collision start |
| `ActorEndOverlap` | Collision end |
| `OnHit` | Physics collision |
| `InputAction` | Player input |

## Material Expressions (Common)

| Node | Purpose |
|------|---------|
| `TextureSample` | Sample texture |
| `Multiply` | Blend/tint |
| `Lerp` | Linear interpolate |
| `Fresnel` | Edge glow effect |
| `WorldPosition` | World coords |
| `Time` | Animation driver |
| `Panner` | UV scrolling |
| `Noise` | Procedural noise |
