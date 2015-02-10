PL/H Translation Scheme


start_symbol 	= 	program
terminals 		= 	[$int, $id, <, >, =, +, -, *, /, (, ), :, ;, \,, #, %, $declare, $put, $get, $stop, $goto, $if, $then, $end, $do ]
nonterminals	=	[program, decls, declist, declexprs, declexpr, states, state, label, ustate, assign, logexpr, relexpr, grexpr, lene_expr, expr, putexpr, putexprs, putlist, var, getexprs, getexpr, getlist, subvar, put, get, stop, goto, if, group, term, terms, fact, facts ]
action_symbols	=	[@add, @mult, @sub, @div, @neg, @begin_if, @end_if, @lt, @gt, @eq, @le, @ge, @ne, @goto, @label, @push, @declare, @in, @out, @quit, @lit, @last_token_val, @address_last_token_val, @sti, @ldi, ]

rules:													parse_actions:
program	->  decls states @quit           	{ $declare, $id, $put, $get, $stop, $goto, $if, $do, :, # }
decls	->  $declare declist ; decls  					{ $declare }
decls	->  							{ $id, $put, $get, $stop, $goto, $if, $do, :, # }
declist	->	declexpr declexprs							{ $id }
declexprs	->	, declexpr declexprs						{ \, }
declexprs	->												{ ; }
declexpr	->	$id @push ( $int @declare ) 			{ $id }
states	->  state states						{ $id, $put, $get, $stop, $goto, $if, $do, :, }
states	->  												{ #, $end }
state	-> 	label ustate									{ : }
state 	->	ustate									{ $id, $put, $get, $stop, $goto, $if, $do }
label 	->	: $id @label :									{ : }

## keywords
ustate	->	assign										{ $id }	
ustate	->	put											{ $put }
ustate	->	get											{ $get }	
ustate	->	stop										{ $stop }
ustate	->	goto										{ $goto }
ustate	->	if											{ $if }
ustate	->	group										{ $do }

assign	->	var = expr @sti ;								{ $id }
put		->	$put putlist ;										{ $put }
get		->	$get getlist ;										{ $get }
stop 	->	$stop @quit ;										{ $stop }
goto	->	$goto $id @goto ;									{ $goto }
if		->	$if logexpr $then @begin_if state @end_if			{ $if }
group 	->	$do	; states $end ;									{ $do }

## logical expressions, relational operators
logexpr	->	expr relexpr 							{ $id, $int, (, +, - }
relexpr	->	= expr @eq									{ = }
relexpr	->	> grexpr 									{ > }
grexpr	->	= expr @ge									{ = }
grexpr	->	expr @gt								{ $id, $int, (, +, - }
relexpr	->	< lene_expr 								{ < }
lene_expr ->  expr @lt								{ $id, $int, (, +, - }
lene_expr ->  =  expr @le									{ = }
lene_expr ->  > expr @ne									{ > }

## variables and expressions (and related io)
getlist	->	getexpr getexprs							{ $id }
getexprs	->	, getexpr getexprs						{ \, }
getexprs	->											{ ; }
getexpr	->	var @in @sti								{ $id }

var	->	$id	@lit @address_last_token_val subvar			{ $id }
subvar	->	( expr @add )									{ ( }
subvar	-> 												{ =, ;, \,, ), +, -, *, /, <, >, $then, # }

putlist	->	putexpr putexprs								{ $id, $int, (, +, - }
putexprs	->	, putexpr putexprs								{ \, }
putexprs	->												{ ; }
putexpr -> 	expr @out 									{ $id, $int, ( , -, + }

expr 	->  term terms 									{ $id, $int, ( }
expr 	->  + term terms 								{ + }
expr 	->  - term @neg terms  								{ - }
terms 	->  + term @add terms 							{ + }
terms 	->  - term @sub terms  							{ - }
terms 	->                      						{ ), ;, <, =, >, $then, #, \, }
term 	->  fact facts               					{ $id, $int, ( }
facts 	->  * fact @mult facts  						{ * }
facts	->	/ fact @div facts							{ / }
facts 	->                      						{ +, -, ), ;, <, =, >, $then, #, \, }
fact 	->  var @ldi									    { $id }
fact	->	$int @lit @last_token_val					{ $int }
fact 	->  ( expr )           							{ ( }


