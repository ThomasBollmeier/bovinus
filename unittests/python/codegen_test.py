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
import os
from bovinus.parsergen.meta_parser import MetaParser
from bovinus.parsergen.output import StdOut, FileOut, CodeWriter
from bovinus.parsergen.python_codegen import PythonCodeGenerator
from bovinus.parsergen.js_codegen import JSCodeGenerator

TEST_GRAMMAR_FILE="test.bovg"

class CodeGenTest(unittest.TestCase):

    def setUp(self):

        self._parser = MetaParser()
        self._generated_file = "" 

    def tearDown(self):

        self._parser = None
        if self._generated_file:
            try:
                os.remove(self._generated_file)
            except:
                pass
        
    def testPythonCode(self):
        
        symbols = self._parser.compile_file(TEST_GRAMMAR_FILE)
        
        self.assertIsNotNone(symbols)
        
        codegen = PythonCodeGenerator()
        output = StdOut()
        
        CodeWriter(symbols, codegen).write(output)
        
    def testPythonRuntime(self):
        
        symbols = self._parser.compile_file(TEST_GRAMMAR_FILE)
        
        self.assertIsNotNone(symbols)
        
        self._generated_file = "godl_parser.py"
        
        codegen = PythonCodeGenerator()
        output = FileOut(self._generated_file)
        
        output.open_file()
        CodeWriter(symbols, codegen).write(output)
        output.close_file()
        
        from godl_parser import GodlParser
        
        parser = GodlParser()
        
        self.assertIsNotNone(parser)
        
        code = """
/* GODL example code */

include "some_external_defs.goc";

package demo {

    gobject Person { // <-- a class
    
        Person { }
        
        method do_something {
            result { type: string; }
            parameter error { type: ref(ref(GError)); }
        }
    
    }

}
        """
        
        try:
            ast = parser.parseString(code)
        except Exception as error:
            self.fail(str(error))
            
        self.assertIsNotNone(ast)
        
        print(ast.toXml())
        
    def testPythonRT_2(self):
        
        symbols = self._parser.compile_file("text_block_test.bovg")
        
        self.assertIsNotNone(symbols)
        
        self._generated_file = "demo_parser.py"
        
        codegen = PythonCodeGenerator()
        
        output = FileOut(self._generated_file)
        
        output.open_file()
        CodeWriter(symbols, codegen).write(output)
        output.close_file()
        
        from demo_parser import TextblockParser
        
        parser = TextblockParser()
        
        self.assertIsNotNone(parser)
        
        code = '''
# Test
var hello;
var world = 'World';
var text = """
This is a long
text block. It
stretches over 
several lines...""";
'''
        
        try:
            ast = parser.parseString(code)
        except Exception as error:
            self.fail(str(error))
            
        self.assertIsNotNone(ast)
        
        print(ast.toXml())
    
    def testJavaScriptCode(self):
        
        symbols = self._parser.compile_file(TEST_GRAMMAR_FILE)
        
        self.assertIsNotNone(symbols)
        
        codegen = JSCodeGenerator()
        output = StdOut()
        
        CodeWriter(symbols, codegen).write(output)
                        
#### Run tests #####

if __name__ == "__main__":

    unittest.main()
