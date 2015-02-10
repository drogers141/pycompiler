#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

import sys, os, StringIO
parent_dir = os.path.abspath( os.path.join(__file__, '../..') )
if not parent_dir in sys.path:
    sys.path.append(parent_dir)

__all__ =['PlhInterpreter']

from globals import *
from util import *
from translator import *
from vm import *
from scanner import *


class  PlhInterpreter:
    def __init__(self, vm=None, translator=None, scanner=None, outputdir=None):
        if not outputdir:
            self.outputdir = os.path.join(os.getcwd(), 'interpreter_files')
        else:
            self.outputdir = outputdir
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)             
        self.translator = translator
        self.vm = vm
        self.trans = translator
        self.scanner = scanner
        self.tokfile = os.path.join(self.outputdir, 'tokfile')
        self.codefile = os.path.join(self.outputdir, 'codefile')
        self.datafile = os.path.join(self.outputdir, 'datafile')
        self.tr_outfile = os.path.join(self.outputdir, 'tr_outfile')
        self.vm_outfile = os.path.join(self.outputdir, 'vm_outfile')
        
    def run_file(self, srcfile, interactive=True):
        """Run srcfile through the scanner, parser, and vm
        @param srcfile: a PL/H source code file
        @param interactive: if False, srcfile is run and any stdout is returned
        but stdin is not available via keyboard
        @return: string containing stdout from running program if interactive False
        """
        self.scanner = Scanner(srcfile=srcfile, tokfile=self.tokfile)
        self.scanner.scan()
        self.trans = PlhTranslator(tokensource=self.tokfile,
                                   codefile=self.codefile, 
                                   datafile=self.datafile,
                                   outfile=self.tr_outfile)
        self.trans.parse()
        self.vm = VM(outfile=self.vm_outfile, 
                     codefile=self.codefile, 
                     datafile=self.datafile)
        if interactive:
            self.vm.execute()
        else:
            sys.stdout.flush()
            old_stdout = sys.stdout
            retstring = ''
            try:
                sys.stdout = StringIO.StringIO()
                self.vm.execute()
                sys.stdout.flush()
                retstring = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
                return retstring
            
if __name__ == '__main__':
    outputdir = os.path.join(tempdir, 'interp_main_files')
    plh = PlhInterpreter(outputdir=outputdir)
    
    srcfile = os.path.join(outputdir, 'interp_main.plh')
    src = \
"""declare x(5);
numtosort=5;
i=1;
:in:
     get x(i);
     i=i+1;
     if i<=numtosort then goto in;
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
    open(srcfile, 'w').write(src)    
    plh.run_file(srcfile)
    print plh.trans.symbol_table_str()
    
