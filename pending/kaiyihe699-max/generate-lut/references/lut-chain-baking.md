# LUT Chain Baking

Use scripts/bake_lut_chain.py when a user needs one file that combines multiple normalized 3D transforms. Supply the stages in the order they should be applied. For a camera log conversion followed by a creative look, put the technical conversion first and the creative look second.

Example:

    python scripts/bake_lut_chain.py --lut vlog-to-rec709.cube --lut warm-film.cube --size 33 --output camera-warm-film.cube

The chain baker creates a new .cube by sampling each source LUT in sequence. It records stage filenames and SHA-256 hashes in comments. The output size can be changed to 17, 33, or 65; a smaller output resamples the combined transform.

The current implementation accepts only 3D .cube LUTs with DOMAIN_MIN 0 and DOMAIN_MAX 1 and output values inside 0..1. Extended-range LUTs are rejected rather than silently clipped. The tool follows the supplied order and cannot determine whether the color-space assumptions between stages are correct. Confirm that each stage's output encoding matches the next stage's input encoding.

For a Panasonic LUMIX DC-S9 output, the baker carries a single consistent `#LUMIXPHOTOSTYLE` tag from the inputs. If input tags conflict, choose the intended camera-side base style with `--lumix-photo-style`. The tag does not validate the color-space handoff between stages.

A combined LUT is convenient for a device with one LUT slot. Keep the separate technical and creative LUTs when the workflow needs independent intensity control or a reversible grading node chain. Baking does not make an approximate transform exact or an unofficial transform vendor-certified.
