# The pycompiler Package

## Overview

All of the components of the compiler are contained in the pycompiler package, with each module handling the full responsibility of a component. In Java or C++ these would probably be divided into their own packages or namespaces. A brief explanation of each of the components follows. Note that there is a globals module for locating common definitions such as paths, etc.

## Scanner
The scanner for the class implemented in C++ is a proper finite state automata that handles the responsibility of scanning input and producing tokens suitable for the parser. For this implementation, I was not really worried about the scanner, as I was focused more on all other aspects of the compiler. However I felt I should have a python scanner to call, so I tried to get the required functionality in in the smallest amount of code--so the scan() method is all that is required. I also have the ability to call a compiled C++ scanner if you have an executable for the right platform. There is a scanner executable for linux that was compiled on Ubuntu. Follow the code for that and put an executable for windows in the resources directory if desired. There is also a method that will test the python scanner against the cpp scanner.
Like many of the modules in the project, scanner.py has an if name == '__main__' clause allowing you to run it as a script. In this case it scans a source file (default is 'srcfile' in the current dir) and produces a tokenfile (default is 'tokfile' in the current dir).

## Virtual Machine
The vm.py module implements a virtual machine simulator that runs an intermediate language. For the compiler/interpreter of this project, this means reading the PL/H language created in the class. As with the parser and translator, however, the vm is not hard coded to the language. Rather the language is read into a dictionary that has the operators as its keys, and executable python statements as the corresponding values. The current behavior is to read in the stock instruction set for PL/H, but any language could be read in and run. If an output file is provided, snapshots of the internal state of the vm will be logged to it, as with the C++ version. See VirtualMachine.doc in the lecture notes.
Note: I lied a little above--the current vm is coupled to the PL/H language in that there is an attribute, self.immed_op_instructions, that sets a flag notifying the vm that there will be instructions with immediate operands that need to be added to the vm snapshot if it is being logged. This would have to be modified to be more flexible to use the vm with another instruction set. See vm.__init__()

## Parser

The parser.py module implements the LL(1) parsing algorithm with the Parser class. It parses according to a context free grammar that has been encapsulated in the Grammar class. The Grammar class can create a Grammar object from a relatively straightforward input file, and can display the grammar as a string as well. The C++ parser used in the class is hard coded to one grammar, whereas with this setup, any cfg that is LL(1) can be read into a Grammar object. The parser also does internal snapshots as with the vm if there is an output file. The parser reads in a token file and outputs a source file according to it's grammar. See the files 06_LLParsing.doc, 07_LLTables1.doc, and 08_LLTables2.doc in the lecture notes for discussion.
The parser module has a main clause allowing it to be run alone on an input token file producing a source output file and optionally producing snapshots. This clause employs the optparse module in python that helps with writing scripts in unix/linux style. Very convenient..

## Translator

The translator.py module turns the parser into a translator. It has a TransScheme subclass of Grammar which encapsulates a translation scheme, i.e. a grammar that has action symbols that will be used to generate intermediate language instructions. The Translator class subclasses Parser, adding a symbol table as well as translation functionality. As with the parser and the vm, action symbols are read into a dictionary, so any translation scheme can be used, but the default is to load the action symbols used to translate PL/H.

## Interpreter

The interpreter.py module combines all the components in the class PLHInterpreter to create an interpreter for the PL/H language in it's limited form. See 09_PLHParser.doc for the BNF form. Additions would be welcome to the scanner, parser, etc to extend the language to handle strings, etc. Note that the interpreter module can be run as a script whose main clause executes a selection sort program that was the test program for the final project. Also note that there is no superclass Interpreter to the PLHInterpreter. This was by design, perhaps a superclass could be distilled after implementing another language, though.

## Util

The util.py module has, surprise, utility stuff in it. In particular, there is a stack implementation. This was not strictly necessary as python's list functionality could be used, and provides for pop() as well. However, I wanted to keep the code for the parser and vm instruction sets to be as close to the C++ versions as possible. Other utility methods are mainly useful for unit testing.

***

Last Modified Date: 2009-07-02   
Dave Rogers    
Email questions, corrections:   
dave at drogers dot us