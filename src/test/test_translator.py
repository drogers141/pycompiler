#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##


from pycompiler import vm

import os, sys, StringIO, glob, shutil
import unittest

from pycompiler.globals import *
import pycompiler
from pycompiler.parser import *
from pycompiler.util import *
from pycompiler.translator import *
from pycompiler.vm import VM

### utility functions used by more than one test case class
def create_file(fname, content):
    """Creates file filename from list or string 'content' adding line seps if list."""
    f = open(fname, 'w')
    buf = "no data for file"
    if isinstance(content, list):
        buf = os.linesep.join(content)
    elif isinstance(content, str):
        buf = content
    f.write(buf)

def create_default_data_file(fname='datafile'):
    """Creates datafile initialized with 5 lines of zeros."""
    create_file(fname, ['0','0','0','0','0'])
    
def make_token_string(string, grammar):
    """This version for translation--handles action_symbols--could combine with the other
    later.
    Take a string with either just the names of tokens, or names and values, separated by whitespace, 
    and return a string in proper tokenfile format.  So--if a valid token name is followed by another 
    valid token name, the first name will be assumed to be a token whose value is '', and thus the 
    relevant section of the returned string would be:
    first_name
    
    second_name
    """
    if not grammar:
        raise Exception('test_translator.make_token_string: need grammar')
    vocab = grammar.terminals + grammar.nonterminals
    all = vocab + grammar.action_symbols
    #empty_val = []#'$goto', ':']     # force their values to be empty no matter what's next
    parts = string.split()
    ret = ''
    i = 0
    while i < len(parts):
        #print 'parts[%d] = %s' % (i, parts[i])
        if parts[i] in vocab:
            try:
                if parts[i+1] in all: # or parts[i] in empty_val:
                    ret += '%s\n\n' % (parts[i])
                    i += 1
                else:
                    ret += '%s\n%s\n' % (parts[i], parts[i+1])
                    i += 2
                    continue
            except IndexError:
                return ret + '%s\n\n' % (parts[i])
        elif parts[i] in grammar.action_symbols:
            ret += '%s\n\n' % (parts[i])
            i += 1
        else: return ''
    return ret + '\n\n'


