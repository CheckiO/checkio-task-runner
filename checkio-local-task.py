from flask import Flask
import sys
import os

app = Flask(__name__)
TASK_PATH = ""

@app.route('/')
def main_page():
    return 'Hello World!'


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
