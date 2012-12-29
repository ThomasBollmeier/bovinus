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

from bovinus.parser import AstNode

class PropertiesNode(AstNode):
    
    def __init__(self):
        
        AstNode.__init__(self, name = 'properties')
        
    def add_property(self, name, value):
        
        prop = AstNode('property')
        prop.addChild(AstNode('name', name))
        prop.addChild(AstNode('value', value))
        
        self.addChild(prop)
        
    def get_property(self, name):
        
        for prop in self.getChildren():
            nameNode = prop.getChild('name')
            if nameNode.getText() == name:
                return prop.getChild('value').getText()
            
        raise PropertyNotFound 
    
class PropertyNotFound(Exception):
    pass
        
class TokenNode(AstNode):
    
    def __init__(self, name, token_id):
        
        AstNode.__init__(self, name)
        self.addChild(AstNode('token-id', token_id))
        
    def _get_token_id(self):
        
        return self.getChild('token-id').getText()
    
    token_id = property(_get_token_id)
    
    def _get_boolean_property(self, name, default = True):
        
        node = self.getChild('properties')
        if not node:
            return default
        else:
            try:
                return ( node.get_property(name) == 'yes' )
            except PropertyNotFound:
                return default
            
    def _get_text_node(self):
        
        return self.getChild('text')
            
    def _get_text_content(self):
        
        node = self._get_text_node()
        return node and node.getText() or ''
    
    text_content = property(_get_text_content)
                
class KeywordNode(TokenNode):
    
    def __init__(self, token_id, text, propertiesNode=None):
        
        TokenNode.__init__(self, 'keyword', token_id)
        self.addChild(AstNode('text', text))
        if propertiesNode:
            self.addChild(propertiesNode)
            
    def _is_case_sensitive(self):
        
        return self._get_boolean_property('case-sensitive')
            
    case_sensitive = property(_is_case_sensitive)
        
class WordNode(TokenNode):
    
    def __init__(self, token_id, pattern, propertiesNode=None):
        
        TokenNode.__init__(self, 'word', token_id)
        self.addChild(AstNode('pattern', pattern))
        if propertiesNode:
            self.addChild(propertiesNode)
            
    def _get_text_node(self):
        
        return self.getChild('pattern')
    
    def _get_filter_callback(self):
        
        props = self.getChild('properties')
        if props:
            try:
                return props.get_property('filter-callback')
            except PropertyNotFound:
                return ""
        else:
            return ""
        
    filter_callback = property(_get_filter_callback)

class PrefixNode(TokenNode):
    
    def __init__(self, token_id, text, propertiesNode=None):
        
        TokenNode.__init__(self, 'prefix', token_id)
        self.addChild(AstNode('text', text))
        if propertiesNode:
            self.addChild(propertiesNode)
            
    def _get_escape(self):
        
        return self._get_boolean_property('escape')
    
    escape = property(_get_escape)

class PostfixNode(TokenNode):
    
    def __init__(self, token_id, text, propertiesNode=None):
        
        TokenNode.__init__(self, 'postfix', token_id)
        self.addChild(AstNode('text', text))
        if propertiesNode:
            self.addChild(propertiesNode)

    def _get_escape(self):
        
        return self._get_boolean_property('escape')
    
    escape = property(_get_escape)
        
class SeparatorNode(TokenNode):
    
    def __init__(self, token_id, text, propertiesNode=None):
        
        TokenNode.__init__(self, 'separator', token_id)
        self.addChild(AstNode('text', text))
        if propertiesNode:
            self.addChild(propertiesNode)

    def _get_escape(self):
        
        return self._get_boolean_property('escape')
    
    escape = property(_get_escape)
    
    def _is_pattern(self):
        
        return self._get_boolean_property('pattern', False)
    
    is_pattern = property(_is_pattern)
    
    def _ws_allowed(self):
        
        return self._get_boolean_property('ws-allowed')
    
    ws_allowed = property(_ws_allowed)

