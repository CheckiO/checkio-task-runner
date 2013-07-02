from flask import Flask, render_template, redirect, json, send_from_directory
import sys
import os

app = Flask(__name__, static_folder="./static-local")
TASK_PATH = "./"
DEFAULT_NAME = "Task's Name"


@app.route('/static/files/illustrations/<path:filename>')
def custom_static(filename):
    print(os.path.join(TASK_PATH, "illustrations"))
    print(filename)
    return send_from_directory(os.path.join(TASK_PATH, "illustrations"), filename)

def error_page(message, er):
    context = {
        "message": message
    }
    return render_template("error.html", **context)

@app.route('/')
def main_page():
    global TASK_PATH
    try:
        description = open(os.path.join(TASK_PATH, "description.html")).read()
    except IOError as er:
        return error_page("Cant find the description file.", er)
    try:
        task_config_file = open(os.path.join(TASK_PATH, "task.json"))
        task_config = json.load(task_config_file)
    except IOError as error:
        return error_page("Cant find the task's config file.", error)
    context = {
        'task_name': task_config.get('title', DEFAULT_NAME),
        'description': description.decode("utf-8"),
    }
    return render_template("task.html", **context)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: checkio-local-task.py <task-path>")
        print("    task-path -- path for special organised folder with task info")
        sys.exit(1)
    global TASK_PATH
    TASK_PATH = sys.argv[1]
    if not os.path.exists(TASK_PATH):
        print("Cant find the folder")
        sys.exit(2)
    app.run()
