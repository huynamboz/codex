"""Parse the hypercorn config for settings."""
from logging import getLogger
import shutil

from hypercorn.config import Config

LOG = getLogger(__name__)


def ensure_config(hypercon_config_toml, hypercorn_config_toml_default):
    """Ensure that a valid config exists."""
    if not hypercon_config_toml.exists():
        shutil.copy(hypercorn_config_toml_default, hypercon_config_toml)
        LOG.info(f"Copied default config to {hypercon_config_toml}")


def get_hypercorn_config(hypercorn_config_toml, hypercorn_config_toml_default, dev):
    """Load the hypercorn config."""
    ensure_config(hypercorn_config_toml, hypercorn_config_toml_default)
    config = Config.from_toml(hypercorn_config_toml)
    LOG.info(f"Loaded config from {hypercorn_config_toml}")
    if dev:
        config.use_reloader = True
        LOG.info("Reload hypercorn if files change")
    return config


def get_root_path(hypercorn_config):
    """Get the root path from hypercorn config if not in debug mode."""
    root_path = hypercorn_config.root_path
    root_path = root_path.lstrip("/")
    # Ensure trailing slash
    if root_path and root_path[-1] != "/":
        root_path += "/"

    LOG.debug(f"PARSED {root_path} from hypercorn")
    return root_path
