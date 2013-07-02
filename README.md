checkio-task-runner
===================

Checkio task local runner is a tool for run your custom task at your machine.
It create local web server, where you can see how your task will be seem at checkio.org.
A task must be special structured folder. For local web server it use Flask.

Requirements
------------

Flask.

Syntax
------

python checkio-task-runner.py path-to-task-folder

Usage
-----

After running open your browser for http://127.0.0.1:5000 and you will see your task.

Task folder
-----------

Task's folder defined and explained in the next github rep -- https://github.com/CheckiO/checkio-task-template
You can just fork it and create your task based on this template (Be careful with files names).
