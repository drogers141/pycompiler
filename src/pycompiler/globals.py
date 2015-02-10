#!/usr/bin/env python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##
"""paths defined to help with importing, tests, and __main__ constructs
the structure is 
pycompiler_home/
          --------src/    contains the source packages
          --------tokfiledir/    contains tokenfiles
          --------grammardir/    contains grammars and translation schemes
          --------temp/        temp for tests, etc.
"""
import os

__all__ = ['pycompiler_home', 'srcfiledir', 'tokfiledir', 'grammardir', 
           'resourcedir', 'tempdir', ]

pycompiler_home = os.path.normpath(__file__ + '/../../..')

srcfiledir = os.path.join(pycompiler_home, 'sourcefiles')
tokfiledir = os.path.join(pycompiler_home, 'tokenfiles')
grammardir = os.path.join(pycompiler_home, 'grammars')
tempdir = os.path.join(pycompiler_home, 'temp')
resourcedir = os.path.join(pycompiler_home, 'resources')

if not os.path.exists(tempdir): os.mkdir(tempdir)

## use for paths in test files
#testdir = os.path.join(pycompiler_home, 'test')