class TestTranslatorAndTSCreation(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.codefile = os.path.join(tempdir, 'tr_codefile')
        self.datafile = os.path.join(tempdir, 'tr_datafile')
        create_default_data_file(self.datafile)
        self.outfile = os.path.join(tempdir, 'translator_out')
        self.tokfile = os.path.join(tempdir, 'tokfile.ts.temp')
        self.tsfile = os.path.join(grammardir, 'plh.ts')
        self.ts = TransScheme.create_ts(self.tsfile)
        self.default_args = {'tokensource': self.tokfile,
                           'outfile': self.outfile,
                           'codefile': self.codefile,
                           'datafile': self.datafile,
                           'grammar': self.ts}
        
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def create_tokfile(self, tokstring):
        tokstring = make_token_string(tokstring, self.ts)
        open(self.tokfile, 'w').write(tokstring)
        
    def test_ts_parts(self):
        expected_actions = ['@add', '@mult', '@sub', '@div', ]
        allfound = True
        for a in expected_actions:
            if not a in self.ts.action_symbols:
                allfound = False            
        self.assertEqual(allfound, True)
        ts_str = str(self.ts)
        expected = 'Action Symbols:  [ @add, @mult, @sub, @div, '
        self.assertEqual( find_without_whitespace(ts_str, expected), True)
        #print ts_str
    
    def test_emit(self):
        tokstring = '$id x = $int 7 ;'
        self.create_tokfile(tokstring)
        self.trans = PlhTranslator(**self.default_args)
        self.trans.emit('lit')
        self.trans.emit(1)
        self.assertEqual(self.trans.code[1:], ['lit', 1])
        
    def test_lookup_or_add(self):
        tokstring = '$id x = $int 7 ;'
        self.create_tokfile(tokstring)
        self.trans = PlhTranslator(**self.default_args)
        firstx = self.trans.lookup_or_add('x', type='intvar')
        firsty = self.trans.lookup_or_add('y', type='intvar')
        secondx = self.trans.lookup_or_add('x')
        secondy = self.trans.lookup_or_add('y')
        self.assertEqual(firstx['address'], 1)
        self.assertEqual(firsty['address'], 2)
        self.assertEqual(secondx['address'], 1)
        self.assertEqual(secondy['address'], 2)
        self.assertEqual(self.trans.symbols['x']['address'], 1)
        self.assertEqual(self.trans.symbols['x']['type'], 'intvar')
        self.assertEqual(self.trans.symbols['y']['address'], 2)
        self.assertEqual(self.trans.symbols['y']['type'], 'intvar')
        
        
    def test_translator_basics(self):
        tokstring = '$id x = $int 7 ;'
        outfile = os.path.join(tempdir, 'parserout.plh.ts.basics')
        self.default_args['outfile'] = outfile
        self.create_tokfile(tokstring)
        self.trans = PlhTranslator(**self.default_args)
        self.trans.parse()
        self.assertEqual(self.trans.code[1:], ['lit', 1, 'lit', 7, 'sti', 'quit'])
        self.assertEqual(self.trans.symbols['x']['address'], 1)
        
        
        
    def test_translator_produces_codefile(self):
        tokstring = '$id pay = $int 7 ;'
        self.create_tokfile(tokstring)
        trans = PlhTranslator(**self.default_args)
  
        expected_code = [None, 'lit', 1, 'lit', 7, 'sti', 'quit']
        trans.parse()
        self.assertEqual(trans.code, expected_code)
        trans = None
        code_from_file = open(self.codefile).readlines()
        #self.assertEqual(code_from_file, expected_code[1:])




class TestPlhTsActionsNonTerms(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.ts = TransScheme.create_ts(os.path.join(grammardir, 'plh.ts'))
        self.codefile = os.path.join(tempdir, 'plh_codefile')
        self.datafile = os.path.join(tempdir, 'plh_datafile')
        self.tr_outfile = os.path.join(tempdir, 'plh_trans_out')
        tokstring = '$id x = $int 1 ;'
        self.trans = PlhTranslator(tokensource= tokstring,
                           outfile= self.tr_outfile,
                           codefile= self.codefile,
                           datafile=self.datafile,
                           grammar= self.ts)
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_actions_in_ts(self):
        # all defined actions are in a rule
        for action in self.ts.action_symbols:
            found = False
            for rule in self.ts.rules:
                rhs = rule[1]
                if action in rhs:
                    found = True
                    break
            self.assertEqual(found, True)
        # all actions in rules are defined   
        for rule in self.ts.rules:
            rhs = rule[1]
            actions = [s for s in rhs.split() if s.startswith('@')]
            found = False
            if actions:
                for action in actions:
                    if action in self.ts.action_symbols:
                        found = True
                        break
                self.assertEqual(found, True)

    def test_all_action_symbols_have_actions(self):
        for action in self.ts.action_symbols:
            found = False
            if action in self.trans.actions: found = True                
            self.assertEqual(found, True)
            
    def test_all_actions_have_action_symbols(self):
        for acts in self.trans.actions:
            found = False
            if acts in self.ts.action_symbols: found = True                
            self.assertEqual(found, True)
            
    def test_all_nonterminals_in_rule(self):
        for nt in self.ts.nonterminals:
            found = False
            for rule in self.ts.rules:
                both_sides = (' '.join(rule)).split()
                #print both_sides
                if nt in both_sides: 
                    found = True
                    break 
            if not found: print 'Nonterminal not found in rules: %s' % (nt)              
            self.assertEqual(found, True)


class TestTranslatorWorksWithTokenString(unittest.TestCase):
    ## follow the lead from the similar test in test_parser
    ## to anyone attempting to make sense, this was to ensure the ability
    ## to handle token strings rather than files uniformly with the subclasses
    ## of parser.Parser, the other approaches--make_token_string(), etc still work,
    ## but aren't necessary
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.codefile = os.path.join(tempdir, 'tr_codefile')
        self.datafile = os.path.join(tempdir, 'tr_datafile')
        self.tokstring = '''$id numtosort = $int 5 ; $goto $id in ; $id numtosort = $int 1 ; 
                                : $id in : $id x = $int 32 ;'''
        self.ts = TransScheme.create_ts(open(os.path.join(grammardir, 'plh.ts')).read())
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_run_all_with_tokstrings(self):
        t = PlhTranslator(codefile=self.codefile,
                          datafile=self.datafile,
                          tokensource=self.tokstring,
                          grammar=self.ts)
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            t.parse()
            self.assertNotEqual( sys.stdout.getvalue().find('accept'), -1 )
            #print 'reject test: stdout =', sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        

class TestPlhTransTokstringsToCode(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.ts = TransScheme.create_ts(os.path.join(grammardir, 'plh.ts'))
        self.codefile = os.path.join(tempdir, 'tr_codefile')
        self.datafile = os.path.join(tempdir, 'tr_datafile')
        create_default_data_file(self.datafile)
        self.outfile = os.path.join(tempdir, 'test_plh_trans_out')
        self.tokfile = os.path.join(tempdir, 'tokfile.ts.temp')
        self.default_args = {'tokensource': self.tokfile,
                           'outfile': self.outfile,
                           'codefile': self.codefile,
                           'datafile': self.datafile,
                           'grammar': self.ts}
        
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def create_tokfile(self, tokstring):
        tokstring = make_token_string(tokstring, self.ts)
        open(self.tokfile, 'w').write(tokstring)
        
    def run_plh_trans_on_tokstring_check_code(self, tokstring, codestring):
        """Run a whitespace delimited tokenstring and compare the resulting
        code array's contents with codestring.
        """
        self.create_tokfile(tokstring)
        trans = PlhTranslator(**self.default_args)
        trans.parse()
        code = [str(s) for s in trans.code[1:]]
        expected = codestring.split()
        self.assertEqual(code, expected)
        
        
    def test_various_statements(self):
        for (tokstring, codestring) in [
            ('$id x = $int 5 + $int 10 ;',
             'lit 1 lit 5 lit 10 add sti quit'),
            ('$id x = $int 5 * $int 10 ;',
             'lit 1 lit 5 lit 10 mult sti quit'),
             ('$id x = $int 1 ; $id y = $int 10 ; $id z = - ( $int 5 ) ;',
               'lit 1 lit 1 sti    lit 2 lit 10 sti    lit 3 lit 5 neg sti quit'),
             ]:
            self.run_plh_trans_on_tokstring_check_code(tokstring, codestring)
        
    def run_plh_trans_and_vm_check_data(self, tokstring, codestring, datalist):
        """same as run_plh_trans_on_tokstring_check_code, but checks the resulting
        datafile from the vm to datalist."""
        self.run_plh_trans_on_tokstring_check_code(tokstring, codestring)
        vm_outfile=os.path.join(tempdir, 'vm_outfile')
        vm_codefile=os.path.join(tempdir, 'vm_codefile')
        open(vm_codefile, 'w').write('\n'.join(codestring.split()))
        vm = VM(codefile=vm_codefile, datafile=self.datafile, outfile=vm_outfile)
        vm.execute()
        self.assertEqual(datalist, open(self.datafile).read().splitlines())
        
        ## use these to test actions in the ts rules and in the
        ## translator
    def test_statements_for_data_storage(self):
        for (tokstring, codestring, datalist) in [
            ('$id x = $int 5 + $int 10 ;',          ### arithmetic actions
             'lit 1 lit 5 lit 10 add sti quit',
             ['None', '15']),
            ('$id x = $int 5 * $int 10 ;',
             'lit 1 lit 5 lit 10 mult sti quit',
             ['None', '50']),
             ('$id y = $int 5 - $int 10 ;',
             'lit 1 lit 5 lit 10 sub sti quit',
             ['None', '-5']),
             ('$id y = $int 10 / $int 5 ;',
             'lit 1 lit 10 lit 5 div sti quit',
             ['None', '2']),
             ('$id y = $int 5 / $int 10 ;',         # integral division
             'lit 1 lit 5 lit 10 div sti quit',
             ['None', '0']),
             #### example from file 11_PlhConstructs, p. 13, initializing x=1, y=10, z=-5
             ('$id x = $int 1 ; $id y = $int 10 ; $id z = - ( $int 5 ) ; $id x = - $id y * $int 345 / $id z - $id x ;',
               '''lit 1 lit 1 sti    lit 2 lit 10 sti    lit 3 lit 5 neg sti  
                lit 1 lit 2 ldi lit 345 mult lit 3 ldi div neg lit 1 ldi sub sti quit''',
               ['None', '689', '10', '-5',]),
               ### had a declare() problem while doing interpreter
               ('$declare $id x ( $int 5 ) ; $id y = $int 5 ;',
                'lit 7 lit 5 sti quit',
                ['None', 'None', 'None', 'None', 'None', 'None', 'None', '5']),
              
                
                
             ]:
            self.run_plh_trans_and_vm_check_data(tokstring, codestring, datalist)
        
    def test_goto_label_and_print_symbol_table(self):
        tokstring = \
'''$id x = $int 5 ;
$goto $id there ;
$id x = $int 10 ;
: $id there : $id y = $int 6 ;'''
        codestring = \
'''lit 
1 
lit 
5 
sti 
lit
2   # set data[2] to :there:
ldi
br        
lit
1
lit
10
sti
lit       # :there: val = 15, remember--code and data indices start at 1
3
lit
6
sti
quit'''
        # run through parser and check code and symbol table
        self.create_tokfile(tokstring)
        #self.default_args['outfile'] = os.path.join(tempdir, 'test_plh_trans_out_goto')
        tr_outfile = os.path.join(tempdir, 'test_plh_trans_out_goto')
        codefile = os.path.join(tempdir, 'codefile_goto')   
        datafile = os.path.join(tempdir, 'datafile_goto')     
        trans = PlhTranslator(tokensource=self.tokfile,
                              codefile=codefile, 
                              datafile=datafile, 
                              outfile=tr_outfile,
                              grammar=self.ts)
        trans.parse()
        code = [str(s) for s in trans.code[1:]]
        expected = [s.split()[0] for s in codestring.splitlines()]
        self.assertEqual(code, expected)
        self.assertEqual(trans.symbols, { 'x': {'address': 1 , 'type': 'intvar'},
                                         'there': {'address': 2, 'type': 'label' },
                                         'y': {'address': 3, 'type': 'intvar'},
                                         })
        self.assertEqual(open(codefile).read().splitlines(), code)
        
        symtable_str = '\n'.join( ['%s = %s' % (key,trans.symbols[key]) 
                                   for key in trans.symbols])
        print trans.symbol_table_str()
        self.assertEqual(find_without_whitespace(trans.symbol_table_str(), 
                                                 symtable_str),
                                                 True)
        
        # run through vm and check memory array
        #codefile = os.path.join(tempdir, 'codefile_goto') 
        #open(codefile, 'w').write(codestring)
        vm_outfile=os.path.join(tempdir, 'vm_outfile_goto')
        #open(self.codefile, 'w').write(codestring)
        vm = VM(codefile=codefile, 
                datafile=datafile, 
                outfile=vm_outfile)
        vm.execute()
        there_val = 15
        self.assertEqual(vm.data[1:], [5, there_val, 6])
        
        ## check that the @label action wrote info to the parser's outfile
        outstr = open(tr_outfile).read()
        self.assertEqual(find_without_whitespace(outstr, "label 'there': set value of data[2] to %d" % there_val), True)

    def test_label_type_declared_in_symbol_table(self):
        ## just test that a label is stored with the type label int the symbol table
        tokstring = ''': $id assignx : $id x = $int 5 ;'''
#        codefile = os.path.join(tempdir, 'codefile_label')   
#        datafile = os.path.join(tempdir, 'datafile_label')
#        outfile = os.path.join(tempdir, 'outfile_label')     
             
        trans = PlhTranslator(tokensource=tokstring,
                              codefile=self.codefile, 
                              datafile=self.datafile, 
                              outfile=self.outfile,
                              grammar=self.ts)
        trans.parse()
        print trans.symbols
        self.assertEqual(trans.symbols['assignx'], {'address': 1, 'type': 'label'})
    
        
#########################################################################################################
##### 
##### Superclass with trans and vm creation and tokstring to vm stdout check

class TestPlhConstructs(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.ts = TransScheme.create_ts(os.path.join(grammardir, 'plh.ts'))
        self.codefile = os.path.join(tempdir, 'plh_codefile')
        self.datafile = os.path.join(tempdir, 'plh_datafile')
        self.tr_outfile = os.path.join(tempdir, 'plh_trans_out')
        self.vm_outfile = os.path.join(tempdir, 'plh_vm_out')
                
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def create_default_trans_and_vm(self, tokstring):
        self.trans = PlhTranslator(tokensource= tokstring,
                           outfile= self.tr_outfile,
                           codefile= self.codefile,
                           datafile=self.datafile,
                           grammar= self.ts)
        self.vm = VM(outfile=self.vm_outfile, 
                     codefile=self.codefile, 
                     datafile=self.datafile)
    
    def run_tokstring_check_vm_stdout(self, tokstring, expected_list, debug=False):
        """Run the translator then vm using tokenstring.  Expected is a list of 
        expected substrings in captured stdout."""
        self.create_default_trans_and_vm(tokstring)
        self.trans.parse()
        if debug: print 'self.trans.code:\n%s' % self.trans.code
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            self.vm.execute()
            if debug: 
                print 'self.vm.code\n%s' % self.vm.code
                print 'self.vm.data\n%s' % self.vm.data
            #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
            for substring in expected_list:
                self.assertNotEqual( sys.stdout.getvalue().find(substring), -1 )            
        finally:
            sys.stdout = old_stdout



#######################################################################################################

class TestPlhArraysAndPut(TestPlhConstructs):    
    
    def test_plh_array_declaration(self):
        # don't forget arrays are different in pl/h 
        tokstring = '$declare $id x ( $int 5 ) ; $id y = $int -1 ;'
        self.create_default_trans_and_vm(tokstring)
        self.trans.parse()
        self.assertEqual(self.trans.symbols['x'], {'address': 1, 'type': 'array', 'size': 6})
        self.assertEqual(self.trans.symbols['y'], {'address': 7, 'type': 'intvar'})

        tokstring = '$declare $id x ( $int 4 ) , $id y ( $int 9 ) , $id z ( $int 9 ) ; $id a = $int -1 ;'
        self.create_default_trans_and_vm(tokstring)
        self.trans.parse()
        self.assertEqual(self.trans.symbols['x'], {'address': 1, 'type': 'array', 'size': 5})
        self.assertEqual(self.trans.symbols['y'], {'address': 6, 'type': 'array', 'size': 10})
        self.assertEqual(self.trans.symbols['z'], {'address': 16, 'type': 'array', 'size': 10})
        self.assertEqual(self.trans.symbols['a'], {'address': 26, 'type': 'intvar'})

    def test_plh_array_assignment(self):
        # x = { 5, 10, None, 15, 20, None },  y = 1
        tokstring = \
        """$declare $id x ( $int 5 ) ; $id y = $int 1 ; 
        $id x ( $int 0 ) = $int 5 ;  $id x ( $id y ) = $int 10 ; $id x ( $int 3 ) = $int 15 ;  
        $id x ( $id y + $int 3 ) = $int 20 ;"""
        self.create_default_trans_and_vm(tokstring)
        self.trans.parse()
        self.assertEqual(self.trans.symbols['x'], {'address': 1, 'type': 'array', 'size': 6})
        self.assertEqual(self.trans.symbols['y'], {'address': 7, 'type': 'intvar'})
        self.vm.execute()
        #print tokstring
        #print self.vm.code
        #print self.vm.data
        self.assertEqual(self.vm.data[1:], [5, 10, None, 15, 20, None, 1])

    def test_put_for_output(self):
        tokstring = """$id x = $int 5 ; $id y = $int -1 ; $put $id x + $int 1 , $id y ;"""
        self.create_default_trans_and_vm(tokstring)
        self.trans.parse()
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            self.vm.execute()
            #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
            self.assertNotEqual( sys.stdout.getvalue().find('6'), -1 )
            self.assertNotEqual( sys.stdout.getvalue().find('-1'), -1 )            
        finally:
            sys.stdout = old_stdout
        
    
    def test_more_put_stmts(self):
        tokstring = \
        """$declare $id x ( $int 5 ) ; $id y = $int 1 ; 
        $id x ( $int 0 ) = $int 5 ;  $id x ( $id y ) = $int 10 ; $id x ( $int 3 ) = $int 15 ;  
        $id x ( $id y + $int 3 ) = $int 20 ; 
        $put $id x ( $int 0 ) , $id x ( $int 1 ) , $id x ( $id y + $int 1 ) ; 
        $put $id x ( $id y * $int 3 ) ; $put $id x ( $id y * $int 3 + $int 1 ) ; $put $id y ;"""
        
        expected_list = ['5', '10', 'None', '15', '20', '1']
        self.run_tokstring_check_vm_stdout(tokstring, expected_list)


class TestPlhLogicalAndIf(TestPlhConstructs):    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.ts = TransScheme.create_ts(os.path.join(grammardir, 'plh.ts'))
        self.codefile = os.path.join(tempdir, 'plh_codefile')
        self.datafile = os.path.join(tempdir, 'plh_datafile')
        self.tr_outfile = os.path.join(tempdir, 'plh_trans_out_logical')
        self.vm_outfile = os.path.join(tempdir, 'plh_vm_out_logical')
    
    def test_if_then(self):
        assign_tokstring = """$id x = $int 1 ; $id y = $int 2 ; """
        
        ## from the example in file 11_PLHConstructs, but
        ## I added the assignment code to make it a fully functioning program
        ## note also that I don't use a $stop ; statement.  stop will work, but so will
        ## proper end of input
        tokstring = assign_tokstring + ' $if $id x < $id y $then $put $id x ; '
        
        self.create_default_trans_and_vm(tokstring)
        self.trans.parse()
        #print self.trans.symbols
        #print self.trans.code
        #print self.trans.actions_stack
        self.assertEqual(self.trans.symbols, 
                          {'x': {'type': 'intvar', 'address': 1}, 'y': {'type': 'intvar', 'address': 2}})
        
        ## ie code generated by:
        ## """$id y = $int 1 ; $id x = $int 2 ; """
        assignment_code = [None, 'lit', 1, 'lit', 1, 'sti', 'lit', 2, 'lit', 2, 'sti']
        
        brf_address = len(assignment_code) + 14
        expected_code = assignment_code + ['lit', 1, 'ldi', 'lit', 2, 'ldi', 'lt', 'lit', brf_address,
                                           'brf', 'lit', 1, 'ldi', 'out', 'quit']
        self.assertEqual(self.trans.code, expected_code)
        
        
    def test_logical_exprs_w_if_then_and_vm_out(self):
        ## runs all combinations checking the code, then vm output
        for (x, y, relop, vmop) in [(1, 2, '<', 'lt'), (2, 1, '>', 'gt'), (1, 1, '=', 'eq'),
                              (1, 2, '< =', 'le'), (2, 1, '> =', 'ge'), 
                              (1, 1, '< =', 'le'), (1, 1, '> =', 'ge'),
                              (1, 2, '< >', 'ne'), (2, 1, '< >', 'ne'),]:
            assign_part = """$id x = $int %d ; $id y = $int %d ; """ % (x, y)
            log_part    = ' $if $id x %s $id y $then $put $id x ; ' % (relop)
            tokstring = assign_part + log_part        
            self.create_default_trans_and_vm(tokstring)
            self.trans.parse()
            assign_code = [None, 'lit', 1, 'lit', x, 'sti', 'lit', 2, 'lit', y, 'sti']        
            brf_address = len(assign_code) + 14
            log_code = ['lit', 1, 'ldi', 'lit', 2, 'ldi', vmop, 'lit', brf_address,
                                               'brf', 'lit', 1, 'ldi', 'out', 'quit']
            expected_code = assign_code + log_code
            self.assertEqual(self.trans.code, expected_code)
            
            ## check vm runs and outputs x
            old_stdout = sys.stdout
            try:
                sys.stdout = StringIO.StringIO()
                self.vm.execute()
                #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
                self.assertNotEqual( sys.stdout.getvalue().find( str(x) ), -1 )            
            finally:
                sys.stdout = old_stdout

    def test_various_if_then(self):
        for (tokstring, expected) in [
                ('''$if $int 5 > $int 6 $then  $put $int 1 , $int 1 + ( $int 2 - $int 3 ) ;
                $put $int -2 ; ''',
                ['-2']),
                ('''$if $int 5 < $int 6 $then  $put $int 1 , $int 1 + ( $int 2 - $int 3 ) ;
                $put $int -2 ; ''',
                ['1', '0', '-2']),
                ('''$id x = $int 1 ; $id y = $int 5 ; 
                $if $id x  < $id y $then  $goto $id label1 ; 
                $put $int 1 , $int 1 + ( $int 2 - $int 3 ) ;
                : $id label1 : $put $int -2 ; ''',
                ['-2']),  
                ('''$id x = $int 1 ; $id y = $id x + $id x * $int 6 / $int 2 ; 
                $if $id x  < $id y $then  $goto $id label1 ; 
                $stop ;
                : $id label1 : $put $int -2 ; ''',
                ['-2']),                 
                                      
                                      ]:
            self.run_tokstring_check_vm_stdout(tokstring, expected)

        
class TestGetAndDo(TestPlhConstructs):
    
    def test_get(self):
        tokstring = """$id x = $int 0 ; $id y = $int 0 ;
        $put $id x , $id y ;
        $get $id x , $id y ;
        $put $id x , $id y ;"""
        
        old_stdin = sys.stdin
        try:
            sys.stdin = StringIO.StringIO('1\n2\n')
            expected = ['0', '1', '2']
            self.run_tokstring_check_vm_stdout(tokstring, 
                                               expected,
                                               debug=True
                                               )
            
        finally:
            sys.stdin = old_stdin
        
        
    def test_do_group_construct(self):
        tokstring = \
"""$id x = $int 0 ; $id y = $int 0 ;
$do ;
    $put $id x , $id y ;
    $id x = $int 1 ; $id y = $int -1 ;
$end ;"""
        expected = ['0', '1', '-1']
        self.run_tokstring_check_vm_stdout(tokstring, 
                                           expected,
                                           debug=True
                                           )
if __name__ == '__main__':
    unittest.main()
    