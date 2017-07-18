import os
import argparse
import jinja2

from sanic import Sanic, response
from sanic.response import json

app = Sanic(__name__)
app.static('/favicon.ico', './static/favicon.ico')


def render_jinja2(tpl_path, context={}):
    """
    Render jinja2 html template
    """
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


@app.route('/')
async def index_view(request):
    html = render_jinja2('./templates/index.html')
    return response.html(html)


@app.route('/tx')
async def tx_view(request):
    return json({'hello': 'tx_view'})


@app.route('/block')
async def block_view(request):
    return json({'hello': 'block_view'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
