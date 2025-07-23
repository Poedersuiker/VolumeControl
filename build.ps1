Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
git fetch origin
git reset --hard origin/main
git clean -fdx
python -m venv venv
.venvScriptsactivate
pip install -r requirements.txt
PyInstaller main.spec
copy *.exe nl.the-underground.streamdock.VolumerControl
deactivate