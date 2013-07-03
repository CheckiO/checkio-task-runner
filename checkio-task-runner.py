from random import randint, choice
from flask import Flask, render_template, redirect, json, send_from_directory, abort
import sys
import os
import traceback

TASK_PATH = "./"
TASK_NAME = "Task's Name"

app = Flask(__name__, static_folder="./static-local")


def random_int():
    return randint(0, 1000)


def random_str():
    return ''.join([chr(randint(48, 126)) for i in range(randint(10, 20))])


def random_list():
    return [randint(0, 100) for i in range(randint(10, 20))]


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


@app.route('/')
def main_page():
    global TASK_PATH
    global TASK_NAME
    try:
        description = open(os.path.join(TASK_PATH, "description.html")).read()
    except IOError as er:
        return error_page("Cant find the description file.",
                          traceback.format_exc())
    try:
        task_config_file = open(os.path.join(TASK_PATH, "task.json"))
        task_config = json.load(task_config_file)
    except IOError:
        return error_page("Cant find the task's config file.",
                          traceback.format_exc())
    TASK_NAME = task_config.get('title', TASK_NAME)
    context = {
        'task_name': TASK_NAME,
        'description': description.decode("utf-8"),
    }
    return render_template("task.html", **context)


@app.route("/explanation")
@app.route("/explanation/<string:category>/<int:number>")
def test_explanation(category=None, number=None):
    test_dir = os.path.join(TASK_PATH, "tests")

    if not os.path.exists(test_dir):
        return error_page("Cant find tests folder.")
    categories = [p.split("_", 1)[1].rsplit(".", 1)[0]
                  for p in os.listdir(test_dir)
                  if p.startswith("test_") and p.endswith(".json")]
    categories = filter(None, categories)
    if not categories:
        return error_page("Cant find any tests files.")
    if not category:
        return redirect("/explanation/{0}/1".format(categories[0]))

    try:
        with open(os.path.join(test_dir,
                               "test_{0}.json".format(category))) as test_file:
            test_dict = json.load(test_file)
    except IOError:
        return error_page("Cant find the test file.",
                          traceback.format_exc())
    try:
        tests = test_dict["tests"]
        try:
            test = tests[number - 1]
        except IndexError:
            abort(404)

        input_data = test["input"]
        answer = test["answer"]
        explanation = test.get("explanation", None)
    except KeyError:
        return error_page("Wrong format for test file",
                          traceback.format_exc())

    try:
        with open(os.path.join(TASK_PATH, 'animation_cfg.json')) as cfg_file:
            cfg = json.load(cfg_file)
    except IOError:
        return error_page("Cant find the animation cfg file.",
                          traceback.format_exc())

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
        'next': number + 1 if number < len(tests) else len(tests)
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
