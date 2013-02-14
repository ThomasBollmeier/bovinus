#! coding=UTF-8

# Copyright 2012 Thomas Bollmeier <tbollmeier@web.de>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Token grammar examples:

word ID "[a-zA-Z_][a-zA-Z_0-9]*";

keyword CLASS "gobject";
keyword INTF "ginterface";

keyword METH "method" { case-sensitive: FALSE }
separator BRACE_LEFT "{" { whitespace-allowed: TRUE, escape: TRUE }
literal LIT;

"""

from bovinus.token import *
from bovinus.grammar import Grammar, Rule, defineRule, \
expand, transform, tokenNode as tn, connector, fork, zeroToMany, \
zeroToOne, oneToMany, sequence
from bovinus.parser import AstNode
from bovinus.parsergen.ast import PropertiesNode, KeywordNode, WordNode, PrefixNode, \
PostfixNode, SeparatorNode, LiteralNode, RuleNode, Multiplicity, TextBlockNode

token_types = []

def register_token_type(tt):
    
    token_types.append(tt)
    
    return tt
    
def register_keyword(keyword):
    
    return register_token_type(Keyword(keyword))

# Tokens:

TOKEN_ID = register_token_type(Word("[A-Z_]([A-Z0-9_])*"))
TOKEN_VALUE = register_token_type(Literal.get())
KEYWORD_NAME = TOKEN_VALUE
BRACE_OPEN = register_token_type(Separator("{"))
BRACE_CLOSE = register_token_type(Separator("}"))
PAR_OPEN = register_token_type(Separator("("))
PAR_CLOSE = register_token_type(Separator(")"))
COLON = register_token_type(Separator(":"))
COMMA = register_token_type(Separator(","))
ASSIGN = register_token_type(Separator("="))
OR = register_token_type(Separator("|"))
SEMICOLON = register_token_type(Separator(";"))
TRUE = register_keyword("TRUE")
FALSE = register_keyword("FALSE")

KEYWORD = register_keyword("keyword")
WORD = register_keyword("word")
SEPARATOR = register_keyword("separator")
PREFIX = register_keyword("prefix")
POSTFIX = register_keyword("postfix")
LITERAL = register_keyword("literal")
TEXT_BLOCK = register_keyword("text-block")
LINE_COMMENT_STYLE = register_keyword("line-comment-style")
BLOCK_COMMENT_STYLE = register_keyword("block-comment-style")
COMMENT_VALUE = Literal.get()
ENABLE = register_keyword('enable')
FULL_BACKTRACKING = register_keyword('full-backtracking')

IS_PATTERN = register_keyword("is-pattern")
CASE_SENSITIVE = register_keyword("case-sensitive")
ESCAPE = register_keyword("escape")
WS_ALLOWED = register_keyword("whitespace-allowed")
FILTER_CB = register_keyword("filter-callback")

RULE_ID = register_token_type(Word("[a-z_]([a-zA-Z0-9_])*"))
GRAMMAR_ANNOTATION = register_keyword("@grammar")
ID = register_token_type(Word("[a-zA-Z_]([a-zA-Z0-9_])*"))
MULT_ZERO_TO_ONE = register_token_type(Separator('?'))
MULT_ZERO_TO_MANY = register_token_type(Separator('*'))
MULT_ONE_TO_MANY = register_token_type(Separator('+'))

# Rules:

ENVVAR_TOKEN_TYPE = "TOKEN_TYPE"

_CommentRule = defineRule("comment")

@expand(_CommentRule)
def _comment_expand(start, end, context):

    start\
    .connect(tn(LINE_COMMENT_STYLE, 'line'))\
    .connect(tn(COMMENT_VALUE, 'begin'))\
    .connect(tn(SEMICOLON))\
    .connect(end)

    start\
    .connect(tn(BLOCK_COMMENT_STYLE, 'block'))\
    .connect(tn(COMMENT_VALUE, 'begin'))\
    .connect(tn(COMMENT_VALUE, 'end'))\
    .connect(tn(SEMICOLON))\
    .connect(end)
    
@transform(_CommentRule)
def _comment_transform(astNode):
    
    line = astNode.getChildById('line')
    if line:
        res = AstNode('line-comment')
        begin = AstNode('begin', astNode.getChildById('begin').getText())
        res.addChild(begin)
    else:
        res = AstNode('block-comment')
        begin = AstNode('begin', astNode.getChildById('begin').getText())
        res.addChild(begin)
        end = AstNode('end', astNode.getChildById('end').getText())
        res.addChild(end)
        
    return res

_EnableRule = defineRule("enable")

@expand(_EnableRule)
def _enable_expand(start, end, context):
    
    start\
    .connect(tn(ENABLE))\
    .connect(tn(FULL_BACKTRACKING))\
    .connect(tn(SEMICOLON))\
    .connect(end)
    
@transform(_EnableRule)
def _enable_transform(astNode):
    
    return AstNode('full-backtracking')
    
_PropsRule = defineRule("properties")

@expand(_PropsRule)
def _props_expand(start, end, context):
    
    tt = context[ENVVAR_TOKEN_TYPE]
    
    start_ = connector()
    end_ = connector()
    hlp = connector()
    prop_end = connector()       
    
    start\
    .connect(tn(BRACE_OPEN))\
    .connect(start_)
    
    is_flag = True
    
    if tt == KEYWORD:
        start_.connect(tn(CASE_SENSITIVE, 'case-sensitive')).connect(hlp)
    elif tt == WORD:
        is_flag = False
        start_\
        .connect(tn(FILTER_CB, 'filter-callback'))\
        .connect(tn(COLON))\
        .connect(tn(ID, 'filter-callback-name'))\
        .connect(prop_end)
    elif tt == PREFIX:
        start_.connect(tn(ESCAPE, 'escape')).connect(hlp)
    elif tt == POSTFIX:
        start_.connect(tn(ESCAPE, 'escape')).connect(hlp)
    elif tt == SEPARATOR:
        start_.connect(tn(IS_PATTERN, 'pattern')).connect(hlp)
        start_.connect(tn(WS_ALLOWED, 'ws-allowed')).connect(hlp)
        start_.connect(tn(ESCAPE, 'escape')).connect(hlp)
    else:
        raise Exception("Unknown property target")
    
    if is_flag:
    
        hlp\
        .connect(tn(COLON))\
        .connect(tn(TRUE, 'true'))\
        .connect(prop_end)
    
        hlp\
        .connect(tn(COLON))\
        .connect(tn(FALSE, 'false'))\
        .connect(prop_end)
    
    prop_end.connect(tn(COMMA)).connect(start_)
    prop_end.connect(end_)
        
    end_\
    .connect(tn(BRACE_CLOSE))\
    .connect(end)

@transform(_PropsRule)
def _props_transform(astNode):
    
    res = PropertiesNode()
    
    children = astNode.getChildren()
    for idx, child in enumerate(children):
        id_ = child.getId() 
        try:
            value = {
                     'true': 'yes',
                     'false': 'no',
                     'filter-callback-name': child.getText()
                     }[id_]
        except KeyError:
            continue
        name = children[idx-2].getId()
        res.add_property(name, value)
            
    return res

class _TokenRule(Rule):
    
    def __init__(self, token_type, identifier=''):
        
        name = {
                KEYWORD : 'keyword',
                WORD : 'word',
                PREFIX : 'prefix',
                POSTFIX : 'postfix',
                SEPARATOR : 'separator',
                LITERAL : 'literal',
                TEXT_BLOCK: 'text'
                }[token_type]
        
        Rule.__init__(self, name, identifier)
        
        self.setEnvVar(ENVVAR_TOKEN_TYPE, token_type)
        self._token_type = token_type
                
    def expand(self, start, end, context):
        
        end_ = connector()
        
        start\
        .connect(tn(self._token_type))\
        .connect(tn(TOKEN_ID, "id"))\
        .connect(end_)
        
        if not self._token_type in [LITERAL, TEXT_BLOCK]:
            end_ = end_.connect(tn(TOKEN_VALUE, "value"))
        
        if self._token_type in [KEYWORD, WORD, PREFIX, POSTFIX, SEPARATOR]:
            end_.connect(_PropsRule('properties')).connect(end)
        
        end_.connect(tn(SEMICOLON)).connect(end)
                        
    def transform(self, astNode):
        
        res = None
        
        token_id = astNode.getChildById('id').getText()
        
        node = astNode.getChildById('value')
        value = node and node.getText() or ''
        if value:
            value = value[1:-1]
        
        propertiesNode = astNode.getChildById('properties') 
        if propertiesNode:
            propertiesNode.setId('')
        
        if self._token_type == KEYWORD:
            res = KeywordNode(token_id, value, propertiesNode)
        elif self._token_type == WORD:
            res = WordNode(token_id, value, propertiesNode)
        elif self._token_type == PREFIX:
            res = PrefixNode(token_id, value, propertiesNode)
        elif self._token_type == POSTFIX:
            res = PostfixNode(token_id, value, propertiesNode)
        elif self._token_type == SEPARATOR:
            res = SeparatorNode(token_id, value, propertiesNode)
        elif self._token_type == LITERAL:
            res = LiteralNode(token_id)
        elif self._token_type == TEXT_BLOCK:
            res = TextBlockNode(token_id)
            
        return res
    
_TokensRule = defineRule("tokens")

@expand(_TokensRule)
def _tokens_expand(start, end, context):
    
    start.connect(fork(
                       _TokenRule(KEYWORD),
                       _TokenRule(WORD),
                       _TokenRule(PREFIX),
                       _TokenRule(POSTFIX),
                       _TokenRule(SEPARATOR),
                       _TokenRule(LITERAL),
                       _TokenRule(TEXT_BLOCK)
                       )).connect(end)
                       
_MultRule = defineRule("mult")

@expand(_MultRule)
def _mult_expand(start, end, context):
    
    start.connect(fork(
                       tn(MULT_ZERO_TO_ONE, 'mult-1'),
                       tn(MULT_ZERO_TO_MANY, 'mult-2'),
                       tn(MULT_ONE_TO_MANY, 'mult-3'),
                       )).connect(end)
    
@transform(_MultRule)
def _mult_transform(astNode):
    
    name = "multiplicity"
    
    if astNode.getChildById('mult-1'):
        return AstNode(name, Multiplicity.ZERO_TO_ONE_STR)
    elif astNode.getChildById('mult-2'):
        return AstNode(name, Multiplicity.ZERO_TO_MANY_STR)
    elif astNode.getChildById('mult-3'):
        return AstNode(name, Multiplicity.ONE_TO_MANY_STR)
    else:
        raise Exception("Unknown multiplicity")
                           
_GroupRule = defineRule("group")

@expand(_GroupRule)
def _group_expand(start, end, context):
    
    start\
    .connect(tn(PAR_OPEN))\
    .connect(_BranchRule('branch'))\
    .connect(zeroToMany(sequence(tn(OR), _BranchRule('branch'))))\
    .connect(tn(PAR_CLOSE))\
    .connect(end)
    
@transform(_GroupRule)
def _group_transform(astNode):
    
    res = AstNode("group")
    
    for child in astNode.getChildrenById('branch'):
        child.setId('')
        res.addChild(child)

    return res
                                                
_BranchElemRule = defineRule("branch-element")

@expand(_BranchElemRule)
def _branch_elem_expand(start, end, context):
    
    token = sequence(zeroToOne(sequence(tn(ID, 'id'), tn(ASSIGN))), 
                     tn(TOKEN_ID, 'token'),
                     zeroToOne(_MultRule('mult'))
                     )
    keyword = sequence(zeroToOne(sequence(tn(ID, 'id'), tn(ASSIGN))), 
                       tn(KEYWORD_NAME, 'keyword'),
                       zeroToOne(_MultRule('mult'))
                       )

    rule = sequence(zeroToOne(sequence(tn(ID, 'id'), tn(ASSIGN))), 
                    tn(RULE_ID, 'rule'),
                    zeroToOne(_MultRule('mult'))
                    )
    
    group = sequence(zeroToOne(sequence(tn(ID, 'id'), tn(ASSIGN))),
                    _GroupRule('group'),
                    zeroToOne(_MultRule('mult')) 
                    )
    
    start.connect(fork(
                       token,
                       keyword,
                       rule,
                       group
                       )).connect(end)

@transform(_BranchElemRule)
def _branch_elem_transform(astNode):
    
    res = AstNode('element')
    
    for child in astNode.getChildren():
        id_ = child.getId()
        if id_ == 'token':
            node = AstNode('token-id', child.getText())
            res.addChild(node)
        elif id_ == 'rule': 
            node = AstNode('rule-id', child.getText())
            res.addChild(node)
        elif id_ == 'keyword': 
            node = AstNode('keyword-text', child.getText()[1:-1])
            res.addChild(node)
        elif id_ == 'group':
            child.setId('') 
            res.addChild(child)
        elif id_ == 'id':
            node = AstNode('id', child.getText())
            res.addChild(node)
        elif id_ == 'mult':
            child.setId('') 
            res.addChild(child)
    
    return res
                       
_BranchRule = defineRule("branch")

@expand(_BranchRule)
def _branch_expand(start, end, context):
    
    start.connect(oneToMany(_BranchElemRule())).connect(end)

@transform(_BranchRule)
def _branch_transform(astNode):
    
    res = AstNode("branch")
    
    for child in astNode.getChildren():
        child.setId("")
        res.addChild(child)
    
    return res
                       
_RuleRule = defineRule("rule")

@expand(_RuleRule)
def _rule_expand(start, end, context):
    
    branch = _BranchRule('branch')
    
    start\
    .connect(zeroToOne(tn(GRAMMAR_ANNOTATION, 'is-grammar')))\
    .connect(tn(RULE_ID, 'rule-id'))\
    .connect(tn(ASSIGN))\
    .connect(branch)\
    .connect(zeroToMany(sequence(tn(OR), branch)))\
    .connect(tn(SEMICOLON))\
    .connect(end)
    
@transform(_RuleRule)
def _rule_transform(astNode):

    is_grammar = bool(astNode.getChildById('is-grammar'))
    
    res = RuleNode(astNode.getChildById("rule-id").getText(), is_grammar)
    
    for branch in astNode.getChildrenById("branch"):
        branch.setId('')
        res.add_branch(branch)
    
    return res
        
class MetaGrammar(Grammar):
    
    def __init__(self):
        
        Grammar.__init__(self, token_types)
        
    def expand(self, start, end, context):
        
        start\
        .connect(zeroToMany(fork(
                                 _CommentRule('comment-style'),
                                 _EnableRule('enable'),
                                 _TokensRule('tokens'),
                                 _RuleRule('rule')
                                 )))\
        .connect(end)
        
    def transform(self, astNode):
        
        res = AstNode('meta-grammar')
        
        commentNodes = astNode.getChildrenById('comment-style')
        if commentNodes:
            node = AstNode('comment-styles')
            res.addChild(node)
            line = None
            block = None
            for cnode in commentNodes:
                if line and block:
                    break
                if line is None and cnode.getName() == 'line-comment':
                    cnode.setId('')
                    node.addChild(cnode)
                    line = cnode
                    continue
                if block is None and cnode.getName() == 'block-comment':
                    cnode.setId('')
                    node.addChild(cnode)
                    block = cnode
                    
        enableNodes = astNode.getChildrenById('enable')
        if enableNodes:
            node = AstNode('enable')
            for item in enableNodes:
                node.addChild(item)
            res.addChild(node)
                        
        tokensNodes = astNode.getChildrenById('tokens')
        if tokensNodes:
            node = AstNode('tokens')
            res.addChild(node)
            for tn in tokensNodes:
                for t in tn.getChildren():
                    node.addChild(t)
                    
        ruleNodes = astNode.getChildrenById('rule')
        if ruleNodes:
            node = AstNode('rules')
            res.addChild(node)
            for rn in ruleNodes:
                rn.setId('')
                node.addChild(rn)
        
        return res
