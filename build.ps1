Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
git clean -fdx
git reset --hard origin/main
python -m venv venv
.venvScriptsactivate
pip install -r requirements.txt
PyInstaller main.spec
copy *.exe nl.the-underground.streamdock.VolumerControl
deactivate