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


def set_globals(path):
    global TASK_DIR, TASK_NAME
    TASK_DIR = path
    task_config = get_task_config()
    TASK_NAME = task_config.get('task_name', TASK_NAME)


def random_int():
    return randint(0, 1000)


def random_str():
    return ''.join([chr(randint(48, 126)) for _ in range(randint(10, 20))])


def random_list():
    return [randint(0, 100) for _ in range(randint(10, 20))]


def random_answer():
    return choice([random_list, random_int, random_str])()


# @app.route('/info/media/<path:filename>')
# def custom_static_illustrations(filename):
#     return send_from_directory(os.path.join(TASK_PATH, "info", "media"),
#                                filename)
#
#
# @app.route('/info/media/logo/<path:filename>')
# def custom_static_icon(filename):
#     return send_from_directory(os.path.join(TASK_PATH, "info", "logo"), filename)
#
#
# @app.route('/media/<path:filename>')
# def custom_media(filename):
#     return send_from_directory(TASK_PATH, filename)
#
#
# def error_page(message, trace=""):
#     context = {
#         "message": message,
#         "traceback": trace,
#         "task_name": TASK_NAME
#
#     }
#     return render_template("error.html", **context)
#
#
# def get_description(path):
#     with open(os.path.join(path, "task_description.html")) as f:
#         return f.read()
#
#

#
#
# def get_categories(path):
#     categories = [p.split("_", 1)[1].rsplit(".", 1)[0]
#                   for p in os.listdir(path)
#                   if p.startswith("test_") and p.endswith(".json")]
#     return filter(None, categories)
#
#
#
#
#
# def get_tests(path, category):
#     with open(os.path.join(path, "test_{0}.json".format(category))) as tf:
#         test_dict = json.load(tf)
#     return test_dict["tests"]
#
#
# def get_initial_codes(path):
#     codes_dir = os.path.join(path, "editor", "initial_code")
#     result = {}
#     for code_file in os.listdir(codes_dir):
#         name = code_file.rsplit(".", 1)[0]
#
#         with open(os.path.join(codes_dir, code_file)) as tf:
#             result[name] = tf.read()
#     return result
#
# def get_template(path):
#     with open(os.path.join(path, 'template.html')) as template:
#         return template.read()
#
# @app.route('/')
# def main_page():
#     global TASK_PATH
#     global TASK_NAME
#     description = get_description(os.path.join(TASK_PATH, "info"))
#     task_config = get_task_config(TASK_PATH)
#
#     TASK_NAME = task_config.get('task_name', TASK_NAME)
#
#     context = {
#         'task_name': TASK_NAME,
#         'description': description.decode("utf-8"),
#         }
#     return render_template("base.html", **context)
#
# @app.route("/editor")
# def test_explanation(category=None, number=None):
#     # test_dir = os.path.join(TASK_PATH, "tests")
#     #
#     # categories = get_categories(test_dir)
#     # if not categories:
#     #     return error_page("Cant find any tests files.")
#     #
#     # if not category:
#     #     return redirect("/explanation/{0}/1".format(categories[0]))
#     #
#     # if category not in categories:
#     #     abort(404)
#     #
#     # category_index = categories.index(category)
#     # prev_category_index = category_index - 1 if category_index > 0 else 0
#     # next_category_index = category_index + 1 if category_index < len(categories) - 1 else len(categories) - 1
#     #
#     #
#     # tests = get_tests(test_dir, category)
#     #
#     # try:
#     #     test = tests[number - 1]
#     # except IndexError:
#     #     abort(404)
#     #
#     # input_data = test["input"]
#     # answer = test["answer"]
#     # explanation = test.get("explanation", None)
#     #
#     cfg = get_task_config(TASK_PATH)["editor"]
#
#     initial_codes = get_initial_codes(TASK_PATH)
#
#     description = get_description(os.path.join(TASK_PATH, "info"))
#     #
#     # template_data = get_template(TASK_PATH)
#     # animation_content = re.search(
#     #     r'<script type="text/template" id="template_animation">' +
#     #     r'(.*?)' +
#     #     r'</script>',
#     #     template_data,
#     #     re.S).groups()[0]
#     #
#     # test_result = choice([True, False])
#     # user_answer = answer if test_result else random_answer()
#     context = {
#         'task_name': TASK_NAME,
#         'description': description,
#         # 'test_data': {
#         #     'result': test_result,
#         #     'input': input_data,
#         #     'answer': answer,
#         #     'explanation': explanation
#         #
#         # },
#         # 'user_answer': user_answer,
#         'right_width': cfg.get("animation_panel_width", 400),
#         'console_height': cfg.get("console_height", 230),
#         'tryit_width': cfg.get("tryit_results_width", 400),
#         'tryit_height': cfg.get("tryit_results_height", 200),
#         'initial_codes': initial_codes
#         # 'number': number,
#         # 'quantity': len(tests),
#         # 'category': category,
#         # 'prev': number - 1 if number > 1 else 1,
#         # 'next': number + 1 if number < len(tests) else len(tests),
#         # "animation_content": animation_content,
#         # 'prev_category': categories[prev_category_index],
#         # 'next_category': categories[next_category_index],
#     }
#
#     return render_template("editor.html", **context)

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

# class Static(resource.Resource):
#


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
    root.putChild('static', static.File(settings.STATIC_DIR))
    root.putChild('logo',
                  static.File(path_join(TASK_DIR,
                                        settings.INFO_DIR,
                                        settings.LOGO_DIR),
                              defaultType="image/svg+xml"))

    site = server.Site(root)

    reactor.listenTCP(settings.WEB_PORT, site)
    reactor.run()