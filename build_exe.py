import os
from zipfile import ZipFile

if __name__ == '__main__':
    os.system('pyinstaller --noconfirm --onefile --windowed '
              '--icon "./ifc/resources/icon.ico" '
              '--name "IFC" '
              '--add-data "./ifc/data;ifc/data/" '
              '--add-data "./ifc/gui;ifc/gui/" '
              '--add-data "./ifc/resources;ifc/resources/"  '
              '"./ifc/main.py"')
    with ZipFile(os.path.join('dist', 'IFC.zip'), mode="w") as archive:
        archive.write(os.path.join('dist', 'IFC.exe'))
