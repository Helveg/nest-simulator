import subprocess
import os

# Running a Linux docker on Windows CI runners messes with the keyboard mapping of bash
# commands which affects symbols like -?/\ and makes writing commands impossible. Somehow,
# if we use .py files instead of .sh files, we can shell out from here with a correct
# keyboard.

BOOST_VERSION = [1, 79, 0]
GSL_VERSION = [2, 7, 1]


def main():
    if not os.path.exists("/boost"):
        install_boost()
    if not os.path.exists("/gsl"):
        install_gsl()


def run_sequence(seq):
    for command in seq:
        subprocess.run(command, shell=True, check=True)


def version(ver, delim="."):
    return delim.join(str(v) for v in ver)


def install_boost():
    boost_ver = version(BOOST_VERSION)
    boost_ver_uscore = version(BOOST_VERSION, delim="_")
    install_seq = (
        (
            'curl -L https://boostorg.jfrog.io/artifactory/main/release/'
            + f'{boost_ver}/source/boost_{boost_ver_uscore}.tar.gz'
            + ' -o boost.tar.gz'
        ),
        'tar -xzf boost.tar.gz',
        f'mv boost_{boost_ver_uscore} /boost'
    )
    run_sequence(install_seq)


def install_gsl():
    gsl_ver = version(GSL_VERSION)
    install_seq = (
        f'curl -L https://mirror.ibcp.fr/pub/gnu/gsl/gsl-{gsl_ver}.tar.gz -o gsl.tar.gz',
        'tar -xzf gsl.tar.gz',
        'mkdir /gsl',
        f'cd gsl-{gsl_ver} && ./configure --prefix=/gsl && make && make install',
    )
    run_sequence(install_seq)

main()
