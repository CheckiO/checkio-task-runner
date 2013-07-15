from random import randint, choice
import sys
import os
import json
from os.path import join as path_join
from django.template import Template, Context
from django.conf import settings as dj_settings

dj_settings.configure()
import settings

from twisted.web import server, resource, static
from twisted.internet import reactor
from twisted.python.log import startLogging

startLogging(sys.stdout)

class TaskException(Exception):
    pass


TASK_DIR = None
TASK_NAME = "Task's Name"


def get_task_config():
    task_config_file = open(path_join(TASK_PATH, settings.TASK_CONFIG_NAME))
    return json.load(task_config_file)


def get_description():
    with open(path_join(TASK_PATH,
                        settings.INFO_DIR,
                        settings.DESCRIPTION_FILE_NAME)) as f:
        return f.read()


def get_template(name):
    with open(path_join(settings.TEMPLATE_DIR, name)) as f:
        return f.read()


def get_initial_codes():
    codes_dir = path_join(TASK_DIR,
                          settings.EDITOR_DIR,
                          settings.INITIAL_CODE_DIR)
    result = {}
    for code_file in os.listdir(codes_dir):
        name = code_file.rsplit(".", 1)[0]

        with open(os.path.join(codes_dir, code_file)) as tf:
            result[name] = tf.read()
    return result

def set_globals(path):
    global TASK_DIR, TASK_NAME
    TASK_DIR = path
    task_config = get_task_config()
    TASK_NAME = task_config.get('task_name', TASK_NAME)


# def get_template(path):
#     with open(os.path.join(path, 'template.html')) as template:
#         return template.read()
#

# @app.route("/tryit")
# def tryit():
#     template_data = get_template(TASK_PATH)
#     tryit_content = re.search(
#         r'<script type="text/template" id="template_tryit">' +
#         r'(.*?)' +
#         r'</script>',
#         template_data,
#         re.S).groups()[0]
#
#     cfg = get_animation_cfg(TASK_PATH)
#     context = {
#         'task_name': TASK_NAME,
#         'width': cfg.get("tryit_results_width", 400),
#         'height': cfg.get("tryit_results_height", 200),
#         "tryit_content": tryit_content,
#         }
#
#     return render_template("tryit.html", **context)

class TaskPage(resource.Resource):
    def getChild(self, path, request):
        if path == '':
            return self
        return resource.Resource.getChild(self, path, request)

    def render_GET(self, request):
        description = get_description()
        context = Context(locals())
        template = Template(get_template("base.html"))

        return str(template.render(context))

class EditorPage(resource.Resource):

    def render_GET(self, request):
        cfg = get_task_config()["editor"]
        initial_codes = get_initial_codes()
        description = get_description()
        context = Context({
            'task_name': TASK_NAME,
            'description': description,
            'right_width': cfg.get("animation_panel_width", 400),
            'console_height': cfg.get("console_height", 230),
            'tryit_width': cfg.get("tryit_results_width", 400),
            'tryit_height': cfg.get("tryit_results_height", 200),
            'initial_codes': initial_codes
        })
        template = Template(get_template("editor.html"))
        return str(template.render(context))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: checkio-task-runner.py <task-path>")
        print(
            "    task-path -- path for special organised folder with task info")
        sys.exit(1)
    TASK_PATH = sys.argv[1]
    if not os.path.exists(TASK_PATH):
        print("Can not find the folder")
        sys.exit(2)
    set_globals(TASK_PATH)

    root = TaskPage()
    root.putChild('editor', EditorPage())
    root.putChild('static', static.File(settings.STATIC_DIR))
    root.putChild('logo',
                  static.File(path_join(TASK_DIR,
                                        settings.INFO_DIR,
                                        settings.LOGO_DIR),
                              defaultType="image/svg+xml"))

    site = server.Site(root)

    reactor.listenTCP(settings.WEB_PORT, site)
    reactor.run()