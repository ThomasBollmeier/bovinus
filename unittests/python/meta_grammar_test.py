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

import unittest
from bovinus.parsergen.meta_parser import MetaParser
import bovinus.parsergen.meta_objects as meta_obj

class ParserTest(unittest.TestCase):

    def setUp(self):

        self._parser = MetaParser()

    def tearDown(self):

        self._parser = None

    def testAll(self):

        code = \
"""

# Tokens:

keyword FOREACH 'foreach';
keyword TRUE 'true' { case-sensitive: FALSE }
word ID '[a-zA-Z_][a-zA-Z0-9_]*';
prefix INCREMENT '++';
postfix DECREMENT '--' { escape: TRUE }
separator DOT '.' { whitespace-allowed: FALSE, is-pattern: FALSE } # <-- some properties
literal LIT; # <-- has no properties
separator MODULE_SEP '::' { whitespace-allowed: FALSE }

type_name = 
    ( module=ID MODULE_SEP )* base=ID
    ;

for_loop =
    ( 'foreach' elem=ID 'in' list=type_name 'do' | 'forall' list=type_name 'do' ) '{' (statements)* '}'
    ;

"""
        self._parser.parse_string(code)
        
        self.assertIsNotNone(self._parser._ast)
           
    def testGrammarFile(self):
        
        self._parser.parse_file("test.bovg")
        
        ast = self._parser._ast
        
        self.assertIsNotNone(ast)
        if ast:
            print(ast.toXml())
            
    def testCompile(self):
        
        symbols = self._parser.compile_file("test.bovg")
        
        self.assertIsNotNone(symbols)
        
        for token_type in symbols.get_token_types():
            print("%s: '%s'" % (token_type.token_id, token_type.text))
            
        for rule in symbols.get_rules():
            dep_info = [(r.rule_id, symbols.get_rule_deps_level(r)) for r in rule.get_rule_deps()]
            level = symbols.get_rule_deps_level(rule)
            print("%d: %s --> %s" % (level, rule.rule_id, dep_info))
                
#### Run tests #####

if __name__ == "__main__":

    unittest.main()
