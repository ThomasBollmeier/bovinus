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
from runtime.python.parser import Parser, TreeCatg
from runtime.python.position import Position
from grammar import TestGrammar

class ParserTest(unittest.TestCase):

    def setUp(self):
        
        self._parser = Parser(TestGrammar())
        self._parser.enableBlockComments()
        self._parser.enableFullBacktracking()
        
        Position.setTabSize(4)
        
    def tearDown(self):
        
        self._parser = None
        
    def testPositionInfo(self):
        
        filePath = os.path.abspath(os.path.dirname(__file__)) + os.sep + "testcode"
        
        root = self._parser.parseFile(filePath, TreeCatg.PARSE_TREE)
        
        print(root.toXml())
        
        children = root.getChildren()
        for1 = children[0]
        for2 = children[1]
        
        self._checkNode(for1.getChildren()[0], 1, 1, 1, 8)
        self._checkNode(for1.getChildren()[1], 1, 9, 1, 14)
        self._checkNode(for2.getChildren()[1], 6, 13, 6, 18)
        
    def _checkNode(self, node, expStartLine, expStartCol, expEndLine, expEndCol):

        line, col = node.getToken().getStartPosition()
        self.assertEqual(line, expStartLine)
        self.assertEqual(col, expStartCol)
        
        line, col = node.getToken().getEndPosition()
        self.assertEqual(line, expEndLine)
        self.assertEqual(col, expEndCol)
        
if __name__ == "__main__":
    
    unittest.main()

