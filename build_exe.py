import os
import sys

if __name__ == '__main__':
    os.system('pyinstaller --noconfirm --onedir --windowed '
              '--icon "./ifc/resources/icon.ico" '
              f'--name "IFC_{sys.platform}" '
              '--add-data "./ifc/data;ifc/data/" '
              '--add-data "./ifc/gui;ifc/gui/" '
              '--add-data "./ifc/resources;ifc/resources/"  '
              '"./ifc/main.py"')
