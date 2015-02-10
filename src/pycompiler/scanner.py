#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

"""A scanner for the pycompiler project.
"""
import sys, os, string, shutil
parent_dir = os.path.abspath( os.path.join(__file__, '../..') )
if not parent_dir in sys.path:
    sys.path.append(parent_dir)


__all__ = ['Scanner', 'alphanum', 'special']

from globals import *
from util import *

whitespace = string.whitespace
letters = string.ascii_letters
digits = string.digits
alphanum = letters + digits
special = sorted( [ch for ch in set(string.printable) - 
                                set(alphanum).union( set(string.whitespace) )] )

class Scanner:
    def __init__(self, srcfile=None,
                    tokfile='tokfile',
                    **kwargs):
        """@param srcfile: will only read srcfile
        @param tokfile: scan will create or overwrite this file
        """
        self.srcfile = srcfile
        self.tokfile_path = tokfile
        self.tokfile = None
        self.reserved = ['declare', 'put', 'get', 'stop', 'goto', 'if', 'then', 'end', 'do',]
        
        
    def scan(self):
        """Scans the sourcefile and produces the tokenfile."""
        self.tokfile = open(self.tokfile_path, 'w')
        word = ''
        for line in open(self.srcfile):
            for ch in line:
                if ch in alphanum: 
                    word += ch
                else:
                    if word:
                        try:
                            self.print_tok('$int', int(word))
                        except ValueError:
                            if word in self.reserved: 
                                self.print_tok('$' + word)
                            else:
                                self.print_tok('$id', word)
                    if ch in special:
                        self.print_tok(ch)
                    word = ''
        self.tokfile.close()
        
    def print_tok(self, name, value=None):
        """Print name and value or '' with lineseps to tokenfile."""
        val = '' if value == None else value
        tokstring = '%s%s%s' % (name, os.linesep, val)        
        print >> self.tokfile, tokstring
        
    def tokfile_equiv_w_cpp_scanner(self):
        """Runs scan and runs the platform dependent executable for the cpp scanner from cs4110
        on the same sourcefile.
        @return: true if tokenfiles produced are equivalent
        """
        self.scan()
        tokfile = os.path.join(tempdir, 'tokfile')
        Scanner.run_cpp_scanner(self.srcfile, tokfile)
        ours = open(self.tokfile_path).read()
        theirs = open(tokfile).read()
        return ours == theirs
    
    @staticmethod
    def run_cpp_scanner(srcfile, tokfile):
        """Runs the platform dependent executable for the cpp scanner from cs4110 on srcfile
        and copies resulting token file to tokfile.
        """
        path = resourcedir
        shutil.copyfile(srcfile, os.path.join(path, 'srcfile'))
        #open(os.path.join(path, 'srcfile'), 'w').write(open(srcfile).read())
        
        if sys.platform[:3] == 'win':
            print 'need win exe'
        elif sys.platform[:5] == 'linux':
            exec_name = 'cpp_scanner_ubuntu'
            cmd = 'cd %s; ./%s; cd -' % (path, exec_name)
            os.popen(cmd)
        
        shutil.copyfile(os.path.join(path, 'tokfile'), tokfile)    
        #open(tokfile, 'w').write( open(os.path.join(path, 'tokfile')).read() )
          

if __name__ == '__main__':
    scanner = Scanner(srcfile='srcfile', 
                      tokfile='tokfile')
    scanner.scan()
    
    