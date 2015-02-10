#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

"""An LL(1) parser implementation in python.
"""
import sys, os
parent_dir = os.path.abspath( os.path.join(__file__, '../..') )
if not parent_dir in sys.path:
    sys.path.append(parent_dir)

__all__ = ['Grammar', 'Parser']

from globals import *
from util import *

class Grammar:
    """A data structure that holds a CFG.  The terminals and nonterminals are lists.
    The rules are encoded as a list of lists, with each sublist having 2 elements:
    rules[0][0] = the first rule, right side
    rules[0][1] = the first rule, left side
    It is defined this way so that the parse actions are a list of lists whose indices
    match the rules they apply to.
    """
    def __init__(self, terminals, nonterminals,
                 rules, parse_actions, start_symbol):
        self.terminals = terminals[:]
        self.nonterminals = nonterminals[:]
        self.rules = rules[:]
        ## pa is the parse actions, didn't want to get confused with 
        ## the method name
        self.pa = parse_actions[:]
        self.start_symbol = start_symbol
        
    def __str__(self):
        """String representation shows the grammar's start symbol, terminals, nonterminals,
        rules, and parse sets if they exist.
        """
        line, nl = '', os.linesep
        gstring = 'Start Symbol:  %s%s' % (self.start_symbol, nl)
        gstring += 'Nonterminals:  %s%s' % ( make_seq_string(self.nonterminals), nl)
        gstring += 'Terminals:     %s%s' % ( make_seq_string(self.terminals), nl)
        # string width of longest rule, left side and total, and where the parse actions start
        left_len, rule_len, pa_start = 0, 0, 0       
        for rule in self.rules:
            left_len = max(left_len, len(rule[0]))
            rule_len = max(rule_len, left_len + 4 + 4 + len(rule[1])) # 4,4=len('1)  '),(' -> ') e.g.
        pa_start = rule_len + 4
        pa_str = 'Parse Actions:' if self.pa else ''
        gstring += '%-*s%s%s' % (pa_start, "Rules:", pa_str, nl)            
        for i in range( len(self.rules) ):
            rule_part = "%d) %*s -> %s" % (i, left_len, self.rules[i][0], self.rules[i][1])
            line = rule_part
            if self.pa:
                line = "%-*s%s" % (pa_start, rule_part, 
                                   make_seq_string(self.pa[i], '{}'))
            gstring += line + nl
        return gstring
        
    def parse_action(self, stack_top, next_token):
        """Returns the index of the rule that works given the nonterminal on top
        of the stack and the next token of input.  
        If no rule applies, then returns -1.
        @param stack_top: string value -- ie the name of the top token in stack
        @param param: string value as well
        """
        index = -1
        for i in range( len(self.pa) ):
            if next_token in self.pa[i]:
                if self.rules[i][0] == stack_top: 
                    index = i
                    break
        return index
            
    @staticmethod
    def get_gse3():
        """Returns a gse3 grammar from cs4110.  Note that I am modifying it
        to add a parse action for the 0th rule:  goal -> e
        And note that the end of token input marker, '#', 
        and the bottom of stack marker, '%', are also terminals.
        """
        t = ['$id', '*', '+', '(', ')', '#', '%']
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
        pa = [['$id', '('], #### added as noted above
                 ['$id', '('], 
                 ['+'],
                 [')', '#'],
                 ['$id', '('],
                 ['*'],
                 ['+', ')', '#'],
                 ['$id'],
                 ['('],  ]
        start = 'goal'
        g = Grammar(terminals = t, nonterminals = nt,
                    rules = r, parse_actions = pa,
                    start_symbol = start)
        return g
    
    @staticmethod
    def create_grammar(string_or_file):
        """Creates a grammar from a string or a file. 
        Use the following format:
        Start with member = value for start_symbol, terminals, nonterminals, each on 
        a line--using brackets for terms, and nonterms.  Then after the line 'rules:' 
        have the rules in string form, one to a line, with the parse action set for that 
        rule to the left on the line, wrapped in brackets, if applicable.  Example follows.
        
        start_symbol = goal
        terminals = [term1, term2, ..]
        nonterminals = [ nonterm1, nonterm2, ..]
                
        rules:                                
        goal -> nonterm nonterm ..           { term, term }
        nonterm -> term nonterm ..            { term, .. }
        
        Don't use quotes for the key = value lines--eg with terminals.  Single quotes can 
        be used in the rules, but prefer not to use them.  They will be removed anyway.  
        Escape characters with a backslash, ie to put a comma in the grammar use [ +, -, \, ...]. 
        For now--only can handle escaping a single character.
        
        """
        grammar_string = string_or_file
        if os.path.exists(string_or_file):
            grammar_string = open(string_or_file).read()
            
        escape_char = '\\'
        def getescaped(string, seq):   # start with case where only one escaped char is expected 
            tok = string.split(escape_char)[1][0]
            seq.append(tok)
            return string.replace(escape_char + tok, '')
        kwargs = {'start_symbol': '', 'terminals': [], 'nonterminals': [],
                  'rules': [], 'parse_actions': []}
        i = -1
        lines = grammar_string.splitlines()
        for line in lines:                  ## parse everything but rules and parse sets
            i += 1
            if not line or line.isspace(): continue
            if line.find('=') != -1:
                parts = line.split('=', 1)
                lside, rside = parts[0].strip(), parts[1].strip().replace("'", "")
                if lside in ('terminals', 'nonterminals'):
                    temp = []
                    if rside.find(escape_char) != -1: rside = getescaped(rside, temp)
                    rside = [s.strip() for s in rside[1:-1].split(',')] + temp
                    rside = [s for s in rside[:] if s]
                #print "rside = ", rside, "type(rside) = ", type(rside)
                if lside in kwargs.keys(): kwargs[lside] = rside
                
            elif line.find('rules') != -1: 
                rules_strings = lines[i+1:]
                break   
            
        for line in rules_strings:                      ## handle rules and parse sets
            if not line or line.isspace(): continue
            if line.find('->') != -1:
                parts = line.split('->')
                rule = [parts[0].strip()]
                parts = parts[1].replace("'", "").split('{')
                rule.append(parts[0].strip())
                kwargs['rules'].append(rule)
                if len(parts) > 1:        # parse actions
                    temp = []; rem = parts[1]
                    if rem.find(escape_char) != -1: rem = getescaped(rem, temp)
                    remparts = [s.strip() for s in rem.strip()[:-1].split(',')]
                    kwargs['parse_actions'].append(
                        [s for s in remparts if s ] + temp)
            
        g = Grammar(**kwargs)
        return g
        

