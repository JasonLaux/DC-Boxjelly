DC-Boxjelly
=====================

DC-Boxjelly Private Github Repository

- [DC-Boxjelly](#dc-boxjelly)
  - [Project Description](#project-description)
  - [Run from source code](#run-from-source-code)
  - [Features](#features)
  - [Documentation](#documentation)
    - [Specify python version](#specify-python-version)
    - [How to develop (Use command line to do the following process)](#how-to-develop-use-command-line-to-do-the-following-process)
    - [Interactive development](#interactive-development)
    - [UI development](#ui-development)
    - [Publish](#publish)
    - [File structure](#file-structure)
  - [System Requirements](#system-requirements)
  - [Technologies Used](#technologies-used)
  - [Setup Guide](#setup-guide)
  - [Testing](#testing)
  - [Release History](#release-history)
  - [Attribution](#attribution)

## Project Description

This repository contains the source code of Digital Certification (Boxjelly Team),
which supports management of MEX measurement and report generating. The reports can
be viewed in the software as well as exported as PDF files.

## Run from source code
- To directly run the program from source code, please use the `bat` script in project root.
- Run `install.bat` to install dependencies through pip.
- Run `run.bat` to start the program.


## Features
- The storage of MEX measurement raw files as well as their CAL jobs and equipments.
- Inputting and viewing of the files and their meta data (date, client information, etc.)
- Comparing and analysing MEX data.
- Generating PDF certification for MEX data.

## Documentation
This section contains the documentation used in developing the software.

### Specify python version
- If you want to do development in specify python version, please specify it in `pipenv`.
  - For example, instead of `pipenv sync`, use `pipenv sync --python 3.6`.
  - All pipenv commands need to add `--python x.x` switch.

### How to develop (Use command line to do the following process)
- Install [pipenv](https://pipenv.pypa.io/en/latest/)
- Run `pipenv sync --dev` to install dependency (including development dependency)
- Run `pipenv shell` to start a shell based on the virtualenv
- Then, use whatever shell command you want in the shell
- If you want to install any packages, use `pipenv install` instead of `pip install`.
  - After installing packages, use `pipenv lock -r > requirements.txt` to regenerate requirements file.

### Interactive development
- After the steps above, you can use `pipenv run repl` to start an interactive shell in IPython. You can import modules and test them, like `from models import Job`.
- If you use repl, modified modules can be reloaded automatically.
  - For documents about auto reloading, see https://ipython.org/ipython-doc/3/config/extensions/autoreload.html

### UI development
- First of all, please ensure that all dependency are install by `pipenv sync`
- Run `qt5-tools designer` in pipenv shell or directly use `pipenv run designer` to start a qt designer.
- After modifying `.ui` files in `app/gui/resources`, please run `pipenv run gen-resource` to generate `resources.py` file.

### Publish 
- Please ensure that pipenv is installed.
- Run `package.bat` to package the project.
- The packaged files are located at `dist` folder.

### File structure
An overview of the source code is listed below. Detail documents can be found in
each file and directory.

- app: Source code for the application
  - core: core function, data reading and writing
  - gui: The gui
  - export: Functions for exporting, such as pdf or digital certification.
  - main.py: The entry point of the program.
- assets: Files that used in publishing
- data: Folder that contains jobs and constants
- test: unit test files for `app/core`
- tools: Utility scripts for developing.

## System Requirements
- Microsoft windows
- Python (>=3.4)
- Microsoft Excel
- (For development only) Pipenv

## Technologies Used
- Python 
- Microsoft Excel
- Pipenv
- PyQt5
- GitHub and Git
- openpyxl
- xlwings

## Setup Guide
See [INSTALL.md](INSTALL.md)

## Testing
- To run unit tests, use `pipenv run test`
- The gui testing are under `gui_testing` folder.

## Release History
See full changelog on [CHANGELOG.md](./CHANGELOG.md)
- 11th Oct 2021: Sprint2
- 17th Sep 2021: Sprint1

## Attribution
1247145 - John Kah Yong Low johnkahyongl@student.unimelb.edu.au Product Owner  
1070917 - ChingYuan Yang chingyuany@student.unimelb.edu.au  Scrum master  
1087943 - Jianheng Shi jianheng@student.unimelb.edu.au Development Environment Lead  
1063288 - Shumin Liu ([@Liu233w](https://github.com/Liu233w))  shumin@student.unimelb.edu.au  Architecture Lead  
1044804 - Jiexin Liu jiexin@student.unimelb.edu.au  Deployment Lead  
1102336 - Chien-Chih Wang chienchihw@student.unimelb.edu.au  Quality Lead  
