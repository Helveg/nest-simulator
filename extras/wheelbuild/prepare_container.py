import subprocess
import os

# This file exists as a Python script because running a Linux docker on Windows CI
# runners messes with the keyboard mapping of bash commands which affects symbols like
# -?/\ and makes writing commands impossible. Somehow, if we use .py files instead of
# .sh files, we can shell out from here with correct keyboard mapping.

BOOST_VERSION = [1, 79, 0]
GSL_VERSION = [2, 7, 1]


def main():
    # Containers run multiple builds, so check if a previous build has installed the
    # dependency already
    if not os.path.exists("/boost"):
        install_boost()
    if not os.path.exists("/gsl"):
        install_gsl()


def run_sequence(seq):
    """Run a sequence of shell commands"""
    for command in seq:
        subprocess.run(command, shell=True, check=True)


def version(ver, delim="."):
    """Format list of semver parts into a string"""
    return delim.join(str(v) for v in ver)


def install_boost():
    """Download, unpack, and move Boost to `/boost`"""
    boost_ver = version(BOOST_VERSION)
    boost_ver_uscore = version(BOOST_VERSION, delim="_")
    install_seq = (
        (
            "curl -L https://boostorg.jfrog.io/artifactory/main/release/"
            + f"{boost_ver}/source/boost_{boost_ver_uscore}.tar.gz"
            + " -o boost.tar.gz"
        ),
        "tar -xzf boost.tar.gz",
        f"mv boost_{boost_ver_uscore} /boost",
    )
    run_sequence(install_seq)


def install_gsl():
    """Download, unpack, configure and make install GSL to `/gsl`"""
    gsl_ver = version(GSL_VERSION)
    install_seq = (
        f"curl -L https://mirror.ibcp.fr/pub/gnu/gsl/gsl-{gsl_ver}.tar.gz -o gsl.tar.gz",
        "tar -xzf gsl.tar.gz",
        "mkdir /gsl",
        f"cd gsl-{gsl_ver} && ./configure --prefix=/gsl && make && make install",
    )
    run_sequence(install_seq)


main()