class Parser:
    """LL(1) parser implementation."""
    def __init__(self, tokensource = 'tokfile',
                 outfile = None,                 
                 grammar = None):
        """@param tokensource: string or file, whitespace delimited, source of tokens
        to parse
        @param outfile: pics of the parser internals will be written to it if it exists
        @param grammar: the grammar required to parse the input, not a translation scheme
        """
        self.token_index = 0
        self.token_list = []
        if os.path.exists(tokensource):
            self.token_list = open(tokensource).read().split()
        else:
            self.token_list = tokensource.strip().split()
        # self.outfile will capture snapshots of the parser executing
        # if it exists, 'accept' and 'reject' will go to stdout as well
        self.outfile = None
        if outfile: self.outfile = open(outfile, 'w')
            
        # if a grammar is not passed, set the default to gse3
        self.grammar = grammar
        if not self.grammar:
            self.grammar = Grammar.get_gse3()
        self.stack = Stack()
        self.stack.multipush([{'name': self.grammar.start_symbol, 'value': ''}, 
                              {'name': '%', 'value':''}]) 
        self.code = []
        self.data = []
        self.pc = 0
        
        # note that tokens are a dictionary with keys 'name' and 'value'
        # the front token of input, advanced by self.next_token()
        self.current_token = None
        
        self.is_parsing = False
        # column width for aligning output
        #self.colwidth = 10
    
        
    def parse(self):
        """Run the parser."""
        self.is_parsing = True
        self.next_token()
        
        begstr = "Beginning Parse:\n\nstack:    %s\n" % token_stack_str(stack=self.stack, reverse=True)
        tokstr =  "token:    %s      value:  %s\n" % (self.current_token['name'],
                                                      self.current_token['value'])
        write_to(begstr + tokstr, self.outfile)
        
        while self.is_parsing:
            self.execute_one_cycle()        
        if self.outfile:  self.outfile.close()
    
    def execute_one_cycle(self):
        """Execute one cycle of the parser."""
        stack = self.stack
        grammar = self.grammar
        current_token = self.current_token
        top = stack.top()['name']        
        if top in grammar.nonterminals:
            n = grammar.parse_action(top, current_token['name'])
            if n == -1:
                write_to('reject', sys.stdout, self.outfile)
                self.is_parsing = False
            else:
                rulestr = "rule %s:   %s" % (n, ' -> '.join( grammar.rules[n]) )
                write_to(rulestr, self.outfile)                
                stack.pop()
                stack.multipush( [{'name': name, 'value': ''} 
                                  for name in grammar.rules[n][1].strip().split()] )
                
        elif top in grammar.terminals:
            if top == current_token['name']:
                matchstr = "matching: %s" % top               
                stack.pop()
                self.next_token()                
                write_to(matchstr, self.outfile)

            elif current_token['name'] == '#' and top == '%':
                write_to('accept', sys.stdout, self.outfile)
                self.is_parsing = False
            else:
                write_to('reject', sys.stdout, self.outfile)
                self.is_parsing = False
        if self.is_parsing:
            stackstr = "stack:    %s\n" % token_stack_str(stack=self.stack, reverse=True)
            tokstr =  "token:    %s      value:  %s\n" % (self.current_token['name'],
                                                      self.current_token['value'])
            write_to(stackstr + tokstr, self.outfile)
        
    def next_token(self):
        """Puts the next token from the input stream into self.current_token--or token with name '#'
        on EOF .  Sets it to None on any further calls after EOF."""
        vocab = self.grammar.terminals + self.grammar.nonterminals
        try:
            name = None
            if self.token_list: name = self.token_list[self.token_index].strip()
            if not name and not self.token_list:
                raise IndexError()    
            if name in vocab:
                self.current_token = {'name': name, 'value': ''}
            else:
                msg = 'Parser.next_token():  problem with token, name=%s ' % name
                raise ValueError(msg)
            try:
                self.token_index += 1
                value = convert_from_str( self.token_list[self.token_index].strip() )                      
                if not value in vocab: 
                    self.current_token['value'] = value
                    self.token_index += 1
            except IndexError:
                return
        except IndexError:
            if self.current_token == {'name':'#','value': ''}:
                self.current_token = None
            else:
                self.current_token = {'name':'#','value': ''}
                
           
if __name__ == '__main__':   
    default_tokfile = os.path.join(tokfiledir, 'tokfile1.accept') 
    import optparse
    op = optparse.OptionParser(description= \
"""Run the LL(1) parser on the default or a specified tokenfile, producing an output file
of the parser's states during the parse.  Outputs 'accept' or 'reject' to stdout as well.
Default grammar is GSE3.  Specify any alternate grammar file.
""")
    op.add_option('-t', '--tokenfile', dest='tfile', default=default_tokfile,
                  help='read tokens from FILE [default: %default]',
                  metavar='FILE')
    op.add_option('-o', '--outfile', dest='ofile', default='parserout.txt',
                  help='write captured output to FILE [default: %default]',
                  metavar='FILE')
    op.add_option('-g', '--grammarfile', dest='gfile',
                  help='read grammar from FILE [default: GSE3 grammar]',
                  metavar='FILE')
    (opts, args) = op.parse_args()
    grammar = Grammar.create_grammar(opts.gfile) if opts.gfile else Grammar.get_gse3()
    p = Parser(tokensource=opts.tfile, outfile=opts.ofile, grammar=grammar)
    p.parse()
    
    