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

$pluginPath = "$env:APPDATA\HotSpot\StreamDock\plugins\nl.the-underground.streamdock.VolumerControl"
$destinationPath = "$env:APPDATA\HotSpot\StreamDock\plugins\"

# Remove the existing directory forcefully and recursively
Remove-Item -Path $pluginPath -Recurse -Force -ErrorAction SilentlyContinue

# Copy the new version
Copy-Item -Path ".\nl.the-underground.streamdock.VolumerControl" -Destination $destinationPath -Recurse -Force