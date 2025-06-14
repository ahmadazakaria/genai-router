import importlib

from config import backend_loader


def test_default_backend(monkeypatch):
    # Clear cache before monkeypatching
    backend_loader._load_raw_config.cache_clear()

    monkeypatch.setattr(backend_loader, "_load_raw_config", lambda: {})
    backend = backend_loader.resolve_backend("any-model")
    assert backend["type"] == "ollama"


def test_routing(monkeypatch):
    sample_cfg = {
        "default_backend": "ollama",
        "backends": {
            "ollama": {"type": "ollama", "base_url": "http://x"},
            "http-mcp": {"type": "http", "base_url": "http://y"},
        },
        "routing": {"company-gpt": "http-mcp"},
    }

    backend_loader._load_raw_config.cache_clear()
    monkeypatch.setattr(backend_loader, "_load_raw_config", lambda: sample_cfg)

    backend = backend_loader.resolve_backend("company-gpt")
    assert backend["type"] == "http"
    assert backend["base_url"] == "http://y" 