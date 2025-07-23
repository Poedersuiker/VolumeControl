Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
git fetch origin
git reset --hard origin/main
git clean -fdx
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
PyInstaller main.spec
copy dist\*.exe nl.the-underground.streamdock.VolumerControl
deactivate