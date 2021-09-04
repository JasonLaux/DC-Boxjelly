pipenv sync
cd app/gui
pyrcc5 resources.qrc -o resources.py
cd ../..
pipenv run main