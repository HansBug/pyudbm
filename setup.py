import logging
import os
import platform
import re
import shutil
import subprocess
import sys
from codecs import open

from setuptools import Extension
from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext
from tools.windows_mingw import find_mingw_bin

_package_name = "pyudbm"

here = os.path.abspath(os.path.dirname(__file__))
meta = {}
with open(os.path.join(here, _package_name, 'config', 'meta.py'), 'r', 'utf-8') as f:
    exec(f.read(), meta)


def _load_req(file: str):
    with open(file, 'r', 'utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]


requirements = _load_req('requirements.txt')

_REQ_PATTERN = re.compile('^requirements-([a-zA-Z0-9_]+)\\.txt$')
group_requirements = {
    item.group(1): _load_req(item.group(0))
    for item in [_REQ_PATTERN.fullmatch(reqpath) for reqpath in os.listdir()] if item
}

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()


def _parse_version_tuple(version: str):
    return tuple(int(part) for part in version.split('.'))


def _find_gnu_compiler(cxx: bool = False):
    executable = 'g++.exe' if cxx else 'gcc.exe'
    if platform.system() == 'Windows':
        try:
            bindir = find_mingw_bin()
        except RuntimeError:
            bindir = None
        if bindir:
            compiler = os.path.join(bindir, executable)
            if os.path.exists(compiler):
                return compiler

    candidates = (
        ['g++-9', 'g++-10', 'g++-11', 'g++-12', 'g++-13', 'g++-14', 'g++']
        if cxx else
        ['gcc-9', 'gcc-10', 'gcc-11', 'gcc-12', 'gcc-13', 'gcc-14', 'gcc']
    )
    for candidate in candidates:
        compiler = shutil.which(candidate)
        if not compiler:
            continue
        try:
            out = subprocess.check_output([compiler, '-v'], stderr=subprocess.STDOUT).decode()
        except (OSError, subprocess.CalledProcessError):
            continue
        if 'gcc version' in out.lower():
            return compiler

    return candidates[0]


def _find_macos_compiler(cxx: bool = False):
    tool = 'clang++' if cxx else 'clang'

    xcrun = shutil.which('xcrun')
    if xcrun:
        try:
            return subprocess.check_output([xcrun, '--find', tool]).decode().strip()
        except (OSError, subprocess.CalledProcessError):
            pass

    compiler = shutil.which(tool)
    if compiler:
        return compiler

    return tool


def _copy_windows_runtime_dlls(extdir: str, compiler_path: str):
    if platform.system() != 'Windows':
        return

    compiler_dir = os.path.dirname(compiler_path)
    runtime_dlls = [
        'libwinpthread-1.dll',
        'libgcc_s_seh-1.dll',
        'libstdc++-6.dll',
        'libssp-0.dll',
    ]
    for dll_name in runtime_dlls:
        src = os.path.join(compiler_dir, dll_name)
        dst = os.path.join(extdir, dll_name)
        if not os.path.exists(src):
            continue
        if os.path.abspath(src) == os.path.abspath(dst):
            continue
        shutil.copy2(src, dst)


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = _parse_version_tuple(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < (3, 1, 0):
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        logging.basicConfig(level=logging.INFO)

        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cfg = os.environ.get('CTEST_CFG') or ('Debug' if self.debug else 'Release')
        generator = os.environ.get('CMAKE_GENERATOR', 'Ninja')
        if platform.system() == 'Darwin':
            cc = os.environ.get('CC') or _find_macos_compiler(False)
            cxx = os.environ.get('CXX') or _find_macos_compiler(True)
        else:
            cc = os.environ.get('CC') or _find_gnu_compiler(False)
            cxx = os.environ.get('CXX') or _find_gnu_compiler(True)
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DCMAKE_RUNTIME_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable,
                      '-G', generator,
                      '-DCMAKE_BUILD_TYPE=' + cfg,
                      '-DCMAKE_C_COMPILER=' + cc,
                      '-DCMAKE_CXX_COMPILER=' + cxx]
        if platform.system() == 'Windows':
            cmake_args += [
                '-DCMAKE_C_FLAGS=-static-libgcc',
                '-DCMAKE_CXX_FLAGS=-static-libgcc -static-libstdc++',
                '-DCMAKE_EXE_LINKER_FLAGS=-static-libgcc -static-libstdc++',
                '-DCMAKE_SHARED_LINKER_FLAGS=-static-libgcc -static-libstdc++',
            ]

        build_args = ['--config', cfg, '--', '-j2']

        env = os.environ.copy()
        env['CC'] = cc
        env['CXX'] = cxx
        compiler_dir = os.path.dirname(cc)
        if compiler_dir:
            env['PATH'] = compiler_dir + os.pathsep + env.get('PATH', '')
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp, exist_ok=True)

        logging.info(f'Using cmake {shutil.which("cmake")!r} ...')
        b1_cmds = [shutil.which('cmake'), ext.sourcedir] + cmake_args
        logging.info(f'Build with {b1_cmds!r} ...')
        subprocess.check_call(b1_cmds, cwd=self.build_temp, env=env)

        b2_cmds = [shutil.which('cmake'), '--build', '.'] + build_args
        logging.info(f'Build with {b2_cmds!r} ...')
        subprocess.check_call(b2_cmds, cwd=self.build_temp, env=env)
        _copy_windows_runtime_dlls(extdir, cc)


setup(
    # information
    name=meta['__TITLE__'],
    version=meta['__VERSION__'],
    packages=find_packages(
        include=(_package_name, "%s.*" % _package_name)
    ),
    description='Compatibility-minded Python wrapper for the UPPAAL UDBM library.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author=meta['__AUTHOR__'],
    author_email=meta['__AUTHOR_EMAIL__'],
    license='GNU General Public License v3 (GPLv3)',
    keywords='uppaal udbm dbm timed automata zones federation pybind11',
    url='https://github.com/HansBug/pyudbm',
    project_urls={
        'Homepage': 'https://github.com/HansBug/pyudbm',
        'Documentation': 'https://pyudbm.readthedocs.io/en/latest/',
        'Source': 'https://github.com/HansBug/pyudbm',
        'Tracker': 'https://github.com/HansBug/pyudbm/issues',
        'Issues': 'https://github.com/HansBug/pyudbm/issues',
        'CI': 'https://github.com/HansBug/pyudbm/actions',
        'Download': 'https://pypi.org/project/pyudbm/#files',
    },

    # environment
    python_requires=">=3.7",
    ext_modules=[
        CMakeExtension('pyudbm.binding._binding'),
    ],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    package_data={
        'pyudbm.binding': ['*.dll'],
    },
    install_requires=requirements,
    extras_require=group_requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