class LiteralNode(TokenNode):
    
    def __init__(self, token_id):
        
        TokenNode.__init__(self, 'literal', token_id)
        
    def _get_text_node(self):
        
        return None
        
class RuleNode(AstNode):
    
    def __init__(self, rule_id, is_grammar=False):
        
        AstNode.__init__(self, is_grammar and 'grammar' or 'rule')
        self.addChild(AstNode('rule-id', rule_id))
        
    def add_branch(self, branch_node):
        
        self.addChild(branch_node)
        
    def get_rule_id(self):
        
        return self.getChild('rule-id').getText()
    
    rule_id = property(get_rule_id)
    
    def get_branches(self):
        
        return self.getChildrenByName('branch')
    
class Multiplicity:
    
    NONE = 1
    ZERO_TO_ONE = 2
    ZERO_TO_MANY = 3
    ONE_TO_MANY = 4   

    ZERO_TO_ONE_STR = "0..1"
    ZERO_TO_MANY_STR = "0..*"
    ONE_TO_MANY_STR = "1..*"   
       
class Visitor(object):
    
    def __init__(self):
        
        pass
    
    def visit_line_comment(self, 
                           begin_literal
                           ):
        
        pass

    def visit_block_comment(self, 
                            begin_literal, 
                            end_literal
                            ):
        
        pass
    
    def visit_enable_full_backtracking(self):
        
        pass
    
    def visit_keyword(self, 
                      keyword_id, 
                      text, 
                      is_case_sensitive
                      ):
        
        pass

    def visit_word(self, 
                   word_id, 
                   pattern,
                   filter_callback
                   ):
        
        pass
    
    def visit_prefix(self, 
                     prefix_id, 
                     text, 
                     escape
                     ):
        
        pass

    def visit_postfix(self, 
                      postfix_id, 
                      text, 
                      escape
                      ):
        
        pass
    
    def visit_separator(self, 
                        separator_id, 
                        text,
                        is_pattern,
                        escape,
                        whitespace_allowed
                        ):
        
        pass
    
    def visit_literal(self, 
                      literal_id
                      ):
        
        pass
    
    def enter_rule(self,
                   rule_id,
                   is_grammar_root
                   ):
        
        pass
    
    def exit_rule(self):
        
        pass
    
    def enter_branch(self):
        
        pass
    
    def exit_branch(self):
        
        pass

    def visit_token_element(self, 
                            token_id,
                            element_id,
                            multiplicity
                            ):
        
        pass
    
    def visit_rule_element(self, 
                           rule_id,
                           element_id, 
                           multiplicity
                           ):
        
        pass
    
    def visit_inline_keyword_def(self,
                                 keyword_text,
                                 element_id,
                                 multiplicity
                                 ):
        
        pass
    
    def enter_group(self,
                    multiplicity
                    ):
        
        pass
    
    def exit_group(self):
        
        pass
    
