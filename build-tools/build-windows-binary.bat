start python3 -m venv ..\venv
venv\Scripts\activate.bat
pip3 install -r ..\requirements\requirements-linux-python3.txt
pip3 install pyinstaller
pyinstaller --onefile labelVid.spec