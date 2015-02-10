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
__all__ = ['ParseTreeWrapper', 'ParseTreeViewer']

import os, sys
## note that this path manipulation is necessary for the command line
## usage, but I should come up with a cleaner way to do this
## the deal is that pydev always adds the src/ dir to the pythonpath
## and relative imports go from that
parent_dir = os.path.abspath( os.path.join(__file__, '../..') )
if not parent_dir in sys.path:
    sys.path.append(parent_dir)
#print parent_dir

from Tkinter import *
from tkMessageBox import showwarning

from treeview_wrappers import TreeViewer, TreeWrapper
from parsetree import *
from pycompiler.parser import *
from pycompiler.util import *
from pycompiler.globals import *
from pycompiler.translator import *
import pycompiler


class ParseTreeWrapper(TreeWrapper):
    """Implementation of Lutz's TreeWrapper interface to use the TreeViewer gui
    for viewing a basic cfg parse tree.
    """
    def __init__(self, treebuilder = None):
        self.treebuilder = treebuilder        
                
    def children(self, node):
        try:
            return node.children
        except:
            return None
    
    def label(self, node):
        return str(node)
#        if not node.value: return node.name
#        else: return '(%s, %s)' % (node.name, node.value)
    
    def onClick(self, node):
        if not self.treebuilder: 
            return 'self.treebuilder is not set, so I have no grammar to show a phrase with'
        result = ""
        try:
            result = "Phrase:  " + node.get_phrase(' ', self.treebuilder.grammar)
        except:
            result = "Error evaluating node."
        return result
        
    def onInputLine(self, line, viewer):            # on input line
        cool = False
        if line:
            cool = viewer.redrawTree(line)
        if not cool:
            showwarning('PyTree', 'Parse tree input was uncool..')


class ParseTreeViewer(TreeViewer):
    def __init__(self, parent=None, show_grammar='plh'):
        TreeViewer.__init__(self, ParseTreeWrapper(), parent)
        # the grammars available by menu, a dictionary of dictionaries
        # short name of the grammar = { name: long name of grammar, 
        #   grammar: Grammar instance, tokstring: tokenstring to open with }
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
                        'plh_ts': {'name': "PL/H Translation Scheme", 
                            'grammar': TransScheme.create_ts(
                                        open(os.path.join(grammardir, 'plh.ts')).read()),
                'tokstring': '''$id numtosort = $int 5 ; $goto $id in ; $id numtosort = $int 1 ; 
                                : $id in : $id x = $int 32 ;'''},
                          }
        self.current_grammar = self.grammars[show_grammar] 
        
        Label(self.master, text=' Enter Sentence In Grammar: ').pack(side=LEFT)
        self.entry = Entry(self.master, bg='white')
        self.entry.pack(side=LEFT, expand=YES, fill=X)
        self.entry.bind('<Return>', lambda event: self.onInputLine())   # button or enter key
        Button(self.master, text=' Input ', 
               command=self.onInputLine).pack(side=RIGHT)
        self.__init_grammar()
        self.make_menu()
        
    def __init_grammar(self):   
        g, tokstr =  self.current_grammar['grammar'], self.current_grammar['tokstring']
        self.treebuilder = ParseTreeBuilder(grammar=g, tokensource=tokstr)
        self.wrapper.treebuilder = self.treebuilder
        self.entry.delete(0, END)
        self.entry.insert(0, tokstr)
        self.drawTree()
        
    
    def onInputLine(self):
        line = self.entry.get()        
        TreeViewer.onInputLine(self, line)        # type a node list or expression

    def redrawTree(self, tokstring):
        """Redraw the tree from new input tokenstring. Returns False if tokstring rejected,
        True if successful."""
        g = self.treebuilder.grammar
        self.treebuilder = ParseTreeBuilder(grammar=g, 
                                   tokensource = tokstring)
        return self.drawTree()
    
    def drawTree(self):
        """Overridden--this one returns true if valid tree is created, False otherwise."""
        tree = self.treebuilder.create_tree()
        if tree: 
            TreeViewer.drawTree(self, tree)
            self.entry.focus()
            return True
        else:
            return False
        
    def clearTree(self):
        TreeViewer.clearTree(self)
        self.title.config(text=self.current_grammar['name'])
        
    def help_dialog(self):
#        parent = parent or self.gui_parent
#        win = Toplevel(parent)                           
        win = Toplevel()                        # make a new window
        win.title('Parse Tree Viewer Usage Blurb')
        helptext =  \
"""Use the entry line at the bottom to write a
sentence in the grammar that this Parse Tree Builder
uses.  Click 'Input' to create a tree for the sentence.
A popup will tell you if the input was rejected by the 
grammar.
Click on a non terminal in the tree to see the phrase in
the sentence for it.
This dialog can stay open.
""" 
        #dfont = ('arial', 14, 'normal') font=dfont, 
        lbl = Label(win, text=helptext, justify=LEFT)
        lbl.pack(expand=YES, fill=BOTH)
        for key in lbl.keys():
            print '%s = %s' % (key, lbl.cget(key))        
        #Button(win, text='Show Grammar', command=self.show_grammar).pack()
    
    
    def show_grammar(self):
        win = Toplevel()
        win.title(self.current_grammar['name'])
        gtext = str(self.current_grammar['grammar'])
        gtext += os.linesep + "This dialog can stay open"
        #gfont = ('arial', 14, 'bold') font=gfont, 
        #print 'len(gtext) = %s' % len(gtext)
        if len(gtext) > 1000:
            gtext = 'Grammar is too big to show, see file'
        Label(win, text=gtext, justify=LEFT).pack()
        
    def switch_grammar(self, grammar_name):
        """Switch the current grammar to the grammar with short name grammar_name
        and reinitialize with the new grammar.
        """
        self.current_grammar = self.grammars[grammar_name]
        self.__init_grammar()
        
        
    def make_menu(self):
        """Creates the menus.  Note that the Switch Grammar submenu is built
        dynamically, based on the dictionary of grammars.
        """
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)
        g_menu = Menu(self.menubar, tearoff=0)   ## grammar menu
        g_submenu = Menu(g_menu, tearoff=0)     # switch grammar submenu
        for gname in self.grammars.keys():
            g_submenu.add_command(label=gname.title(), underline=0,
                                  command=lambda gname=gname:self.switch_grammar(gname))
        g_menu.add_cascade(label='Switch Grammar', underline=0, menu=g_submenu)
        
        g_menu.add_command(label='Show Grammar', underline=5,
                             command=self.show_grammar)        
        self.menubar.add_cascade(label='Grammar', 
                                 underline=0, menu=g_menu)
        help_menu = Menu(self.menubar, tearoff=0)
        help_menu.add_command(label='Help Dialog', underline=0,
                             command=self.help_dialog)
        self.menubar.add_cascade(label='Help', 
                                 underline=0, menu=help_menu)
    
if __name__ == '__main__':
    ParseTreeViewer().mainloop()
