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
    
    _TABSIZE = 4
    
    _NEW_LINE = 1
    _TAB = 2
    _OTHER_CHAR = 3
        
    def __init__(self, charGroups=None):
        
        self._charGrps = charGroups or []
        self._cloned = False
        
    def clone(self):
        
        res = Position(self._charGrps)
        res._cloned = True
        
        self._cloned = True
        
        return res
    
    @staticmethod
    def setTabSize(tabsize):
        
        Position._TABSIZE = tabsize
        
    def forwardChar(self, ch):
        
        if self._cloned:
            self._copyOnWrite()
            self._cloned = False
        
        if ch == "\n":
            catg = self._NEW_LINE
        elif ch == "\t":
            catg = self._TAB
        else:
            catg = self._OTHER_CHAR
            
        if self._charGrps:
            curGroup = self._charGrps[-1]
            if curGroup[0] == catg:
                curGroup[1] += 1
            else:
                self._charGrps.append([catg, 1])
        else:
            self._charGrps.append([catg, 1])
            
    def forward(self, text):
        
        for ch in text:
            self.forwardChar(ch)
            
    def backwardChar(self):

        if self._cloned:
            self._copyOnWrite()
            self._cloned = False

        if self._charGrps:
            lastGrp = self._charGrps[-1]
            lastGrp[1] -= 1
            if lastGrp[1] == 0:
                self._charGrps.pop()
            
    def backward(self, text):
        
        for _ in range(0, len(text)):
            self.backwardChar()
                    
    def getLine(self):
        
        return 1 + sum([grp[1] for grp in self._charGrps if grp[0] == self._NEW_LINE])
        
    line = property(getLine)
    
    def getColumn(self):
        
        curLine = []
        
        for idx in range(len(self._charGrps), 0, -1):
            grp = self._charGrps[idx-1]
            if grp[0] != self._NEW_LINE:
                curLine.insert(0, grp)
            else:
                break
            
        offset = 0
        for grp in curLine:
            if grp[0] == self._OTHER_CHAR:
                offset += grp[1]
            else:
                for _ in range(0, grp[1]):
                    offset = int(offset/self._TABSIZE + 1) * self._TABSIZE
        
        return 1 + offset
    
    column = property(getColumn)
    
    def _copyOnWrite(self):
        
        tmp = []
        for grp in self._charGrps:
            tmp.append(grp[:])
            
        self._charGrps = tmp
    
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
