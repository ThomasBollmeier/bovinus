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

from .util import DynamicObject
            
class InputBuffer(object):

    def __init__(self, stream, fillSize = 1):
         
        self._stream = stream
        self._fillSize = fillSize
        
        self._content = ""
        self._line = 1
        self._column = 0
            
    def setFillSize(self, newFillSize):
        
        self._fillSize = newFillSize
        
    def getContent(self):

        self._fillContent()
        
        return self._content[0:self._fillSize]

    def getPositionInfo(self):
        
        res = DynamicObject()
        res.line = self._line
        res.column = self._column
        
        return res
    
    def consumeChar(self):
        
        if self._content:
            
            ch = self._content[0]
            
            if len(self._content) > 1:
                self._content = self._content[1:]
            else:
                self._content = ""
                
            self._fillContent()
            
            self._updatePosInfo(ch)
                
            return ch
        
        else:
            
            return ""
        
    def consumeAll(self):
        
        if len(self._content) <= self._fillSize:
            
            res = self._content
            self._content = ""
            
        else:
            
            res = self._content[0:self._fillSize]
            self._content = self._content[self._fillSize:]
        
        for ch in res:
            self._updatePosInfo(ch)
                
        return res

    def _fillContent(self):

        while len(self._content) < self._fillSize:
            if self._stream.endOfInput():
                break
            self._content += self._stream.getNextChar()
            
    def _updatePosInfo(self, ch):
        
        if ch != "\n":
            self._column += 1
        else:
            self._line += 1
            self._column = 0
