# PyCompiler
This is a compiler and parse tree viewer implemented in Python that I wrote in 2009.  It was early into 
my experience with python, so the code may not be as pythonic as it could be, but I was generally happy 
with the project.

While this is a general LL(1) compiler, the work stems from Dr. James Daley's 
undergrad compiler class at CSU East Bay. While the requirements for the class were 
generally met by students extending an existing code base in C/C++ to form a parser, vm, and 
interpreter for a simplified language with syntax similar to PL/1 called PL/H, I reimplemented the 
compiler in python adding quite a bit more power and generality, with less code. 

## Overview
The PyCompiler project is an implementation of a compiler based on the course work of CS4110 at 
California State University East Bay (CSUEB), as taught by Prof. James Daley.  It does not have any 
code generation.  Rather it combines:

- an LL(1) parser
- a hastily implemented scanner
- a virtual machine simulator
- a translator that adds translation functionality to the parser
- a tree package that allows creation and viewing of parse trees for any grammar or translation scheme 
that the parser can handle.  

The lecture notes related to the compiler/interpreter
are in the doc/lecture_notes/ directory.  Look there for discussion of anything mentioned in this
documentation that is not explained.  

## Source and docs
The source code is organized into three packages under src/:

- pycompiler - all the components of the compiler
- test - unit tests of the components
- tree - gui implemented in Tkinter allowing graphical display of LL(1) parse trees.  It is an
extension of the generic tree viewer from Mark Lutz's Programming Python, 3rd. Ed.  

There is documentation for each of the packages as well:
- [pycompiler] (./doc/pycompiler_package.html)
- [test] (./doc/test_package.html)
- [tree] (./doc/tree_package.html)

## Usage
For compiler usage examples, consult the tests.  The grammars/, resources/, and sourcefiles/ directories
have input and output files showing all compilation levels, and these files are actually used in
the tests.

For viewing parse trees, you must have Tkinter installed.  Then just run the parsetree_viewer module 
from it's directory:

```
drogers@drogers-mbp:~/eclipse/ws_default/PyCompiler/src/tree (master)
$ python parsetree_viewer.py
```

You can interactively switch grammars and enter different sentences.  Clicking on a
node in the tree will show a phrase evaluated from that node.

Here is an example using the exemplary arithmetic GSE3 grammar:

![Crap, image not available..)] (doc/screenshot-parsetree-gse3.png)
