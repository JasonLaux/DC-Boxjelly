pipenv sync
cd app/gui
pyrcc5 resources.qrc -o resources.py
cd ../..
pipenv run pyinstaller --name="Digital Calibration" --windowed --icon=app/gui/resources/app.ico --onefile app/main.py
