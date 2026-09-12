from aiohttp.web import Application, AppRunner, TCPSite, Response
import logging

logger = logging.getLogger(__name__)

PORT = 8080

ADVICE = """
I love odette <3 ...
"""


async def checkHealth(request):
    return Response(text=ADVICE, content_type="text/plain")


async def startServer() -> None:
    app = Application()

    app.router.add_get("/", checkHealth)
    app.router.add_get("/healthz", checkHealth)

    app.router.add_static(
        "/images/",
        "gidownloads/"
    )

    runner = AppRunner(app, access_log=None)
    await runner.setup()

    site = TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info(f"HTTP server listening on port {PORT}")