﻿============
Installation
============

Graphbrain is compatible with 64-bit CPython >=3.6, <3.9 and runs on macOS, Linux and Windows. 

We currently have binary releases for macOS only. Given a working build environment, installation on Linux should be equally simple. Installation on Windows is at the moment less straightforward, because of our dependency on LevelDB, which in turn requires a bit of effort to install in this OS. `For such cases or to build from the sources, check the prerequisites for your OS <#prerequisites>`_.

Make sure you are using Python 3, with version >=3.6, <3.9.

Install with pip (recommended)
==============================

::

   $ pip install graphbrain


It is advisable to work with virtual environments. This avoids conflicts with the system-wide installed packages and creates a nice self-contained environment for you to work on. It is particularly important with graphbrain because we maintain dependencies to specific versions of downstream machine learning tools, as to keep results consistent.

To create a virtual environment in the current directory you can do this::

   $ virtualenv -p <path to python3> venv

Common locations for python3:

* /usr/local/bin/python3
* /usr/bin/python3

If you are on macOS, do this instead (for the reason `explained here <http://matplotlib.org/faq/osx_framework.html#osxframework-faq>`_)::

   $ python3 -m venv venv

Then to switch to the virtual environment and install graphbrain::

   $ source venv/bin/activate
   $ pip install graphbrain

It is still necessary to download a spaCy language model::

   $ python -m spacy download en_core_web_lg


Install from the code repository (github)
=========================================

Another way to install graphbrain is to build it from the GitHub repository source. You should use this method if you wish to make changes to the code base.

Start by cloning the source code to your current local directory.
::

   $ git clone https://github.com/graphbrain/graphbrain.git
   $ cd graphbrain

It is advisable to work with virtual environments, for reasons that are explained in the previous section. Please refer to it for details.

Install Cython::

   $ pip install cython

Now we can build and install graphbrain::

   $ pip install .

It is then necessary to download a spaCy language model::

   $ python -m spacy download en_core_web_lg


Building Graphbrain with parser-level coreference resolution support
--------------------------------------------------------------------

If you want to build graphbrain with parser-level coreference resolution support through neuralcoref, you should do instead::

   $ NEURALCOREF=true pip install .

It is still necessary to download a spaCy language model::

   $ python -m spacy download en_core_web_lg

Currently, parser-level coreference resolution relies on neuralcoref, which requires Python >=3.6, <3.9, and spaCy >=2.1.0, <3.0.0. These restrictions are the reason why we kept it out of the default distribution.

For developers
--------------

If you want to help develop graphbrain, you should also install the development dependencies::

   $ pip install '.[dev]'

Run tests
---------

From the project's root directory::

  $ pytest graphbrain

Notice that this requires the `pytest` package to be installed. The `pytest` package is included in the above mentioned development dependencies.

Prerequisites
=============

Naturally, you can ignore the prerequisites that are already installed in your machine.

Linux
-----

Linux distributions are diverse in terms of package managers. Please use the appropriate package manager for your
distribution to install the prerequisites.

* gcc
* Python 3
* pip (Python package manager)
* virtualenv (Virtual Python Environment builder)

macOS
-----

* XCode and the "Command Line Tools"::

   $ xcode-select --install

* The `Homebrew package manager <http://brew.sh/>`.

* Python 3

If python 3 is not already included with your current version os macOS::

   $ brew install python3

* pip (Python package manager)::

   $ sudo easy_install pip

* virtualenv (Virtual Python Environment builder)::

   $ sudo -H pip install virtualenv


* LevelDB (database engine)

LevelDB can also be installed with brew, but currently the latest version is not compatible with the Python wrapper (plyvel). The solution is to install LevelDB version 1.22. With brew, this can be achieved in the following way::

   $ brew tap bagonyi/homebrew-formulae git@github.com:bagonyi/homebrew-formulae.git
   $ brew extract --version=1.22 leveldb bagonyi/formulae
   $ brew install leveldb@1.22

