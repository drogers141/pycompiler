#!/usr/bin/env python
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

"""A Tkinter gui that displays parse trees.  Uses Mark Lutz's treeview_wrappers module, subclassing
for our grammar application.  See treeview_wrappers.py
"""
__all__ = ['Node', 'ParseTreeBuilder']

import sys, os
parent_dir = os.path.abspath( os.path.join(__file__, '../..') )
if not parent_dir in sys.path:
    sys.path.append(parent_dir)

from pycompiler.globals import *    
from pycompiler.parser import *
from pycompiler.util import *
from pycompiler.translator import *

class Node:
    """Basic node.  name == '', value == '', children == [] if not initialized.
    Give only terminals a value, for the get_phrase method."""
    def __init__(self, name='', value=''):
        self.name = name
        self.value = value
        self.children = []
    
    def __str__(self):
        """String representation is the node's name if value = '', otherwise a tuple (name, value)."""
        if self.value: return '(%s, %s)' % (self.name, self.value)
        return self.name
    
    def add_child(self, child_node):
        self.children.append(child_node)
    
    def get_phrase(self, delim='  ', grammar=None):
        """Returns the string rep of this node and all of its children, separated by delim.  
        If grammar provided, does not include nonterminals with no children (ie empty).
        """        
        result = ''
        if self.children: 
            for child in self.children:
                result += child.get_phrase(delim, grammar) + delim
        else:
            if grammar:
                if self.name in grammar.terminals: result += str(self)  
            else: result += str(self)          
        return result.strip()
    
    def get_phrases_for(self, nonterminal, phrases, delim, grammar=None):
        """Recursively searches for all occurrences of param nonterminal in this nodes 
        subtree, using delimiter delim to separate tokens in the phrases, and appends
        the results to phrases.  
        """
        phrase = ''
        if self.name == nonterminal: 
            phrase = self.get_phrase(delim, grammar)
            if phrase:
                phrases.append(phrase)
        if self.children:
            for child in self.children:
                child.get_phrases_for(nonterminal, phrases, delim, grammar)
        #print self.name, 'phrase was', phrase, 'returning', phrases
        #return phrases[:] 
    
class ParseTreeBuilder(Parser):
    def __init__(self, **kwargs):
        Parser.__init__(self, **kwargs)
        ## tree stack holds nodes that mirror the parser's stack, but
        #  no '%'
        self.tree_stack = Stack()
        ## same init as in Parser, though this should be fixed
        ## as we don't need it, but for now
        self.tree = Node(name=self.grammar.start_symbol)
        self.tree_stack.push(self.tree)
        ## parsetree can handle a grammar or translation scheme
        ## set flag to true for ts
        self.grammar_is_ts = isinstance(self.grammar, TransScheme)
        
        
    def create_tree(self):
        """Create and return parse tree based on our grammar and tokenfile.
        Returns None if parser rejects input."""
        self.parse()
        return self.tree
        
    def parse(self):
        """Run the parser."""
        self.is_parsing = True
        #self.tree = Node()
        self.next_token()
        
        while self.is_parsing:
            self.execute_one_cycle()        
        
    def execute_one_cycle(self):
        """Execute one cycle of the parser. If the parser rejects the input, the tree is
        set to none."""
        stack = self.stack
        tree_stack = self.tree_stack
        grammar = self.grammar
        current_token = self.current_token
        top = stack.top()['name']        
        if top in grammar.nonterminals:
            n = grammar.parse_action(top, current_token['name'])
            if n == -1:
                self.tree = None
                self.is_parsing = False
            else:
                #rulestr = "rule %s:   %s" % (n, ' -> '.join( grammar.rules[n]) )
                #write_to(rulestr, self.outfile)                
                stack.pop()
                right_side_parts =  [{'name': name, 'value': ''} 
                                  for name in grammar.rules[n][1].strip().split()]  
                stack.multipush(right_side_parts)
                
                ## for any level in a parse tree/subtree
                ## we want the tree_stack to read in reverse as with the other stack
                ## but the children list should read forward (ie left to right)
                top_node = tree_stack.pop()
                for tok in right_side_parts: 
                    child = Node(tok['name'], tok['value'])
                    top_node.add_child(child)
                tree_stack.multipush(top_node.children)
                
        elif top in grammar.terminals:
            if top == current_token['name']:
                tok = stack.pop()
                node = tree_stack.pop()
                # check for value in node at this point
                if current_token['value']:
                    node.value = current_token['value']
                self.next_token()                
           
            elif current_token['name'] == '#' and top == '%':
                self.is_parsing = False
            else:
                self.is_parsing = False
                
        elif self.grammar_is_ts and top in grammar.action_symbols:
            # if it's an action symbol, we want it displayed, but nothing else
            # it should already be a child of the nonterminal on the left hand side
            # of the rule that generated it
            stack.pop()
            tree_stack.pop()
                
                   
    @staticmethod
    def get_phrases_for(nonterminal, root, delim = ' ', grammar=None):
        """Returns a list of all phrases for param nonterminal in the parse tree or subtree
        rooted at param root, using delimiter delim to separate tokens in the phrases. 
        """
        phrases = []
        root.get_phrases_for(nonterminal, phrases, delim, grammar)
        return phrases

if __name__ == '__main__':
#    g = Grammar.create_grammar( os.path.join(grammardir, 'plh.g') )
#    tokstring = '$if $id i < = $id numtosort + $int 2 $then $goto $id in ;'       
#    treebuilder = ParseTreeBuilder(tokensource=tokstring,
#                                   grammar=g)
#    tree = treebuilder.create_tree()
#    result = tree.get_phrase(' ', g)
#    print 'test_get_phrases_for: \ntokstring:  %s\nresult:  %s' % (tokstring, result)
#    sys.exit()
    
    grammar_files = {'1': 'phrase_project_grammar',
                     '2': 'semi-simple_assign_g',
                     '3': 'gse3',
                     '4': 'plh.g', }
    if len(sys.argv) == 1:
        avail = ''
        for key in sorted(grammar_files): avail += "%s) %s\n" % (key, grammar_files[key])
        gfile = raw_input('Grammars:\n%s\nSelect grammar--> ' % (avail))
        tokstring = raw_input('Enter tokenstring--> ')
    else:
        print "use interactively"
    
    grammar_file = os.path.join(grammardir, grammar_files[gfile])    
    g = Grammar.create_grammar(grammar_file)
    treebuilder = ParseTreeBuilder(tokensource = tokstring,
                                   grammar = g)
    root = treebuilder.create_tree()
    if root:
        while True:
            nonterm = raw_input('Enter nonterminal or q--> ')
            if nonterm == 'q': break
            phrase_list = ParseTreeBuilder.get_phrases_for(nonterm, root, ' ', g)  
            print "Token string = %s" % tokstring
            print "Phrases for %s:" % nonterm
            for phrase in phrase_list:
                print phrase
    else:
        print 'invalid token string:\n%s' % tokstring
    
        
    