" Vim syntax file 
" Language: Bovinus grammar
" Maintainer: Thomas Bollmeier <tbollmeier@web.de>
" Latest Revision: 18 October 2012

if exists("b:current_syntax")
	finish
endif

" Keywords

syn keyword bovBool TRUE FALSE

syn keyword bovKey keyword word separator 
syn keyword bovKey prefix postfix literal 
syn match bovKey 'line-comment-style'
syn match bovKey 'block-comment-style'
syn keyword bovKey enable 

syn match bovArg 'full-backtracking'
syn match bovArg 'is-pattern'
syn match bovArg 'case-sensitive'
syn keyword bovArg escape
syn match bovArg 'whitespace-allowed'

syn match bovAnnotation '@grammar'

syn match bovLineComment '#.*$'
syn region bovBlockComment start="<!--" end="-->"

syn region bovLiteral start="'" end="'" 
syn region bovLiteral start="\"" end="\"" 

syn region bovCodeBlock start="^%\s\+[^{]\+{" end="^%\s\+}"

let b:current_syntax="bovg"

hi def link bovBool Boolean
hi def link bovKey Keyword
hi def link bovArg Keyword
hi def link bovAnnotation Comment
hi def link bovLineComment Comment
hi def link bovBlockComment Comment
hi def link bovLiteral String
hi def link bovCodeBlock Comment

