PL/H CFG (no translation)


start_symbol 	= 	program
terminals 		= 	[$int, $id, <, >, =, +, -, *, /, (, ), :, ;, \,, #, %, $declare, $put, $get, $stop, $goto, $if, $then, $end, $do ]
nonterminals	=	[program, decls, decl, declist, declexprs, declexpr, states, state, label, ustate, assign, logexpr, relop, lessorne, greater, leorne, ge, expr, exprs, exprlist, var, vars, varlist, subvar, put, get, stop, goto, if, group, term, terms, fact, facts ]

rules:													parse_actions:
program	->  decls states            	{ $declare, $id, $put, $get, $stop, $goto, $if, $do, :, # }
decls	->  $declare declist ; decls  					{ $declare }
decls	->  							{ $id, $put, $get, $stop, $goto, $if, $do, :, # }
declist	->	declexpr declexprs							{ $id }
declexprs	->	, declexpr declexprs					{ \, }
declexprs	->											{ ; }
declexpr	->	$id ( $int ) 							{ $id }
states	->  state states				{ $id, $put, $get, $stop, $goto, $if, $do, :, }
states	->  											{ #, $end }
state	-> 	label ustate								{ : }
state 	->	ustate							{ $id, $put, $get, $stop, $goto, $if, $do }
label 	->	: $id :										{ : }

## keywords
ustate	->	assign										{ $id }	
ustate	->	put											{ $put }
ustate	->	get											{ $get }	
ustate	->	stop										{ $stop }
ustate	->	goto										{ $goto }
ustate	->	if											{ $if }
ustate	->	group										{ $do }

assign	->	var = expr ;								{ $id }
put		->	$put exprlist ;								{ $put }
get		->	$get varlist ;								{ $get }
stop 	->	$stop ;										{ $stop }
goto	->	$goto $id ;									{ $goto }
if		->	$if logexpr $then state						{ $if }
group 	->	$do	; states $end ;							{ $do }

## logical expressions, relational operators
logexpr	->	expr relop expr								{ $id, $int, (, +, - }
relop 	->  lessorne									{ < }
relop	-> 	greater										{ > }
relop 	-> 	=											{ = }
lessorne	->	< leorne								{ < }
leorne	->												{ $id, $int, (, +, - }
leorne	->	=											{ = }
leorne	-> 	>											{ > } 

greater	->	> ge										{ > }
ge	->													{ $id, $int, (, +, - }
ge	->	=												{ = }

## variables and expressions
varlist	->	var vars									{ $id }
vars	->	, var vars									{ \, }
vars	->												{ ; }
var	->	$id	subvar										{ $id }
subvar	->	( expr )									{ ( }
subvar	-> 												{ =, ;, \,, ), +, -, *, /, <, >, $then, # }

exprlist	->	expr exprs								{ $id, $int, (, +, - }
exprs	->	, expr exprs								{ \, }
exprs	->												{ ; }
expr 	->  term terms 									{ $id, $int, ( }
expr 	->  + term terms 								{ + }
expr 	->  - term terms  								{ - }
terms 	->  + term terms 								{ + }
terms 	->  - term terms  								{ - }
terms 	->                      						{ ), ;, <, =, >, $then, #, \, }
term 	->  fact facts               					{ $id, $int, ( }
facts 	->  * fact facts  								{ * }
facts	->	/ fact facts								{ / }
facts 	->                      						{ +, -, ), ;, <, =, >, $then, #, \, }
fact 	->  var 									    { $id }
fact	->	$int										{ $int }
fact 	->  ( expr )           							{ ( }


