#this script writes a new .pth file to site packages
import site
import os
import pathlib
import pdb

parentDir = pathlib.Path(__file__).resolve().parent
subDirs = [child for child in parentDir.rglob('*') if child.is_dir() and '__' not in child.name]

site_packages_path = site.getsitepackages()[0]
pth_file_path = os.path.join(site_packages_path, 'tlm.pth')
with open(pth_file_path, 'w') as f:
    for subDir in subDirs:
        f.write(str(subDir) + '\n')