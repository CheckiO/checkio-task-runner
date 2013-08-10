import sys
import os
import json
import re
import urllib
import urlparse
from os.path import join as path_join

from django.template import Template, Context
from django.conf import settings as dj_settings
from twisted.web.client import getPage
from twisted.web.server import NOT_DONE_YET
from twisted.web import server, resource, static
from twisted.internet import reactor
from twisted.python.log import startLogging

dj_settings.configure()

import settings

from runners import settings as r_settings
from runners.web import WebServerSite, WebResource
from runners.echo import EchoServerFactory

startLogging(sys.stdout)

TASK_DIR = None
TASK_NAME = "Task's Name"
TASK_SLUG = None

TEST_BY_CODE = 2


def get_task_config():
    task_config_file = open(path_join(TASK_PATH, settings.TASK_CONFIG_NAME))
    return json.load(task_config_file)


def get_description():
    with open(path_join(TASK_PATH,
                        settings.INFO_DIR,
                        settings.DESCRIPTION_FILE_NAME)) as f:
        description = f.read()
        return Template(description).render(
            Context({'TASK_SLUG': TASK_SLUG,
                     'MEDIA_URL': settings.MEDIA_URL})
        )


def get_story():
    with open(path_join(TASK_DIR,
                        settings.INFO_DIR,
                        settings.STORY_FILE_NAME)) as f:
        return f.read()


def get_template(name):
    with open(path_join(settings.TEMPLATE_DIR, name)) as f:
        return f.read()


def get_initial_codes():
    codes_dir = path_join(TASK_DIR,
                          settings.EDITOR_DIR,
                          settings.INITIAL_CODE_DIR)
    result = {}
    temp_code_path = path_join(settings.TEMP_DIR, settings.TEMP_CODE)
    temp_code = None
    if os.path.exists(temp_code_path):
        with open(temp_code_path) as tf:
            temp_code = tf.read()
    for code_file in os.listdir(codes_dir):
        name = code_file.rsplit(".", 1)[0]
        if temp_code:
            result[name] = temp_code
        else:
            with open(os.path.join(codes_dir, code_file)) as tf:
                result[name] = tf.read()
    return result


def get_referee():
    with open(path_join(TASK_DIR,
                        settings.VERIFICATION_DIR,
                        settings.REFEREE_NAME)) as f:
        return f.read()


def get_tests():
    tests_dir = path_join(TASK_DIR,
                          settings.VERIFICATION_DIR,
                          settings.TESTS_DIR)
    result = {}
    for code_file in os.listdir(tests_dir):
        if re.match("test_\w+\.py", code_file):
            name = code_file.rsplit(".", 1)[0].split("_", 1)[-1]

            with open(os.path.join(tests_dir, code_file)) as tf:
                result[name] = tf.read()
    return result


def py_to_json(text):
    TESTS = OPTIONS = None
    exec (text)
    res = {
        "tests": TESTS,
        "options": OPTIONS
    }
    return res


def get_animation_js():
    with open(path_join(TASK_DIR,
                        settings.EDITOR_DIR,
                        settings.ANIMATION_JS)) as f:
        return f.read()

def get_animation_css():
    with open(path_join(TASK_DIR,
                        settings.EDITOR_DIR,
                        settings.ANIMATION_CSS)) as f:
        return f.read()

def set_globals(path):
    global TASK_DIR, TASK_NAME, TASK_SLUG
    TASK_DIR = path
    task_config = get_task_config().get('global', {})
    TASK_NAME = task_config.get('task_name', TASK_NAME)
    TASK_SLUG = task_config.get('task_slug', TASK_SLUG)


def get_animation_templates():
    with open(path_join(TASK_DIR,
                        settings.EDITOR_DIR,
                        settings.TEMPLATE_HTML)) as tf:
        return tf.read()

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
    isLeaf = False

    def getChild(self, path, request):
        if path == '':
            return self
        return resource.Resource.getChild(self, path, request)

    def render_GET(self, request):
        description = get_description()
        story = get_story()
        task_name = TASK_NAME
        context = Context(locals())
        template = Template(get_template("base.html"))

        return str(template.render(context))


