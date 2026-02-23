from dataclasses import dataclass
import os


BASE_URL = "https://api.unlock.govilo.xyz"


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    api_key: str
    seller_address: str
    base_url: str = BASE_URL


def load_config(
    cli_api_key: str | None = None,
    cli_address: str | None = None,
) -> Config:
    api_key = cli_api_key or os.environ.get("GOVILO_API_KEY")
    if not api_key:
        raise ConfigError(
            "API Key not configured. See references/setup-guide.md for registration steps. "
            "Register at https://govilo.xyz/ then set GOVILO_API_KEY=sk_live_xxx"
        )

    seller_address = cli_address or os.environ.get("SELLER_ADDRESS")
    if not seller_address:
        raise ConfigError(
            "Seller address required (Base chain). Use --address 0x... or set SELLER_ADDRESS env var. "
            "See references/setup-guide.md for wallet setup"
        )

    return Config(api_key=api_key, seller_address=seller_address)
