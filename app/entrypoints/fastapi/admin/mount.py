from starlette.routing import Mount
from starlette.types import ASGIApp, Receive, Scope, Send


class AdminMountPath:
    """Give the mounted admin router a root path that is a prefix of the request.

    FastAPI writes ``/api/v1`` into the ASGI root path. SQLAdmin then appends
    ``/admin``. The request path does not start with that combined value, and
    the panel routes ``/login`` as ``/admin/login``.
    """

    def __init__(self, app: ASGIApp, mount_path: str) -> None:
        self.app = app
        self.mount_path = mount_path.rstrip('/')

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Rewrite the root path before the admin application routes the request."""
        if scope['type'] in {'http', 'websocket'}:
            scope = _with_mount_root_path(scope, self.mount_path)
        await self.app(scope, receive, send)


def install_admin_mount_path(app: ASGIApp, mount_path: str = '/admin') -> None:
    """Wrap the SQLAdmin mount so its routes match."""
    routes = getattr(app, 'routes', None)
    if routes is None:
        return
    normalized = mount_path.rstrip('/')
    for route in routes:
        if isinstance(route, Mount) and route.path == normalized:
            route.app = AdminMountPath(route.app, normalized)
            return


def _with_mount_root_path(scope: Scope, mount_path: str) -> Scope:
    path = scope.get('path', '')
    if not isinstance(path, str):
        return scope
    marker = f'{mount_path}/'
    mount_at = path.find(marker)
    if mount_at == -1:
        if path.rstrip('/') != mount_path:
            return scope
        root_path = mount_path
    else:
        root_path = path[: mount_at + len(mount_path)]
    return {**scope, 'root_path': root_path}
