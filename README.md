# Student-Registration-System
This project is part of our institute's pre-final year Course IT314-Software Development.


##Installation and Guide

Pre-requisites:
You must have python and supporting IDE installed.

###Setting up Virtual Environment
1. Clone this project into a designated folder and open git bash/ CLI/ VSCode.
2. If there are any virtual environment folders, delete them.
3. Once you are in project folder, create a virtual environment by using "py -m venv <name-of-virtual-env>"
4. Activate the virtual environment using "./<name-of-virtual-env>/Scripts/activate"
5. Move to SRS folder, and install requirements.txt to your virtual environment using "pip install -r requirements.txt"

Your virtual environment is ready to use.

###Working with Django
1. Once you are in your project folder, with your virtual environment activated, run "py manage.py runserver" to start the server on localhost.
2. To quit the server, you must press "ctrl + c".

Note:- 
Beware not to delete any files of the project.
Always use makemigrations before migrate.


###Commiting your work to repository
1. Always push your changes in your branch unless compiling.
2. You may want to add your virtual environment file to .gitignore file to avoid uploading it to github.
