# DC-Boxjelly
DC-Boxjelly Private Github Repository


## Team Members
1247145 - John Kah Yong Low johnkayongl@student.unimelb.edu.au Product Owner  
1070917 - ChingYuan Yang chingyuany@student.unimelb.edu.au  Scrum master  
1087943 - Jianheng Shi jianheng@student.unimelb.edu.au Development Environment Lead  
1063288 - Shumin Liu  shumin@student.unimelb.edu.au  Architecture Lead  
1044804 - Jiexin Liu jiexin@student.unimelb.edu.au  Deployment Lead  
1102336 - Chien-Chih Wang chienchihw@student.unimelb.edu.au  Quality Lead  

## Run from source code
- To directly run the program from source code, please use the `bat` script in project root.
- Run `install.bat` to install dependencies through pip.
- Run `run.bat` to start the program.

## How to develop (Use command line to do the following process)
- Install [pipenv](https://pipenv.pypa.io/en/latest/)
- Run `pipenv sync` to install dependency
- Run `pipenv shell` to start a shell based on the virtualenv
- Then, use whatever shell command you want in the shell
- If you want to install any packages, use `pipenv install` instead of `pip install`.
  - After installing packages, use `pipenv lock -r > requirements.txt` to regenerate requirements file.
- To run unit tests, use `pipenv run test`

## Interactive development
- After the steps above, you can use `pipenv run repl` to start an interactive shell in IPython. You can import modules and test them, like `from models import Job`.
- If you use repl, modified modules can be reloaded automatically.
  - For documents about auto reloading, see https://ipython.org/ipython-doc/3/config/extensions/autoreload.html

## UI development
- First of all, please ensure that all dependency are install by `pipenv sync`
- Run `qt5-tools designer` in pipenv shell or directly use `pipenv run designer` to start a qt designer.
- After modifying `.ui` files in `app/gui/resources`, please run `pipenv run gen-resource` to generate `resources.py` file.

## Publish 
- Please ensure that pipenv is installed.
- Run `package.bat` to package the project.
- The packaged files are located at `dist` folder.

## File structure
The purpose of source code files are listed below:
- app: Source code for the application
  - core: core function, data reading and writing
  - gui: The gui
  - output: Functions for output, such as pdf or digital certification.
  - main.py: The entry point of the program.
- assets: Files that used in publishing
- data: Folder that contains jobs and constants
- test: unit test files for `app/core`
- tools: Utility scripts for developing.