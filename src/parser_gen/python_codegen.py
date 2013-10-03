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

from bovinus.parsergen.output import AbstractCodeGenerator
from bovinus.parsergen.edit_sections import EditableSections
from bovinus.parsergen.ast import Multiplicity
from bovinus.parsergen.meta_objects import TokenType, Grammar

class PythonCodeGenerator(AbstractCodeGenerator):
    
    VAR_ALL_TOKEN_TYPES = "all_token_types"
    
    def __init__(self):
        
        AbstractCodeGenerator.__init__(self, PythonEditableSections())
        
        self._first_token_def = True
        self._sort_token_types = False
        
    def _create_default_comment(self):
        
        res = []
        self._add(res, "# This file has been generated by Bovinus from a grammar file.")
        self._add(res, "# (See http://bovinus.bollmeier.de for details)")
        self._add(res, "# All changes outside of editable sections will be overwritten.")
        self._add(res)
                
        return res

    def _create_top_section(self, symbols):

        res = []
        self._add(res, "import bovinus.token as token")
        self._add(res, "import bovinus.grammar as grammar")
        self._add(res, "import bovinus.parser as parser")
        self._add(res, "from bovinus.parser import AstNode")
        self._add(res)
        self._insert_editable_section(res, "init")
        
        return res        
    
    def _create_single_parser_code(self, grammar, symbols):
        
        res = []
        
        self._add(res, "class %sParser(parser.Parser):" % self._to_camel_case(grammar.rule_id))
        self._add(res)
        
        self._indent()
        self._add(res, "def __init__(self):")
        
        self._indent()
        self._add(res)
        self._add(res, "parser.Parser.__init__(self, %s())" % self._rule_class_name(grammar))
        self._add(res)
        line_comment = symbols.get_line_comment()
        if line_comment:
            self._add(res, "self.enableLineComments(%s)" % line_comment)  
        block_comment = symbols.get_block_comment()
        if block_comment:
            self._add(res, "self.enableBlockComments(%s, %s)" % block_comment)
        bt = symbols.is_full_backtracking_enabled()
        if bt:
            self._add(res, "self.enableFullBacktracking(True)")
        if line_comment or block_comment or bt:
            self._add(res)
        self._dedent()
        
        self._dedent()        
        
        return res
    
    def _create_token_type_def(self, ttype):

        res = []
        
        if self._first_token_def:
            self._add(res, "# ========== Private section ==========")
            self._add(res)
            self._add(res, self.VAR_ALL_TOKEN_TYPES + " = []")
            self._add(res)
            self._first_token_def = False

        if ttype.token_type == TokenType.KEYWORD:
            line = "%s = token.Keyword('%s', caseSensitive=%s)" % (ttype.token_id, ttype.text, ttype.case_sensitive)
            self._add(res, line) 
        elif ttype.token_type == TokenType.WORD:
            if not ttype.filter_callback:
                line = "%s = token.Word('%s')" % (ttype.token_id, ttype.text)
            else:
                line = "%s = token.Word('%s', filterCallback=%s)" % (ttype.token_id, ttype.text, ttype.filter_callback)
            self._add(res, line)
        elif ttype.token_type == TokenType.PREFIX:
            line = "%s = token.Prefix('%s', escape=%s)" % (ttype.token_id, ttype.text, ttype.escape)
            self._add(res, line)
        elif ttype.token_type == TokenType.POSTFIX:
            line = "%s = token.Postfix('%s', escape=%s)" % (ttype.token_id, ttype.text, ttype.escape)
            self._add(res, line)
        elif ttype.token_type == TokenType.SEPARATOR:
            if not ttype.is_pattern:
                line = "%s = token.Separator('%s', whitespaceAllowed=%s, escape=%s)" % \
                (ttype.token_id, ttype.text, ttype.whitespace_allowed, ttype.escape)
            else:
                line = "%s = token.Separator.create('%s')" % (ttype.token_id, ttype.text)
            self._add(res, line)
        elif ttype.token_type == TokenType.LITERAL:
            line = "%s = token.Literal.get()" % ttype.token_id
            self._add(res, line)
        elif ttype.token_type == TokenType.TEXT_BLOCK:
            line = "%s = token.MultiLineLiteral.get()" % ttype.token_id
            self._add(res, line)
        else:
            raise Exception("Unknown token type")
        
        line = "%s.name = '%s'" % (ttype.token_id, ttype.token_id)
        self._add(res, line)
        
        self._add(res, "%s.append(%s)" % (self.VAR_ALL_TOKEN_TYPES, ttype.token_id))
        self._add(res)
        
        return res
        
    def _create_rule_begin(self, rule):
        
        res = []
        
        is_grammar = isinstance(rule, Grammar)
        
        if not is_grammar:
            self._add(res, "class %s(grammar.Rule):" % self._rule_class_name(rule))
        else:
            self._add(res, "class %s(grammar.Grammar):" % self._rule_class_name(rule))
        self._add(res)

        self._indent()

        if not is_grammar:
            self._add(res, "def __init__(self, ident=''):")
            self._add(res)
            self._indent()
            self._add(res, "grammar.Rule.__init__(self, '%s', ident)" % rule.rule_id)
        else:
            self._add(res, "def __init__(self):")
            self._add(res)
            self._indent()
            self._add(res, "grammar.Grammar.__init__(self, %s)" % self.VAR_ALL_TOKEN_TYPES)
        self._add(res)
        self._add(res, "self.setContextIndependent()")
        self._add(res)
        self._dedent()
                
        return res

    def _create_rule_expand_method(self, top_branch_names):
        
        res = []
        self._add(res, "def expand(self, start, end, context):")
        self._indent()
        
        self._add(res)
        for name in top_branch_names:
            self._add(res, "start.connect(self.%s()).connect(end)" % name)
        self._add(res)
                
        self._dedent()

        return res

    def _create_rule_transform_method(self, rule):
        
        res = []
        self._add(res, "def transform(self, astNode):")
        self._indent()

        self._add(res)
        
        section_name = "%s-transform" % rule.rule_id
        default_lines = ["", "return astNode", ""]

        self._insert_editable_section(res, section_name, default_lines)
        
        self._dedent()
                
        return res
    
    def _create_sequence_code(self, name, subrule_names):
        
        res = []
        
        self._add(res, "def %s(self):" % name)
        self._indent()
        self._add(res)
        
        num_subrules = len(subrule_names)
        
        if num_subrules != 1:
            self._add(res, "elements = []")
            for subrule_name in subrule_names:
                self._add(res, "elements.append(self.%s())" % subrule_name)
            self._add(res)
            self._add(res, "return grammar.Sequence(elements)")
        else:
            self._add(res, "return self.%s()" % subrule_names[0])
            
        self._add(res)
        self._dedent()
        
        return res
                
    def _create_fork_code(self, name, subrule_names, multiplicity):
        
        res = []
        
        self._add(res, "def %s(self):" % name)
        self._indent()
        self._add(res)
        
        num_subrules = len(subrule_names)
        
        if num_subrules != 1:
            self._add(res, "branches = []")
            for subrule_name in subrule_names:
                self._add(res, "branches.append(self.%s())" % subrule_name)
            self._add(res)
            result_str = "grammar.Fork(branches)"
        else:
            result_str = "self.%s()" % subrule_names[0]
            
        result_str = self._result_with_mult(result_str, multiplicity)
                    
        self._add(res, "return %s" % result_str)
        self._add(res)
        self._dedent()
        
        return res
    
    def _create_subrule_code(self, name, rule, element_id, multiplicity):
        
        res = []
        
        self._add(res, "def %s(self):" % name)
        self._indent()
        self._add(res)
        result_str = "%s(" % self._rule_class_name(rule)
        if element_id:
            result_str += "'%s'" % element_id
        result_str += ')'
        result_str = self._result_with_mult(result_str, multiplicity)
        self._add(res, "return " + result_str)
        self._add(res)
        self._dedent()
        
        return res

    def _create_token_type_code(self, name, token_type, element_id, multiplicity):
        
        res = []
        
        self._add(res, "def %s(self):" % name)
        self._indent()
        self._add(res)
        result_str = "grammar.tokenNode(%s" % token_type.token_id
        if element_id:
            result_str += ", '%s'" % element_id
        result_str += ')'
        result_str = self._result_with_mult(result_str, multiplicity)
        self._add(res, "return " + result_str)
        self._add(res)
        self._dedent()
        
        return res

    def _create_rule_end(self, rule):
        
        self._dedent()
        
        return []

    def _create_bottom_section(self, symbols):
        
        return []
    
    def _rule_class_name(self, rule):
        
        res = self._to_camel_case(rule.rule_id)
            
        if not isinstance(rule, Grammar):
            res += "Rule"
        else:
            res += "Grammar"
            
        res = "_" + res
            
        return res
    
    def _to_camel_case(self, name):
        
        res = ""
        
        prev = ""
        for ch in name:
            if prev:
                if ch not in ['-', '_']:
                    if prev not in ['-', '_']:
                        res += ch
                    else:
                        res += ch.upper()
            else:
                res += ch.upper()
            prev = ch
            
        return res

    def _result_with_mult(self, res_str, mult):

        if mult == Multiplicity.ZERO_TO_ONE:
            return "grammar.zeroToOne(%s)" % res_str
        elif mult == Multiplicity.ZERO_TO_MANY:
            return "grammar.zeroToMany(%s)" % res_str
        elif mult == Multiplicity.ONE_TO_MANY:
            return "grammar.oneToMany(%s)" % res_str
        else:
            return res_str

class PythonEditableSections(EditableSections):

    def __init__(self):

        EditableSections.__init__(
            self,
            r"\s*#\s+edit-section\s+([\w\-]+)\s+{\s*",
            r"\s*#\s+}\s+edit-section-end\s*"
            )

    def _create_section_begin(self, section_name):

        return "# edit-section %s {" % section_name

    def _create_section_end(self, section_name):

        return "# } edit-section-end"