class EditorPage(resource.Resource):
    isLeaf = True

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
            'initial_codes': initial_codes,
            'animation_js': get_animation_js(),
            'animation_css': get_animation_css(),
            'templates': get_animation_templates()
        })
        template = Template(get_template("editor.html"))
        return str(template.render(context))


class CenterForward(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        d = None
        data = urllib.urlencode(
            dict([(k, v[0]) for k, v in request.args.items()]))
        if request.postpath[0] == 'check':
            d = getPage("http://" + settings.CENTER_IP + ":"
                        + str(settings.CENTER_PORT) + "/center/check",
                        method="POST",
                        postdata=data)
        elif request.postpath[0] == 'console':
            d = getPage("http://" + settings.CENTER_IP + ":"
                        + str(settings.CENTER_PORT) + "/center/console",
                        method="POST",
                        postdata=data)

        def getPageResult(data):
            data = "[" + data.strip(",") + "]"
            request.write(data)
            request.finish()
        if d:
            d.addCallback(getPageResult)
        return NOT_DONE_YET


class ForCenter(resource.Resource):
    isLeaf = True

    def get_check_info(self, in_data):
        data = urlparse.parse_qs(in_data)
        src = get_referee()

        tests_py = get_tests()
        tests_json = dict([(k, py_to_json(v)) for k, v in tests_py.items()])
        show_process = 'f'
        prog_lang = 'python-27'

        tests = []
        for k in sorted(tests_json.keys()):
            tests.append([
                src,
                tests_json[k],
                show_process,
                prog_lang,
                k])
        info = {
            'user_id': 1,
            'tests': tests,
            'type': TEST_BY_CODE,
            'owner_run': 1
        }
        return json.dumps(info)

    def log_req(self, data):
        return json.dumps({})

    def save_code(self, data):
        temp_code = path_join(settings.TEMP_DIR, settings.TEMP_CODE)
        with open(temp_code, "w") as tf:
            tf.write(data)
        return json.dumps(os.path.abspath(temp_code))

    def reset_code(self, data):
        temp_code_path = path_join(settings.TEMP_DIR, settings.TEMP_CODE)
        if os.path.exists(temp_code_path):
            os.remove(temp_code_path)
        initial_codes = get_initial_codes()
        return json.dumps(initial_codes.get('python_27', ""))

    def get_user_info(self, data):
        return json.dumps({
            'id': 1,
            'super': True
        })

    def render_GET(self, request):
        data = request.content.read()
        request.write(self.get_user_info(data))
        request.finish()
        return NOT_DONE_YET

    def render_POST(self, request):
        data = request.content.read()

        function_map = {
            'get-check-info': self.get_check_info,
            'log': self.log_req,
            'save': self.save_code,
            'reset': self.reset_code,
            'get-user-info': self.get_user_info

        }
        act = request.postpath[0]
        res = function_map[act](data)
        request.write(res)
        request.finish()
        return NOT_DONE_YET


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
    root.putChild('center', CenterForward())
    root.putChild('for-center', ForCenter())

    root.putChild('static', static.File(settings.STATIC_DIR))
    root.putChild('logo',
                  static.File(path_join(TASK_DIR,
                                        settings.INFO_DIR,
                                        settings.LOGO_DIR),
                              defaultType="image/svg+xml"))
    media = static.File(
        path_join(TASK_DIR, settings.INFO_DIR, settings.MEDIA_DIR))
    root.putChild(settings.MEDIA_URL, media)
    media.putChild(TASK_SLUG, static.File(
        path_join(TASK_DIR, settings.INFO_DIR, settings.MEDIA_DIR)))

    site = server.Site(root)

    reactor.listenTCP(r_settings.CHAT_SERVICE_PORT, EchoServerFactory())
    reactor.listenTCP(r_settings.WEB_SERVICE_PORT, WebServerSite(WebResource()))
    reactor.listenTCP(settings.WEB_PORT, site)
    reactor.run()
