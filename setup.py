from setuptools import setup, find_packages
import os

def gen_data_files(*dirs):
    results = []

    for src_dir in dirs:
        for root,dirs,files in os.walk(src_dir):
            results.append((root, map(lambda f:root + "/" + f, files)))
    return results

data_files = gen_data_files("PyAuto/lib")

setup(
    name = 'PyAuto',
    version = '1.0.0',
    description = 'python auto tools',
    license = 'GPL',
    packages = find_packages(exclude = ['contrib', 'docs', 'tests*']),
    install_requires = ['pyautogui'],
    author = 'pxx',
    data_files = data_files,
    author_email = 'pxx1991824@gmail.com',
    keywords = ['python', 'auto'],
    url = ''
)
