from guardian_dashboard import display_text


def test_dashboard_encodes_mailbox_text_before_rendering():
    assert display_text('<img src=x onerror=alert(1)>') == '&lt;img src=x onerror=alert(1)&gt;'
    assert display_text('"quoted"') == '&quot;quoted&quot;'
