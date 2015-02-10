##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

import unittest
import pycompiler.util
from pycompiler.util import *

import os.path, sys, StringIO, types

        
class TestStack(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    def test_stack_push_an_int(self):
        stack = pycompiler.util.Stack()
        stack.push(1)
        self.assertEqual(stack.data, [1])
        
    def test_stack_push_2_ints_and_pop_1_int(self):
        stack = pycompiler.util.Stack()
        stack.push(1)
        stack.push(-256)
        self.assertEqual(stack.data, [1, -256])
        top = stack.pop()
        self.assertEqual(top, -256)
        self.assertEqual(stack.data, [1])
        
    def test_push_and_pop_string_and_int(self):
        stack = pycompiler.util.Stack()
        stack.push('hello world')
        stack.push(7)
        self.assertEqual(stack.data, ['hello world', 7])
        top = stack.pop()
        self.assertEqual(top, 7)
        self.assertEqual(stack.data, ['hello world'])

    def test_pop_empty_stack_throws_AssertionError(self):
        stack = pycompiler.util.Stack()
        self.assertRaises(AssertionError, stack.pop)
        
    def test_string_representation_of_stack(self):
        stack = pycompiler.util.Stack()
        stack.data = [1, 2, 'hello']
        strval = "%s" % stack
        self.assertEqual(strval, "1\t2\thello")
        
    def test_stack_has_top_method(self):
        stack = pycompiler.util.Stack()
        stack.push(1)
        stack.push('wow')
        self.assertEqual(stack.top(), 'wow')
        
    def test_top_called_on_empty_stack_throws_AssertionError(self):
        stack = pycompiler.util.Stack()
        self.assertRaises(AssertionError, stack.top)
        
    def test_push_multiple_elements_in_stack_order(self):
        stack = pycompiler.util.Stack()
        stack.multipush([1, 2, 3])
        self.assertEqual(stack.data, [3, 2, 1])
        stack = pycompiler.util.Stack()
        stack.multipush(['a', 'b', 'c'])
        self.assertEqual(stack.data, ['c', 'b', 'a'])
        
    def test_stack_prints_reverse(self):
        stack = pycompiler.util.Stack()
        stack.multipush(['a', 'b', 'c'])
        self.assertEqual(stack.data, ['c', 'b', 'a'])
        strval = stack.print_reverse()
        self.assertEqual(strval, "a\tb\tc")
        self.assertEqual(stack.data, ['c', 'b', 'a'])
        # add ability to specify delimiter other than '\t'
        strval = stack.print_reverse('   ')
        self.assertEqual(strval, "a   b   c")
        self.assertEqual(stack.data, ['c', 'b', 'a'])
        
    def test_push_then_pop_returns_item_not_copy(self):
        stack = pycompiler.util.Stack()
        stack2 = pycompiler.util.Stack()
        stack2.push('stack2')
        stack.push(stack2)
        self.assertEqual(stack.data, [stack2])
        alias_stack = stack.pop()
        self.assertEqual(stack2, alias_stack)
        stack3 = pycompiler.util.Stack()
        stack3.push('stack2')
        self.assertNotEqual(stack3, stack2)
        self.assertNotEqual(stack3, alias_stack)
        
        
            
    
    
class TestConvertFromString(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
      
    def test_util_convert_from_string_utility(self):
        self.assertTrue( isinstance( pycompiler.util.convert_from_str('42'), int) )
        self.assertTrue( isinstance( pycompiler.util.convert_from_str('3.1415'), float) )
        self.assertTrue( isinstance( pycompiler.util.convert_from_str('howdy'), str) )
        ## add None
        self.assertTrue( isinstance( pycompiler.util.convert_from_str('None'), types.NoneType) )
        

class TestMyWrite(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.outfile = open('my_write_outfile', 'w')
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.outfile.close()
        os.remove('my_write_outfile')
        
    def test_write_to(self):
        string1 = \
"""Multiline string
that goes to
stdout and outfile"""
        
        string2 = 'only goes to file'
        string3 = 'only goes to stdout'
        
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            pycompiler.util.write_to(string1, sys.stdout, self.outfile)
            pycompiler.util.write_to(string2, self.outfile)
            pycompiler.util.write_to(string3, sys.stdout)
            
            self.outfile.close()
            outfile_contents = open('my_write_outfile').read()
            stdout_contents = sys.stdout.getvalue()
            
            self.assertNotEqual(outfile_contents.find(string1), -1)
            self.assertNotEqual(outfile_contents.find(string2), -1)
            self.assertEqual(outfile_contents.find(string3), -1)
            self.assertNotEqual(stdout_contents.find(string1), -1)
            self.assertNotEqual(stdout_contents.find(string3), -1)
        finally:
            sys.stdout = old_stdout
                   
    def test_file_none_no_problem(self):
        # make sure that if an argument == None is passed, it doesn't
        # cause an exception
        string1 = "only goes to that which exists"
        file2 = None
        pycompiler.util.write_to(string1, self.outfile, file2)
        
        self.outfile.close()
        outfile_contents = open('my_write_outfile').read()
        self.assertNotEqual(outfile_contents.find(string1), -1)
                    
class TestMisc(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self) 
        
    def test_equal_w_out_whitespace(self):
        string1 = '  hi    there        dave, what  up?'
        string2 = '''hi there dave,
        what    up?'''
        string3 = 'hi there dave, what up?'
        self.assertEqual(equal_without_whitespace(string1, string2), True)
        self.assertEqual(equal_without_whitespace(string1, string3), True)
        
    def test_find_without_whitespace(self):
        string1 = '  hi    there        dave, what  up?'
        string2 = '''hi there dave,
        '''
        string3 = 'dave, what up?'
        self.assertEqual(find_without_whitespace(string1, string2), True)
        self.assertEqual(find_without_whitespace(string1, string3), True)
        self.assertEqual(find_without_whitespace(string2, string1), False)
    
    def test_token_stack_str(self):
        stack = Stack()
        for (name, val) in [('goal',''), ('$id', 'varname'), ('$int', 5), ('t', '')]:
            stack.push( {'name': name, 'value': val} )
        self.assertEqual(token_stack_str(stack, reverse=True, delim=' '),
                         't ($int, 5) ($id, varname) goal')
        
        
if __name__ == '__main__':
    unittest.main()
    
    