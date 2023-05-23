import os

if __name__ == '__main__':
    os.system('pyinstaller --noconfirm --onedir --windowed '
              '--icon "./ifc/icon.ico" '
              '--name "IFC" '
              '--add-data "./ifc/data.csv;." '
              '--add-data "./ifc/pokemon_pixel_font.ttf;." '
              '--add-data "./ifc/data;data/" '
              '--add-data "./ifc/gui;gui/"  '
              '"./ifc/main.py"')