class AstTraverser(object):
    
    def __init__(self, ast):
        
        self._root = ast
    
    def walk(self, visitor):
        
        comment_styles = self._root.getChild('comment-styles')
        enablements = self._root.getChild('enable')
        tokens = self._root.getChild('tokens')
        rules = self._root.getChild('rules')

        self._walk_comment_styles(comment_styles, visitor)
        self._walk_enablements(enablements, visitor)        
        self._walk_tokens(tokens, visitor)
        self._walk_rules(rules, visitor)
        
    def _walk_comment_styles(self, comment_styles, visitor):
        
        if not comment_styles:
            return
        
        for child in comment_styles.getChildren():
            name = child.getName()
            if name == 'line-comment':
                begin = child.getChild('begin').getText()
                visitor.visit_line_comment(begin)
            elif name == 'block-comment':
                begin = child.getChild('begin').getText()
                end = child.getChild('end').getText()
                visitor.visit_block_comment(begin, end)
                
    def _walk_enablements(self, enablements, visitor):
        
        if not enablements:
            return
        
        for item in enablements.getChildren():
            name = item.getName()
            if name == 'full-backtracking':
                visitor.visit_enable_full_backtracking()
            
    def _walk_tokens(self, tokens, visitor):
        
        for child in tokens.getChildren():
            
            name = child.getName()
            
            if name == 'keyword':
                self._walk_keyword(child, visitor)
            elif name == 'word':
                self._walk_word(child, visitor)
            elif name == 'prefix':
                self._walk_prefix(child, visitor)
            elif name == 'postfix':
                self._walk_postfix(child, visitor)
            elif name == 'separator':
                self._walk_separator(child, visitor)
            elif name == 'literal':
                self._walk_literal(child, visitor)
    
    def _walk_keyword(self, keyword, visitor):
        
        visitor.visit_keyword(keyword.token_id, 
                              keyword.text_content,
                              keyword.case_sensitive 
                              )
    
    def _walk_word(self, word, visitor):
        
        visitor.visit_word(word.token_id, word.text_content, word.filter_callback)
        
    def _walk_prefix(self, prefix, visitor):
        
        visitor.visit_prefix(prefix.token_id, prefix.text_content, prefix.escape)

    def _walk_postfix(self, postfix, visitor):
        
        visitor.visit_postfix(postfix.token_id, postfix.text_content, postfix.escape)

    def _walk_separator(self, separator, visitor):
        
        visitor.visit_separator(separator.token_id,
                                separator.text_content,
                                separator.is_pattern,
                                separator.escape,
                                separator.ws_allowed
                                )

    def _walk_literal(self, literal, visitor):
        
        visitor.visit_literal(literal.token_id)
        
    def _walk_rules(self, rules, visitor):
        
        for child in rules.getChildren():
            self._walk_rule(child, visitor)
            
    def _walk_rule(self, rule, visitor):

        is_grammar_root = rule.getName() == 'grammar'
        
        visitor.enter_rule(rule.rule_id, is_grammar_root)
        
        for branch in rule.get_branches():
            self._walk_branch(branch, '', visitor)
        
        visitor.exit_rule()
        
    def _walk_branch(self, branch, group_id, visitor):
        
        visitor.enter_branch()
        
        for elem in branch.getChildrenByName('element'):
            self._walk_element(elem, group_id, visitor)
        
        visitor.exit_branch()
        
    def _walk_element(self, element, group_id, visitor):
        
        multNode = element.getChild('multiplicity')
        if multNode:
            tmp = multNode.getText()
            if tmp == Multiplicity.ZERO_TO_ONE_STR:
                mult = Multiplicity.ZERO_TO_ONE
            elif tmp == Multiplicity.ZERO_TO_MANY_STR:
                mult = Multiplicity.ZERO_TO_MANY
            elif tmp == Multiplicity.ONE_TO_MANY_STR:
                mult = Multiplicity.ONE_TO_MANY
        else:
            mult = Multiplicity.NONE
            
        idNode = element.getChild('id')
        if idNode:
            elem_id = idNode.getText()
        else:
            elem_id = group_id
            
        while True:
            
            node = element.getChild('token-id')
            if node:
                visitor.visit_token_element(node.getText(), elem_id, mult)
                break
        
            node = element.getChild('rule-id')
            if node:
                visitor.visit_rule_element(node.getText(), elem_id, mult)
                break
            
            node = element.getChild('keyword-text')
            if node:
                visitor.visit_inline_keyword_def(node.getText(), elem_id, mult)
                break
            
            node = element.getChild('group')
            if node:
                self._walk_group(node, elem_id, mult, visitor)
                break
            
            raise Exception("Unknown element")
        
    def _walk_group(self, group, group_id, mult, visitor):
        
        visitor.enter_group(mult)
        
        for branch in group.getChildren():
            self._walk_branch(branch, group_id, visitor)
            
        visitor.exit_group()
        