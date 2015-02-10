##
# Dave Rogers
# dave at drogers dot us
# This software is for instructive purposes.  Use at your own risk - not meant to be robust at all.
# Feel free to use anything, credit is appreciated if warranted.
##

# utility stuff for the pycompiler package

__all__ = ['Stack', 'convert_from_str', 'write_to', 'intersect',
           'have_equal_contents', 'equal_without_whitespace',
           'find_without_whitespace', 'make_seq_string', 'remove_file',
           'token_stack_str', 'make_token', 'make_token_seq']
import os, sys, types

class Stack:
    """Stack data structure, type not restricted."""
    def __init__(self):
        self.data = []
        
    def __str__(self):
        """String representation is tab separated."""
        return '\t'.join([str(item) for item in self.data])
    
    def push(self, content):
        """Push content onto stack."""
        self.data.append(content)
        
    def pop(self):
        """Returns top element of stack and removes it.  Raises an AssertionError
        if called on empty stack.
        """
        assert self.data, "Stack:  pop() called on empty stack"
        return self.data.pop()
    
    def top(self):
        """Returns top element of stack without removing it.  Raises an AssertionError
        if called on empty stack.
        """
        assert self.data,  "Stack: top() called on empty stack"
        return self.data[-1]
    
    def multipush(self, list_of_elements):
        """Push the elements of a list onto the stack in reverse order.
        ie empty_stack.multipush([1, 2, 3]) => empty_stack.data == [3, 2, 1]
        """
        for i in range(len(list_of_elements)-1, -1, -1):
            self.push(list_of_elements[i])
        
    def print_reverse(self, delim='\t'):
        """Returns string representation with top of stack on left hand side.
        Can specify string delimiter other than default '\t' with delim"""
        retstr = ""
        for i in range(len(self.data)-1, -1, -1):
            retstr += str(self.data[i]) + delim
        return retstr.rstrip(delim).strip()
    
def token_stack_str(stack, reverse=False, delim='  '):
    """Returns string representation of a stack of tokens separated by delim.  If value is '', 
    just name of token is printed to the string, else (name, value) is.  If reverse, top of stack
    is on left.  Tokens are assumed to be dict with keys 'name' and 'value'.
    Returns '' on error.
    """
    try:
        ret = ''
        elems = stack.data[:]
        if reverse: elems.reverse()
        for elem in elems:
            name, val = elem['name'], elem['value'] 
            if val: ret += '(%s, %s)%s' % (name, str(val), delim)
            else: ret += '%s%s' % (name, delim)
        return ret.strip()
    except Exception, msg:
        print sys.stderr >> 'util.token_stack_str:  ' + msg
        return ''
        
        
def convert_from_str(strval):
    """Returns param as int, long, float, or string, whichever is best."""
    try:
        ret = int(strval)
        return ret
    except ValueError:
        pass
    try:
        ret = float(strval)
        return ret
    except ValueError:
        if strval == 'None': return None
    return strval
        
def remove_file(fname):
    """Removes file using os.remove, but pauses on error for Windows."""
    try:
        os.remove(fname)
    except OSError, msg:
        string = \
'''util.remove_file error (probably the dread Windows...)
sys.platform = %s
Error Message:
%s
'''     % (sys.platform, msg)
        print >> sys.stderr, string
        
def write_to(string, *files):
    """Writes string + newline to params files, files can be any number of file-like objects.
    A file that equals None will be ignored safely."""
    for f in files:
        if f: print >> f, string

def intersect(seq1, seq2):
    """Returns a list of elements in both seq1 and seq2."""
    ret = []
    for elem in seq1:
        if elem in seq2:
            ret.append(elem)
    return ret

def have_equal_contents(*seqs):
    """Takes any number of sequences as params, returns True if the all have the same contents
    disregarding order.
    """
    ret = True
    if seqs[1:]:
        for seq in seqs[1:]:
            interlen = len(intersect(seqs[0], seq))
            if (interlen != len(seqs[0]) or 
                interlen != len(seq)): ret = False
    return ret
    
def equal_without_whitespace(string1, string2):
    """Returns True if string1 and string2 have the same nonwhitespace tokens
    in the same order."""
    return string1.split() == string2.split()
    
def find_without_whitespace(string, substring):
    """Returns True if string contains substring, disregarding whitespace,
    False otherwise."""
    strlist = string.strip().split()
    sublist = substring.strip().split()
    strnorm = ' '.join(strlist)
    subnorm = ' '.join( sublist )
    return strnorm.find(subnorm) != -1

def make_seq_string(seq, container_chars = '[]'):
    """Returns a string representing the sequence, wrapped in the container_chars 
    (can be '{}', etc).  Each element is str(element), but no quotes are used.
    For example: make_seq_string([ a, b, c ], '{}') -> '{ a, b, c }'.
    """
    string = '%s ' % container_chars[0]
    for elem in seq: string += str(elem) + ', '
    string = '%s %s' % (string[:-2], container_chars[1])
    return string
        
            
def make_token(name, value=''): 
    """Make a token with name and optional value."""
    return {'name': name, 'value': value}
        
def make_token_seq(seq):
    """Make a token using all strings in seq as names. (Values = '').
    """
    ret = []
    for name in seq: ret.append(make_token(name))
    return ret

