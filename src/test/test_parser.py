#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

from tree.parsetree import ParseTreeBuilder
import os, sys, StringIO, glob
import unittest
from pycompiler.globals import *
from pycompiler.parser import *
from pycompiler.util import *
from pycompiler.translator import *
import pycompiler

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
    """Take a string with either just the names of tokens, or names and values, separated by whitespace, 
    and return a string in proper tokenfile format.  So--if a valid token name is followed by another 
    valid token name, the first name will be assumed to be a token whose value is '', and thus the 
    relevant section of the returned string would be:
    first_name
    
    second_name
    """
    if not grammar:
        grammar = Grammar.get_gse3()
        #grammar = Grammar.create_grammar( os.path.join(grammardir, 'plh.g') )
    vocab = grammar.terminals + grammar.nonterminals
    parts = string.split()
    ret = ''
    i = 0
    while i < len(parts):
        #print 'parts[%d] = %s' % (i, parts[i])
        if parts[i] in vocab:
            try:
                if parts[i+1] not in vocab:
                    ret += '%s\n%s\n' % (parts[i], parts[i+1])
                    i += 2
                    continue
                else: 
                    ret += '%s\n\n' % (parts[i])
                    i += 1
            except IndexError:
                return ret + '%s\n\n' % (parts[i])
        else: return ''
    return ret + '\n\n'
    
# just wanted this handy for later perhaps
#  note--have added parse sets
gse3_grammar_string = \
"""
goal -> e        { $id, ( }
e -> t mt        { $id, ( }
mt -> + t mt     { + }
mt ->            { ), # }
t -> f mf        { $id, ( }
mf -> * f mf     { * }
mf ->            { +, ), # }
f -> $id         { $id }
f -> ( e )       { ( }
"""

                     
simple_token_content = \
"""
$id

+

$id

"""

