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

def create_keyword(token_id, 
                   text, 
                   case_sensitive = True
                   ):
    
    res = TokenType(TokenType.KEYWORD, token_id, text)
    res.case_sensitive = case_sensitive
    
    return res

def create_word(token_id, 
                text,
                filter_callback
                ):
    
    res = TokenType(TokenType.WORD, token_id, text)
    res.filter_callback = filter_callback
    
    return res

def create_separator(token_id, 
                     text, 
                     is_pattern = False,
                     escape = True,
                     whitespace_allowed = True
                     ):
    
    res = TokenType(TokenType.SEPARATOR, token_id, text)
    res.is_pattern = is_pattern
    res.escape = escape
    res.whitespace_allowed = whitespace_allowed
    
    return res

def create_prefix(token_id, 
                  text,
                  escape = True
                  ):

    res = TokenType(TokenType.PREFIX, token_id, text)
    res.escape = escape
    
    return res

def create_postfix(token_id, 
                   text,
                   escape = True
                   ):

    res = TokenType(TokenType.POSTFIX, token_id, text)
    res.escape = escape
    
    return res

def create_literal(token_id):

    res = TokenType(TokenType.LITERAL, token_id, "")
    
    return res

class TokenType(object):
    
    KEYWORD = 1
    WORD = 2
    SEPARATOR = 3
    PREFIX = 4
    POSTFIX = 5
    LITERAL = 6
    
    def __init__(self,
                 token_type, 
                 token_id, 
                 text
                 ):
        
        self.token_type = token_type
        self.token_id = token_id
        self.text = text
        
class _BranchContainer(object):
    
    def __init__(self):
        
        self.branches = []
    
    def add_branch(self, branch):
        
        self.branches.append(branch)

    def get_rule_deps(self):
        
        res = []
        
        for branch in self.branches:
            for rule in branch.get_rule_deps():
                if rule not in res:
                    res.append(rule)
            
        return res
        
class Rule(_BranchContainer):
    
    def __init__(self, rule_id):
        
        _BranchContainer.__init__(self)
        self.rule_id = rule_id
        
class Grammar(Rule):
    
    def __init__(self, grammar_id):
        
        Rule.__init__(self, grammar_id)
        
class Branch(object):
    
    ELEM_TOKEN = 1
    ELEM_RULE = 2
    ELEM_GROUP = 3
    
    def __init__(self):
        
        self.elements = []

    def add_token(self, token_type, element_id, multiplicity):
        
        self.elements.append((Branch.ELEM_TOKEN, token_type, element_id, multiplicity))
        
    def add_rule(self, rule, element_id, multiplicity):
        
        self.elements.append((Branch.ELEM_RULE, rule, element_id, multiplicity))
        
    def add_group(self, group, multiplicity):
        
        self.elements.append((Branch.ELEM_GROUP, group, multiplicity))
        
    def get_rule_deps(self):
        
        res = []
        
        for elem in self.elements:
            if elem[0] == Branch.ELEM_RULE:
                if elem[1] not in res:
                    res.append(elem[1])
            elif elem[0] == Branch.ELEM_GROUP:
                for rule in elem[1].get_rule_deps(): 
                    if rule not in res:
                        res.append(rule)
            
        return res
        
class Group(_BranchContainer):
    
    def __init__(self):
        
        _BranchContainer.__init__(self)
