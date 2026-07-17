#!/usr/bin/env python3
"""Detect and operate authentic Roblox Studio-exported Blender rigs.

This adapter supports Cautioned's current metadata-based importer workflow,
the pinned R6 IK/FK V2.22 control rig, and conventional skinned FBX rigs.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import importlib.util
import os
import secrets
import shutil
import sys
import tempfile
import types
import zipfile
from pathlib import Path
from typing import Any, Iterable


R6_PARTS = {"Head", "Torso", "Left Arm", "Right Arm", "Left Leg", "Right Leg"}
R15_PARTS = {
    "Head",
    "UpperTorso",
    "LowerTorso",
    "LeftUpperArm",
    "LeftLowerArm",
    "LeftHand",
    "RightUpperArm",
    "RightLowerArm",
    "RightHand",
    "LeftUpperLeg",
    "LeftLowerLeg",
    "LeftFoot",
    "RightUpperLeg",
    "RightLowerLeg",
    "RightFoot",
}
IMPORTER_BONE_PROPERTIES = {"is_transformable", "transform", "transform1", "nicetransform"}
BUNDLED_ADDON_SHA256 = "218b5e43e414fe3fa5d8a42cc5fd162b70e66f4cb82efd73ac5006b63895769a"
R6_V222_BLEND_SHA256 = "ff75c44b572d32328b62095141c6ce6255c4e9b772ee63d46d92280de1edcdc8"
R6_PROVENANCE_PROPERTY = "animate_roblox_r6_source_sha256"
R6_LINEAGE_ID_PROPERTY = "animate_roblox_r6_lineage_id"
R6_LINEAGE_PROPERTY = "animate_roblox_r6_lineage_hmac"
R6_ACTIVATION_NAMESPACE = "ANIMATE_ROBLOX_R6_V222_BOOTSTRAP"
R6_ATTESTATION_NAMESPACE = "ANIMATE_ROBLOX_R6_V222_ATTESTATION"
SKINNED_PROVENANCE_PROPERTY = "animate_roblox_skinned_source"
VERIFIED_SKINNED_SOURCES = {"studio-rig-builder", "studio-export", "user-verified-studio-export"}
R6_REQUIRED_CONTROLS = {
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
R6_V222_TEXT_SHA256 = {
    "RigBootstrap.py": "2e87eae515b129b0eac2db0138cd2ec215f101e45c975fe7b1eeaabfe38033e7",
    "RigEvents.py": "01731b7ad8c77ac4160f76a513e740c965aa78a7aa5e4072101024a4783e0211",
    "RigSelector.py": "7deaa1d7c3480896b90b148cde7fc24fa974865de5cff691208d537187194e9f",
    "RigSettings.py": "e9b334ee31ebc87af15b3e75242fea8249b7ff841a7487f1e4c2221cce590edd",
    "RigUtilities.py": "dc96f3453e5cdb0bea7a3af3f4c8823a06492c81d90ae5f34190e7ef5332760a",
}

CONTROL_ALIASES = {
    "master": ("MasterControl", "MasterController", "RootControl", "CTRL_Root"),
    "lower_torso_fk": ("LowerTorso-FK", "LowerTorso_FK", "Torso-FK", "Torso"),
    "upper_torso_fk": ("UpperTorso-FK", "UpperTorso_FK", "UpperTorso"),
    "left_leg_ik": ("LeftLeg-IK", "LeftLeg_IK", "CTRL_LeftFoot_IK", "LeftFoot-IK"),
    "right_leg_ik": ("RightLeg-IK", "RightLeg_IK", "CTRL_RightFoot_IK", "RightFoot-IK"),
    "left_arm_fk": ("LeftUpperArm-FK", "LeftUpperArm_FK", "LeftUpperArm", "Left Arm"),
    "right_arm_fk": ("RightUpperArm-FK", "RightUpperArm_FK", "RightUpperArm", "Right Arm"),
    "head_fk": ("Head-FK", "Head_FK", "Head"),
}


def build_control_map(bone_names: Iterable[str]) -> dict[str, str]:
    names = list(bone_names)
    lower = {name.lower(): name for name in names}
    result = {}
    for role, aliases in CONTROL_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower:
                result[role] = lower[alias.lower()]
                break
    return result


def classify_snapshot(
    *,
    armature_name: str,
    bone_names: Iterable[str],
    bone_property_names: Iterable[str] = (),
    object_names: Iterable[str] = (),
    generated_by: str | None = None,
    has_rig_meta: bool = False,
    has_armature_deformed_mesh: bool = False,
    importer_available: bool = False,
    exporter_available: bool = False,
    verified_control_rig: bool = False,
    skinned_source: str | None = None,
) -> dict[str, Any]:
    """Classify a rig from a pure-Python snapshot for testing and Blender use."""
    bones = set(bone_names)
    objects = set(object_names)
    properties = set(bone_property_names)
    controls = build_control_map(bones)
    matched_r6_parts = sorted(R6_PARTS & (bones | objects))
    matched_r15_parts = sorted(R15_PARTS & (bones | objects))
    metadata_matches = sorted(IMPORTER_BONE_PROPERTIES & properties)

    if generated_by:
        source = "generated-or-repository-proxy"
        workflow = "diagnostic-only"
        authentic_ready = False
        authoring_ready = False
        reason = "Repository-generated or proxy rigs are forbidden; use the pinned premade Roblox rig or a Studio-derived target."
    elif armature_name == "__PrimaryArmature" and (
        "MasterControl" in bones or any(name.endswith(("-IK", "-FK")) for name in bones)
    ):
        source = "community-r6-ik-fk-control-rig"
        workflow = "motor6d-rbxanim"
        authentic_ready = bool(verified_control_rig)
        authoring_ready = bool(verified_control_rig)
        reason = (
            "Validated the pinned R6 V2.22 structure, embedded-script hashes, and same-session activation receipt."
            if verified_control_rig
            else "Detected an R6-like control convention without verified V2.22 provenance."
        )
    elif len(metadata_matches) >= 3 and (len(matched_r6_parts) >= 5 or len(matched_r15_parts) >= 10):
        source = "studio-motor6d-import"
        workflow = "motor6d-rbxanim"
        authentic_ready = bool(has_rig_meta and exporter_available)
        authoring_ready = bool(has_rig_meta and importer_available and exporter_available)
        reason = (
            "Detected associated Roblox joint metadata and the verified import/export operators."
            if authentic_ready
            else "Detected Roblox-like joint metadata, but associated rig metadata or required operators are missing."
        )
    elif has_armature_deformed_mesh and len(matched_r15_parts) >= 10:
        source = "studio-or-fbx-skinned-r15"
        workflow = "skinned-fbx"
        authentic_ready = skinned_source in VERIFIED_SKINNED_SOURCES
        authoring_ready = authentic_ready
        reason = (
            f"Verified the skinned R15 source as {skinned_source}."
            if authentic_ready
            else "Detected a skinned R15-like hierarchy without verified Studio provenance."
        )
    elif has_armature_deformed_mesh and len(matched_r6_parts) >= 5:
        source = "fbx-r6-like-rig"
        workflow = "verify-before-export"
        authentic_ready = False
        authoring_ready = False
        reason = "The scene looks R6-like but lacks Motor6D importer metadata; verify the Studio export path before animation."
    else:
        source = "unknown"
        workflow = "unverified"
        authentic_ready = False
        authoring_ready = False
        reason = "No trusted Studio-export metadata or recognized authentic control-rig convention was found."

    return {
        "source": source,
        "workflow": workflow,
        "authentic_ready": authentic_ready,
        "authoring_ready": authoring_ready,
        "reason": reason,
        "control_map": controls,
        "matched_r6_parts": matched_r6_parts,
        "matched_r15_parts": matched_r15_parts,
        "importer_metadata": metadata_matches,
        "provenance": {
            "verified_control_rig": bool(verified_control_rig),
            "skinned_source": skinned_source,
        },
        "addon": {
            "import_operator": importer_available,
            "rbxanim_export_operator": exporter_available,
        },
    }


def _require_blender():
    try:
        import bpy  # type: ignore
    except ImportError as exc:  # pragma: no cover - Blender-only path
        raise RuntimeError("Run authentic_rig.py inside Blender") from exc
    return bpy


def _operator_available(operator) -> bool:
    try:
        operator.get_rna_type()
        return True
    except (AttributeError, KeyError, RuntimeError):
        return False


def _r6_structure_present(bpy, armature) -> bool:
    object_names = set(bpy.data.objects.keys())
    internal = bpy.data.objects.get("InternalArmature")
    body_variants = [
        name
        for name in object_names
        if name.endswith(("_F2012", "_F2016", "_FBlocky", "_M2012", "_M2016", "_MBlocky"))
    ]
    return bool(
        armature.name == "__PrimaryArmature"
        and internal is not None
        and internal.type == "ARMATURE"
        and R6_REQUIRED_CONTROLS.issubset(set(armature.pose.bones.keys()))
        and R6_PARTS.issubset(object_names)
        and len(body_variants) >= 20
        and bpy.data.images.get("R6rig1_diff.png") is not None
    )


def _r6_activation_attested(bpy, armature) -> bool:
    """Require a same-session receipt created by the verified activation path."""
    receipt = bpy.app.driver_namespace.get(R6_ATTESTATION_NAMESPACE)
    if not isinstance(receipt, dict):
        return False
    return bool(
        receipt.get("armature_pointer") == int(armature.as_pointer())
        and receipt.get("source_sha256") == R6_V222_BLEND_SHA256
        and receipt.get("text_sha256") == R6_V222_TEXT_SHA256
        and R6_ACTIVATION_NAMESPACE in bpy.app.driver_namespace
    )


def _r6_lineage_directory() -> Path:
    """Use one per-user location shared by every installed Blender version."""
    return Path.home() / ".animate-roblox-characters"


def _r6_lineage_key(_bpy, create: bool) -> bytes | None:
    """Load a machine-local key; never place the key or its path in a .blend."""
    key_directory = _r6_lineage_directory()
    key_path = key_directory / "r6-lineage.key"
    if key_path.is_symlink():
        raise RuntimeError("Refusing a symlinked R6 lineage key")
    if not key_path.exists():
        if not create:
            return None
        key_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        key = secrets.token_bytes(32)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(key_path, flags, 0o600)
        except FileExistsError:
            pass
        else:
            try:
                os.write(descriptor, key)
            finally:
                os.close(descriptor)
    if key_path.is_symlink() or not key_path.is_file():
        raise RuntimeError("R6 lineage key is not a regular file")
    key = key_path.read_bytes()
    if len(key) != 32:
        raise RuntimeError("R6 lineage key has an invalid length")
    return key


def _r6_lineage_signature(bpy, lineage_id: str, create_key: bool) -> str | None:
    if not isinstance(lineage_id, str) or len(lineage_id) != 32:
        return None
    try:
        int(lineage_id, 16)
    except ValueError:
        return None
    key = _r6_lineage_key(bpy, create=create_key)
    if key is None:
        return None
    payload = R6_V222_BLEND_SHA256.encode("ascii") + b"\0" + lineage_id.encode("ascii")
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def _r6_lineage_verified(bpy, armature) -> bool:
    lineage_id = armature.get(R6_LINEAGE_ID_PROPERTY)
    stored = armature.get(R6_LINEAGE_PROPERTY)
    if not isinstance(lineage_id, str) or not isinstance(stored, str) or len(stored) != 64:
        return False
    try:
        expected = _r6_lineage_signature(bpy, lineage_id, create_key=False)
    except (OSError, RuntimeError):
        return False
    return expected is not None and hmac.compare_digest(stored, expected)


def _extract_verified_addon(addon_path: Path, digest: str) -> Path:
    root = Path(tempfile.gettempdir()) / f"animate-roblox-cautioned-{digest[:16]}"
    marker = root / ".verified-sha256"
    with zipfile.ZipFile(addon_path) as archive:
        members = archive.infolist()
        if len(members) > 512 or sum(member.file_size for member in members) > 16 * 1024 * 1024:
            raise RuntimeError("Bundled add-on archive exceeds safe extraction limits")
        for member in archive.infolist():
            target = (root / member.filename).resolve()
            if root.resolve() not in target.parents and target != root.resolve():
                raise RuntimeError(f"Unsafe path in bundled add-on: {member.filename}")
            if member.file_size > 4 * 1024 * 1024:
                raise RuntimeError(f"Bundled add-on member is unexpectedly large: {member.filename}")

        cache_valid = marker.is_file() and marker.read_text(encoding="utf-8").strip() == digest
        if cache_valid:
            for member in members:
                if member.is_dir():
                    continue
                target = root / member.filename
                if not target.is_file() or hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(
                    archive.read(member)
                ).digest():
                    cache_valid = False
                    break
        if cache_valid:
            return root

        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)
        archive.extractall(root)
    marker.write_text(digest + "\n", encoding="utf-8")
    return root


def enable_bundled_addon() -> dict[str, Any]:
    """Register the pinned Cautioned 2.6.3 extension for this Blender session.

    Registration does not start its optional localhost sync server or OAuth flow.
    """
    bpy = _require_blender()
    module_name = "animate_roblox_cautioned_v263"
    operators_available = _operator_available(bpy.ops.object.rbxanims_importmodel) and _operator_available(
        bpy.ops.object.rbxanims_bake_file
    )
    addon_path = Path(__file__).resolve().parents[1] / "assets" / "blender-addons" / "rbx_anims_v2.6.3.zip"
    if not addon_path.is_file():
        return {"ok": False, "warnings": [], "errors": ["Bundled Cautioned 2.6.3 add-on is missing"]}
    digest = hashlib.sha256(addon_path.read_bytes()).hexdigest()
    if digest != BUNDLED_ADDON_SHA256:
        return {
            "ok": False,
            "warnings": [],
            "errors": ["Bundled Cautioned 2.6.3 add-on failed its SHA-256 integrity check"],
        }
    module = None
    module_loaded_here = False
    try:
        extracted = _extract_verified_addon(addon_path, digest)
        module = sys.modules.get(module_name)
        expected_module_file = (extracted / "__init__.py").resolve()
        if module is not None:
            module_file = Path(getattr(module, "__file__", "")).resolve()
            if module_file != expected_module_file:
                raise RuntimeError("The pinned add-on module name is occupied by a different module")
            if operators_available:
                return {
                    "ok": True,
                    "already_available": True,
                    "sha256": digest,
                    "warnings": [],
                    "errors": [],
                }
        elif operators_available:
            raise RuntimeError(
                "Conflicting Roblox animation operators are registered without the verified bundled module"
            )
        if module is None:
            spec = importlib.util.spec_from_file_location(
                module_name,
                expected_module_file,
                submodule_search_locations=[str(extracted)],
            )
            if spec is None or spec.loader is None:
                raise RuntimeError("Could not create a module spec for the bundled extension")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            module_loaded_here = True
        module.register()
    except Exception as exc:
        unregister = getattr(module, "unregister", None) if module_loaded_here and module is not None else None
        if callable(unregister):
            try:
                unregister()
            except Exception:
                pass
        if module_loaded_here:
            sys.modules.pop(module_name, None)
        return {"ok": False, "warnings": [], "errors": [f"Bundled add-on registration failed: {exc}"]}
    available = _operator_available(bpy.ops.object.rbxanims_importmodel) and _operator_available(
        bpy.ops.object.rbxanims_bake_file
    )
    return {
        "ok": available,
        "already_available": False,
        "sha256": digest,
        "warnings": [],
        "errors": [] if available else ["Bundled add-on registered without the required operators"],
    }


def activate_verified_r6_v222() -> dict[str, Any]:
    """Activate pinned R6 scripts from the exact master or a locally attested working copy."""
    bpy = _require_blender()
    filepath = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
    if filepath is None or not filepath.is_file():
        return {"ok": False, "errors": ["No saved .blend is open"], "warnings": []}
    blend_digest = hashlib.sha256(filepath.read_bytes()).hexdigest()
    text_hashes = {}
    for name, expected in R6_V222_TEXT_SHA256.items():
        text = bpy.data.texts.get(name)
        if text is None:
            return {"ok": False, "errors": [f"Pinned R6 rig is missing embedded text: {name}"], "warnings": []}
        digest = hashlib.sha256(text.as_string().encode("utf-8")).hexdigest()
        text_hashes[name] = digest
        if digest != expected:
            return {"ok": False, "errors": [f"Embedded R6 script failed SHA-256 verification: {name}"], "warnings": []}
    armature = bpy.data.objects.get("__PrimaryArmature")
    if armature is None or armature.type != "ARMATURE" or not armature.get("_Rbx_R6_Rig_", False):
        return {"ok": False, "errors": ["Pinned R6 control armature marker is missing"], "warnings": []}
    if not _r6_structure_present(bpy, armature):
        return {"ok": False, "errors": ["Pinned R6 control/body structure is incomplete"], "warnings": []}
    exact_master = blend_digest == R6_V222_BLEND_SHA256
    verified_lineage = bool(
        armature.get(R6_PROVENANCE_PROPERTY) == R6_V222_BLEND_SHA256
        and _r6_lineage_verified(bpy, armature)
    )
    resumed_working_copy = bool(not exact_master and verified_lineage)
    if not exact_master and not verified_lineage:
        return {
            "ok": False,
            "errors": [
                "Open file is neither the exact pinned R6 V2.22 master nor a locally attested working copy"
            ],
            "warnings": [],
        }
    previous_provenance = armature.get(R6_PROVENANCE_PROPERTY)
    previous_lineage_id = armature.get(R6_LINEAGE_ID_PROPERTY)
    previous_lineage = armature.get(R6_LINEAGE_PROPERTY)
    lineage_id = previous_lineage_id if verified_lineage else secrets.token_hex(16)
    try:
        lineage_signature = _r6_lineage_signature(bpy, lineage_id, create_key=True)
    except (OSError, RuntimeError) as exc:
        return {
            "ok": False,
            "errors": [f"Could not establish local R6 working-copy lineage: {exc}"],
            "warnings": [],
        }
    if lineage_signature is None:
        return {
            "ok": False,
            "errors": ["Could not establish local R6 working-copy lineage"],
            "warnings": [],
        }
    if R6_ACTIVATION_NAMESPACE not in bpy.app.driver_namespace:
        loaded_modules = []
        try:
            for text_name in ("RigSelector.py", "RigSettings.py", "RigUtilities.py", "RigEvents.py"):
                module_name = "animate_roblox_r6_v222_" + text_name.removesuffix(".py").lower()
                module = types.ModuleType(module_name)
                module.__file__ = text_name
                sys.modules[module_name] = module
                source = bpy.data.texts[text_name].as_string()
                exec(compile(source, text_name, "exec"), module.__dict__, module.__dict__)
                register = getattr(module, "register", None)
                if callable(register):
                    register()
                loaded_modules.append(module)
        except Exception as exc:
            for module in reversed(loaded_modules):
                unregister = getattr(module, "unregister", None)
                if callable(unregister):
                    try:
                        unregister()
                    except Exception:
                        pass
                sys.modules.pop(module.__name__, None)
            if previous_provenance is None:
                if R6_PROVENANCE_PROPERTY in armature:
                    del armature[R6_PROVENANCE_PROPERTY]
            else:
                armature[R6_PROVENANCE_PROPERTY] = previous_provenance
            if previous_lineage_id is None:
                if R6_LINEAGE_ID_PROPERTY in armature:
                    del armature[R6_LINEAGE_ID_PROPERTY]
            else:
                armature[R6_LINEAGE_ID_PROPERTY] = previous_lineage_id
            if previous_lineage is None:
                if R6_LINEAGE_PROPERTY in armature:
                    del armature[R6_LINEAGE_PROPERTY]
            else:
                armature[R6_LINEAGE_PROPERTY] = previous_lineage
            return {
                "ok": False,
                "errors": [f"Verified R6 control-script activation failed: {exc}"],
                "warnings": [],
            }
        bpy.app.driver_namespace[R6_ACTIVATION_NAMESPACE] = loaded_modules
    armature[R6_PROVENANCE_PROPERTY] = R6_V222_BLEND_SHA256
    armature[R6_LINEAGE_ID_PROPERTY] = lineage_id
    armature[R6_LINEAGE_PROPERTY] = lineage_signature
    bpy.app.driver_namespace[R6_ATTESTATION_NAMESPACE] = {
        "armature_pointer": int(armature.as_pointer()),
        "source_sha256": R6_V222_BLEND_SHA256,
        "text_sha256": dict(R6_V222_TEXT_SHA256),
    }
    return {
        "ok": True,
        "blend_sha256": blend_digest,
        "text_sha256": text_hashes,
        "armature": armature.name,
        "resumed_working_copy": bool(resumed_working_copy and not exact_master),
        "portable_working_copy": True,
        "lineage_updated": (
            previous_lineage_id != lineage_id or previous_lineage != lineage_signature
        ),
        "warnings": [],
        "errors": [],
    }


def _mesh_uses_armature(mesh, armature) -> bool:
    if mesh.type != "MESH":
        return False
    if mesh.parent == armature:
        return True
    if any(modifier.type == "ARMATURE" and modifier.object == armature for modifier in mesh.modifiers):
        return True
    return any(
        constraint.type == "CHILD_OF" and constraint.target == armature for constraint in mesh.constraints
    )


def _associated_rig_meta_objects(bpy, armature) -> list[Any]:
    """Find unambiguous Cautioned metadata associated with this armature."""
    armature_collections = {collection.name for collection in armature.users_collection}
    candidates = []
    for obj in bpy.data.objects:
        if obj.type != "EMPTY" or "RigMeta" not in obj:
            continue
        conventional_name = obj.name.startswith("__") and "Meta" in obj.name
        explicit = getattr(obj, "parent", None) == armature or str(obj.get("armature", "")) == armature.name
        shared_master = any(
            collection.name in armature_collections and collection.name.startswith("RIG:")
            for collection in obj.users_collection
        )
        if (conventional_name and shared_master) or explicit:
            candidates.append(obj)
    return candidates


def inspect_authenticity(armature) -> dict[str, Any]:
    bpy = _require_blender()
    bone_names = [bone.name for bone in armature.data.bones]
    property_names = set()
    metadata_bone_count = 0
    for bone in armature.data.bones:
        bone_properties = {str(key) for key in bone.keys()}
        property_names.update(bone_properties)
        if IMPORTER_BONE_PROPERTIES & bone_properties:
            metadata_bone_count += 1
    driven_meshes = [obj for obj in bpy.context.scene.objects if _mesh_uses_armature(obj, armature)]
    object_names = [obj.name for obj in driven_meshes]
    has_deformed_mesh = any(
        obj.vertex_groups
        or any(modifier.type == "ARMATURE" and modifier.object == armature for modifier in obj.modifiers)
        for obj in driven_meshes
    )
    rig_meta_candidates = _associated_rig_meta_objects(bpy, armature)
    has_associated_rig_meta = len(rig_meta_candidates) == 1
    # Bone properties identify the importer convention, but only an associated
    # One associated rig-named __*Meta object carrying RigMeta proves the
    # reconstructed rig/export mapping is complete.
    has_rig_meta = has_associated_rig_meta
    importer_available = _operator_available(bpy.ops.object.rbxanims_importmodel)
    exporter_available = _operator_available(bpy.ops.object.rbxanims_bake_file)
    verified_control_rig = bool(
        armature.get(R6_PROVENANCE_PROPERTY) == R6_V222_BLEND_SHA256
        and _r6_activation_attested(bpy, armature)
        and armature.get("_Rbx_R6_Rig_", False)
        and _r6_structure_present(bpy, armature)
        and all(
            (text := bpy.data.texts.get(name)) is not None
            and hashlib.sha256(text.as_string().encode("utf-8")).hexdigest() == expected
            for name, expected in R6_V222_TEXT_SHA256.items()
        )
    )
    result = classify_snapshot(
        armature_name=armature.name,
        bone_names=bone_names,
        bone_property_names=property_names,
        object_names=object_names,
        generated_by=armature.get("generated_by"),
        has_rig_meta=has_rig_meta,
        has_armature_deformed_mesh=has_deformed_mesh,
        importer_available=importer_available,
        exporter_available=exporter_available,
        verified_control_rig=verified_control_rig,
        skinned_source=str(armature.get(SKINNED_PROVENANCE_PROPERTY, "")) or None,
    )
    result["armature"] = armature.name
    result["driven_meshes"] = sorted(object_names)
    result["images"] = sorted(image.name for image in bpy.data.images if image.source == "FILE")
    result["provenance"]["same_session_activation"] = _r6_activation_attested(bpy, armature)
    result["metadata_bone_count"] = metadata_bone_count
    result["associated_rig_meta"] = has_associated_rig_meta
    result["rig_meta_candidates"] = sorted(obj.name for obj in rig_meta_candidates)
    result["rig_meta_ambiguous"] = len(rig_meta_candidates) > 1
    return result


def mark_verified_skinned_rig(armature_name: str, source: str) -> dict[str, Any]:
    """Record Studio provenance after the agent verifies the actual skinned R15 source."""
    bpy = _require_blender()
    armature = bpy.data.objects.get(armature_name)
    if armature is None or armature.type != "ARMATURE":
        return {"ok": False, "errors": [f"Armature not found: {armature_name}"], "warnings": []}
    if source not in VERIFIED_SKINNED_SOURCES:
        return {
            "ok": False,
            "errors": [f"Unsupported skinned-rig provenance: {source}"],
            "warnings": [],
        }
    bone_names = set(armature.data.bones.keys())
    driven_meshes = [obj for obj in bpy.context.scene.objects if _mesh_uses_armature(obj, armature)]
    has_deformed_mesh = any(
        obj.vertex_groups
        or any(modifier.type == "ARMATURE" and modifier.object == armature for modifier in obj.modifiers)
        for obj in driven_meshes
    )
    if len(R15_PARTS & bone_names) < 10 or not has_deformed_mesh:
        return {
            "ok": False,
            "errors": ["Skinned provenance requires an R15 hierarchy and an armature-driven visible mesh"],
            "warnings": [],
        }
    previous_source = armature.get(SKINNED_PROVENANCE_PROPERTY)
    armature[SKINNED_PROVENANCE_PROPERTY] = source
    authenticity = inspect_authenticity(armature)
    if not authenticity["authentic_ready"]:
        if previous_source is None:
            del armature[SKINNED_PROVENANCE_PROPERTY]
        else:
            armature[SKINNED_PROVENANCE_PROPERTY] = previous_source
    return {
        "ok": bool(authenticity["authentic_ready"]),
        "armature": armature.name,
        "authenticity": authenticity,
        "warnings": [],
        "errors": [] if authenticity["authentic_ready"] else ["Provenance mark did not pass authenticity checks"],
    }


def import_motor6d_obj(filepath: str | Path, rigging_type: str = "LOCAL_YAXIS_EXTEND") -> dict[str, Any]:
    """Import a Studio-plugin OBJ and reconstruct its metadata-backed armature."""
    bpy = _require_blender()
    source = Path(filepath).expanduser().resolve()
    if source.suffix.lower() != ".obj" or not source.is_file():
        return {"ok": False, "errors": ["A readable Studio-exported .obj file is required"], "warnings": []}
    addon = enable_bundled_addon()
    if not addon["ok"] or not _operator_available(bpy.ops.object.rbxanims_importmodel):
        return {
            "ok": False,
            "errors": addon["errors"] or ["The Roblox Animations Importer/Exporter add-on is unavailable"],
            "warnings": [],
        }
    try:
        imported = bpy.ops.object.rbxanims_importmodel(filepath=str(source))
    except Exception as exc:
        return {"ok": False, "errors": [f"Rig import operator failed: {exc}"], "warnings": []}
    if "FINISHED" not in imported:
        return {"ok": False, "errors": [f"Rig import returned {sorted(imported)}"], "warnings": []}
    if not _operator_available(bpy.ops.object.rbxanims_genrig):
        return {"ok": False, "errors": ["The imported rig cannot be rebuilt because the add-on operator is missing"], "warnings": []}
    try:
        rebuilt = bpy.ops.object.rbxanims_genrig(pr_rigging_type=rigging_type)
    except Exception as exc:
        return {"ok": False, "errors": [f"Rig rebuild operator failed: {exc}"], "warnings": []}
    if "FINISHED" not in rebuilt:
        return {"ok": False, "errors": [f"Rig rebuild returned {sorted(rebuilt)}"], "warnings": []}
    settings = getattr(bpy.context.scene, "rbx_anim_settings", None)
    armature_name = getattr(settings, "rbx_anim_armature", "") if settings is not None else ""
    armature = bpy.data.objects.get(armature_name) if armature_name else bpy.context.view_layer.objects.active
    if armature is None or armature.type != "ARMATURE":
        return {"ok": False, "errors": ["The add-on did not create a selectable armature"], "warnings": []}
    authenticity = inspect_authenticity(armature)
    if not authenticity["authentic_ready"]:
        return {
            "ok": False,
            "armature": armature.name,
            "authenticity": authenticity,
            "artifacts": {"source_obj": str(source)},
            "warnings": [],
            "errors": [
                "Imported Motor6D rig is incomplete: require one associated rig-named __*Meta object carrying "
                "RigMeta, mapped joints, and the export operator"
            ],
        }
    return {
        "ok": True,
        "armature": armature.name,
        "authenticity": authenticity,
        "artifacts": {"source_obj": str(source)},
        "warnings": [],
        "errors": [],
    }


def export_rbxanim(
    output_path: str | Path,
    armature_name: str,
    action_name: str | None = None,
    frame_start: int | None = None,
    frame_end: int | None = None,
) -> dict[str, Any]:
    """Export a metadata-backed Motor6D action through the companion add-on."""
    bpy = _require_blender()
    armature = bpy.data.objects.get(armature_name)
    if armature is None or armature.type != "ARMATURE":
        return {"ok": False, "errors": [f"Armature not found: {armature_name}"], "warnings": []}
    authenticity = inspect_authenticity(armature)
    if authenticity["workflow"] != "motor6d-rbxanim" or not authenticity["authentic_ready"]:
        return {
            "ok": False,
            "errors": ["The selected rig is not a verified, metadata-backed Motor6D/.rbxanim workflow"],
            "warnings": [],
        }
    addon = enable_bundled_addon()
    if not addon["ok"] or not _operator_available(bpy.ops.object.rbxanims_bake_file):
        return {
            "ok": False,
            "errors": addon["errors"] or ["The Roblox Animations .rbxanim export operator is unavailable"],
            "warnings": [],
        }
    settings = getattr(bpy.context.scene, "rbx_anim_settings", None)
    if settings is None or not hasattr(settings, "rbx_anim_armature"):
        return {
            "ok": False,
            "errors": ["The bundled add-on did not register its armature-selection settings"],
            "warnings": [],
        }
    action = bpy.data.actions.get(action_name) if action_name is not None else None
    if action_name is not None and action is None:
        return {"ok": False, "errors": [f"Action not found: {action_name}"], "warnings": []}
    if action_name is None and action is None and armature.animation_data:
        action = armature.animation_data.action
    if action is None:
        return {"ok": False, "errors": ["No active action is available to export"], "warnings": []}
    export_start = int(round(action.frame_range[0])) if frame_start is None else int(frame_start)
    export_end = int(round(action.frame_range[1])) if frame_end is None else int(frame_end)
    if export_end < export_start:
        return {"ok": False, "errors": [".rbxanim export requires frame_start <= frame_end"], "warnings": []}

    try:
        output = Path(output_path).expanduser().resolve().with_suffix(".rbxanim")
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"ok": False, "errors": [f"Unable to prepare .rbxanim export: {exc}"], "warnings": []}
    created_animation_data = armature.animation_data is None
    if created_animation_data:
        armature.animation_data_create()
    previous_action = armature.animation_data.action
    previous_active = bpy.context.view_layer.objects.active
    previous_active_mode = previous_active.mode if previous_active is not None else None
    previous_selected = list(bpy.context.selected_objects)
    previous_frame = int(bpy.context.scene.frame_current)
    previous_frame_start = int(bpy.context.scene.frame_start)
    previous_frame_end = int(bpy.context.scene.frame_end)
    previous_rbx_armature = settings.rbx_anim_armature
    nla_states = [(track, track.mute) for track in armature.animation_data.nla_tracks]
    try:
        temporary_handle = tempfile.NamedTemporaryFile(
            prefix=f".{output.stem}-",
            suffix=".rbxanim",
            dir=output.parent,
            delete=False,
        )
    except OSError as exc:
        if created_animation_data:
            armature.animation_data_clear()
        return {"ok": False, "errors": [f"Unable to create temporary .rbxanim export: {exc}"], "warnings": []}
    temporary_handle.close()
    temporary_output = Path(temporary_handle.name)
    errors = []
    try:
        for track, _mute in nla_states:
            track.mute = True
        armature.animation_data.action = action
        bpy.context.scene.frame_start = export_start
        bpy.context.scene.frame_end = export_end
        settings.rbx_anim_armature = armature.name
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        result = bpy.ops.object.rbxanims_bake_file(filepath=str(temporary_output))
        if "FINISHED" not in result:
            raise RuntimeError(f".rbxanim exporter returned {sorted(result)}")
        if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
            raise RuntimeError(".rbxanim exporter did not create a non-empty file")
        temporary_output.replace(output)
    except Exception as exc:
        errors.append(f".rbxanim export failed: {exc}")
    finally:
        temporary_output.unlink(missing_ok=True)
        armature.animation_data.action = previous_action
        for track, mute in nla_states:
            track.mute = mute
        if created_animation_data:
            armature.animation_data_clear()
        bpy.context.scene.frame_start = previous_frame_start
        bpy.context.scene.frame_end = previous_frame_end
        bpy.context.scene.frame_set(previous_frame)
        settings.rbx_anim_armature = previous_rbx_armature
        bpy.ops.object.select_all(action="DESELECT")
        for obj in previous_selected:
            if obj.name in bpy.context.scene.objects:
                obj.select_set(True)
        if previous_active and previous_active.name in bpy.context.scene.objects:
            bpy.context.view_layer.objects.active = previous_active
            if previous_active_mode and previous_active_mode != "OBJECT":
                previous_active.select_set(True)
                try:
                    bpy.ops.object.mode_set(mode=previous_active_mode)
                except RuntimeError:
                    errors.append(f"Could not restore prior object mode: {previous_active_mode}")
    return {
        "ok": not errors,
        "armature": armature.name,
        "authenticity": authenticity,
        "action": action.name,
        "frame_start": export_start,
        "frame_end": export_end,
        "artifacts": {"rbxanim": str(output)} if not errors else {},
        "warnings": [],
        "errors": errors,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--armature", required=True)
    import_parser = subparsers.add_parser("import-obj")
    import_parser.add_argument("--input", required=True)
    import_parser.add_argument("--rigging-type", default="LOCAL_YAXIS_EXTEND")
    export_parser = subparsers.add_parser("export-rbxanim")
    export_parser.add_argument("--armature", required=True)
    export_parser.add_argument("--output", required=True)
    export_parser.add_argument("--action")
    export_parser.add_argument("--frame-start", type=int)
    export_parser.add_argument("--frame-end", type=int)
    verify_parser = subparsers.add_parser("mark-skinned")
    verify_parser.add_argument("--armature", required=True)
    verify_parser.add_argument("--source", required=True, choices=sorted(VERIFIED_SKINNED_SOURCES))
    subparsers.add_parser("enable-addon")
    subparsers.add_parser("activate-r6-v222")
    return parser.parse_args(argv)


def main() -> int:
    bpy = _require_blender()
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = _parse_args(argv)
    if args.operation == "inspect":
        armature = bpy.data.objects.get(args.armature)
        result = (
            {"ok": True, "authenticity": inspect_authenticity(armature), "errors": []}
            if armature and armature.type == "ARMATURE"
            else {"ok": False, "errors": [f"Armature not found: {args.armature}"]}
        )
    elif args.operation == "import-obj":
        result = import_motor6d_obj(args.input, args.rigging_type)
    elif args.operation == "export-rbxanim":
        result = export_rbxanim(args.output, args.armature, args.action, args.frame_start, args.frame_end)
    elif args.operation == "mark-skinned":
        result = mark_verified_skinned_rig(args.armature, args.source)
    elif args.operation == "enable-addon":
        result = enable_bundled_addon()
    else:
        result = activate_verified_r6_v222()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