class TestParser(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tokfile = os.path.join(tempdir, 'tokfile')
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    # a test to come back to after we're pretty functional
#    def test_parser_input_to_output_easy_case(self):
#        
#        tokfile_contents =\
#"""$id
#
#*
#
#$id
#
#+
#
#$id
#
#
#"""
#        self.parser.parse()
#        
#        stdout = "accept"
#        
#        self.assertNotEqual(stdout.find("accept"), -1)
        
    # this tests various initialization stuff, that is changing a bit
    # I've eliminated the init() method of the parser and moved the logic
    # to the constructor, which seems to be fine
    # the codefile and datafile will become important as we deal with 
    # translation, though I may restructure anyway ...
    def test_init(self):
        tokfile_contents =\
"""$id

*

$id

+

$id


"""
        create_file(self.tokfile, tokfile_contents)  
        self.parser = pycompiler.parser.Parser(tokensource=self.tokfile)      
        self.assert_( (self.parser.token_list) )
        self.assertEqual(self.parser.stack.data, make_token_seq(['%', 'goal']))
        self.assert_( self.parser.code == [] and self.parser.data == [])
        self.assertEqual(self.parser.pc, 0)
        # set current token to None
        self.assertEqual(self.parser.current_token, None)



    def test_next_token(self):
        tokfile_contents =\
"""$id

*

$id

"""
        create_file(self.tokfile, tokfile_contents)  
        self.parser = pycompiler.parser.Parser(tokensource=self.tokfile)      
        self.assertEqual(self.parser.current_token, None)
        
        self.parser.next_token()
        self.assertEqual(self.parser.current_token, make_token('$id'))
        self.parser.next_token()
        self.assertEqual(self.parser.current_token, make_token('*'))
        self.parser.next_token()
        self.assertEqual(self.parser.current_token, make_token('$id'))
        self.parser.next_token()
        self.assertEqual(self.parser.current_token, make_token('#'))
        self.parser.next_token()
        self.assertEqual(self.parser.current_token, None)
        
    def test_next_token_handles_strings_and_action_symbols(self):
        #parser = Parser(tokensource, outfile, codefile, datafile, grammar)
        print 'come back to test_parser.test_next_token_handles_strings_and_action_symbols sometime'
        
        
class TestTokens(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tokfile = os.path.join(tempdir, 'tokfile')
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_token_is_dict_with_keys_name_and_value(self):
        tokfile_contents = \
"""$id
numtosort
=

$int
5
"""
        tc = make_token_string(tokfile_contents, None)
        create_file(self.tokfile, tokfile_contents)
        parser = pycompiler.parser.Parser(tokensource=self.tokfile)
        parser.next_token()
        self.assertEqual(parser.current_token['name'], '$id')
        self.assertEqual(parser.current_token['value'], 'numtosort')

        
class TestGrammar(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.parser = pycompiler.parser.Parser()
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    # load a grammar into a data structure--rather than hard coding
    def test_load_grammar(self):
        t = ['$id', '*', '+', '(', ')', ]
        nt = ['e', 'goal', 't', 'mt', 'f', 'mf', ]
        r = [['goal', 'e'], 
                 ['e', 't mt'], 
                 ['mt', '+ t mt'],
                 ['mt', ''],
                 ['t', 'f mf'],
                 ['mf', '* f mf'],
                 ['mf', ''],
                 ['f', '$id'],
                 ['f', '( e )'], ]
        pa = [[], 
                 ['$id', '('], 
                 ['+'],
                 [')', '#'],
                 ['$id', '('],
                 ['*'],
                 ['+', ')', '#'],
                 ['$id'],
                 ['('],  ]
        start = 'goal'
        g = pycompiler.parser.Grammar(terminals=t, nonterminals=nt, 
                                      rules=r, parse_actions=pa,
                                      start_symbol=start)
        self.assertEqual(g.rules[0], ['goal', 'e'])
        self.assertEqual(g.rules[1], ['e', 't mt'])
        self.assertEqual(g.pa[1], ['$id', '('])


### for reference ####        
### gse3 rules and pa sets:
#    note that x is $id for us, and for now we start with 0
#        but the 0th rule is goal -> e, so these rule numbers should be the same
#
#    Rule            PA(Rule)  
#
#  [ 0 goal -> e       {} ]
#    1) e -> t mt        { x ( }
#    2) mt -> '+' t mt    { + }
#    3) mt -> ''        { ) # }
#    4) t -> f mf        { x ( }
#    5) mf -> '*' f mf    { * }
#    6) mf -> ''        { + ) # }
#    7) f -> 'x'        { x }
#    8) f -> '(' e ')'    { ( }


    def test_default_grammar_is_gse3(self):
        g = self.parser.grammar
        self.assertEqual(g.rules[0], ['goal', 'e'])
        self.assertEqual(g.rules[1], ['e', 't mt'])
        self.assertEqual(g.pa[1], ['$id', '('])
        
    def test_grammar_start_symbol(self):
        g = self.parser.grammar
        self.assertEqual(g.start_symbol, 'goal')
        
    def test_grammar_parse_action(self):
        # the grammar should return the index of the appropriate rule
        # when passed an element of a parse action set
        ## modified to handle tokens as dicts
        index = self.parser.grammar.parse_action(('t'), ('$id'))
        self.assertEqual(index, 4)
        index = self.parser.grammar.parse_action(('e'), ('$id'))
        self.assertEqual(index, 1)
        index = self.parser.grammar.parse_action(('f'), ('$id'))
        self.assertEqual(index, 7)
        index = self.parser.grammar.parse_action(('mt'), ('#'))
        self.assertEqual(index, 3)
        index = self.parser.grammar.parse_action(('t'), (')'))
        self.assertEqual(index, -1)
    
    def test_grammar_has_string_representation(self):
        ## using the gse3 grammar as with other examples
        g = self.parser.grammar
        gstring = str(g)        # ;-)
        #print 'grammar string\n', gstring
        
        nonterm_string = '[ e, goal, t, mt, f, mf ]'
        term_string = '[ $id, *, +, (, ), #, % ]'
        foundnt = foundt = False
        for gline in gstring.split(os.linesep):
            if find_without_whitespace(gline, nonterm_string):
                foundnt = True
                continue
            if find_without_whitespace(gline, term_string):
                foundt = True
                continue
        self.assertEqual( (foundnt, foundt), (True, True) )
        
#        print 'nonterminals\n%s' % g.nonterminals
#        print 'terminals\n%s' % g.terminals
        # check for all the rules
        # note that I use '\n' in the split statement rather than os.linesep
        # this is because the grammar_string uses triple quotes and 
        # the newlines weren't translated on windows
        ## note--I added parse action sets to the string representation,
        ## should be wrapped in brackets in column to the left of the rules, 
        ## with each pa set on the same line as the rule it goes with
        for g3line in gse3_grammar_string.strip().split('\n'):
            found = False
            for gline in gstring.split(os.linesep):
                if find_without_whitespace(gline, g3line):
                    found = True
                    break;
#            if not found:
#                print 'not found: gline = %s\ng3line = %s\n***' % (gline, g3line)
            self.assertEqual(found, True)
        
        
    def test_read_grammar_created_from_string_and_file_gse3(self):
        #g = self.parser.grammar
        gstring = \
"""
start_symbol = goal
terminals = [$id, +, *, (, ), #, %]
nonterminals = [goal, e, t, mt, f, mf]

rules:
"""

        gstring += gse3_grammar_string
        gfile = os.path.join(grammardir, 'gse3')
        for gsource in (gstring, gfile):
            g = pycompiler.parser.Grammar.create_grammar(gsource)
            self.assertEqual(g.start_symbol, 'goal')
            terms = ['$id', '+', '*', '(', ')', '#', '%']
            nonterms = ['goal', 'e', 't', 'mt', 'f', 'mf']
            ### note that with the expected rules here, we are also
            ## making sure that terminals are no longer wrapped with 's
            rules = [['goal', 'e'],
                     ['e', 't mt'],
                     ['mt', '+ t mt'],
                     ['mt', ''],
                     ['t', 'f mf'],
                     ['mf', '* f mf'],
                     ['mf', ''],
                     ['f', '$id'],
                     ['f', '( e )'] ]
            parse_actions = [
                     ['$id', '('],      
                     ['$id', '('],          
                     ['+'],                 
                     [')', '#'],
                     ['$id', '('],
                     ['*'],
                     ['+', ')', '#'],
                     ['$id'],
                     ['('],  ]
            self.assertEqual(have_equal_contents(g.terminals, terms),
                             True)
            self.assertEqual(have_equal_contents(g.nonterminals, nonterms),
                             True)
            self.assertEqual(g.pa, parse_actions)
            self.assertEqual(have_equal_contents(g.rules, rules),
                             True)
        
    def test_grammar_with_commas_uses_slash_escape_in_input_file_or_string(self):
        gstring = """Example grammar with commas
start_symbol = a
terminals = [ $x, (, ), \,, +]
nonterminals = [ a, t, mt, e ]

rules:                            parse_actions
a    -> t mt                { $x, ( }
mt    -> , t mt            { \, }
"""
        g = Grammar.create_grammar(gstring)
        terminals = g.terminals
        self.assertEqual( (',' in g.terminals), True)
        self.assertEqual( g.pa[1], [','])
        
        gstring = """Example grammar with commas
start_symbol = a
terminals = [ $x, (, ), +, \,, $id ]
nonterminals = [ a, t, mt, e ]

rules:                            parse_actions
a    -> t mt                { $x, ( }
mt    -> , t mt            { \,, +}
"""
        g = Grammar.create_grammar(gstring)
        terminals = g.terminals
        self.assertEqual( (',' in g.terminals), True)
        self.assertEqual( have_equal_contents(g.pa[1], [',', '+']), True)


class TestExecuteParser(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        tokfile_contents =\
"""$id

*

$id

+

$id


"""
        create_file('tokfile', tokfile_contents)        
        self.parser = pycompiler.parser.Parser()
        
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    # I did this to drive adding the is_parsing flag, however it would be 
    # to modify the parse() method to stop to see that the flag is set
    # to true, so I will abandon that effort
    def test_parsing_flag(self):
        self.assertEqual(self.parser.is_parsing, False)
        
        
        
    def test_step_by_step(self):
        # note for single cycle execution, we have to control next token
        self.parser.next_token()
        self.assertEqual(self.parser.current_token, make_token('$id'))
        self.parser.execute_one_cycle()
#        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'goal'] )) 
#        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'e'] ))
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 't'] ))
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', 'f'] ))
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', '$id'] ))
        
        ## now the terminal cases as well
        self.assertEqual(self.parser.current_token, make_token( '$id' ))
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', ] ))
        self.assertEqual(self.parser.current_token, make_token( '*' ))

        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', 'f', '*'] ))
        self.assertEqual(self.parser.current_token, make_token( '*' ))

        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', 'f',] ))
        self.assertEqual(self.parser.current_token, make_token( '$id' ))

        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', '$id'] ))
        self.assertEqual(self.parser.current_token, make_token( '$id' ))

        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf',] ))
        self.assertEqual(self.parser.current_token, make_token( '+' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt',] ))
        self.assertEqual(self.parser.current_token, make_token( '+' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 't', '+'] ))
        self.assertEqual(self.parser.current_token, make_token( '+' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 't',] ))
        self.assertEqual(self.parser.current_token, make_token( '$id' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', 'f', ] ))
        self.assertEqual(self.parser.current_token, make_token( '$id' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf', '$id'] ))
        self.assertEqual(self.parser.current_token, make_token( '$id' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', 'mf',] ))
        self.assertEqual(self.parser.current_token, make_token( '#' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', 'mt', ] ))
        self.assertEqual(self.parser.current_token, make_token( '#' ))
        
        self.parser.execute_one_cycle()
        self.assertEqual(self.parser.stack.data, make_token_seq( ['%', ] ))
        self.assertEqual(self.parser.current_token, make_token( '#' ))
        
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            self.parser.execute_one_cycle()
            #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
            self.assertNotEqual( sys.stdout.getvalue().find('accept'), -1 )
            
        finally:
            sys.stdout = old_stdout
        
        
    def test_execute_accept(self):
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            self.parser.parse()
            #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
            self.assertNotEqual( sys.stdout.getvalue().find('accept'), -1 )
            
        finally:
            sys.stdout = old_stdout


class TestUsingCustomParsers(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)    
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def create_custom_parser(self, tokfile_contents, outputfile=None): 
        """Create and return a parser using the string tokfile_contents to initialize
        the tokenfile with, and optionally specifying a path for outputfile to contain
        parser_pics."""
        create_file('tokfile', tokfile_contents)        
        p = pycompiler.parser.Parser('tokfile', outfile=outputfile)  
        return p
        
    def test_execute_reject(self):
        old_stdout = sys.stdout
        try:
            tokfile_contents =\
"""$id

*

$id

+

"""
            p = self.create_custom_parser(tokfile_contents)
        
            sys.stdout = StringIO.StringIO()
            p.parse()
            #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
            self.assertNotEqual( sys.stdout.getvalue().find('reject'), -1 )
            
        finally:
            sys.stdout = old_stdout
        
    def run_with_arbitrary_tokenfile(self, tokfile_or_contents):
        """Runs a test creating a parser whose token file either has the contents of the
        string param tokfile_or_contents or is the actual file with filename tokfile_or_contents.  
        Captures stdout and returns it as a string.
        """
        retval = ''
        old_stdout = sys.stdout
        try:
            if os.path.isfile(tokfile_or_contents):
                p = self.create_custom_parser(open(tokfile_or_contents).read()) 
            elif isinstance(tokfile_or_contents, str):
                p = self.create_custom_parser(tokfile_or_contents)
            sys.stdout = StringIO.StringIO()
            p.parse()
            #print >> sys.stderr, "sys.stdout.getvalue() = %s\n" % sys.stdout.getvalue()
            retval = sys.stdout.getvalue()
            #self.assertNotEqual( sys.stdout.getvalue().find(expected_out_substring), -1 )
            
        finally:
            sys.stdout = old_stdout
            return retval
    
    def test_accept_w_parens(self):
        tokfile_contents =\
"""$id

*

$id

+

(

$id

*

$id

)

"""
        result = self.run_with_arbitrary_tokenfile(tokfile_contents)
        self.assertNotEqual(result.find('accept'), -1)
    
        
    ## for each tokenfile in the tokenfiles dir in this dir (test/)
    ## run the test checking the results with 'accept' or 'reject' 
    ## at the end of each tokenfile's name
    def test_w_all_files_in_tokenfile_dir(self):
        tokfiledir = os.path.abspath('tokenfiles')
        tokdir_glob = tokfiledir + os.sep + 'tokfile*'
        for tokfile in glob.glob(tokdir_glob):
            result = self.run_with_arbitrary_tokenfile(tokfile)
            expected = tokfile.split('.')[-1]   
            self.assertNotEqual(result.find(expected), -1)
        
        
    def test_parser_construct_w_out_output_file(self):
        # passing no output file should mean that none is created and 
        # parser_pics are not output
        p = pycompiler.parser.Parser()
        self.assertEqual(p.outfile, None)
        
    
    def test_parser_output_file(self):
        tokfname = os.path.join(tokfiledir, 'tokfile1.accept')
        outfname = 'parserout.txt'
        p = pycompiler.parser.Parser(tokensource = tokfname,
                                     outfile = outfname)
        self.assert_(p.outfile)
        p.parse()
        self.assertEqual(p.outfile.closed, True)
        
    def test_parser_pic_output(self):
        tokfname = os.path.join(tokfiledir, 'tokfile.simple.accept')
        outfname = 'parserout.txt'
        p = pycompiler.parser.Parser(tokensource = tokfname,
                                     outfile = outfname)
        p.parse()
        parser_pic_lines = open(outfname).readlines()
#        print "parser_pic_lines:"
#        for line in parser_pic_lines:
#            if not line.isspace(): print line.strip()
            
        self.assert_(parser_pic_lines)
        
        stack_strings = ["goal     %",
                   "e     % ",
                   "t    mt     % ",
                   "f    mf    mt     %",
                   "$id    mf    mt     %",
                   "mf    mt     %",
                   "*     f    mf    mt     %",
                   "f    mf    mt     %" ,
                   "+     t    mt     %", 
                   "%"]
        found = False
        for sline in stack_strings:
            found = False
            for pline in parser_pic_lines:
                #print "sline: %s" % sline
                #print "pline: %s\n" % pline
                if find_without_whitespace(pline, sline): 
                    found = True
                    break
                
            self.assertEqual(found, True)
        
        
        rule_strings = ['goal -> e', 'e -> t mt', 't -> f mf', 
                        'f -> $id', 'mf -> * f mf', 'f -> $id', 
                        'mf ->', 'mt -> + t mt', 't -> f mf', 
                        'f -> $id', 'mf ->', 'mt ->']
        
        for rline in rule_strings:
            found = False
            for pline in parser_pic_lines:
                #self.assertEqual(find_without_whitespace(pline, rline), True)
                if find_without_whitespace(pline, rline): 
                    found = True
                    break
                
            self.assertEqual(found, True)
    

class TestPhraseProjectGrammar(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.outfile = os.path.join(tempdir, 'parserout_phrprojgramm')
        self.tokfile = os.path.join(tempdir, 'phraseproj_tokfile')
        grammar_string = open(os.path.join(grammardir, 
                                           'phrase_project_grammar')).read()
        self.g = Grammar.create_grammar(grammar_string)
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    
    def create_tokfile(self, tokstring):
        #tokstring = os.linesep.join(tokstring.split() )        
        open(self.tokfile, 'w').write(tokstring)
        
    def test_phrase_project_grammar(self):
        self.assertEqual(self.g.terminals, 
                         ['int', 'x', ';', '=', '+', '*', '(', ')', '#', '%'])  
        self.assertEqual( len(self.g.nonterminals), 10)
        self.assertEqual( len(self.g.rules), 15)
        self.assertEqual( self.g.pa, [['int', 'x', '#'], 
                                 ['int'], 
                                 ['x', '#'], 
                                 ['int'], 
                                 ['x'], 
                                 ['#'], 
                                 ['x'], 
                                 ['x', '('], 
                                 ['+'], 
                                 [')', ';'], 
                                 ['x', '('], 
                                 ['*'], 
                                 ['+', ')', ';'], 
                                 ['x'], 
                                 ['(']] )
#        print "Phrase Grammar"
#        print str(self.g)
        
    def test_phrase_proj_grammar_reject(self):
        tokstring = make_token_string("int x ; x = x + x * ( x + x )", self.g)
        self.create_tokfile(tokstring)
        p = Parser(tokensource=self.tokfile, 
                   #outfile=self.outfile, 
                   grammar=self.g)
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            p.parse()
            self.assertEqual( sys.stdout.getvalue().find('accept'), -1 )
            #print 'reject test: stdout =', sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

    def test_phrase_proj_grammar_accept(self):
        tokstring = make_token_string("int x ; x = x + x * ( x + x ) ;", self.g)
        #tokstring = "int x ; x = x + ( x + x ) ;"
        self.create_tokfile(tokstring)
        p = Parser(tokensource=self.tokfile, 
                   outfile=self.outfile, 
                   grammar=self.g)
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            p.parse()
            self.assertNotEqual( sys.stdout.getvalue().find('accept'), -1 )
            #print 'accept test: stdout =', sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
 
        str_out = open(self.outfile).read()
        self.assertEqual(str_out.find('reject'), -1)

# test the grammar for the assignment--semi-simple with unary op only at
# the front of expressions
class TestSemiSimpleAssignGrammar(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.outfile = os.path.join(tempdir, 'parserout_semi_simple')
        self.tokfile = os.path.join(tempdir, 'semi-simple_tokfile')
        grammar_string = open(os.path.join(grammardir, 
                                           'semi-simple_assign_g')).read()
        self.g = Grammar.create_grammar(grammar_string)
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    
    def create_tokfile(self, tokstring):
        #tokstring = os.linesep.join(tokstring.split() )        
        tokstring = make_token_string(tokstring, self.g)
        open(self.tokfile, 'w').write(tokstring)
        
        # testing Grammar.create_grammar() with string and file sources as well
    def test_semi_simple_assign_grammar(self):
        gfromfile = Grammar.create_grammar(os.path.join(grammardir, 'semi-simple_assign_g'))
        for g in (self.g, gfromfile):
            self.assertEqual(g.terminals, 
                             ['$int', '$id', '=', '+', '-', '*', '/',
                              '(', ')', '#', '%'])  
            self.assertEqual( len(g.nonterminals), 7)
            self.assertEqual( len(g.rules), 15)
            expected_pa = [['$id'],
                          ['$id', '$int','(', '-', '+'],
                          ['+'],
                          ['-'], 
                          [')', '#'],
                          ['$id', '$int', '('],          
                          ['*'],
                          ['/'],
                          ['+', '-', ')', '#'],
                          ['$id'],
                          ['$int'],
                          ['('],
                          ['-'],
                          ['+'], 
                          ['(', '$id', '$int']]
            #print 'real, expected:\n%s\n%s' % ( g.pa, expected_pa )
            self.assertEqual( g.pa, expected_pa )
        
    # expected == 'accept' or 'reject'
    def run_simple_assign_grammar_string(self, tokstring, expected):
        self.create_tokfile(tokstring)
        p = Parser(tokensource=self.tokfile, 
                   #outfile=self.outfile, 
                   grammar=self.g)
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            p.parse()
            self.assertNotEqual( sys.stdout.getvalue().find(expected), -1 )
            #print 'reject test: stdout =', sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
     
    def test_simple_assign_grammar_w_stringtoks(self):
        sentences = [('$id = - ( $id + $int ) / $id $id',
                      'reject'),
                     ('$id = - ( $id + $int ) / $id * $int - $id',
                      'accept'),
                     ('$id = - $id + $int / $id * $int - $id',
                      'accept'),
                     ('$id = + $id / ( $int / $id ) * $int - $id',
                       'accept'),  
                     ('$id = $int * $id / - $id  + $id * - $id',
                      'reject')
                     ]
        for (tokstring, expected) in sentences:
            self.run_simple_assign_grammar_string(tokstring, expected)
                     

class TestPlhGrammar(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.outfile = os.path.join(tempdir, 'parserout.plh')
        self.tokfile = os.path.join(tempdir, 'plh_tokfile')
        self.g = Grammar.create_grammar(os.path.join(grammardir, 'plh.g'))
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    
    def create_tokfile(self, tokstring):
        tokstring = make_token_string(tokstring, self.g)
        open(self.tokfile, 'w').write(tokstring)
        
            
    def test_grammar_parts(self):
#        pa = ['=', ';', ',', ')' , '+', '-', '*', '/', '<', '>']
#        index = self.g.rules.index(['subvar', ''])
#        #print 'index = ', index
#        rule = self.g.rules[index]
#        print 'rule %d) %s -> %s    pa = %s\n' % (index, rule[0], rule[1], str(self.g.pa[index]) )
        ## no empty parse actions
        for pa in self.g.pa:
            for x in pa:
                if not x: print 'empty member in pa:  %s' % pa
                self.assertEqual( not x or x.isspace(), False)
        for x in self.g.terminals + self.g.nonterminals:
                self.assertEqual( not x or x.isspace(), False)
        
        self.assertEqual( ',' in self.g.terminals, True)
    
    # expected == 'accept' or 'reject'
    def run_plh_grammar_string(self, tokstring, expected):
        self.create_tokfile(tokstring)
        p = Parser(tokensource=self.tokfile, 
                   outfile=self.outfile, 
                   grammar=self.g)
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            p.parse()
            self.assertNotEqual( sys.stdout.getvalue().find(expected), -1 )
            #print 'reject test: stdout =', sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
     
    def test_plh_w_stringtoks(self):
        print "PL/H Grammar:\n%s" % str(self.g)
        sentences = [
                     ('$id numsort =  $int 5 ; $id i = $int 1 ;',
                      'accept'),      
                     ('$declare $id x ( $int 5 ) ;', 'accept'), 
                     (':  $id in  :   $get  $id x  (  $id i  )  ;  $id i  =  $id i  +  $int 1  ;',
                      'accept'),
                      ('$if $id i < = $id numtosort $then $goto $id in ;', 'accept'),
                      ('$if $id i < = $id numtosort * $id x $then $goto $id in ;', 
                       'accept'),
                     ('$if $id i < = $id numtosort * $int 2 $then $goto $id in ;', 
                       'accept'),
                     ('$if $id i < = $id numtosort + $int 2 $then $goto $id in ;', 
                     'accept'),
                     ('$if $id i = $id numtosort + $int 2 $then $goto $id in ;', 
                     'accept'),
                     ('$if $id x ( $int 2 ) = - ( $id numtosort / $int 2 ) $then $id y = $id x ;', 
                     'accept'),
                     ('', 'accept'),
                     ('$declare $id y ( $int 365 ) , $id x ( $int 10 ) ; $id x ( $id i ) = $int 5 ;',
                      'accept'),
                     ('$id y = $int 6 ; $put $id x ( $id numtosort ) ; $stop ;',
                      'accept'),
                     ('$id y = $int 6 ; $put $id x ( $id numtosort ) , $id y ;',
                      'accept'),
                     ('$id y = $int 6 ; $put $id x ( $id numtosort ) , $id y , $int 5 * $id y ;',
                      'accept'),
                     ]
        for (tokstring, expected) in sentences:
            print 'tokstring:\n%s\n' % tokstring
            self.run_plh_grammar_string(tokstring, expected)
                     

    def test_plh_w_selection_sort_tokfile(self):
        tokfile = os.path.join(tokfiledir, 'selection_sort_tokfile')
        outfile = os.path.join(tempdir, 'parserout_plh_sel_sort')
        p = Parser(tokensource=tokfile, 
                   outfile=outfile, 
                   grammar=self.g)
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO.StringIO()
            p.parse()
            self.assertNotEqual( sys.stdout.getvalue().find('accept'), -1 )
            #print 'reject test: stdout =', sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
     

class TestParserWorksWithTokenStringAndNextTokenHandlesSubclasses(unittest.TestCase):
    ## a bit late in the game, but I thinkg we can set it up so the base class 
    ## handles token strings or files, and next_token doesn't need to be overridden 
    ## need to test all grammars
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.grammars = {
            "gse3": {'name': 'GSE3 Grammar', 
                     'grammar': Grammar.get_gse3(), 
                      'tokstring': '$id * $id * ( $id + $id )'},
            'phrases': {'name': "Phrases Project Grammar", 
                        'grammar': Grammar.create_grammar(open(
                os.path.join(grammardir, 'phrase_project_grammar')).read()),
                        'tokstring': 'int x ; x = x * ( x + x ) ;'},
            'semi_simple': {'name': "Semi-Simple Assignments Grammar", 
                            'grammar': Grammar.create_grammar(
            open(os.path.join(grammardir, 'semi-simple_assign_g')).read()),
                        'tokstring': '$id = - $id * ( - $id - $int ) / $id + $int'},
                       'plh': {'name': "PL/H Grammar Without Translation Symbols", 
                            'grammar': Grammar.create_grammar(
            open(os.path.join(grammardir, 'plh.g')).read()),
                'tokstring': '$if $id i < = $id numtosort + $int 2 $then $goto $id in ;'},
                        
                          }    
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_run_all_with_tokstrings(self):
        for g in self.grammars:
            print g
            print self.grammars[g]['tokstring']
            p = Parser(tokensource=self.grammars[g]['tokstring'],
                           grammar=self.grammars[g]['grammar'])
            old_stdout = sys.stdout
            try:
                sys.stdout = StringIO.StringIO()
                p.parse()
                self.assertNotEqual( sys.stdout.getvalue().find('accept'), -1 )
                #print 'reject test: stdout =', sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
 

        
if __name__ == '__main__':
    unittest.main()
    
    