#!/usr/bin/env python3
"""Validate the installed authentic R6 V2.22 rig inside Blender."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from authentic_rig import activate_verified_r6_v222, enable_bundled_addon, inspect_authenticity  # noqa: E402


REQUIRED_CONTROLS = {
    "MasterControl",
    "LowerTorso-FK",
    "LeftLeg-IK",
    "RightLeg-IK",
    "LeftArm-IK",
    "RightArm-IK",
    "LeftArm_FK",
    "RightArm_FK",
    "LookToPoint",
}
REQUIRED_BODY_OBJECTS = {"Head", "Torso", "Left Arm", "Right Arm", "Left Leg", "Right Leg"}


def validate() -> dict:
    import bpy  # type: ignore

    activation = activate_verified_r6_v222()
    addon = enable_bundled_addon()
    errors = list(activation.get("errors", [])) + list(addon.get("errors", []))
    armature = bpy.data.objects.get("__PrimaryArmature")
    internal = bpy.data.objects.get("InternalArmature")
    if armature is None or armature.type != "ARMATURE":
        errors.append("Missing __PrimaryArmature")
    if internal is None or internal.type != "ARMATURE":
        errors.append("Missing InternalArmature")
    valid_armature = armature is not None and armature.type == "ARMATURE"
    control_names = set(armature.pose.bones.keys()) if valid_armature else set()
    object_names = set(bpy.data.objects.keys())
    missing_controls = sorted(REQUIRED_CONTROLS - control_names)
    missing_body = sorted(REQUIRED_BODY_OBJECTS - object_names)
    if missing_controls:
        errors.append(f"Missing R6 controls: {', '.join(missing_controls)}")
    if missing_body:
        errors.append(f"Missing visible R6 body objects: {', '.join(missing_body)}")
    body_variants = sorted(name for name in object_names if name.endswith(("_F2012", "_F2016", "_FBlocky", "_M2012", "_M2016", "_MBlocky")))
    if len(body_variants) < 20:
        errors.append("Expected premade colored/labeled R6 body variants were not found")
    authenticity = inspect_authenticity(armature) if valid_armature else None
    if not authenticity or not authenticity["authentic_ready"]:
        errors.append("R6 asset did not classify as authentic-ready")
    rig_texture = bpy.data.images.get("R6rig1_diff.png")
    texture_packed = bool(rig_texture and (rig_texture.packed_file or rig_texture.packed_files))
    texture_resolved = bool(rig_texture and bpy.path.abspath(rig_texture.filepath) and Path(bpy.path.abspath(rig_texture.filepath)).is_file())
    if rig_texture is None or not (texture_packed or texture_resolved):
        errors.append("The labeled/orientation R6 rig texture is missing or unresolved")
    return {
        "ok": not errors,
        "activation": activation,
        "addon": addon,
        "authenticity": authenticity,
        "controls": sorted(control_names),
        "body_objects": sorted(REQUIRED_BODY_OBJECTS & object_names),
        "body_variant_count": len(body_variants),
        "rig_texture": {
            "name": rig_texture.name if rig_texture else None,
            "packed": texture_packed,
            "resolved_external_file": texture_resolved,
        },
        "errors": errors,
    }


if __name__ == "__main__":
    payload = validate()
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(0 if payload["ok"] else 1)
