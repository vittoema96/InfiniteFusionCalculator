import os
from zipfile import ZipFile

if __name__ == '__main__':
    APP_NAME = 'IFC'
    win_ext = 'exe'
    mac_ext = 'app'

    os.system('pyinstaller --noconfirm --onefile --windowed '
              '--icon "./ifc/resources/icon.ico" '
              f'--name "{APP_NAME}" '
              '--add-data "./ifc/data:ifc/data/" '
              '--add-data "./ifc/gui:ifc/gui/" '
              '--add-data "./ifc/resources:ifc/resources/"  '
              '"./ifc/main.py"')
    os.chdir('dist')

    result_file_name = None
    ext = None
    for extension in [win_ext, mac_ext]:
        f = f'{APP_NAME}.{extension}'
        if os.path.exists(f):
            result_file_name = f
            ext = extension
            break

    assert result_file_name, "Resulting file is either inexistent or does not have an .exe or .app extension"


    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(path, '..')))

    with ZipFile(f'{APP_NAME}_{ext}.zip', mode="w") as archive:
        zipdir(f'{APP_NAME}.{ext}', archive)

    if os.path.exists(APP_NAME):
        os.remove(APP_NAME)
