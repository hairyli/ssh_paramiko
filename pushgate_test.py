import prometheus_client
from prometheus_client import Counter,Gauge
from prometheus_client.core import CollectorRegistry
from aiohttp import web
import aiohttp
import asyncio
import uvloop
import random,logging,time,datetime
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
routes = web.RouteTableDef()
# metrics包含
requests_total = Counter("request_count", "Total request cout of the host")
random_value = Gauge("random_value", "Random value of the request")
@routes.get('/metrics')
async def metrics(request):
  requests_total.inc()
  # requests_total.inc(2)
  data = prometheus_client.generate_latest(requests_total)
  return web.Response(body = data,content_type="text/plain")
@routes.get("/metrics2")
async def metrics2(request):
  random_value.set(random.randint(0, 10))
  return web.Response(body = prometheus_client.generate_latest(random_value),content_type="text/plain")
@routes.get('/')
async def hello(request):
  return web.Response(text="Hello, world")

c = Counter('requests_total', 'HTTP requests total', ['method', 'clientip'])
c.labels('get', '127.0.0.1').inc()
c.labels('post', '192.168.0.1').inc(3)
c.labels(method="get", clientip="192.168.0.1").inc()
g = Gauge('my_inprogress_requests', 'Description of gauge',['mylabelname'])
g.labels(mylabelname='str').set(3.6)  #

if __name__ == '__main__':
  logging.info('server start：%s'% datetime.datetime.now())
  app = web.Application(client_max_size=int(2)*1024**2)  #
  app.add_subapp(routes)
  web.run_app(app,host='0.0.0.0',port=2222)
  logging.info('server close：%s'% datetime.datetime.now())