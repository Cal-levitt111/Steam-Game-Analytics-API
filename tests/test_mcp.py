from app import main as main_module


def _route_paths(app) -> list[str]:
    return [path for path in (getattr(route, 'path', None) for route in app.routes) if path]


def test_mcp_mount_route_registered() -> None:
    app = main_module.create_app()
    paths = _route_paths(app)
    assert '/mcp' in paths


def test_mcp_uses_read_only_tag_allowlist(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class DummyMCP:
        def __init__(self, fastapi, **kwargs):
            captured['include_tags'] = kwargs.get('include_tags')
            captured['name'] = kwargs.get('name')

        def mount(self, router=None, mount_path: str = '/mcp', transport: str = 'sse') -> None:
            captured['mount_path'] = mount_path

    monkeypatch.setattr(main_module, 'FastApiMCP', DummyMCP)
    app = main_module.create_app()

    assert captured.get('name') == main_module.settings.app_name
    assert captured.get('include_tags') == main_module.MCP_READONLY_TAGS
    assert 'auth' not in main_module.MCP_READONLY_TAGS
    assert 'collections' not in main_module.MCP_READONLY_TAGS
    assert captured.get('mount_path') == main_module.settings.mcp_mount_path
    assert hasattr(app.state, 'mcp')


def test_mcp_can_be_disabled(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, 'enable_mcp_server', False)
    app = main_module.create_app()
    paths = _route_paths(app)
    assert '/mcp' not in paths
