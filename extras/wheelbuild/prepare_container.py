import subprocess
import os

# Running a Linux docker on Windows CI runners messes with the keyboard mapping of bash
# commands which affects symbols like -?/\ and makes writing commands impossible. Somehow,
# if we use .py files instead of .sh files, we can shell out from here with a correct
# keyboard.

if not os.path.exists("/skrepo"):
    subprocess.run('git clone https://github.com/scikit-build/scikit-build /skrepo', shell=True, check=True)

if not os.path.exists("/boost"):
    for command in (
        'curl -L https://boostorg.jfrog.io/artifactory/main/release/1.79.0/source/boost_1_79_0.tar.gz -o boost.tar.gz',
        'tar -xzf boost.tar.gz',
        'mv boost_1_79_0 /boost'
    ):
        subprocess.run(command, shell=True, check=True)
