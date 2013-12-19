checkio-task-runner
===================

The CheckiO task local runner is a tool for you to run your custom task
on your local machine. It creates a local web server where you can see
how your task will appear on checkio.org. A task must be in a specially
structured folder. For the local web server it uses Flask.

Requirements
------------

Twisted.

Syntax
------

python checkio-task-runner.py path-to-task-folder

Usage
-----

After running open your browser and go to http://127.0.0.1:5000 to see your task.



Task folder
-----------

The tasks folder is defined and explained in the next github
rep -- https://github.com/CheckiO/checkio-task-template
You can just fork it and create your task based on this
 template (Be careful with files names and structure).
