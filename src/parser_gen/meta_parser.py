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

from bovinus.parser import Parser
from bovinus.parsergen.meta_grammar import MetaGrammar
from bovinus.parsergen.ast import Visitor, AstTraverser
import bovinus.parsergen.meta_objects as meta_obj

class MetaParser(object):
    
    def __init__(self):

        self._parser = Parser(MetaGrammar())
        self._parser.enableLineComments('#')
        self._parser.enableBlockComments('<!--', '-->')
        self._full_backtracking = False
        
        self._ast = None
        self._clear()
        
    def compile_string(self, content):
        
        self.parse_string(content)
        
        return self._create_symbols()
        
    def compile_file(self, file_path):
        
        self.parse_file(file_path)
        
        return self._create_symbols()
        
    def _create_symbols(self):
        
        self.analyze()
        
        return Symbols(self._symbols,
                       self._token_types,
                       self._line_comment,
                       self._block_comment,
                       {
                        "full-backtracking" : self._full_backtracking 
                        }
                       )
            
    def parse_string(self, content):
        
        self._ast = self._parser.parseString(content)
        self._clear()
        
    def parse_file(self, file_path):
        
        self._ast = self._parser.parseFile(file_path)
        self._clear()
    
    def analyze(self):
        
        if not self._ast:
            return
        
        self._clear()

        traverser = AstTraverser(self._ast)
        traverser.walk(_AnalyseStep1(self))
        traverser.walk(_AnalyseStep2(self))
        
    def _clear(self):
        
        self._symbols = {}
        self._token_types = []
        self._kw_to_token_id_map = {}
        self._line_comment = None
        self._block_comment = None
                
class Symbols(object):
    
    def __init__(self, 
                 symbol_table,
                 token_types,
                 line_comment,
                 block_comment,
                 config = {}
                 ):
        
        self._symbols = symbol_table
        self._token_types = token_types
        self._line_comment = line_comment
        self._block_comment = block_comment
        self._config = config
        
        rules = [
                 self._symbols[key] for key in self._symbols 
                 if isinstance(self._symbols[key], meta_obj.Rule) 
                ]
        self._rule_deps = _RuleDeps(rules)
        
    def get_all(self):
        
        return self._symbols

    def get_token_types(self, sort=True):
        
        res = self._token_types
                
        if sort:
            res.sort(key = lambda token_type: token_type.token_id)
                
        return res
    
    def get_rules(self, sort=True):
        
        res = [sym for sym in self._symbols.values() if isinstance(sym, meta_obj.Rule)]
        
        if sort:
            res.sort(key = lambda r: self.get_rule_deps_level(r))
            
        return res
    
    def get_grammar(self):
        
        for symbol in self._symbols.values():
            if isinstance(symbol, meta_obj.Grammar):
                return symbol
            
        return None
    
    def get_grammars(self):
        
        res = []
        
        for symbol in self._symbols.values():
            if isinstance(symbol, meta_obj.Grammar):
                res.append(symbol)
                
        return res
            
    def get_symbol(self, symbol_id):
        
        return self._symbols[symbol_id]
    
    def get_rule_deps_level(self, rule):
        
        return self._rule_deps.get_dependency_level(rule)
    
    def get_line_comment(self):
        
        return self._line_comment
    
    def get_block_comment(self):
        
        return self._block_comment
    
    def is_full_backtracking_enabled(self):
        
        try:
            return self._config["full-backtracking"]
        except KeyError:
            return False
    
    def __iter__(self):
        
        return _SymbolsIter(self._symbols)
    
class _SymbolsIter(object):
    
    def __init__(self, symdict):
        
        self._keys = [key for key in symdict]
        self._symbols = symdict
        self._idx = 0
        
    def __next__(self):
        
        if self._idx < len(self._keys):
            key = self._keys[self._idx]
            self._idx += 1
            return self._symbols[key]
        else:
            raise StopIteration
        
class _RuleDeps(object):
    
    def __init__(self, rules):
        
        self._known_levels = {}
        self._pending = {}
        
        for rule in rules:
            self.get_dependency_level(rule)
            
    def get_dependency_level(self, rule):
        
        if rule.rule_id not in self._known_levels:
            
            self._known_levels[rule.rule_id] = level = -1
            rule_deps = rule.get_rule_deps()
            cyclic_deps = []

            if rule_deps:
                
                for rule_dep in rule_deps:
                    val = self.get_dependency_level(rule_dep)
                    if val > -1:
                        if val > level:
                            level = val
                    else:
                        # cycle found:
                        cyclic_deps.append(rule_dep.rule_id)
                        
                if level > -1:
                    level += 1
            
            else:
                
                level = 0
                
            # (Level might have been determined already in recursion)
            current_level = self._known_levels[rule.rule_id]
                
            if current_level == -1 and level != current_level:
                
                self._known_levels[rule.rule_id] = level
                if level != -1:
                    for id_ in cyclic_deps:
                        self._known_levels[id_] = level
            
        return self._known_levels[rule.rule_id]
            
