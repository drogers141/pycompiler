# The tree Package

## Overview
The modules in the tree package allow a graphical display of parse trees for sentences in any of the LL(1) grammars. Though this wasn't part of the course work, it is kind of cool, and helpful for students learning about parsing. For the python programmer, it is a good example of code reuse. The gui is a tkinter application that is an extension of generic tree viewer from Mark Lutz's Programming Python, 3rd. Ed. 

## treeview_wrappers

This module is Lutz's implementation of a generic tree viewer and a tree wrapper interface that the viewer works with. See the module for more details, and especially see the book, as it is pretty great.. Note that I tweaked the code (look for the ## drogers annotated comment) to allow display of bigger nodes for more text. This could also allow some nodes to obscure others, but it is worth it if you have long text strings as node values.
parsetree

In order to use the tree viewer, I first had to have an actual tree representation of a parse. This module has a recursive tree structure implemented with the Node class. The ParseTreeBuilder subclasses Parser and creates trees using Nodes. Note that one improvement that could be made would be to employ the Visitor design pattern for visiting functionality. This would remove the need for the get_phrases_for() method. However, since that was all I needed to do, it sufficed at the time. Visitor would mean more classes, but more possibilities as well.
The parsetree module has a main clause that allows you to select a grammar, then enter a token string (sentence) within that    grammar and query for nonterminals in the grammar. It will display a list of all phrases in the sentence for the grammar.

## parsetree_viewer

This module contains the realization of Lutz's treewrapper interface using the Node and Treebuilder classes. It also contains a ParseTreeViewer subclass of Lutz's TreeViewer that customizes it and adds functionality.
This module's main clause runs the gui application, allowing grammars to be selected, displayed, and to have parse trees created and displayed from an input box on the bottom of the screen.




***

Last Modified Date: 2009-07-02 
Dave Rogers 
Email questions, corrections: 
drogers141 at sbcglobal dot net, or if no response, 
drogers141 at gmail dot com