(from https://github.com/bagonyi/homebrew-formulae)

The first command above might cause an error, but it appears it can be ignored. If a preexisting installation of LevelDB exists, it should be removed first::

   $ brew uninstall leveldb

Another option is to perform your own custom build of LevelDB 1.23, with the following line removed from its ``CMakeLists.txt``::

   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")

For more details: https://github.com/wbolster/plyvel/issues/114.

Windows
-------

*plyvel* is required for installing *graphbrain* on Windows. Unfortunately, this currently requires more effort than in the other platforms. To install *plyvel*, *boost.lib* and *leveldb.lib* must be compiled first. 

* **boost.lib (x64)**

**step 1** download and unzip the *Boost* library:  https://www.boost.org/

**step 2** make sure *cl* is the environment variable

**step 3** open *x64 Native Tools Command Prompt* for *VS2017*. Get into the directory of the unzipped *Boost*

**step 4** run command::

$ bootstrap.bat 

*b2.exe* and *bjam.exe* will be added after this step.
    
**step 5** open and modify *project-config.jam* in the current directory::
   

   $ import option ;
   $ using msvc : 14.1 : “E: \VS2017\VC\Tools\MSVC\14.1-.250117\bin\HostX64\x64\cl.exe” ;
   $ option.set keep-going : false ;


Please note that you should: i) use your own VS version number (e.g. 14.1) ii) use your own directory of _cl.exe_.

**step 6** *(note: this step may take 1 - 3 hours)* create a folder named build in the current directory, then run command:: 

   $ b2.exe stage --toolset=msvc-14.1 address-model=64 --stagedir="E:\mylib\boost\bin1.64.0\VC14.
   $ 1" threading=multi --build-type=complete --build-dir="E:\mylib\boost\boost_1_64_0\build"

Please note that you should: i) use your own directory names ii) be careful about the VS version number


* **leveldb.lib**

**step 1** download the source code of *LevelDB* for windows: https://github.com/vaskomitanov/leveldb  

**step 2** open *Visual Studio* (2017). Create a project: 

      •	file – new – project from existing code
      •	choose the type of project: *Visual C++*
      •	project file location: the directory of *LevelDB*
      •	project name: *LevelDB*
      •	project type: *LIB*
      •	preprocessor definition: *LEVELDB_PLATFORM_WINDOWS;OS_WIN; WIN32*
      •	include search path: *E:\LIB\leveldb-windows;E:\LIB\leveldb-windows\include* (the directory of *LevelDB* and its *include*)
      •	click *finish*

**step 3** set *LevelDB.lib*:

      •	project – properties – configuration properties – configuration type: *LIB*
      •	configuration properties – C/C++ - General – preprocessor – preprocessor definition: *LEVELDB_PLATFORM_WINDOWS;OS_WIN; WIN32*
      •	linker – general – additional library directory: *E:\LIB\boost64\stage\lib* (use your own path)

**step 4** open *solution explorer*, exclude the following files *(tip: you can search and right click on the target files)*:
      
      •	files ends with *_test.cc* and *_bench.cc*
      •	*port/port_android.cc*
      •	*port/port_posix.cc*
      •	*util/env_posix.cc*

**step 5** modify code:

in *db\c.cc*::
   
   $ delete #include < unistd.h>
   
in *port\port.h* - add the lines below before first ``#endif``::
      
   $ elif defined(LEVELDB_PLATFORM_WINDOWS)
   $ include "port/port_win.h"
   
**step 6** note: remember to compile as *release x64*


* **plyvel**

modify *setup.py*::
     
    Extension(
		    ...
		    libraries=['leveldb vaskomitanov-r x64',
				       'libboost_chrono-vc141-mt-x64-1_69',
				       'libboost_date_time-vc141-mt-x64-1_69',
				       'libboost_filesystem-vc141-mt-x64-1_69',
				       'libboost_system-vc141-mt-x64-1_69',
				       'libboost_thread-vc141-mt-x64-1_69'],
		    ...
        )
       
* **Cmake**

you may also need to install Cmake, please check the official guidance here: https://cgold.readthedocs.io/en/latest/first-step/installation.html#windows


Troubleshooting
===============

Plyvel ImportError on Anaconda (seen on macOS)
----------------------------------------------

We have found cases where the plyvel library that is installed as a dependency by Graphbrain does not work in Anaconda environments. This was observed on macOS Big Sur, on MacBook Pro laptops with the M1 chip. It is unknown if it might apply in other cases.

You might get error messages such as this one::

   ImportError: dlopen(/opt/anaconda3/lib/python3.8/site-packages/plyvel/plyvel.cpython-38-darwin.so, 2): Symbol not found: _ZTIN7leveldb10ComparatorE
   Referenced from: /opt/anaconda3/lib/python3.8/site-packages/plyvel/_plyvel.cpython-38-darwin.so
   Expected in: /usr/local/opt/leveldb/lib/libleveldb.1.dylib
   in /opt/anaconda3/lib/python3.8/site-packages/plyvel/_plyvel.cpython-38-darwin.so

The solution is to replace plyvel with one from the Anaconda repositories::

   $ pip uninstall plyvel
   $ conda install -c conda-forge plyvel