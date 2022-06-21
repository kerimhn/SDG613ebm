
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask import Flask, request, url_for, render_template_string
from pathlib import Path
from importlib import import_module
import os

# Simple application dispatching for Dash. Adding all dash instances
# to the same flask instance is apparently quite bug-prone, so we
# instantiate a new flask instance for each dash component, and
# dispatch with Wergzeug middleware.

# module_dir = "Apper_SDG613"
module_dir = "modules"
global_prefix = os.environ.get("PASSENGER_BASE_URI")
if global_prefix is None:
    global_prefix = ''

modules = [ f.stem for f in Path(module_dir).glob("*.py") ]
server = Flask(__name__)

module_registry = {}
module_index = {}
for module in modules:
    prefix = global_prefix + '/' + module 
    try:
        dash_module = import_module(module_dir +  '.' + module)
        # Create local server to avoid blueprint collisions. (Probably a dash bug)
        local_server = Flask(prefix)
        dash_app = dash_module.app
        dash_app.init_app(local_server, url_base_pathname = module + '/', requests_pathname_prefix=prefix + '/')

        module_registry['/' + module] = local_server
        module_index[prefix] = dash_app.title if dash_app.title is not None else module
    except Exception as inst:
        module_index[prefix] =  module  + ' (not loaded)'
        server.logger.info("Invalid dash module " + module)

@server.route('/')
def index():
    return render_template_string('''<!doctype html>
<html><body><h1>Modules</h1>
<ul>
    {% for path, title  in modules %}
      <li><a href="{{path}}/">{{path}} -  {{title}}</li>
    {% endfor %}
</ul>    
</body></html>
''', modules=module_index.items())

    
app = DispatcherMiddleware(server, module_registry)

if __name__ == '__main__':
    run_simple('localhost', 8181, app,  use_reloader=True)
