#!/usr/bin/env  python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

"""A translator based on the LL(1) parser.  See parser.py
"""
import sys, os
parent_dir = os.path.abspath( os.path.join(__file__, '../..') )
if not parent_dir in sys.path:
    sys.path.append(parent_dir)
__all__ = ['TransScheme', 'PlhTranslator']

from globals import *
from util import *
#from parser import *
from pycompiler.parser import *

class  TransScheme(Grammar):
    """Translation scheme subclassed from Grammar, a TransScheme has action_symbols
    in addition to the grammar attributes.
    """
    def __init__(self, **kwargs):
        self.action_symbols = []
        if 'action_symbols' in kwargs:
            self.action_symbols = kwargs.pop('action_symbols') 
        Grammar.__init__(self, **kwargs)
    
    def __str__(self):
        """Adds action_symbols to Grammar's string representation."""
        lines = Grammar.__str__(self).splitlines(True)
        i = 0
        for line in lines:
            i += 1
            if line.startswith('Terminals:'): break
        s = 'Action Symbols:     %s%s' % ( make_seq_string(self.action_symbols), 2*os.linesep )
        lines.insert(i, s)
        return ''.join(lines)
        
    @staticmethod
    def create_ts(string_or_file):
        """Create a translation scheme from the string or file source."""
        g = Grammar.create_grammar(string_or_file)
        ts = TransScheme(terminals=g.terminals, nonterminals=g.nonterminals,
                         rules=g.rules, parse_actions=g.pa, 
                         start_symbol=g.start_symbol)
        ts_string = string_or_file
        if os.path.exists(string_or_file):
            ts_string = open(string_or_file).read()
        for line in ts_string.splitlines():
            if line.find('action_symbols') != -1:
                rside = line.split('=', 1)[1].strip().replace("'", "")                
                rside = [s.strip() for s in rside[1:-1].split(',')]
                ts.action_symbols = [s for s in rside[:] if s]
                break
        return ts
    
    
