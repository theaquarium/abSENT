import cherrypy
import os
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from .websocket import DevWebsocket

cherrypy.config.update({'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

cherrypy.config.update({
    'global': {
        'engine.autoreload.on': False,
        'checker.on': True,
        'tools.log_headers.on': False,
        'request.show_tracebacks': True,
        'request.show_mismatched_params': False,
        'log.screen': False,
    },
})


class Root(object):
    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler


def start_webserver():
    # cherrypy.quickstart(Root(), '/')

    cherrypy.tree.mount(Root(), '/', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': DevWebsocket,
        },
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
            'tools.staticdir.index': 'index.html',
        }
    })
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
