#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

import os, sys, StringIO, glob, shutil
import unittest
from pycompiler.globals import *
from pycompiler.parser import *
from pycompiler.util import *
from pycompiler.translator import *
from pycompiler.scanner import *
import pycompiler.scanner

class TestPlhScanner(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.srcfile = os.path.join(tempdir, 'scanner_srcfile')
        self.tokfile = os.path.join(tempdir, 'scanner_tokfile')
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
#    
#    def test_run_cpp_scanner(self):
#        srcfile = os.path.join(srcfiledir, 'selection_sort.plh')
#        Scanner.run_cpp_scanner(srcfile=srcfile, 
#                                tokfile=self.tokfile)
#        ## this below is just to make sure that line separators don't mess with us
#        txtfile = os.path.join(resourcedir, 'SelectionSortTokfile.txt')
#        expected_lines = open(txtfile).read().splitlines()
#        actual_lines = open(self.tokfile).read().splitlines()
#        self.assertEqual(expected_lines, actual_lines)
#    
#    def test_compare_w_cpp_scanner(self):
#        ## since the compare_w_cpp_scanner calls scan() in the method body
#        ## to test it in isolation from the scan() method, we'll override
#        ## the scan method here--aka monkeypatching according to Younker
#        srcfile = os.path.join(srcfiledir, 'selection_sort.plh')
#        fake_tokfile = os.path.join(tempdir, 'sel_sort_tokfile')
#        Scanner.run_cpp_scanner(srcfile, fake_tokfile)
#        
#        orig_scan_method = Scanner.scan
#        
#        def new_scan(scanner):
#            scanner.srcfile = srcfile
#            scanner.tokfile = fake_tokfile
#        Scanner.scan = new_scan
#
#        scanner = Scanner(srcfile=srcfile,
#                          tokfile=self.tokfile)
#
#        is_equiv = scanner.tokfile_equiv_w_cpp_scanner()
#        self.assertEqual(is_equiv, True)
#        
#        Scanner.scan = orig_scan_method
        
     
    def test_on_selection_sort(self):
        srcfile = os.path.join(srcfiledir, 'selection_sort.plh')
        scanner = Scanner(srcfile=srcfile,
                          tokfile=self.tokfile)
        scanner.scan()
        txtfile = os.path.join(resourcedir, 'SelectionSortTokfile.txt')
        expected_lines = [line.split() for line in open(txtfile).read().splitlines()]
        actual_lines = [line.split() for line in open(self.tokfile).read().splitlines()]
        j=0
#        for i in range(len(expected_lines)):
#            if expected_lines[i].strip() != actual_lines[i].strip():
#                print 'expected_lines[%d]:\n%s' % (i, expected_lines[i])
#                print 'actual_lines[%d]:\n%s' % (i, actual_lines[i])
#                j+=1
#                if j>10: break
            
        self.assertEqual(expected_lines, actual_lines)
        
    def test_scan_zero_int(self):  
        src = 'i = 0;'
        expected = \
"""$id
i
=

$int
0
;

"""
        open(self.srcfile, 'w').write(src)
        scanner = Scanner(srcfile=self.srcfile, tokfile=self.tokfile)
        scanner.scan()
        self.assertEqual(open(self.tokfile).read().replace('\r\n', '\n'), expected)
        
#        scanner = Scanner(srcfile=self.srcfile, tokfile=self.tokfile)
#        self.assertEqual(scanner.tokfile_equiv_w_cpp_scanner(), True)
        
        
if __name__ == '__main__':
    unittest.main()