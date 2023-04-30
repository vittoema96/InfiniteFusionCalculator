import os

if __name__ == '__main__':
    os.system('pyinstaller --noconfirm --onedir --windowed '
              '--icon "./ifft/icon.ico" '
              '--name "IFFT" '
              '--add-data "./ifft/data.csv;." '
              '--add-data "./ifft/pokemon_pixel_font.ttf;." '
              '--add-data "./ifft/data;data/" '
              '--add-data "./ifft/gui;gui/"  '
              '"./ifft/main.py"')
