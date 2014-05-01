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

import os
from bovinus.parsergen.meta_objects import Branch, TokenType, Rule, Group

class CodeWriter(object):
    
    def __init__(self, symbols, codegen):
        
        self._symbols = symbols
        self._codegen = codegen
    
    def write(self, output):
        
        lines = self._codegen.create_code(self._symbols)
        for line in lines:
            output.writeln(line)
        
class AbstractOutput(object):
    
    def __init__(self):
        
        if self.__class__ == AbstractOutput:
            raise Exception("Cannot instantiate abstract class")
        
    def write(self, text):
        
        raise NotImplementedError
        
    def writeln(self, line):
        
        raise NotImplementedError

class AbstractCodeGenerator(object):
    
    def __init__(self, edit_sections):
        
        if self.__class__ == AbstractCodeGenerator:
            raise Exception("Cannot instantiate abstract class")
        
        self._edit_sections = edit_sections
        self._header_comment_lines = []
        self._indent_level = 0
        self._sort_token_types = True
        self._parser_class_name = ""
        
    def create_code(self, symbols):
        
        res = []
        
        token_types = symbols.get_token_types(self._sort_token_types)
        rules = symbols.get_rules()
        
        res += self._start_code_creation()
        res += self._create_comment()
        res += self._create_top_section(symbols)
        res += self._create_parser_code(symbols)
        res += self._create_token_types_section(token_types)
        res += self._create_rules_section(rules)
        res += self._create_bottom_section(symbols)
        
        return res
    
    def init_editable_sections(self, file_path):

        self._edit_sections.init_from_file(file_path)

    def set_editable_sections(self, sections):

        for section_name in sections:
            self._edit_sections.set_section(section_name, sections[section_name])
        
    def set_header_comment(self, lines):
        
        self._header_comment_lines = lines
        
    def set_parser_class_name(self, name):
		
        self._parser_class_name = name
        
    def _enable_token_type_sorting(self, enable):
        
        self._sort_token_types = enable

    def _insert_editable_section(self, 
                                 code_lines, 
                                 section_name, 
                                 default_lines=[]
                                 ):
        
        lines = []
        for line in default_lines:
            self._add(lines, line)
        
        edit_section_lines = self._edit_sections.get_section(section_name, lines)

        # For content that has been set externally (e.g. as embedded code in the grammar file)
        # we must create the section as read only. Otherwhise all manual changes would be 
        # overwritten the next time the parser is generated.
        external = self._edit_sections.is_section_set_externally(section_name)

        if not external:
            self._add(code_lines, edit_section_lines[0])
            tmp = self._indent_level
            self._indent_level = 0

        for line in edit_section_lines[1:-1]:
            self._add(code_lines, line)

        if not external:
            self._indent_level = tmp
            self._add(code_lines, edit_section_lines[-1])
            
        self._add(code_lines)
        
    def _start_code_creation(self):
        
        return []

    def _create_comment(self):
        
        if not self._header_comment_lines:
            return self._create_default_comment()
        else:
            res = []
            for line in self._header_comment_lines:
                self._add(res, line)
            self._add(res)
            return res

    def _create_default_comment(self):
        
        raise NotImplementedError

    def _create_top_section(self, symbols):
        
        return []
    
    def _create_parser_code(self, symbols):
        
        res = []
        
        for grammar in symbols.get_grammars():
            res += self._create_single_parser_code(grammar, symbols)
            self._add(res)
            
        return res
            
    def _create_single_parser_code(self, grammar, symbols):
        
        raise NotImplementedError
            
    def _create_token_types_section(self, token_types):
        
        res = []
        
        for ttype in token_types:
            res += self._create_token_type_def(ttype)
            
        return res
    
    def _create_token_type_def(self, token_type):
        
        raise NotImplementedError
    
    def _create_rules_section(self, rules):
        
        res = []
        
        for rule in rules:
            res += self._create_rule_code(rule)
        
        return res
    
    def _create_rule_code(self, rule):
        
        res = []
        
        self._subrules_info = self._get_subrules_info(rule)
        top_branch_names = [info_item[0] for info_item in self._subrules_info]
        
        res += self._create_rule_begin(rule)
        res += self._create_rule_expand_method(top_branch_names)
        res += self._create_rule_transform_method(rule)
        res += self._create_subrules(self._subrules_info)
        res += self._create_rule_end(rule)
        
        return res
        
    def _create_rule_begin(self, rule):
        
        raise NotImplementedError

    def _create_rule_expand_method(self, top_branch_names):
        
        raise NotImplementedError

    def _create_rule_transform_method(self, rule):
        
        raise NotImplementedError
    
    def _create_subrules(self, subrule_info):
        
        res = []
        
        for name, obj, children in subrule_info:
            
            if isinstance(obj, Branch):
                subrule_names = [child[0] for child in children]
                res += self._create_sequence_code(name, subrule_names)
                res += self._create_subrules(children)
            else:
                element_type = obj[0]
                if element_type == Branch.ELEM_GROUP:
                    subrule_names = [child[0] for child in children]
                    multiplicity = obj[2]
                    res += self._create_fork_code(name, subrule_names, multiplicity)
                    res += self._create_subrules(children)
                elif element_type == Branch.ELEM_RULE:
                    rule = obj[1]
                    element_id = obj[2]
                    multiplicity = obj[3]
                    res += self._create_subrule_code(name, rule, element_id, multiplicity)
                elif element_type == Branch.ELEM_TOKEN:
                    token_type = obj[1]
                    element_id = obj[2]
                    multiplicity = obj[3]
                    res += self._create_token_type_code(name, token_type, element_id, multiplicity)
        
        return res
    
    def _create_sequence_code(self, name, subrule_names):
        
        raise NotImplementedError
    
    def _create_fork_code(self, name, subrule_names, multiplicity):
        
        raise NotImplementedError
    
    def _create_subrule_code(self, name, rule, element_id, multiplicity):
        
        raise NotImplementedError

    def _create_token_type_code(self, name, token_type, element_id, multiplicity):
        
        raise NotImplementedError

    def _create_rule_end(self, rule):
        
        raise NotImplementedError

    def _create_bottom_section(self, symbols):
        
        return []
    
    def _get_subrules_info(self, rule):
        
        res = []
        
        for idx, branch in enumerate(rule.branches):
            name = self._subrule_name([idx])
            children = []
            res.append((name, branch, children))
            self._get_branch_info(branch, children, [idx])
            
        return res
            
    def _get_branch_info(self, branch, children, indices):
        
        for idx, element in enumerate(branch.elements):
            ename = self._subrule_name(indices + [idx])
            echildren = []
            children.append((ename, element, echildren))
            if element[0] == Branch.ELEM_GROUP:
                group = element[1]
                for bidx, b in enumerate(group.branches):
                    bname = self._subrule_name(indices + [idx, bidx])
                    bchildren = []
                    echildren.append((bname, b, bchildren))
                    self._get_branch_info(b, bchildren, indices + [idx, bidx])
    
    def _subrule_name(self, indices):
        
        res = "_sub"
        for idx in indices:
            res += "_%d" % (idx + 1)
            
        return res
        
    def _indent(self):
        
        self._indent_level += 1
        
    def _dedent(self):
        
        self._indent_level -= 1
        
    def _add(self, lines, line=""):
        
        line = self._indent_level * "\t" + line
        lines.append(line)
        
class StdOut(AbstractOutput):
    
    def __init__(self):
        
        AbstractOutput.__init__(self)
        
    def write(self, text):
        
        print(text, end='')
        
    def writeln(self, line):
        
        print(line)

class StringOut(AbstractOutput):
    
    def __init__(self):
        
        AbstractOutput.__init__(self)
        
        self.content = ""
        
    def write(self, text):
        
        self.content += text
        
    def writeln(self, line):
        
        self.content += line + os.linesep

class FileOut(AbstractOutput):
    
    def __init__(self, file_path):
        
        AbstractOutput.__init__(self)
        
        self._file_path = file_path
        
    def write(self, text):
        
        self._file.write(text)
        
    def writeln(self, line):
        
        self._file.write(line + os.linesep)
        
    def open_file(self):
        
        try:
            self._file = open(self._file_path, "w")
        except FileNotFoundError:
            gendir = os.path.abspath(os.path.dirname(self._file_path))
            os.makedirs(gendir, mode=0o755)
            self._file = open(self._file_path, "w")
                
    def close_file(self):
        
        self._file.close()
