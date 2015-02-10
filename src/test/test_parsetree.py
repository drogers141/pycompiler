## tests the parse tree addition to pycompiler
##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

import os, sys, StringIO
import unittest

from pycompiler.globals import *
from pycompiler.parser import *
from pycompiler.translator import *
from tree.parsetree import *

from pycompiler.util import *
import pycompiler

class TestNode(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
                
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    def test_node(self):
        r = Node(name='root')
        self.assertEqual(r.name, 'root')
        self.assertEqual(len(r.children), 0)        
        r.add_child(Node('first'))
        r.add_child(Node('second'))        
        self.assertEqual(map(str, r.children), ['first', 'second'])

    def test_string_repr(self):
        r = Node(name='root')
        self.assertEqual(str(r), 'root')
        v = Node(name='$id', value='var_name')
        self.assertEqual(str(v), '($id, var_name)')

class TestCFGParseTree(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cfg = Grammar.get_gse3()
        self.treebuilder = ParseTreeBuilder(grammar=self.cfg, 
                                       tokensource = os.path.join(tokfiledir, 
                                                                'tokfile.simple.accept') )
         
    def tearDown(self):
        unittest.TestCase.tearDown(self)
                
        
    def test_cfg_tree_creation_steps(self):
        tree = self.treebuilder.tree
        tree_stack = self.treebuilder.tree_stack
        self.assertEqual(tree.name, 'goal')
        self.assertEqual(tree_stack.data, [tree])
        self.assertEqual(tree.children, [])
        
        # imitate parse() initialization so we can isolate steps
        self.treebuilder.is_parsing = True
        self.treebuilder.next_token()
        
        self.assertEqual(tree_stack.data, [tree])
        self.assertEqual(tree.children, [])
        
        self.treebuilder.execute_one_cycle()
        
        level1_children = tree.children
        self.assertEqual(map(str, level1_children), ['e'])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'e']))        

        self.treebuilder.execute_one_cycle()        
        level2_children = level1_children[0].children
        self.assertEqual(map(str, level2_children), ['t', 'mt'])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 't']))
        
       
        self.treebuilder.execute_one_cycle()        
        level3_children_of_t = level2_children[0].children
        self.assertEqual(map(str, level3_children_of_t), ['f', 'mf'])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 'mf', 'f']))
        
        self.treebuilder.execute_one_cycle()        
        level4_children_of_f = level3_children_of_t[0].children
        self.assertEqual(map(str, level4_children_of_f), ['$id'])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 'mf', '$id']))
        self.assertEqual(map(str, tree_stack.data), ['mt', 'mf', '$id'])
        
        self.treebuilder.execute_one_cycle()        
        level5_children_of_terminal = level4_children_of_f[0].children
        self.assertEqual(level5_children_of_terminal, [])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 'mf']))
        self.assertEqual(map(str, tree_stack.data), ['mt', 'mf'])
        
        self.treebuilder.execute_one_cycle()        
        level4_children_of_mf = level3_children_of_t[1].children
        self.assertEqual(map(str, level4_children_of_mf), ['*', 'f', 'mf'])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 'mf', 'f', '*']))
        self.assertEqual(map(str, tree_stack.data), ['mt', 'mf', 'f', '*'])
        
        self.treebuilder.execute_one_cycle()        
        level5_children_of_terminal = level4_children_of_mf[0].children
        self.assertEqual(level5_children_of_terminal, [])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 'mf', 'f']))
        self.assertEqual(map(str, tree_stack.data), ['mt', 'mf', 'f'])
        
        self.treebuilder.execute_one_cycle()        
        level5_children_of_f = level4_children_of_mf[1].children
        self.assertEqual(map(str, level5_children_of_f), ['$id'])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 'mf', '$id']))
        self.assertEqual(map(str, tree_stack.data), ['mt', 'mf', '$id'])
        
        self.treebuilder.execute_one_cycle()        
        level6_children_of_terminal = level5_children_of_f[0].children
        self.assertEqual(level6_children_of_terminal, [])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 'mf']))
        self.assertEqual(map(str, tree_stack.data), ['mt', 'mf'])
        
        self.treebuilder.execute_one_cycle()        
        level5_children_of_mf = level4_children_of_mf[2].children
        self.assertEqual(level5_children_of_mf, [])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt']))
        self.assertEqual(map(str, tree_stack.data), ['mt'])
        
        self.treebuilder.execute_one_cycle()        
        level3_children_of_mt = level2_children[1].children
        self.assertEqual(map(str, level3_children_of_mt), ['+', 't', 'mt'])
        self.assertEqual(self.treebuilder.stack.data, make_token_seq(['%', 'mt', 't', '+']))
        self.assertEqual(map(str, tree_stack.data), ['mt', 't', '+'])
        
    def test_eval_tree_subtree(self):
        # for evaluation, in this easy case, we want the result to be
        # the phrase for the root node of any tree/subtree
        r = Node(name='root')
        self.assertEqual(r.name, 'root')
        self.assertEqual(len(r.children), 0)        
        r.add_child(Node('first', '1st'))
        second = Node('second', '2nd')
        r.add_child(second)        
        self.assertEqual(map(str, r.children), ['(first, 1st)', '(second, 2nd)'])
        second.add_child(Node('child of second'))
        delim = '   '
        phrase = r.get_phrase(delim)
        self.assertEqual(phrase, 
                         '(first, 1st)' + delim + 'child of second')
        
    def test_eval_simple_cfg(self):
        self.treebuilder.parse()
        delim = ' '
        sentence = self.treebuilder.tree.get_phrase(delim, self.treebuilder.grammar)
        self.assertEqual(sentence, '$id * $id + $id')
  
    def test_create_tree(self):
        tree = self.treebuilder.create_tree()
        delim = ' '
        sentence = tree.get_phrase(delim, self.treebuilder.grammar)
        self.assertEqual(sentence, '$id * $id + $id')
  
        
    def test_eval_subtree(self):
        root = self.treebuilder.create_tree()
        level2 = root.children[0].children      # counting the 'goal' level as 0, 'e' as 1
        self.assertEqual(map(str, level2), ['t', 'mt'])
        delim = ' '
        level2_t_phrase = level2[0].get_phrase(delim, self.treebuilder.grammar)
        self.assertEqual(level2_t_phrase, '$id * $id')
        level2_mt_phrase = level2[1].get_phrase(delim, self.treebuilder.grammar)
        self.assertEqual(level2_mt_phrase, '+ $id')
        
        
        
