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

class InStream(object):

    def __init__(self):
        pass

    def getNextChar(self):
        return ''

    def endOfInput(self):
        return True

class StringInput(InStream):

    def __init__(self, text):

        InStream.__init__(self)

        self._text = text
        self._idx = 0

    def getNextChar(self):

        if not self.endOfInput():
            res = self._text[self._idx]
            self._idx += 1
            return res
        else:
            return ''

    def endOfInput(self):

        return self._idx >= len(self._text)

class FileInput(InStream):

    def  __init__(self, filePath):

        InStream.__init__(self)

        self._filePath = filePath
        self._lines = None

    def endOfInput(self):

        if self._lines is None:
            self._read()

        if self._curLineNum >= len(self._lines):
            return True
        else:
            line = self._lines[self._curLineNum]
            return self._curColumn >= len(line)

    def getNextChar(self):

        if self._lines is None:
            self._read()

        if not self.endOfInput():
            line = self._lines[self._curLineNum]
            res = line[self._curColumn]
            self._next()
            return res
        else:
            return ''

    def _next(self):

        line = self._lines[self._curLineNum]
        self._curColumn += 1
        if self._curColumn >= len(line):
            self._curLineNum += 1
            self._curColumn = 0

    def _read(self):

        f = open(self._filePath, "r")
        self._lines = f.readlines()
        f.close()
        self._curLineNum = 0
        self._curColumn = 0