class  PlhTranslator(Parser):
    """Translator for the PL/H Language used in Prof. Jim Daley's CS4110 class.
    Produces code using a plh translation scheme that will run on the pycompiler vm. 
    This translator understands action_symbols in the PL/H Translation Scheme.  They
    all start with @ and have no whitespace.  See the actions dictionary for what
    actions are taken based on the symbol.
    """
    def __init__(self, codefile = 'codefile',
                 datafile = 'datafile',
                 **kwargs):
        ## codefile and datafile are written out by the translator after parsing
        self.codefile, self.datafile = codefile, datafile
        kwargs['grammar'] = TransScheme.create_ts(os.path.join(grammardir, 'plh.ts'))
        Parser.__init__(self, **kwargs)
        
        # the symbol table, a dictionary keyed by identifier name 
        # to a nested dictionary holding the address, type of var, length, and possibly more
        # structure:
        # {'name':  {'address': index, where data[index]='name', 
        #              'type': 'intvar'|'array'|'label',
        #              'size': (number of memory spaces allocated--for arrays, etc)},
        #           }
        self.symbols = {}
        # dictionary of actions keyed to action symbols they handle
        self.actions = self.get_actions()
        # to facilitate memory in the actions independent of the parsing stack
        self.actions_stack = Stack()
        # holds the value of the last token that was parsed
        self.last_token_val = None
        # make sure code and data arrays (lists) start at index 1
        self.code = [None]
        self.data = [None]
        
    def emit(self, elem):
        """Append elem to code.  Not type specific."""
        self.code.append(elem)
        write_to('(%s appended to code array)\n' % str(elem),self.outfile)
    
    def lookup_or_add(self, name, **kwargs):
        """Look up identifier by name in the symbol table.  If not found, insert
        into the symbol table.  
        @param kwargs: adds to the dictionary keyed to the name in the symbol table. 
        eg type='intvar', or for arrays, type='array', size=5, see comments in constructor
        @return: the dictionary keyed to name in the symbol table
        """
        if not name in self.symbols:
            ## naive memory storage--just append a null value to the list
            ## and give that as the address for simple variables,
            ## with the type default type 'intvar'
            ## for arrays (or other sequences), append the size of the array
            ## the type will be changed by the update() if in **kwargs
            self.data.append(None)
            entry = {'address': len(self.data)-1,
                     'type': 'intvar'}
            ## add size - 1 memory cells for non simple var.
            if 'size' in kwargs: 
                size = kwargs['size'] - 1
                for i in range(size):
                    self.data.append(None)
            # add other keys in entry
            entry.update(**kwargs)
            # add entry to symbol table
            self.symbols.update( {name: entry } )
            
        return self.symbols[name]
    
    def parse(self):
        """Run the translator and write code and memory to codefile and datafile."""     
        Parser.parse(self) 
        for (l, f) in [(self.code[1:], self.codefile),
                       (self.data[1:], self.datafile)]:  
            if l: open(f, 'w').write("\n".join( [str(elem) for elem in l] ))
        
    def execute_one_cycle(self):
        """Execute one cycle of the translator."""
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
                self.last_token_val = self.current_token['value']
                self.next_token()                
                write_to(matchstr, self.outfile)

            elif current_token['name'] == '#' and top == '%':
                write_to('accept', sys.stdout, self.outfile)
                self.is_parsing = False
            else:
                write_to('reject', sys.stdout, self.outfile)
                self.is_parsing = False
        elif top in grammar.action_symbols:
            exec self.actions[top]
            stack.pop()
            
        if self.is_parsing:
            stackstr = "stack:    %s\n" % token_stack_str(stack=self.stack, reverse=True)
            tokstr =  "token:    %s      value:  %s\n" % (self.current_token['name'],
                                                      self.current_token['value'])
            write_to(stackstr + tokstr, self.outfile)
 
    def symbol_table_str(self):
        """Returns string version of the symbol table."""
        max_key_len = max([len(k) for k in self.symbols])
        symtable_str = '\n'.join( ['%*s = %s' % (max_key_len, key,self.symbols[key]) 
                                   for key in self.symbols])
        return symtable_str
        
    def get_actions(self):
        """Returns the set of executable actions for the action symbols this translator
        understands.
        """
        # for actions not commented, the action emits an op in the instruction set
        # to the code array, for questions see the instruction set in the vm
        actions = {
'@quit': "self.emit('quit')",
'@lit': "self.emit('lit')",

# emit the value of the last token parsed to the code array
'@last_token_val': "self.emit(self.last_token_val)",

# emit the address of the last token value to the code array
# if it's not in the symbol table, add it and return the address
'@address_last_token_val': 'self.emit( self.lookup_or_add(self.last_token_val)["address"] )',

## storage
'@ldi': "self.emit('ldi')",
'@sti': "self.emit('sti')",

# arithmetic
'@add': "self.emit('add')",
'@mult': "self.emit('mult')",
'@sub': "self.emit('sub')",
'@div': "self.emit('div')",
'@neg': "self.emit('neg')",

# io
'@out': "self.emit('out')",
'@in': "self.emit('in')",

# relational
'@lt': "self.emit('lt')",
'@gt': "self.emit('gt')",
'@eq': "self.emit('eq')",
'@le': "self.emit('le')",
'@ge': "self.emit('ge')",
'@ne': "self.emit('ne')",

# goto action puts the label (last token value) in the symbol table with type='label'
# and emits branching code using the address
'@goto': """name = self.last_token_val
address = self.lookup_or_add(name=name, type='label')['address']
for line in ['lit', address, 'ldi', 'br']: self.emit(line)""",

# for now, a label is stored as a symbol in the symbol table, with 'type'='label'
# however all identifiers still have to be unique as they are keyed by name, but this could change
# the label action stores the index of the next line of code in the address
# of the last token value, note that since our code array is a python list, it's length
# is all we need, but watch out if implementation is changed
'@label': """goto_line = len(self.code)
label_address = self.lookup_or_add(self.last_token_val, type='label')['address']
self.data[label_address] = goto_line
write_to("(label  '%s':  set value of data[%d] to %d)%s" % (self.last_token_val, 
                                            label_address, goto_line, os.linesep), self.outfile)""",

# use the actions stack for storage
# push pushes the last token value on the actions_stack
'@push': """self.actions_stack.push(self.last_token_val)""",
# pop pops the action_stack and pushes the result on the parse stack
#'@pop': """token_val = self.actions_stack.pop()
#self.stack.push(token_val)""",


# declare an array--the declare action comes after 'lit' and the token's value
# have been emitted, when we get the size, which is in last token val currently 
# well, actually, for PL/H the size is one more than it -- declare x(5) -> size(x) == 6
'@declare': """size = self.last_token_val + 1
name = self.actions_stack.pop()
self.lookup_or_add(name=name, size=size, type='array')""",

# if then construct
# we have a @begin_if that pushes the code address needing to be filled with the address
# to branch to if the condition is false onto the actions_stack, while a placeholder string '?if?'
# is placed in the code, for debugging, etc
'@begin_if': """self.emit('lit')
self.emit('?if?')
if_line = len(self.code)-1
self.actions_stack.push({'type':'if', 'code_line': if_line})
self.emit('brf')""",

# the @end_if action pops the action stack and puts the code address of the next
# statement into the code_line stored on the stack in the 'if' address dict
'@end_if': """ifdict = self.actions_stack.pop()
assert ifdict['type'] == 'if', '@endif action, popped action stack, got %s' % ifdict
## this is the address of the next line in code, not current** check it
self.code[ifdict['code_line']] = len(self.code)""",
 

                   }        
        return actions
    