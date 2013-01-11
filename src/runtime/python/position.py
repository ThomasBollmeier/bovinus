# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class Position(object):
    
    TABSIZE = 4
    
    def __init__(self, line=1, numNonTabChars=0, numTabs=0):
        
        self._line = line
        self._numNonTabChars = numNonTabChars
        self._numTabs = numTabs
        
    def clone(self):
        
        return Position(self._line, self._numNonTabChars, self._numTabs)
        
    def updateFromChar(self, ch):
        
        if ch == "\n":
            self._line += 1
            self._numNonTabChars = 0
            self._numTabs = 0
        elif ch == "\t":
            self._numTabs += 1
        else:
            self._numNonTabChars += 1
        
    def getLine(self):
        
        return self._line
    
    line = property(getLine)
    
    def getColumn(self, tabSize=None):
        
        tsize = tabSize is not None and tabSize or Position.TABSIZE

        return 1 + self._numNonTabChars + self._numTabs * tsize
    
    column = property(getColumn)
    
    def __lt__(self, other):
        
        return self.line < other.line or self.line == other.line and self.column < other.column

    def __le__(self, other):
        
        return self.line < other.line or self.line == other.line and self.column <= other.column
    
    def __eq__(self, other):
        
        return self.line == other.line and self.column == other.column

    def __ne__(self, other):
        
        return self.line != other.line or self.column != other.column

    def __gt__(self, other):
        
        return self.line > other.line or self.line == other.line and self.column > other.column
    
    def __ge__(self, other):
        
        return self.line > other.line or self.line == other.line and self.column >= other.column