class _AnalyseStep1(Visitor):
    
    _ID_INLINE_KW = 1
    
    def __init__(self, analyzer):
        
        Visitor.__init__(self)
        self._symbols = analyzer._symbols
        self._kw_to_token_id_map = analyzer._kw_to_token_id_map
        self._analyzer = analyzer
        
    def visit_line_comment(self, 
                           begin_literal
                           ):
        
        self._analyzer._line_comment = begin_literal
        
    def visit_block_comment(self, 
                            begin_literal, 
                            end_literal
                            ):
        
        self._analyzer._block_comment = (begin_literal, end_literal)
        
    def visit_enable_full_backtracking(self):
        
        self._analyzer._full_backtracking = True
        
    def visit_keyword(self, 
                      keyword_id, 
                      text, 
                      is_case_sensitive
                      ):
        
        obj = meta_obj.create_keyword(keyword_id, text, is_case_sensitive)
        self._symbols[keyword_id] = obj
        self._analyzer._token_types.append(obj)

    def visit_word(self, 
                   word_id, 
                   pattern,
                   filter_callback
                   ):
        
        obj = meta_obj.create_word(word_id, pattern, filter_callback)
        self._symbols[word_id] = obj
        self._analyzer._token_types.append(obj)
    
    def visit_prefix(self, 
                     prefix_id, 
                     text, 
                     escape
                     ):
        
        obj = meta_obj.create_prefix(prefix_id, text, escape)
        self._symbols[prefix_id] = obj
        self._analyzer._token_types.append(obj)

    def visit_postfix(self, 
                      postfix_id, 
                      text, 
                      escape
                      ):
        
        obj = meta_obj.create_prefix(postfix_id, text, escape)
        self._symbols[postfix_id] = obj
        self._analyzer._token_types.append(obj)
    
    def visit_separator(self, 
                        separator_id, 
                        text,
                        is_pattern,
                        escape,
                        whitespace_allowed
                        ):
        
        obj = meta_obj.create_separator(separator_id,
                                        text,
                                        is_pattern,
                                        escape,
                                        whitespace_allowed
                                        )
        self._symbols[separator_id] = obj
        self._analyzer._token_types.append(obj)
    
    def visit_literal(self, 
                      literal_id
                      ):
        
        obj = meta_obj.create_literal(literal_id)
        self._symbols[literal_id] = obj
        self._analyzer._token_types.append(obj)
        
    def visit_text_block(self,
                         text_block_id
                         ):
        
        text_block = meta_obj.create_text_block(text_block_id)
        self._symbols[text_block_id] = text_block
        self._analyzer._token_types.append(text_block)

    def enter_rule(self,
                   rule_id,
                   is_grammar_root
                   ):
        
        if not is_grammar_root:
            obj = meta_obj.Rule(rule_id)
        else:
            obj = meta_obj.Grammar(rule_id)
        self._symbols[rule_id] = obj
    
    def visit_inline_keyword_def(self,
                                 keyword_text,
                                 element_id,
                                 multiplicity
                                 ):
        
        if keyword_text not in self._kw_to_token_id_map:
            keyword_id = self._get_next_keyword_id()
            keyword = meta_obj.create_keyword(keyword_id, keyword_text)
            self._symbols[keyword_id] = keyword
            self._analyzer._token_types.append(keyword)
            self._kw_to_token_id_map[keyword_text] = keyword_id
        
    def _get_next_keyword_id(self):
        
        while True:
            keyword_id = "KEY_%d" % self._ID_INLINE_KW
            self._ID_INLINE_KW += 1
            if keyword_id not in self._symbols:
                return keyword_id

class _AnalyseStep2(Visitor):
    
    def __init__(self, analyzer):
        
        Visitor.__init__(self)
        self._symbols = analyzer._symbols
        self._kw_to_token_id_map = analyzer._kw_to_token_id_map
        self._stack = []
         
    def enter_rule(self,
                   rule_id,
                   is_grammar_root
                   ):
        
        try:
            rule = self._symbols[rule_id]
        except KeyError:
            raise ParseError("Unknown rule '%s'" % rule_id)
        self._stack.append(rule)
    
    def exit_rule(self):
        
        self._stack.pop()
    
    def enter_branch(self):
        
        branch = meta_obj.Branch()
        self._stack.append(branch)
    
    def exit_branch(self):
        
        branch = self._stack.pop()
        self._stack[-1].add_branch(branch)

    def visit_token_element(self, 
                            token_id,
                            element_id,
                            multiplicity
                            ):
        
        branch = self._stack[-1]
        try:
            token = self._symbols[token_id]
        except KeyError:
            raise ParseError("Unknown token '%s'" % token_id)
        branch.add_token(token, element_id, multiplicity)
    
    def visit_rule_element(self, 
                           rule_id,
                           element_id, 
                           multiplicity
                           ):

        branch = self._stack[-1]
        try:
            rule = self._symbols[rule_id]
        except KeyError:
            raise ParseError("Unknown rule '%s'" % rule_id)
        branch.add_rule(rule, element_id, multiplicity)
        
    def visit_inline_keyword_def(self,
                                 keyword_text,
                                 element_id,
                                 multiplicity
                                 ):
        
        branch = self._stack[-1]
        keyword_id = self._kw_to_token_id_map[keyword_text]
        token = self._symbols[keyword_id]
        branch.add_token(token, element_id, multiplicity)
    
    def enter_group(self,
                    multiplicity
                    ):
        
        branch = self._stack[-1]
        group = meta_obj.Group()
        branch.add_group(group, multiplicity)
        self._stack.append(group)
    
    def exit_group(self):
        
        self._stack.pop()
  
class ParseError(Exception):
    
    def __init__(self, message):
        
        Exception.__init__(self)
        self._message = message
        
    def __str__(self):
        
        return self._message
