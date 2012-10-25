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

from bovinus.token import *
from bovinus.grammar import Grammar, defineRule, expand, transform, tokenNode as tn, connector
from bovinus.parser import AstNode

token_types = []

def register_token_type(tt):
    
    token_types.append(tt)
    
    return tt
    
def register_keyword(keyword):
    
    return register_token_type(Keyword(keyword))

# Define token types:

ID = register_token_type(Word("[_a-zA-z][_a-zA-Z0-9]*"))
FOREACH = register_keyword("foreach")
FORALL = register_keyword("forall")
IN = register_keyword("in")
BRACE_OPEN = register_token_type(Separator("{"))
BRACE_CLOSE = register_token_type(Separator("}"))

# Rules

ForRule = defineRule("For")

@expand(ForRule)
def for_expand(start, end, context):

    _hlp = connector()

    start\
    .connect(tn(FORALL))\
    .connect(tn(ID, 'list'))\
    .connect(_hlp)

    start\
    .connect(tn(FOREACH))\
    .connect(tn(ID, 'element'))\
    .connect(tn(IN))\
    .connect(tn(ID, 'list'))\
    .connect(_hlp)

    _hlp\
    .connect(tn(BRACE_OPEN))\
    .connect(tn(BRACE_CLOSE))\
    .connect(end)

@transform(ForRule)
def for_transform(astNode):

    res = AstNode("for")
    res.addChild(AstNode("list-var", astNode.getChildById("list").getText()))

    tmp  = astNode.getChildById("element")
    if tmp:
        res.addChild(AstNode("element-var", tmp.getText()))

    return res

class TestGrammar(Grammar):

    def __init__(self):

        Grammar.__init__(self, token_types)

    def expand(self, start, end, context):

        start.connect(ForRule()).connect(start)
        start.connect(end)

    def transform(self, astNode):

        return astNode
