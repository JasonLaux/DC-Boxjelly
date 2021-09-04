pipenv sync
cd app/gui
pipenv run pyrcc5 resources.qrc -o resources.py
cd ../..
pipenv run pyinstaller --name="Digital Calibration" --windowed --icon=app/gui/resources/app.ico --add-data="app/core/constant.xlsx;app/core" --onefile app/main.py
