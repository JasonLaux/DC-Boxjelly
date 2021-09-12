pipenv sync
cd app/gui
pipenv run pyrcc5 resources.qrc -o resources.py
cd ../..
pipenv run pyinstaller --name="Digital Calibration" --windowed --icon=app/gui/resources/app.ico --add-data="constant.xlsx;." app/main.py
copy "assets\Digital Calibration.bat" dist

