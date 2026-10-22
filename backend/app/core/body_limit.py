from starlette.responses import JSONResponse


class BodyLimit:
    """Bound actual bytes, including chunked requests without Content-Length."""
    def __init__(self, app, maximum=15_000_000):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        parts, total = [], 0
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            total += len(event.get("body", b""))
            if total > self.maximum:
                response = JSONResponse({"error": {"code": 413, "message": "Request body too large"}}, status_code=413)
                return await response(scope, receive, send)
            parts.append(event.get("body", b""))
            if not event.get("more_body", False):
                break
        delivered = False
        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(parts), "more_body": False}
            return await receive()
        await self.app(scope, bounded_receive, send)
