#!/bin/sh
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/maier/gr-lte/python
export PATH=/home/maier/gr-lte/build-cb/python:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DYLD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DYLD_LIBRARY_PATH
export PYTHONPATH=/home/maier/gr-lte/build-cb/swig:$PYTHONPATH
/usr/bin/python2 /home/maier/gr-lte/python/qa_pcfich_demux_vcvc.py 
