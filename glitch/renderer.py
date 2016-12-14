from aiohttp import web
import asyncio

app = web.Application()

async def moosic(req):
	print("req", type(req))
	resp = web.StreamResponse()
	resp.content_type = "text/plain" # "audio/mpeg"
	await resp.prepare(req)
	resp.write(b"Hello, world!")
	for i in range(5):
		print(i,"...")
		await asyncio.sleep(i)
		resp.write(b"\n\nWaited %d seconds" % i)
		await resp.drain()
	resp.write(b"\n\nDone waiting.")
	print("Done.")
	await resp.drain()
	await resp.write_eof()
	return resp

app.router.add_get("/all.mp3", moosic)

web.run_app(app, port=8889)
