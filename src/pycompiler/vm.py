#!/usr/bin/env python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

"""Implementation of the virtual machine emulator"""

__all__ = ['VM', 'VmException']

import os, sys
from util import *
from globals import *

class VmException(Exception): pass
        
class VM:
    """An instance of the virtual machine simulator."""
    def __init__(self, outfile=None, 
                 codefile='codefile', 
                 datafile=None):
        """@param outfile: relative or absolute path of file to collect 
        vm snapshots during execution, if not given, no file will be created
        @param codefile: the code to be read in
        @param datafile: if provided, the contents of memory, ie the data array,
        will be written to it
        """
        self.stack = Stack()
        # running is True when the vm is executing
        self.running = False
        # pc is the program counter
        self.pc = 0
        # the program code is stored in a list that starts with index 1,
        # so index 0 is None as a place holder
        self.code = [None]
        # the same goes for memory, data storage in a list with index 1
        # note, load and store instructions must take care of initializing data, if required
        self.data = [None]
        # the instruction set for the vm is a dictionary of ops matched to strings containing 
        # executable statements
        self.instr_set = self.get_instr_set()
        # contains a string indicating input or output on current instruction
        # that vm_pic will display and remove, or None if no io on curr instr
        self.io_on_previous_instr = None
        # possible values for above
        self.input_logstring =  "vm input --------> "
        self.output_logstring = "vm output -------> "
        
        # see read_files for info on the code and data files
        self.codefile = codefile
        self.datafile = datafile
        self.outfile = None
        try:
            if outfile: self.outfile = open(outfile, 'w')
        except Exception, msg:
            print >> sys.stderr, msg
        
        # keep track of which instructions have immediate ops so we can add
        # the immediate ops in vm_pic()
        # note that this couples the vm to the instruction set, which is otherwise
        # not too much of a problem, so fix it if more flexibility is required
        self.immed_op_instructions = ['lit', 'load', 'store',
                                      'brl', 'inc', 'dec'] 
        
    
    def read_files(self): 
        """Read in the code and data files and store them into the code
        and data lists.  Both files will only have their first whitespace delimited token
        for each line read in, so anything past that is a comment.  The token that is
        read in will be converted properly to an int, float, or string value, so both the
        code and data lists support these types.
            For this vm, a datafile only needs to be initialized if there is persistent 
        data to be read in.  The data array (list) will be written out to a datafile,
        however, if one is specified.
        """
        for line in open(self.codefile):
            val = line.split()[0]
            val = convert_from_str(val)
            self.code.append(val)
            
        if self.datafile and os.path.exists(self.datafile):
            for line in open(self.datafile):
                val = line.split()[0]
                self.data.append( convert_from_str(val) )         
            
    def execute(self):
        """Run the vm."""
        self.read_files()
        self.running = True
        if self.outfile: self.outfile.write(self.vm_pic())
        while self.running:
            self.exec_current_instr()            
        if self.datafile:
            out = open(self.datafile, 'w')
            for line in self.data: out.write(str(line) + os.linesep)
            out.close()
            
    def exec_current_instr(self):
        """Executes one cycle of execution.  Increments the program counter and executes
        the instruction pointed to by it.
        @raise VmException: on unknown operator"""
        try:
            self.pc = self.pc + 1            
            op = self.code[self.pc]
            
            ### vm_pic related output stuff
            if self.outfile:
                outstring = ""
                if self.io_on_previous_instr:
                    outstring += self.io_on_previous_instr + 2 * os.linesep
                    self.io_on_previous_instr = None 
                outstring += self.vm_pic()
                self.outfile.write(outstring)
            
            exec self.instr_set[op]
        except KeyError, msg:
            msg = 'Unknown operator %s' % msg
            raise VmException(msg)
        except IndexError, msg:
            msg = str(msg) + '\nself.pc = %d, len(self.code) = %d' % (self.pc, len(self.code))
            raise VmException(msg)
        
    def immed_op(self):
        """Increments program counter and returns value of next code line."""
        self.pc = self.pc + 1
        return self.code[self.pc]
    
    def vm_pic(self):
        """Returns a string containing a 3 line picture of the vm's state followed by a blank line."""
        nl = os.linesep
        # width of first column
        col_width = 9
        s1 = "%-*s %s%s" % (col_width-1, "stack", self.stack.__str__(), nl) 
        s2 = "%-*s %s%s" % (col_width-1, "data",
                          '\t'.join( [str(item) for item in self.data[1:]] ), nl )   
        s3 = ""   
        instruct = self.code[self.pc]
        if instruct in self.instr_set.keys():
            if instruct in self.immed_op_instructions:
                instruct = "%s  %s" % (instruct, self.code[self.pc + 1])
            s3 = "%-*s at  %d%s" % (col_width-1, instruct, self.pc, nl)
        
        return "%s%s%s%s" % (s1, s2, s3, nl)
    
        
    def get_instr_set(self):
        """Returns the instruction set as a dictionary of instructions as keys matched to executable
        code."""

        instr_set = {
'quit':  """self.running = False""",
'lit':   """self.stack.push( self.immed_op() )""",

## storage instructions
'load':  """self.stack.push( self.data[ self.immed_op() ] )""",
'store': """address = self.immed_op()
while len(self.data) <= address: self.data.append(None)
self.data[address] = self.stack.pop()""",

'ldi':   """self.stack.push( self.data[self.stack.pop()] )""",

'sti':   """top = self.stack.pop()
next = self.stack.pop()
while len(self.data) <= next: self.data.append(None)
self.data[ next ] = top""",

## arithmetic instructions
'add':  """self.stack.push(self.stack.pop() + self.stack.pop())""",

'sub':  """top = self.stack.pop()
self.stack.push(self.stack.pop() - top)""",

'mult': """self.stack.push(self.stack.pop() * self.stack.pop())""",

# div raises ZeroDivisionError exception if necessary
'div':  """top = self.stack.pop()
if top == 0:  raise ZeroDivisionError
self.stack.push(self.stack.pop() / top)""",

'neg':  """self.stack.push( -self.stack.pop() )""",

## relational instructions
'eq':   """top = self.stack.pop()
self.stack.push(1 if self.stack.pop() == top else 0)""",

'lt':   """top = self.stack.pop()
self.stack.push(1 if self.stack.pop() < top else 0)""",

'gt':   """top = self.stack.pop()
self.stack.push(1 if self.stack.pop() > top else 0)""",

'ne':   """top = self.stack.pop()
self.stack.push(1 if self.stack.pop() != top else 0)""",

'le':   """top = self.stack.pop()
self.stack.push(1 if self.stack.pop() <= top else 0)""",

'ge':   """top = self.stack.pop()
self.stack.push(1 if self.stack.pop() >= top else 0)""",

## branch instructions
'br':   """self.pc = self.stack.pop() - 1""",
'brl':  """self.pc = self.immed_op() - 1""",
'brf':   """top = self.stack.pop()
if self.stack.pop() == 0:  self.pc = top - 1""",

## io instructions
# in converts input to int if possible, otherwise it pushes a string
'in':   """input = raw_input('> ')
self.io_on_previous_instr = "%s%s" % (self.input_logstring, input)
self.stack.push( convert_from_str(input) )""",

# out outputs top of stack + newline to stdout
'out':  """output = self.stack.pop()
print output
self.io_on_previous_instr = "%s%s" % (self.output_logstring, output)
""",
    
## logical instructions
'and':  """top = self.stack.pop()
self.stack.push( self.stack.pop() and top )""",

'or':   """top = self.stack.pop()
self.stack.push( self.stack.pop() or top )""",

'not':  """self.stack.push( not (self.stack.pop()) )""",

## increment and decrement
'inc':  """self.stack.push( self.stack.pop() + self.immed_op() )""",
'dec':  """self.stack.push( self.stack.pop() - self.immed_op() )""",

        }
        ### Note--the code below works, but unless we are running a *long*
        ##    program, or store the compiled code, it actually takes
        ##    longer to execute because of the compile time, I believe
        ##    So I'm commenting out
        ###
        # compile the code for efficiency, note that '\r\n' newlines
        # on Windows must be converted to '\n' (silly Windows :) )
#        for statements in instr_set.values():
#            statements.replace('\r\n', '\n')
#            compile(statements, '<string>', 'exec')
        
        return instr_set
     
        
if __name__ == '__main__':
    vM = VM('py_simulout.txt')
    vM.execute()
    
    