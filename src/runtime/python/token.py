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

import re
from .position import Position

class Token(object):

    def __init__(self, text, types):

        self._text = text
        self._types = types
        self._start = Position()
        self._end = Position()

    def getText(self):

        return self._text

    def getTypeIds(self):

        return [type_.getId() for type_ in self._types]

    def getTypes(self):

        return self._types

    def setStartPosition(self, pos):

        self._start = pos

    def getStartPosition(self):

        return self._start.line, self._start.column
    
    def setEndPosition(self, pos):
        
        self._end = pos
        
    def getEndPosition(self):
        
        return self._end.line, self._end.column
    
    def __str__(self):
        
        type_info = ""
        for tokenType in self._types:
            if type_info:
                type_info += ", "
            if not tokenType.name:
                type_info += "{ id: %s}" % tokenType.getId()
            else:
                type_info += "{ id: %s, name: %s}" % \
                             (tokenType.getId(), tokenType.name)
            type_info = "[%s]" % type_info
        
        return self._text + " : " + type_info

class TokenType(object):

    currentId = 0

    def __init__(self):

        if self.__class__ == TokenType:
            raise AbstractInstantiationError

        TokenType.currentId += 1
        self._id = TokenType.currentId
        self.name = ""
        self._len = 0

    def getId(self):

        return self._id

    def createToken(self, text):

        raise NotImplementedError

    @staticmethod
    def compare(tokenType_1, tokenType_2):

        if tokenType_1._len > tokenType_2._len:
            return -1
        elif tokenType_1._len < tokenType_2._len:
            return 1
        else:
            return 0

    def _escape(self, text):

        for ch in ['+', '-', '*', '?', '.', '|', '(', ')', '[', ']']:
            text = text.replace(ch, '\\' + ch)

        return text

class Word(TokenType):

    def __init__(self, pattern, filterCallback=None):

        TokenType.__init__(self)

        self._regex = re.compile(r"\A(%s)\Z" % pattern)
        self._len = len(pattern)
        self._filterCb = filterCallback

    def createToken(self, text):
        
        match = self._regex.match(text)
        if match:
            if self._filterCb and not self._filterCb(text):
                return None
            return Token(match.group(1), [self])
        else:
            return None

    def matches(self, text):

        if self._regex.match(text):
            if self._filterCb and not self._filterCb(text):
                return False
            return True
        else:
            return False
        
    def setFilterCallback(self, filterCallback):
        
        self._filterCb = filterCallback

class Keyword(TokenType):

    def __init__(self, keyword, caseSensitive=True):

        TokenType.__init__(self)

        self._caseSensitive = caseSensitive
        if self._caseSensitive:
            self._keyword = keyword
        else:
            self._keyword = keyword.upper()

    def getKeyword(self):

        return self._keyword

    def isCaseSensitive(self):

        return self._caseSensitive

    def createToken(self, text):
        
        if text == self._keyword:
            return Token(text, [self])
        else:
            return None

class Literal(TokenType):

    DELIMITERS = ['\'', '\"']
    ESCAPE_CHAR = '\\'

    _single = None

    @staticmethod
    def get():

        if not Literal._single:
            Literal._single = Literal()

        return Literal._single

    def __init__(self):

        TokenType.__init__(self)

    def createToken(self, text):
        
        if self.isLiteral(text):
            return Token(text, [self])
        else:
            return None

    def isLiteral(self, text):

        if len(text) >= 2:
            first = text[0]
            return (first in Literal.DELIMITERS) and (text[-1] == first)
        else:
            return False
        
class MultiLineLiteral(TokenType):
    
    DELIMITER = '"""'
    
    _single = None
    
    @staticmethod
    def get():
        if not MultiLineLiteral._single:
            MultiLineLiteral._single = MultiLineLiteral()
        return MultiLineLiteral._single
    
    def __init__(self):
        
        TokenType.__init__(self)
        
        self._minLength = 2 * len(self.DELIMITER)
        
    def createToken(self, text):
        
        l = len(text)
        
        if l >= self._minLength:
            start = text[:len(self.DELIMITER)]
            end = text[-len(self.DELIMITER):]
            if start == self.DELIMITER and end == self.DELIMITER:
                return Token(text, [self])
            else:
                return None
        else:
            return None
        
    @staticmethod
    def isMultiLineLiteral(text):
        
        delimLen = len(MultiLineLiteral.DELIMITER)
        
        if len(text) >= 2 * delimLen:
            start = text[:delimLen]
            end = text[-delimLen:]
            return start == MultiLineLiteral.DELIMITER and end == MultiLineLiteral.DELIMITER
        else:
            return False
        
class Prefix(TokenType):

    def __init__(self, tokenText, escape=True):

        TokenType.__init__(self)

        if escape:
            tmp = self._escape(tokenText)
        else:
            tmp = tokenText

        regexStr = r"\A(%s)(\S+)\Z" % tmp
        self._regex = re.compile(regexStr)
        self._len = len(tokenText)

    def createToken(self, text):
        
        match = self._regex.match(text)

        if match:
            return Token(match.group(1), [self])
        else:
            return None

    def getRemainingRight(self, text):

        match = self._regex.match(text)

        if match:
            return match.group(2) or ""
        else:
            return ""

class Postfix(TokenType):

    def __init__(self, tokenText, escape=True):

        TokenType.__init__(self)

        if escape:
            tmp = self._escape(tokenText)
        else:
            tmp = tokenText

        regexStr = r"\A(\S+)(%s)\Z" % tmp
        self._regex = re.compile(regexStr)
        self._len = len(tokenText)

    def createToken(self, text):

        match = self._regex.match(text)

        if match:
            return Token(match.group(2), [self])
        else:
            return None

    def getRemainingLeft(self, text):

        match = self._regex.match(text)

        if match:
            return match.group(1) or ""
        else:
            return ""

class Separator(TokenType):

    @staticmethod
    def create(pattern):

        res = Separator('')
        res._regex = re.compile(pattern)
        res._regexIgnoreWS = res._regex
        res._len = len(pattern)

        return res

    def __init__(self, tokenText, whitespaceAllowed=True, escape=True):

        TokenType.__init__(self)

        if escape:
            tmp = self._escape(tokenText)
        else:
            tmp = tokenText

        if whitespaceAllowed:
            regexStr = tmp
            self._regex = re.compile(regexStr)
            self._regexIgnoreWS = self._regex
        else:
            regexStr = "(?<=\S)" + tmp + "(?=\S)"
            self._regex = re.compile(regexStr)
            self._regexIgnoreWS = re.compile(tmp)
            
        self._len = len(tokenText)

    def createToken(self, text):

        match = self._regex.match(text)

        if match:
            return Token(text[match.start():match.end()], [self])
        else:
            return None
        
    def getRegex(self):
        
        return self._regex
    
    def getRegexIgnoreWS(self):
        """
        The tokenizer requires a regular expression
        that does ignore the no-whitespace-allowed 
        restriction. Otherwise the input stream may not 
        be correctly split into tokens 
        """
        return self._regexIgnoreWS

class AbstractInstantiationError(Exception):
    pass
