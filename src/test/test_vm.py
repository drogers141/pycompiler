##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

import unittest
from pycompiler.globals import *
import pycompiler.vm
from pycompiler.vm import *
from pycompiler.util import *
import os.path, sys, StringIO, re

## Note on capturing stdout:  just use '\n\ rather than os.linesep for 
## your expected line separator, apparently python is translating it in stdout

### utility functions used by more than one test case class
def create_file(fname, lines):
    """Creates file filename from list 'lines' adding line seps."""
    f = open(fname, 'w')
    buf = os.linesep.join(lines)
    f.write(buf)

## Refactoring note--this isn't necessary anymore as I'm no longer following the 
## the c++ version of the vm, so no initialized data file is required
def create_default_data_file(fname='datafile'):
    """Creates datafile initialized with 5 lines of zeros."""
    create_file(fname, ['0','0','0','0','0'])

def create_codefile(fname, string):
    open(fname, 'w').write('\n'.join(string.split()))
    
class TestVm(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.codefile = 'codefile'
        self.datafile = 'datafile'
        self.vM = pycompiler.vm.VM(codefile=self.codefile, 
                                   datafile=self.datafile)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    # note can make this into a generic test
    def run_code_through_vm(self, code, expected_out):
        """Runs a test by using the string code as the contents of the code
        file and expected_out as the string value of expected stdout."""
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            create_default_data_file()
            create_file('codefile', [])
            f = open('codefile', 'w')
            f.write(code)
            f.close()
            #self.vM = VM(datafile='datafile')
            self.vM.execute()
            self.assertEqual(expected_out, sys.stdout.getvalue())
            
        finally:
            sys.stdout = old_stdout

   
    def test_add_two_ints_input_produces_correct_output(self):
        code = \
"""lit
30
lit
5
add
out
quit"""
        expected_out = \
"""35
"""
        self.run_code_through_vm(code, expected_out)            
            
    def test_branching_produces_correct_output(self):
        code = \
"""lit
0
lit  
8
brf     # should output 33 #
brl
11
lit
33
out
quit"""
        expected_out = \
"""33
"""
        self.run_code_through_vm(code, expected_out)            
                
    def test_read_in_code_and_data_files(self):
        # the code and data memory representations start with index 1,
        # so index 0 is None as a placeholder
        self.assertEqual(self.vM.code, [None])
        self.assertEqual(self.vM.data, [None])
        # create codefile with the easiest code
        create_file('codefile', ['quit'])
        create_file('datafile', ['0','0','0','0'])
        self.vM.datafile = 'datafile'
        self.vM.read_files()
        self.assertEqual(self.vM.code, [None, 'quit'])
        self.assertEquals(self.vM.data, [None,0,0,0,0])
    
    def test_read_files_with_type_conversion_and_comments(self):
        create_file('codefile', ['42  # comment',
                                  '3.14  // comment',
                                   'quit also a comment'])
        self.vM.datafile = 'datafile'
        create_file(self.vM.datafile, ['0','hi world'])                
        self.vM.read_files()        
        self.assertTrue( isinstance( self.vM.code[1], int) )
        self.assertTrue( isinstance( self.vM.code[2], float) )
        self.assertTrue( isinstance( self.vM.code[3], str) )
        self.assertTrue( isinstance( self.vM.data[1], int) )
        self.assertTrue( isinstance( self.vM.data[2], str) )
                
        
    # since I'm following the vm Prof. Daley implemented in C++, the assembly language
    # only accepts 1 word/token per line, so a command with an immediate operand
    # will always need to read the next line and advance the program counter
    def test_immediate_operand_helper_method(self):
        code = self.vM.code
        self.assertEqual(self.vM.pc, 0)
        self.vM.pc = 1
        code.extend(['lit', 1])
        self.assertEqual(code, [None, 'lit', 1])
        lit_op_val = self.vM.immed_op()
        self.assertEqual(self.vM.pc, 2)
        self.assertEqual(lit_op_val, 1)
       
    def test_util_convert_from_string_utility(self):
        self.assertTrue( isinstance( pycompiler.util.convert_from_str('42'), int) )
        self.assertTrue( isinstance( pycompiler.util.convert_from_str('3.1415'), float) )
        self.assertTrue( isinstance( pycompiler.util.convert_from_str('howdy'), str) )


    def test_run_vm_data_file(self):
        outfile = os.path.join(tempdir,'temp_vm_out')
        codefile = os.path.join(tempdir,'temp_vm_code')
        datafile = os.path.join(tempdir,'temp_vm_data')
        codestrings = [
"""lit
1
lit
20
lit
5
mult
sti
quit
""",
'lit 10 lit 10 mult store 1 quit',

]
        for codestring in codestrings:
            create_codefile(codefile, codestring)
            vM = pycompiler.vm.VM(outfile=outfile,
                                  codefile=codefile,
                                  datafile=datafile)
            vM.execute()
            data = open(datafile).read()
            #print data
            self.assertNotEqual(data.find('100'), -1)

    def test_vm_throws_VmException_on_bad_operator(self):
        code = \
"""lit
30
lit
5
add
kilroy_was_here
quit"""
        self.assertRaises(VmException, self.run_code_through_vm, code, '')
        
        
class TestVmPic(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.outfile = os.path.join(tempdir,'temp_out')
        self.vM = pycompiler.vm.VM(self.outfile)
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        remove_file(os.path.join(tempdir,'temp_out'))
        
    def test_take_picture_of_vm_vanilla(self):
        # vanilla because, no instructions are required to work for this test
        # not trying to be realistic yet
        # note--have noticed that the C++ imp. of simpic is tightly coupled to the
        # instruction set--so if you have immediate operands, you have to include the
        # instruction in the if clause in simpic()
        # though this is uncool, for now I am going to follow this as I don't want to 
        # increase complexity (no doubt the original reason)--however I'm thinking that
        # turning the instructions into a class with immediate operands as a subclass
        # would deal with this and might be nice for the design in various ways
        data = self.vM.data
        code = self.vM.code
        stack = self.vM.stack
        self.vM.pc = 1
        data.extend( [12, -1, 0, 0] )
        code.append('add')
        stack.push(1)
        stack.push(2)
        strpic = self.vM.vm_pic()
        expected = os.linesep.join(['stack    1\t2',
                                   'data     12\t-1\t0\t0',
                                   'add      at  1',
                                   os.linesep])
        self.assertEqual(strpic, expected)
## note below didn't work on Windows
#"""stack    1\t2 
#data     12\t-1\t0\t0 
#add      at  1 
#
#"""
        
    def test_vm_pic_logs_input(self):
        self.vM.code = [None,'in', 'quit']
        old_stdin = sys.stdin
        try:
            sys.stdin = StringIO.StringIO('42')
            self.vM.execute()
            self.assertEqual(self.vM.stack.data, [42])
            
            input_msg = self.vM.input_logstring + '42'
            
            self.vM.outfile.close()
            self.assertNotEqual(open(self.outfile).read().find(input_msg), -1)
            
        finally:
            sys.stdin = old_stdin
        
   
    def test_vm_pic_logs_output(self):
        self.vM.stack.push('string_on_stack')
        self.vM.code = [None,'out', 'quit']
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            self.vM.execute()
            self.assertEqual(sys.stdout.getvalue(), 
                             'string_on_stack\n')
            
            output_msg = self.vM.output_logstring + 'string_on_stack'
            
            self.vM.outfile.close()
            self.assertNotEqual(open(self.outfile).read().find(output_msg), -1)
            # also test that the message is gone after instruction
            self.assertEqual(self.vM.io_on_previous_instr, None)
        finally:
            sys.stdout = old_stdout
            
    def test_vm_pic_adds_immediate_op(self):
        for instruct in self.vM.immed_op_instructions:
            vm1 = pycompiler.vm.VM(self.outfile)
            vm1.data = [0, 0, 0, 0, 0]
            vm1.code = [None, instruct, 3, 'quit']
            vm1.stack.push(100)
            vm1.execute()
            vm1.outfile.close()
            found = False
            for line in open(self.outfile):
                if ' '.join(line.split()).find('%s 3' % instruct) != -1: found = True
            self.assertEqual( found, True, 'instruct = %s' % instruct)
#        try:
#            os.remove(self.outfile)
#        except Exception, msg:
#            totalmsg = \
#"""
#TestVmPic.test_vm_pic_adds_immediate_op():
#Caught exception (probably Windows couldn't delete a file so you'll have to
#do it manually.
#Exception msg:
#""" + str(msg)
#            print >> sys.stdout, totalmsg
    
    def test_output_file_and_vm_pic(self):
        vm1 = pycompiler.vm.VM(self.outfile)
        vm1.code = [None,'lit', 27, 'out', 'lit', 'hello', 'quit']
        #vm1.stack.push(27)
        vm1.execute()
        vm1.outfile.close()
        file_contents = open(self.outfile).read()
        self.assertNotEqual(file_contents.find('27'), -1)
        self.assertNotEqual(file_contents.find(vm1.output_logstring), -1)
        # test that io string is logged at appropriate instruction execution
        # 
        parts = file_contents.split('stack')
        found = False
        for part in parts:
            if part.find('out ') != -1 and part.find(vm1.output_logstring) != -1: 
                found = True
        self.assertEqual(found, True)
        
        
        
        
class TestVmInstructions(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        create_default_data_file()
        self.vM = pycompiler.vm.VM(datafile='datafile')
        create_file('codefile', [])
        self.vM.read_files()
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
        
    ## method note, at this point, before getting into the instruction tests,
    # I realize that I want to keep the exec_cycle method unchanged by the need for
    # testing, but I also want to check the vm internals after executing only a command
    # so I can't override the method locally, as that would defeat the above purpose
    # Since I was going to implement a vm_pic() method following Prof. Daley's simpic()
    # that captures the state of the vm, I might as well go do that now and use its
    # output for testing
    
    ## update to above:  after implementing the vm_pic(), I realized that using it for
    # testing would still be a pain--indicating a problem
    # the need to test a single instruction at a time while adding it to the instruction set
    # force an increase in orthogonality that I implemented by refactoring the vm
    # to use a dictionary based instruction set so the instructions are not in the middle
    # of the exec_cycle() method
    # I like it, but I ran into a slight snafu--in order to
    # make the execution context occur within the vm class body
    # I had to add exec_current_instr() to it, although this is probably cool
    
    # for all the instructions the literal op is used in the test name
    
    def test_lit(self):
        self.vM.code.extend(['lit', 5])
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [5])
        self.assertEqual(self.vM.pc, 2)
        
    # storage instuctions
            
    def test_load(self):
        self.vM.code.extend(['load', 1])
        self.vM.data[1] = 23
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [23])
        
    def test_store(self):
        self.vM.code.extend(['store', 1])
        self.vM.stack.push(5)
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.data[1], 5)
        
    def test_ldi(self):
        self.vM.data[2] = -1
        self.vM.stack.push(2)
        self.vM.code.extend(['ldi'])
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [-1])
        
    def test_sti(self):
        self.vM.stack.push(4)
        self.vM.stack.push(13)
        self.vM.code.append('sti')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.data[4], 13)
        
    # arithmetic instructions
        
    def test_add(self):
        self.vM.stack.push(4)
        self.vM.stack.push(13)
        self.vM.code.append('add')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [17])
    
        
    def test_sub(self):
        self.vM.stack.push(4)
        self.vM.stack.push(13)
        self.vM.code.append('sub')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [-9])
        
    def test_mult(self):
        self.vM.stack.push(4)
        self.vM.stack.push(13)
        self.vM.code.append('mult')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [52])
        
    def test_div(self):
        self.vM.stack.push(100)
        self.vM.stack.push(5)
        self.vM.code.append('div')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [20])
        
    def test_div_by_zero_raises_ZeroDivisionError(self):
        self.vM.stack.push(5)
        self.vM.stack.push(0)
        self.vM.code.append('div')
        self.assertRaises(ZeroDivisionError, self.vM.exec_current_instr)
        
    def test_neg(self):
        self.vM.stack.push(1)
        self.vM.code.append('neg')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [-1])
        
    def test_eq(self):
        self.vM.stack.push(4)
        self.vM.stack.push(4)
        self.vM.code.append('eq')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        self.vM.stack.push(2)
        self.vM.code.append('eq')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])

    def test_lt(self):
        self.vM.stack.push(4)
        self.vM.stack.push(5)
        self.vM.code.append('lt')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        self.vM.stack.push(-1)
        self.vM.code.append('lt')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])
        
    def test_gt(self):
        self.vM.stack.push(4)
        self.vM.stack.push(5)
        self.vM.code.append('gt')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])
        self.vM.stack.push(-1)
        self.vM.code.append('gt')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        
    def test_ne(self):
        self.vM.stack.push(4)
        self.vM.stack.push(4)
        self.vM.code.append('ne')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])
        self.vM.stack.push(2)
        self.vM.code.append('ne')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])

    def test_le(self):
        self.vM.stack.push(4)
        self.vM.stack.push(5)
        self.vM.code.append('le')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        self.vM.stack.push(-1)
        self.vM.code.append('le')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])
        self.vM.stack.push(0)
        self.vM.code.append('le')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        
    def test_ge(self):
        self.vM.stack.push(4)
        self.vM.stack.push(5)
        self.vM.code.append('ge')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])
        self.vM.stack.push(-1)
        self.vM.code.append('ge')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        self.vM.stack.push(1)
        self.vM.code.append('ge')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
                
    def test_inc(self):
        self.vM.stack.push(13)
        self.vM.code.extend(['inc', 2])
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [15])
        
    def test_dec(self):
        self.vM.stack.push(13)
        self.vM.code.extend(['dec', 2])
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [11])

        
    # branching instructions
    def test_br(self):
        # unconditional branch to top of stack
        self.vM.stack.push(4)
        self.vM.code.append('br')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.pc, 4-1)
        
    def test_brl(self):
        # branch to label--unconditional branch to immediate operand
        self.vM.code.extend(['brl', 4])
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.pc, 4-1)
    
    def test_brf(self):
        # branch on false
        self.vM.stack.push(0)
        self.vM.stack.push(3)
        self.vM.code.append('brf')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.pc, 3-1)
    
    # io instructions
    def test_in(self):
        old_stdin = sys.stdin
        try:
            sys.stdin = StringIO.StringIO('42')
            self.vM.code.append('in')
            self.vM.exec_current_instr()
            self.assertEqual(self.vM.stack.data, [42])
            
            # in handles strings as well
            sys.stdin = StringIO.StringIO('Hidee Ho')
            self.vM.code.append('in')
            self.vM.exec_current_instr()
            self.assertEqual(self.vM.stack.data, [42, 'Hidee Ho'])
            
        finally:
            sys.stdin = old_stdin
        
    def test_out(self):
        # out prints top of stack + newline
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            self.vM.stack.push(13)
            self.vM.code.append('out')
            self.vM.exec_current_instr()
            # note below works on Windows, but os.linesep does not
            self.assertEqual(sys.stdout.getvalue(), '13\n')
        finally:
            sys.stdout = old_stdout
            
    # logical instructions
    def test_and(self):
        self.vM.stack.push(0)
        self.vM.stack.push(1)
        self.vM.code.append('and')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])
        self.vM.stack.push(0)
        self.vM.code.append('and')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])
        self.vM.stack.push(1)
        self.vM.stack.push(1)
        self.vM.code.append('and')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0, 1])
        
    def test_or(self):
        self.vM.stack.push(0)
        self.vM.stack.push(1)
        self.vM.code.append('or')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        self.vM.stack.push(1)
        self.vM.code.append('or')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1])
        self.vM.stack.push(0)
        self.vM.stack.push(0)
        self.vM.code.append('or')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [1, 0])
        
    def test_not(self):
        self.vM.stack.push(1)
        self.vM.code.append('not')
        self.vM.exec_current_instr()
        self.assertEqual(self.vM.stack.data, [0])

    
if __name__ == '__main__':
    unittest.main()
    