call activate DC
cd app/gui
pyrcc5 resources.qrc -o resources.py
cd ../..
python -m app.main