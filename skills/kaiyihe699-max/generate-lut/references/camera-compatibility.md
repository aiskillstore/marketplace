# Camera Compatibility Profiles

A compatibility profile is a checklist of facts verified for one camera or device. It is not inferred from a generic .cube file. Create a blank template with scripts/check_camera_compatibility.py --create-template camera-profile.json.

Fill the fields from the camera's official manual or official support documentation. Keep the source URL and verification date. Do not set verified to true until each configured requirement has been checked against those sources. A limit that the source does not document must stay null; a camera import profile does not necessarily prescribe one input color encoding.

Profile fields:

- schema_version: currently 1.
- device: manufacturer and exact model.
- verified: true only after checking official source material.
- verification_date: date in YYYY-MM-DD form.
- sources: official source URLs.
- accepted_formats: include .cube only if the device documentation says it accepts it.
- allowed_3d_sizes: supported 3D LUT edge sizes, such as 17 or 33.
- max_file_bytes: maximum accepted file size, or null if undocumented.
- expected_input_space: LUT input primaries or color space, or null if unknown.
- expected_input_transfer: LUT input transfer function, or null if unknown.
- supported_lumix_photo_styles: Panasonic `#LUMIXPHOTOSTYLE` tags accepted by the device, when documented.
- missing_lumix_photo_style_defaults_to: documented camera fallback when the tag is absent, when known.
- check_full_range_domain: check explicit `.cube` `DOMAIN_MIN 0` and `DOMAIN_MAX 1` when camera documentation recommends or requires full range.
- card_filesystems: optional filename rules keyed by card filesystem, for use with `--card-filesystem`.

Example of a deliberately unverified template:

    {
      "schema_version": 1,
      "device": "Enter manufacturer and model",
      "verified": false,
      "verification_date": null,
      "sources": [],
      "accepted_formats": [],
      "allowed_3d_sizes": [],
      "max_file_bytes": null,
      "expected_input_space": null,
      "expected_input_transfer": null
    }

Run a check with scripts/check_camera_compatibility.py --lut selected.cube --profile camera-profile.json. A result of UNCONFIRMED means the profile is incomplete or unverified; it must not be described as camera-compatible. INCOMPATIBLE means the file fails at least one configured requirement.

The checker verifies the .cube structure, size, configured file-size limit, optional source metadata, Panasonic Photo Style tag, full-range domain, and (when requested) card filename. If the profile defines card filename rules but no `--card-filesystem` is selected, the result stays UNCONFIRMED. For a Panasonic profile, `--card-filesystem FAT32` or `--card-filesystem exFAT` checks the filename length and alphanumeric stem. Copy LUT files to the SD card root as instructed by the manual. The checker cannot verify actual camera import or visual behavior.

## Panasonic LUMIX DC-S9

Use [camera-profiles/panasonic-dc-s9.json](camera-profiles/panasonic-dc-s9.json) as the source-backed DC-S9 profile. Panasonic documents `.cube` support with 2–33 point 3D LUTs (and also accepts `.vlt`, which this checker does not parse), recommends full-range LUTs, and gives different SD-card filename limits for FAT32 and exFAT. The documented base Photo Style tags are available to the generator; if the tag is absent or invalid, the camera uses V-Log. Panasonic does not document a maximum LUT file size in these pages, so the profile leaves that field unspecified.

Generate a camera-targeted creative LUT with an explicit base style:

    python scripts/generate_cube_lut.py --look warm-film --size 33 --lumix-photo-style VLOG --output vlog-warm-film.cube

Check its format and SD-card filename:

    python scripts/check_camera_compatibility.py --lut vlog-warm-film.cube --profile references/camera-profiles/panasonic-dc-s9.json --card-filesystem FAT32

Generate a complete handoff folder and ZIP in one command:

    python scripts/build_camera_lut_package.py --look warm-film --strength 0.55 --size 33 --lumix-photo-style VLOG --card-filesystem FAT32 --name WARMFILM --preview-image sample.jpg --output-dir delivery/warm-film

To package an existing creative LUT and blend it to a lower strength, replace `--look warm-film` with `--lut source.cube`. Leave technical conversion LUTs at strength 1 unless you intentionally want an approximate transform. The resulting package includes the LUT, a compatibility report, a LUT quality report, a manifest, a short README, and an optional preview. FAT32 names must be at most eight ASCII letters or digits; use the actual SD card filesystem.

The Photo Style marker describes the camera-side base style. It does not prove that a creative LUT is a technically accurate V-Log conversion. A non-full-range domain is reported as unconfirmed because Panasonic says it may display or record incorrectly.
