cd app/gui
pipenv run pyrcc5 resources.qrc -o resources.py
cd ../..
pipenv run main