class TestsUsingDifferentOrNoTreeBuilders(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cfg = Grammar.get_gse3()
#        self.treebuilder = ParseTreeBuilder(grammar=self.cfg, 
#                                       tokensource = os.path.join(tokfile_dir, 
#                                                                'tokfile.simple.accept') )
#         
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    def test_tokfile_1(self):
        expected = "$id * $id * ( $id + $id )"
        treebuilder = ParseTreeBuilder( tokensource=os.path.join(tokfiledir, 'tokfile1.accept'),
                                        grammar=self.cfg )
        tree = treebuilder.create_tree()
        delim = ' '
        sentence = tree.get_phrase(delim, treebuilder.grammar)
        self.assertEqual(sentence, expected)

        
    def test_create_tree_builder_with_token_string(self):
        ## use a token string instead of a token file
        tokstring = '$id * $id * ( $id + $id )'
        treebuilder = ParseTreeBuilder(tokensource = tokstring,
                                       grammar = self.cfg)
        tree = treebuilder.create_tree()
        expected = tree.get_phrase(' ', self.cfg)
        self.assertEqual(tokstring, expected)
    
    ## need to rethink or abandon
#    def test_traverse_nodes_with_visitor(self):
#        tokstring = '$id * $id'
#        treebuilder = ParseTreeBuilder(tokensource = tokstring,
#                                       grammar = self.cfg)
#        root = treebuilder.create_tree()
#        
#        def collect_names(node, namelist):
#            namelist.append(node.name)
#            return namelist
#                
#        retlist = []
#        root.traverse(collect_names, namelist=retlist)
#        self.assertEqual(len(retlist), 11)
        
    def test_have_equal_contents(self):
        s1 = [1, 2, 3]; s2 = [1, 3, 2]; s3 = [1, 2, 3]
        self.assertEqual( have_equal_contents(s1, s2, s3), True )
        s1 = [1, 2, 3]; s2 = [1, 2]; s3 = [1, 2, 3]
        self.assertEqual( have_equal_contents(s1, s2, s3), False )
        s1 = [1, 2, 3]; s3 = [1, 2, 3]
        self.assertEqual( have_equal_contents(s1, s3), True )
        
    def test_get_all_phrases_for_nonterminal(self):
        tokstring = '$id * $id * ( $id + $id )'
        treebuilder = ParseTreeBuilder(tokensource = tokstring,
                                       grammar = self.cfg)
        root = treebuilder.create_tree()
        phrase_list = ParseTreeBuilder.get_phrases_for(nonterminal='mf', root=root, grammar=self.cfg )
        expected = ['* $id * ( $id + $id )', '* ( $id + $id )']
        self.assertEqual( have_equal_contents(phrase_list, expected), True )
        
        phrase_list = ParseTreeBuilder.get_phrases_for(nonterminal='mt', root=root, grammar=self.cfg )
        expected = ['+ $id']
        self.assertEqual( have_equal_contents(phrase_list, expected), True )
        



class TestPhraseProjectGrammarTree(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    
    def test_phrase_project_grammar_reject(self):
        grammar_string = open(os.path.join(grammardir, 'phrase_project_grammar')).read()
        g = Grammar.create_grammar(grammar_string)
#        print "Phrase Grammar"
#        print str(g)

        tokstring = "int x ; x = x + x * ( x + x )"
        treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=g)
        tree = treebuilder.create_tree()
        self.assertEqual(tree, None)


    def test_phrase_project_grammar_accept(self):
        grammar_string = open(os.path.join(grammardir, 'phrase_project_grammar')).read()
        g = Grammar.create_grammar(grammar_string)

        tokstring = "int x ; x = x + x * ( x + x ) ;"
        treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=g)
        tree = treebuilder.create_tree()
        self.assertNotEqual(tree, None)

        expected = tree.get_phrase(' ', g)
        self.assertEqual(tokstring, expected)
        
        

