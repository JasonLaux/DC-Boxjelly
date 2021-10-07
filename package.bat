pipenv sync
pipenv run pyinstaller "Digital Calibration.spec"
copy "assets\Digital Calibration.bat" dist

