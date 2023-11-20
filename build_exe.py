import os
import shutil
import zipfile
from zipfile import ZipFile

if __name__ == '__main__':
    APP_NAME = 'IFC'
    output_dir = 'dist'
    zip_name = f'{APP_NAME}.zip'
    win_name = f'{APP_NAME}.exe'
    mac_name = f'{APP_NAME}.app'

    def clean_dist(keep=zip_name):
        if os.path.isdir(output_dir):
            files = os.listdir(output_dir)
            for f in files:
                if f != keep:
                    p = os.path.join(output_dir, f)
                    if os.path.isdir(p):
                        shutil.rmtree(p)
                    else:
                        os.remove(p)

    clean_dist()

    zip_path = os.path.join(output_dir, zip_name)
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

    os.system('pyinstaller --noconfirm --onefile --windowed '
              '--icon "./ifc/resources/icon.ico" '
              f'--name "{APP_NAME}" '
              '--add-data "./ifc/data:ifc/data/" '
              '--add-data "./ifc/gui:ifc/gui/" '
              '--add-data "./ifc/resources:ifc/resources/"  '
              '"./ifc/main.py"')

    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(path, '..')))

    with ZipFile(zip_path, mode='w', compresslevel=9) as archive:
        archive.write(os.path.join(output_dir, win_name), win_name)
        zipdir(os.path.join(output_dir, mac_name), archive)

    clean_dist()
