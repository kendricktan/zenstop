import time
import os
import argparse
import jinja2
import argparse

from sanic import Sanic, response
from sanic.response import json
from pyzen import PyZen


# CLI Var
parser = argparse.ArgumentParser(description='zens.top config')
parser.add_argument('--username', required=True, type=str)
parser.add_argument('--password', required=True, type=str)
parser.add_argument('--host', default='127.0.0.1', type=str)
parser.add_argument('--port', default='8231', type=str)
args, unknown = parser.parse_known_args()

# ZEN client
zen_client = PyZen(host=args.host, port=args.port,
                   username=args.username, password=args.password)

# Sanic
app = Sanic(__name__)
app.static('/favicon.ico', './static/favicon.ico')


""" Helper functions """


def epoch_to_datetime(e):
    """ 
    Convert epoch to human readable time

    Args:
        e: epoch
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e))


def render_jinja2(tpl_path, context={}):
    """
    Render jinja2 html template

    Args:
        tpl_path: template path
        context: template context
    """
    path, filename = os.path.split(tpl_path)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './'),
    )

    # Add template calls
    env.globals['epoch_to_datetime'] = epoch_to_datetime

    return env.get_template(filename).render(context)


def simpletx(txid):
    tx = zen_client.gettx(txid)

    if tx is None:
        return {}

    # Extract coinbase info
    coinbase = '???'
    if len(tx['vin']) > 0:
        coinbase = tx['vin'][0].get('coinbase', '???')

    # Get transaction addresses and output total
    tx_value_total = 0.0
    tx_addr = []
    for t in tx['vout']:
        current_value = t.get('value', 0.0)
        tx_value_total += current_value

        if 'scriptPubKey' in t:
            for addr in t['scriptPubKey'].get('addresses', []):
                tx_addr.append([addr, current_value])

    return {
        'txid': txid,
        'locktime': tx['locktime'],
        'version': tx['version'],
        'coinbase': coinbase,
        'tx_value_total': tx_value_total,
        'tx_addr': tx_addr
    }


""" Endpoint routes below """


@app.route('/')
async def index_view(request):
    latest_blocks = zen_client.getbestnblock(10)
    mining_info = zen_client.getmininginfo()

    cntxt = {
        'mining_info': mining_info,
        'latest_blocks': latest_blocks,
        'title': 'zens.top | Your one stop ZENCash blockchain explorer'
    }

    html = render_jinja2('./templates/index.html', cntxt)
    return response.html(html)


@app.route('/tx/<txid>')
async def tx_view(request, txid):
    tx = simpletx(txid)
    cntxt = {
        'title': 'tx {}'.format(txid),
        **tx,
    }

    html = render_jinja2('./templates/tx.html', cntxt)
    return response.html(html)


@app.route('/block/<block_hash>')
async def block_view(request, block_hash):
    try:
        block = zen_client.getblock(block_hash)
    except:
        block = {}

    cntxt = {
        'title': 'block {}'.format(block_hash),
        **block,
    }

    html = render_jinja2('./templates/block.html', cntxt)
    return response.html(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
