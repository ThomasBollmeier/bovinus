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
import sys
import os

from runtime.python.token import Literal, Word, Separator, MultiLineLiteral
from runtime.python.lexer import Lexer
from runtime.python.instream import StringInput, FileInput

class LexerTest(unittest.TestCase):

    def setUp(self):
        
        self._lexer = Lexer()
        
        self._lexer.addTokenType(Literal.get())
        self._lexer.addTokenType(MultiLineLiteral.get())
        self._lexer.addTokenType(Word('[a-zA-Z_][a-zA-Z_0-9]*'))
        self._lexer.addTokenType(Separator('('))
        self._lexer.addTokenType(Separator(')'))
        self._lexer.addTokenType(Separator(';'))
        self._lexer.addTokenType(Separator('+'))
        self._lexer.addTokenType(Separator('='))
        self._lexer.addTokenType(Separator('.', whitespaceAllowed=False))
        
        self._lexer.enableLineComments('#')
        
    def tearDown(self):

        self._lexer = None

    def testSeparatorInLiteral(self):
        
        code = "'1.23 '.toNumber();"
        self._lexer.setInputStream(StringInput(code))
        
        tokens = []
        
        token = self._lexer.getNextToken()
        while token:
            tokens.append(token)
            token = self._lexer.getNextToken()
            
        self._print(code, tokens)
   
        self.assertIsNot(tokens, [])
        self.assertEqual(len(tokens), 6)

    def testSeparatorBetweenLiterals(self):
        
        code = "'1.23'+'4.56';"
        self._lexer.setInputStream(StringInput(code))
        
        tokens = []
        
        token = self._lexer.getNextToken()
        while token:
            tokens.append(token)
            token = self._lexer.getNextToken()

        self._print(code, tokens)    
            
        self.assertIsNot(tokens, [])
        self.assertEqual(len(tokens), 4)
        
    def testNoWSAllowedSeperator(self):
        
        code = "person.getAddress().street"
        self._lexer.setInputStream(StringInput(code))
        
        tokens = []
        
        token = self._lexer.getNextToken()
        while token:
            tokens.append(token)
            token = self._lexer.getNextToken()

        self._print(code, tokens)    
            
        self.assertIsNot(tokens, [])
        self.assertEqual(len(tokens), 7)
        
        lastText = tokens[-1].getText()
        self.assertEqual(lastText, "street")
        
    def testMultLineLiterals(self):
        
        print("Multi-Line-Literals:")
        
        self._lexer.setInputStream(FileInput("multi-line-lit.txt"))

        token = self._lexer.getNextToken()
        while token:
            print(token.getText(), token.getTypes())
            token = self._lexer.getNextToken()
                
    def _print(self, code, tokens):

        print("code: %s" % code)
        print()

        for t in tokens:
            print(t.getText(), t.getTypes())
        print()

#### Run tests #####

if __name__ == "__main__":
    
    unittest.main()
