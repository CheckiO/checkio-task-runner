from flask import Flask, render_template, redirect, json, send_from_directory
import sys
import os
import traceback

TASK_PATH = "./"
TASK_NAME = "Task's Name"

app = Flask(__name__, static_folder="./static-local")

@app.route('/static/files/illustrations/<path:filename>')
def custom_static_illustrations(filename):
    return send_from_directory(os.path.join(TASK_PATH, "illustrations"), filename)

@app.route('/static/files/icon/<path:filename>')
def custom_static_icon(filename):
    return send_from_directory(os.path.join(TASK_PATH, "icon"), filename)


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
        trace = traceback.format_exc()
        return error_page("Cant find the description file.", trace)
    try:
        task_config_file = open(os.path.join(TASK_PATH, "task.json"))
        task_config = json.load(task_config_file)
    except IOError as error:
        return error_page("Cant find the task's config file.", error)
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
    print(category)
    if not category:
        print(categories)
        return redirect("/explanation/{0}/1".format(categories[0]))

    context = {
        'task_name': TASK_NAME
    }

    return render_template("explanation.html", **context)






if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: checkio-task-runner.py <task-path>")
        print("    task-path -- path for special organised folder with task info")
        sys.exit(1)
    global TASK_PATH
    TASK_PATH = sys.argv[1]
    if not os.path.exists(TASK_PATH):
        print("Cant find the folder")
        sys.exit(2)
    app.debug = True
    app.run()
