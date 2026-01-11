#!/usr/bin/env python3
"""Generate a Livekit connection token for the voice agent playground."""

import os
import sys
from pathlib import Path

# Load environment
env_file = Path("/home/adamsl/ottomator-agents/livekit-agent/.env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

try:
    from livekit import api
except ImportError:
    print("ERROR: livekit package not installed")
    print("Run: pip install livekit")
    sys.exit(1)

def generate_token(room_name: str = "test-room", identity: str = "user1"):
    """Generate a connection token."""
    api_key = os.environ.get('LIVEKIT_API_KEY')
    api_secret = os.environ.get('LIVEKIT_API_SECRET')
    livekit_url = os.environ.get('LIVEKIT_URL', 'ws://localhost:7880')

    if not api_key or not api_secret:
        print("ERROR: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
        print(f"Checked: {env_file}")
        sys.exit(1)

    token = api.AccessToken(api_key, api_secret) \
        .with_identity(identity) \
        .with_name('User') \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
        ))

    jwt = token.to_jwt()

    print("=" * 60)
    print("LIVEKIT CONNECTION INFO")
    print("=" * 60)
    print(f"URL: {livekit_url}")
    print(f"Room: {room_name}")
    print()
    print("Token:")
    print(jwt)
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Go to: https://agents-playground.livekit.io/")
    print("2. Click 'Connect' and enter the URL and Token above")
    print("3. Allow microphone access")
    print("4. Start talking!")

    return jwt

if __name__ == "__main__":
    room = sys.argv[1] if len(sys.argv) > 1 else "test-room"
    generate_token(room)
