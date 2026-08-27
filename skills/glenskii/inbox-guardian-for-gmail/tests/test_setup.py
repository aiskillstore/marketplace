from unittest.mock import MagicMock

import guardian


def test_setup_explains_missing_credentials(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(guardian, "CREDENTIALS_FILE", str(tmp_path / "credentials.json"))

    result = guardian.run_setup()

    assert result == 1
    assert "OAuth desktop client file" in capsys.readouterr().out


def test_setup_authenticates_and_confirms_account(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    credentials = tmp_path / "credentials.json"
    credentials.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(guardian, "CREDENTIALS_FILE", str(credentials))
    service = MagicMock()
    service.users().getProfile().execute.return_value = {
        "emailAddress": "owner@example.com"
    }
    monkeypatch.setattr(guardian.GmailAuth, "get_service", lambda scopes: service)

    result = guardian.run_setup()

    assert result == 0
    service.users().getProfile.assert_any_call(userId="me")
    assert "Connected to owner@example.com" in capsys.readouterr().out
