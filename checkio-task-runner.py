from random import randint, choice
from flask import Flask, render_template, redirect, json, send_from_directory,\
    abort
import sys
import os
import re


class TaskException(Exception):
    pass


TASK_PATH = "./"
TASK_NAME = "Task's Name"

app = Flask(__name__, static_folder="./static-local")


def random_int():
    return randint(0, 1000)


def random_str():
    return ''.join([chr(randint(48, 126)) for _ in range(randint(10, 20))])


def random_list():
    return [randint(0, 100) for _ in range(randint(10, 20))]


def random_answer():
    return choice([random_list, random_int, random_str])()


@app.route('/static/files/illustrations/<path:filename>')
def custom_static_illustrations(filename):
    return send_from_directory(os.path.join(TASK_PATH, "illustrations"),
                               filename)


@app.route('/static/files/icon/<path:filename>')
def custom_static_icon(filename):
    return send_from_directory(os.path.join(TASK_PATH, "icon"), filename)


@app.route('/media/<path:filename>')
def custom_media(filename):
    return send_from_directory(TASK_PATH, filename)


def error_page(message, trace=""):
    context = {
        "message": message,
        "traceback": trace,
        "task_name": TASK_NAME

    }
    return render_template("error.html", **context)


def get_description(path):
    with open(os.path.join(path, "description.html")) as f:
        return f.read()


def get_task_config(path):
    task_config_file = open(os.path.join(path, "task.json"))
    return json.load(task_config_file)


def get_categories(path):
    categories = [p.split("_", 1)[1].rsplit(".", 1)[0]
                  for p in os.listdir(path)
                  if p.startswith("test_") and p.endswith(".json")]
    return filter(None, categories)


@app.route('/')
def main_page():
    global TASK_PATH
    global TASK_NAME
    description = get_description(TASK_PATH)
    task_config = get_task_config(TASK_PATH)

    TASK_NAME = task_config.get('task_name', TASK_NAME)

    context = {
        'task_name': TASK_NAME,
        'description': description.decode("utf-8"),
    }
    return render_template("task.html", **context)


def get_tests(path, category):
    with open(os.path.join(path, "test_{0}.json".format(category))) as tf:
        test_dict = json.load(tf)
    return test_dict["tests"]


def get_animation_cfg(path):
    with open(os.path.join(path, 'animation_cfg.json')) as cfg_file:
        return json.load(cfg_file)


def get_template(path):
    with open(os.path.join(path, 'template.html')) as template:
        return template.read()


@app.route("/explanation")
@app.route("/explanation/<string:category>/<int:number>")
def test_explanation(category=None, number=None):
    test_dir = os.path.join(TASK_PATH, "tests")

    categories = get_categories(test_dir)
    if not categories:
        return error_page("Cant find any tests files.")

    if not category:
        return redirect("/explanation/{0}/1".format(categories[0]))

    if category not in categories:
        abort(404)

    tests = get_tests(test_dir, category)

    try:
        test = tests[number - 1]
    except IndexError:
        abort(404)

    input_data = test["input"]
    answer = test["answer"]
    explanation = test.get("explanation", None)

    cfg = get_animation_cfg(TASK_PATH)

    template_data = get_template(TASK_PATH)
    animation_content = re.search(
        r'<script type="text/template" id="template_animation">' +
        r'(.*?)' +
        r'</script>',
        template_data,
        re.S).groups()[0]

    test_result = choice([True, False])
    user_answer = answer if test_result else random_answer()
    context = {
        'task_name': TASK_NAME,
        'test_data': {
            'result': test_result,
            'input': input_data,
            'answer': answer,
            'explanation': explanation

        },
        'user_answer': user_answer,
        'width': cfg.get("animation_panel_width", 400),
        'number': number,
        'quantity': len(tests),
        'category': category,
        'prev': number - 1 if number > 1 else 1,
        'next': number + 1 if number < len(tests) else len(tests),
        "animation_content": animation_content
    }

    return render_template("explanation.html", **context)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: checkio-task-runner.py <task-path>")
        print(
            "    task-path -- path for special organised folder with task info")
        sys.exit(1)
    global TASK_PATH
    TASK_PATH = sys.argv[1]
    if not os.path.exists(TASK_PATH):
        print("Cant find the folder")
        sys.exit(2)
    app.debug = True
    app.run()
