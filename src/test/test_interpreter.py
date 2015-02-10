#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

import os, sys, StringIO, glob

import unittest
from pycompiler.globals import *
from pycompiler.parser import *
from pycompiler.util import *
from pycompiler.translator import *
from pycompiler.interpreter import *

#interpreterdir = os.path.join(tempdir, 'interpreter')

class TestDefaultPlhInterpreter(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.interpdir = os.path.join(tempdir, 'test_interpreter')
        if not os.path.exists(self.interpdir):
            os.mkdir(self.interpdir)        
        self.hal = PlhInterpreter(outputdir=self.interpdir)
        self.srcfile = os.path.join(self.interpdir, 'srcfile')        
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hal = None
        
    def test_run_source_file(self):
        src = \
"""declare x(5);
i = 0; max = 5;
:assignloop:
    x(i) = i;
    i = i + 1;
    if i <= max then goto assignloop;
if x(3) = 3 then put x(3);
stop;
"""
        open(self.srcfile, 'w').write(src)
        #print 'self.srcfile:\n%s' % open(self.srcfile).read()
        old_stdout = sys.stdout
        try:
            sys.stdout.flush()
            sys.stdout = StringIO.StringIO()
            self.hal.run_file(srcfile=self.srcfile)
            sys.stdout.flush()
            #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
            self.assertNotEqual( sys.stdout.getvalue().find( '3' ), -1 )            
        finally:
            sys.stdout = old_stdout
            sys.stdout.flush()
            
   
    def test_run_w_interactive_false(self):
        src = \
"""declare x(5);
i = 0; max = 5;
:assignloop:
    x(i) = i * i;
    i = i + 1;
    if i <= max then goto assignloop;
i = 0;
:out:
    put x(i);
    i = i + 1;
    if i <= max then goto out;
stop;
"""
        open(self.srcfile, 'w').write(src)
        out = self.hal.run_file(srcfile=self.srcfile,
                          interactive=False
                          )   
        #print 'out: ', out
        expected = '0 1 4 9 16 25 '
        self.assertEqual(find_without_whitespace(out, expected), True)
        
    def test_selection_sort_no_input(self):
        src = \
"""declare x(5);
numtosort=5;
x(1) = 9; 
x(2) = 7; 
x(3) = 8; 
x(4) = 5; 
x(5) = 1; 
i=1;
:nexti:
     j=i+1;
     :nextj:
          if x(j)<x(i) then
               do;
               temp=x(i);
               x(i)=x(j);
               x(j)=temp;
               end;
          j=j+1;
          if j<=numtosort then goto nextj;
     put x(i);
     i=i+1;
     if i<=numtosort-1 then goto nexti;
put x(numtosort);
stop;
"""  
        open(self.srcfile, 'w').write(src)
        out = self.hal.run_file(srcfile=self.srcfile,
                          interactive=False
                          )   
        expected = '1 5 7 8 9'
        self.assertEqual(find_without_whitespace(out, expected), True)
        #print self.hal.vm.data
        #print self.hal.trans.symbol_table_str()
        
        
        
        
    def test_run_w_get(self):
        src = \
"""declare x(5);
i = 0; max = 5;
:in:
    get x(i);
    i = i + 1;
    if i <= max then goto in;
stop;
"""
        open(self.srcfile, 'w').write(src)
        old_stdin = sys.stdin
        try:
            sys.stdin = StringIO.StringIO('1\n2\n3\n4\n5\n6\n')

            self.hal.run_file(srcfile=self.srcfile)
            expected = [1, 2, 3, 4, 5, 6]
            address = self.hal.trans.symbols['x']['address']
            size = self.hal.trans.symbols['x']['size']
            self.assertEqual( self.hal.vm.data[address:address+size], 
                              expected)
        finally:
            sys.stdin = old_stdin            
            #print 'hal.data:  %s' % self.hal.vm.data

    def test_run_w_get_and_put(self):
        src = \
"""declare x(5);
i = 0; max = 5;
:in:
    get x(i);
    i = i + 1;
    if i <= max then goto in;
i = max;
:out:
    put x(i);
    i = i - 1;
    if i >= 0 then goto out;
stop;
"""
        open(self.srcfile, 'w').write(src)
        old_stdin = sys.stdin
        try:
            sys.stdin = StringIO.StringIO('1\n2\n3\n4\n5\n6\n')

            out = self.hal.run_file(srcfile=self.srcfile,
                                    interactive=False)
            #print 'out == ', out
            expected = '6 5 4 3 2 1 '
            self.assertEqual( find_without_whitespace(out, expected), True)
        finally:
            sys.stdin = old_stdin
            
            #print 'hal.data:  %s' % self.hal.vm.data

        ## fulfills the cs4110 assignment: Project Interpreter
    def test_run_selection_sort_plh_w_input_from_cs4110_project(self):
        srcfile = os.path.join(srcfiledir, 'selection_sort.plh')
        old_stdin = sys.stdin
        try:
            sys.stdin = StringIO.StringIO('20\n19\n18\n17\n16\n')

            out = self.hal.run_file(srcfile=srcfile,
                                    interactive=False)
            #print 'out == ', out
            expected = '16 17 18 19 20'
            self.assertEqual( find_without_whitespace(out, expected), True)
        finally:
            sys.stdin = old_stdin

    
    
##### uncomment and use to play with stdin and stdout           
        
#    def test_grab_stdin(self):
#        old_stdin = sys.stdin
#        #old_stdout = sys.stdout
#        out = ''
#        try:
#            sys.stdin = StringIO.StringIO('1\n2\n3\n4\n5\n6\n')
#            #sys.stdout = StringIO.StringIO()
#            max = 5
#            for i in range(max+1):
#                out += '%s ' % raw_input() 
#                 
#            #out = sys.stdout.getvalue()
#            self.assertEqual(find_without_whitespace(out, '1 2 3 4 5 6'), True)
#        finally:
#            sys.stdin = old_stdin
            #sys.stdout = old_stdout
            
#    def test_grab_stdin_and_stdout(self):
#        old_stdin = sys.stdin
#        old_stdout = sys.stdout
#        out = ''
#        try:
#            sys.stdin = StringIO.StringIO('1\n2\n3\n4\n5\n6\n')
#            sys.stdout = StringIO.StringIO()
#            max = 5
#            for i in range(max+1):
#                #print '%s ' % raw_input() 
#                 
#            out = sys.stdout.getvalue()
#            self.assertEqual(find_without_whitespace(out, '1 2 3 4 5 6'), True)
#        finally:
#            sys.stdin = old_stdin
#            sys.stdout = old_stdout
#            
#            print out

###########################################################

        
if __name__ == '__main__':
    unittest.main()