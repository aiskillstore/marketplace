import json
import os
import stat

from guardian_storage import write_private_json


def test_private_json_is_written_atomically_with_owner_permissions(tmp_path):
    target = tmp_path / "review.json"
    write_private_json(target, {"message": "local only"})

    assert json.loads(target.read_text(encoding="utf-8")) == {"message": "local only"}
    if os.name != "nt":
        assert stat.S_IMODE(target.stat().st_mode) == 0o600
