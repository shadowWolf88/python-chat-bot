import os
import warnings

# Optional HashiCorp Vault integration if hvac is installed and configured
try:
    import hvac
    HAS_VAULT = True
except Exception:
    hvac = None
    HAS_VAULT = False

class SecretsManager:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.vault_addr = os.environ.get('VAULT_ADDR') or os.environ.get('HASHICORP_VAULT_ADDR')
        self.vault_token = os.environ.get('VAULT_TOKEN')
        self.client = None
        if HAS_VAULT and self.vault_addr and self.vault_token:
            try:
                self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)
            except Exception:
                self.client = None

    def _from_vault(self, name: str):
        if not self.client:
            return None
        try:
            # Simple KV v2 read; adapt if using different mount
            path = f"secret/data/{name}"
            r = self.client.secrets.kv.v2.read_secret_version(path=name)
            data = r.get('data', {}).get('data', {})
            return data.get('value') or data.get(name)
        except Exception:
            return None

    def _from_env(self, name: str):
        return os.environ.get(name)

    def get_secret(self, name: str):
        """Return secret value or None if not found. In debug mode env fallback is allowed."""
        # Try vault first
        val = None
        try:
            val = self._from_vault(name)
        except Exception:
            val = None
        if val:
            return val
        # Fallback to env
        val = self._from_env(name)
        if val:
            return val
        return None

    def require_secret(self, name: str):
        """Return secret or raise RuntimeError if missing and not in debug mode."""
        val = self.get_secret(name)
        if val is None:
            if self.debug:
                warnings.warn(f"Secret {name} not provided. Running in DEBUG mode with no secret.")
                return None
            raise RuntimeError(f"Required secret {name} not available from secrets manager or environment")
        return val