class TestSemiSimpleAssignGrammar(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tokfile = os.path.join(tempdir, 'semi-simple_tokfile')
        grammar_string = open(os.path.join(grammardir, 
                                           'semi-simple_assign_g')).read()
        self.g = Grammar.create_grammar(grammar_string)
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    
        
    # expected == 'accept' or 'reject'
    def run_simple_assign_grammar_string_accept(self, tokstring):
        treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=self.g)
        tree = treebuilder.create_tree()
        self.assertNotEqual(tree, None)

        expected = tree.get_phrase(' ', self.g)
        self.assertEqual(tokstring, expected)
     
    def test_simple_assign_grammar_accept_w_stringtoks(self):
        sentences = ['$id = - ( $id + $int ) / $id * $int - $id',
                     '$id = - $id + $int / $id * $int - $id',
                     '$id = + $id / ( $int / $id ) * $int - $id',
                     ]
        for tokstring in sentences:
            self.run_simple_assign_grammar_string_accept(tokstring)
#
#        tokstring = '$id = - ( $id + $int ) / $id $id'
#        expected = 'reject'
#        self.run_simple_assign_grammar_string(tokstring, expected)

class TestPlhGrammar(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.g = Grammar.create_grammar(os.path.join(grammardir, 'plh.g'))
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    
        
    def test_plh_w_stringtoks(self):
        #print "PL/H Grammar:\n%s" % str(self.g)
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
             ('$if $id i > = $int 2 $then $put $id x ( $id numtosort ) , $id y , $int 5 ;',
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
            #print 'tokstring:\n%s\n' % tokstring
            treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=self.g)
            tree = treebuilder.create_tree()
            if expected == 'accept':
                self.assertNotEqual(tree, None)
                ## test get_phrase (ie what get phrases for uses )
                get_phrase = tree.get_phrase(' ', self.g)
                
                #phrase
#                print 'tokstring:', tokstring
#                print 'get_phrase:', get_phrase
#                print "stripped"
                (ts, ps) =  map( (lambda s:''.join(s.split())),(tokstring, get_phrase))
                self.assertEqual( len(ps) >= len(ts), True )
                
                (ts, ps) =  map((lambda s: s.replace('(','').replace(')','').replace(',','')),
                                  (ts, ps))
                self.assertEqual( ts, ps )
            else:
                self.assertEqual(tree, None)
    
    def test_get_phrase(self):
        tokstring = '$if $id i < = $id numtosort + $int 2 $then $goto $id in ;'       
        treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=self.g)
        tree = treebuilder.create_tree()
        result = tree.get_phrase(' ', self.g)
        #print 'test_get_phrase_for: \ntokstring:  %s\nresult:  %s' % (tokstring, result)
        self.assertNotEqual(result.find('($id, numtosort)'), -1)
            

    def test_plh_w_selection_sort_tokfile(self):
        tokfile = os.path.join(tokfiledir, 'selection_sort_tokfile')
        treebuilder = ParseTreeBuilder(tokensource=tokfile, 
                                       grammar=self.g)
        tree = treebuilder.create_tree()
        self.assertNotEqual(tree, None)
       


class TestPlhTranslationScheme(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.ts = TransScheme.create_ts(os.path.join(grammardir, 'plh.ts'))
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_parsetree_recognizes_trans_scheme(self):
        tokstring = '$id x = $int 5 + $int 10 ;'
        treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=self.ts)
        self.assertEqual(treebuilder.grammar_is_ts, True)
        g = Grammar.create_grammar(os.path.join(grammardir, 'plh.g'))
        tokstring = '$id x = $int 5 + $int 10 ;'
        treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=g)
        self.assertEqual(treebuilder.grammar_is_ts, False)
        
        
    def test_plh_ts_w_stringtoks(self):
        #print "PL/H Grammar:\n%s" % str(self.ts)
        sentences = [
             ('$id x = $int 5 + $int 10 ;', 'accept'),
             ('$id numsort =  $int 5 ; $id i = $int 1 ;', 'accept'),
             
                     ]
        for (tokstring, expected) in sentences:
            #print 'tokstring:\n%s\n' % tokstring
            treebuilder = ParseTreeBuilder(tokensource=tokstring,
                                       grammar=self.ts)
            tree = treebuilder.create_tree()
            if expected == 'accept':
                self.assertNotEqual(tree, None)
                ## test get_phrase (ie what get phrases for uses )
                get_phrase = tree.get_phrase(' ', self.ts)
                
                #phrase
#                print 'tokstring:', tokstring
#                print 'get_phrase:', get_phrase
#                print "stripped"
                (ts, ps) =  map( (lambda s:''.join(s.split())),(tokstring, get_phrase))
                self.assertEqual( len(ps) >= len(ts), True )
                
                (ts, ps) =  map((lambda s: s.replace('(','').replace(')','').replace(',','')),
                                  (ts, ps))
                self.assertEqual( ts, ps )
            else:
                self.assertEqual(tree, None)
    


if __name__ == '__main__':
    unittest.main()

