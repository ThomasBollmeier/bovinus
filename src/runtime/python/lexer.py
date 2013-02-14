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
from .token import Token, Keyword, Word, Prefix, Postfix, Separator, Literal, MultiLineLiteral
from .tokenizer import Tokenizer
from .input_buffer import InputBuffer
from .util import DynamicObject

class WSCharCode:
    
    TAB = 9
    LINEBREAK =  10
    VTAB = 11
    FORMFEED = 12
    SPACE = 32

class LexerMode:
    
    NORMAL = 1
    LINE_COMMENT = 2
    BLOCK_COMMENT = 3
    WSPACE = 4
    MULTI_LINE_LIT = 5

class Lexer(object):
    
    def __init__(self):
        
        self._instream = None
        self._tokenizer = Tokenizer()
        self._stack = []
        self._keywords = {}
        self._words = []
        self._prefixes = []
        self._postfixes = []
        self._separators = []
        self._literal = None
        self._literalDelims = []
        self._literalEscChar = None
        self._currentLitDelim = ''
        self._multiLineLiteral = None
        self._wsCharCodes = [WSCharCode.TAB, 
                             WSCharCode.LINEBREAK, 
                             WSCharCode.VTAB, 
                             WSCharCode.FORMFEED, 
                             WSCharCode.SPACE]
        self._mode = LexerMode.NORMAL
        self._lineCommentEnabled = False
        self._lineCommentStart = ''
        self._blockCommentEnabled = False
        self._blockCommentStart = ''
        self._blockCommentEnd = ''
        
    def setInputStream(self, instream):
        
        self._instream = instream
        self._reset()
        
    def _reset(self):
        
        self._stack = []
        self._inputBuffer = None
        self._mode = LexerMode.NORMAL
        
    def addTokenType(self, tt):
        
        if isinstance(tt, Keyword):
            self._keywords[tt.getKeyword()] = tt
        elif isinstance(tt, Word):
            self._words.append(tt)
        elif isinstance(tt, Prefix):
            self._prefixes.append(tt)
        elif isinstance(tt, Postfix):
            self._postfixes.append(tt)
        elif isinstance(tt, Separator):
            self._separators.append(tt)
            self._tokenizer.add_separator(tt)
        elif isinstance(tt, Literal):
            self._literal = tt
            self._literalDelims = Literal.DELIMITERS
            self._literalEscChar = Literal.ESCAPE_CHAR
            self._tokenizer.set_literal(tt)
        elif isinstance(tt, MultiLineLiteral):
            self._multiLineLiteral = tt
        else:
            raise Exception('Unknown token type')
        
        return tt
        
    def enableLineComments(self, lineCommentStart = "//"):

        self._lineCommentEnabled = True
        self._lineCommentStart = lineCommentStart

    def enableBlockComments(self, 
                            blockCommentStart = "/*", 
                            blockCommentEnd = "*/"
                            ):

        self._blockCommentEnabled = True
        self._blockCommentStart = blockCommentStart
        self._blockCommentEnd = blockCommentEnd
        
    def getNextToken(self):

        if not self._instream:
            return None

        if self._stack:
            return self._stack.pop()

        if not self._inputBuffer:
            self._initBuffer()

        hlp = self._getNextChars()

        if hlp:
            tokenStr = hlp.text
            endPos = hlp.position
        else: 
            return None
        
        multiLineLit = self._multiLineLiteral and self._multiLineLiteral.createToken(tokenStr) or None
        if multiLineLit is None:
            self._stack = self._getTokens(tokenStr, endPos)
        else:
            self._stack = [multiLineLit]
        
        if self._stack:
            return self._stack.pop()
        else:
            msg = "Unknown token '" + tokenStr + "'";
            msg += " at line " + endPos.line + ", column " + endPos.column;
            raise Exception(msg)
  
    def _getNextChars(self):

        res = None

        while (True):

            content = self._inputBuffer.getContent()

            if not content:
                if self._consumed:
                    res = DynamicObject()
                    res.text = self._consumed
                    res.position = self._inputBuffer.getPositionInfo()
                self._consumed = ""
                break

            newMode = self._getNewMode(content) 

            if newMode  > 0:
                res = self._onNewMode(newMode)
                if res:
                    break;
            else:
                self._consumeContent(content)

        return res

    def _initBuffer(self):
            
        fillSize = 2 # <-- needed to detect escape chars in literals
        
        if self._multiLineLiteral:
            minlen = len(self._multiLineLiteral.DELIMITER)
            if minlen > fillSize:
                fillSize = minlen 
            
        if self._lineCommentEnabled:
            if len(self._lineCommentStart) > fillSize:
                fillSize = len(self._lineCommentStart)

        if self._blockCommentEnabled:
            if len(self._blockCommentStart) > fillSize:
                fillSize = len(self._blockCommentStart)
            if len(self._blockCommentEnd) > fillSize:
                fillSize = len(self._blockCommentEnd)
    
        self._inputBuffer = InputBuffer(self._instream, fillSize)
        self._consumed = ""

    def _getNewMode(self, content):

        res = -1
        
        if self._mode == LexerMode.NORMAL:
            if self._startsWS(content):
                res = LexerMode.WSPACE
            elif self._startsLineComment(content):
                res = LexerMode.LINE_COMMENT
            elif self._startsBlockComment(content):
                res = LexerMode.BLOCK_COMMENT
            elif self._startsMultiLineLiteral(content):
                res = LexerMode.MULTI_LINE_LIT
        elif self._mode == LexerMode.WSPACE:
            if not self._isWhiteSpace(content[0]):
                if self._startsLineComment(content):
                    res = LexerMode.LINE_COMMENT
                elif self._startsBlockComment(content):
                    res = LexerMode.BLOCK_COMMENT
                elif self._startsMultiLineLiteral(content):
                    res = LexerMode.MULTI_LINE_LIT
                else:
                    res = LexerMode.NORMAL
        elif self._mode == LexerMode.LINE_COMMENT:
            if self._endsLineComment(content):
                res = LexerMode.NORMAL
        elif self._mode == LexerMode.BLOCK_COMMENT:
            if self._endsBlockComment(content):
                res = LexerMode.NORMAL
        elif self._mode == LexerMode.MULTI_LINE_LIT:
            if self._endsMultiLineLiteral(content):
                res = LexerMode.NORMAL
 
        return res;
    
    def _startsWith(self, content, start):
        
        tmp = start.replace('*', '\\*')
        regex = re.compile(r'\A%s' % tmp)
        
        return bool(regex.match(content))

    def _startsWS(self, content):
        
        if not self._currentLitDelim:
            return ord(content[0]) in self._wsCharCodes
        else:
            return False
        
    def _startsLineComment(self, content):
        
        if self._lineCommentEnabled and not self._currentLitDelim:
            return self._startsWith(content, self._lineCommentStart)
        else:
            return False

    def _startsBlockComment(self, content):
        
        if self._blockCommentEnabled and not self._currentLitDelim:
            return self._startsWith(content, self._blockCommentStart)
        else:
            return False
        
    def _startsMultiLineLiteral(self, content):
        
        if self._multiLineLiteral:
            return self._startsWith(content, self._multiLineLiteral.DELIMITER)
        else:
            return False
        
    def _endsLineComment(self, content):
        
        if self._lineCommentEnabled and not self._currentLitDelim:
            return ord(content[0]) == WSCharCode.LINEBREAK
        else:
            return False

    def _endsBlockComment(self, content):
        
        if self._blockCommentEnabled and not self._currentLitDelim:
            return self._startsWith(content, self._blockCommentEnd)
        else:
            return False
        
    def _endsMultiLineLiteral(self, content):
        
        return self._startsMultiLineLiteral(content)

    def _onNewMode(self, newMode):

        res = None
        
        if self._mode == LexerMode.NORMAL:
            
            lenToConsume = 0
            if newMode == LexerMode.WSPACE:
                lenToConsume = 1
            elif newMode == LexerMode.LINE_COMMENT:
                lenToConsume = len(self._lineCommentStart)
            elif newMode == LexerMode.BLOCK_COMMENT:
                lenToConsume = len(self._blockCommentStart)
            elif newMode == LexerMode.MULTI_LINE_LIT:
                lenToConsume = 0
                
            savedPos = self._inputBuffer.getPositionInfo()
                
            for dummy in range(0, lenToConsume):
                self._inputBuffer.consumeChar()
            
            if self._consumed:
                res = DynamicObject()
                res.text = self._consumed
                res.position = savedPos
                
            self._consumed = ""
            if newMode == LexerMode.MULTI_LINE_LIT:
                # multi-line-literal delimiter must be kept as part of the literal 
                for _ in range(0, len(self._multiLineLiteral.DELIMITER)):
                    self._consumed += self._inputBuffer.consumeChar()
            
        elif self._mode == LexerMode.WSPACE:
            
            if newMode == LexerMode.NORMAL:
                newChar = self._inputBuffer.consumeChar()
                if newChar in self._literalDelims:
                    self._currentLitDelim = newChar
                self._consumed += newChar
            elif newMode == LexerMode.LINE_COMMENT:
                for dummy in range(0, len(self._lineCommentStart)):
                    self._inputBuffer.consumeChar()
            elif newMode == LexerMode.BLOCK_COMMENT:
                for dummy in range(0, len(self._blockCommentStart)):
                    self._inputBuffer.consumeChar()
            elif newMode == LexerMode.MULTI_LINE_LIT:
                self._consumed = ""
                for _ in range(0, len(self._multiLineLiteral.DELIMITER)):
                    self._consumed += self._inputBuffer.consumeChar()

        elif self._mode == LexerMode.LINE_COMMENT:
            self._inputBuffer.consumeChar() # <-- consume linebreak '\n'

        elif self._mode == LexerMode.BLOCK_COMMENT:
            for dummy in range(0, len(self._blockCommentEnd)):
                self._inputBuffer.consumeChar()
                
        elif self._mode == LexerMode.MULTI_LINE_LIT:
            
            for _ in range(0, len(self._multiLineLiteral.DELIMITER)):
                self._consumed += self._inputBuffer.consumeChar()
                
            res = DynamicObject()
            res.text = self._consumed
            res.position = self._inputBuffer.getPositionInfo()
            
            self._consumed = ""
                                        
        self._mode = newMode

        return res

    def _consumeContent(self, content):

        if self._mode == LexerMode.NORMAL:

            if self._literal:

                escaped = False
 
                if not self._currentLitDelim:
                    if content[0] in self._literalDelims:
                        self._currentLitDelim = content[0]
                else:
                    # Currently inside literal =>
                    # Check for escape characters and treat them separately:
                    if self._literalEscChar:
                        escChar = self._literalEscChar.replace("\\", "\\\\")
                        for delim in self._literalDelims:
                            regex = re.compile(r"\A%s%s.*" % (escChar, delim))
                            if regex.match(content):
                                escaped = True
                                break                    
                    
                    if content[0] == self._currentLitDelim:
                        self._currentLitDelim = ""
            
                if escaped:
                    self._inputBuffer.consumeChar()

                self._consumed += self._inputBuffer.consumeChar()
                
            else:

                self._consumed += self._inputBuffer.consumeChar()
                
        elif self._mode == LexerMode.MULTI_LINE_LIT:
            
            self._consumed += self._inputBuffer.consumeChar()

        else:
            
            self._inputBuffer.consumeChar()
    
    def _getTokens(self, text, endPos):
        
        res = []
        
        # Split text along separators:
        parts = self._tokenizer.split_at_separators(text)
        parts.reverse()
        
        curEndPos = endPos.clone() 
        
        for text_, sep in parts:
            if sep is not None:
                token = Token(text_, [sep])
                end = curEndPos.clone()
                start = end.clone()
                start.backward(text_)
                token.setStartPosition(start)
                token.setEndPosition(end)
                res.append(token)
            else:
                res += self._getNonSepTokens(text_, curEndPos)
            curEndPos.backward(text_)
            
        return res
            
    def _getNonSepTokens(self, text, endPos):
                
        # Handle literals:
        if self._literal:
            token = self._literal.createToken(text)
            if token:
                end = endPos.clone()
                start = end.clone()
                start.backward(text)
                token.setStartPosition(start)
                token.setEndPosition(end)
                return [token]

        res = []
        
        # Check for whitespace:
        whiteSpaceOnly = True
        for ch in text:
            if ord(ch) not in self._wsCharCodes:
                whiteSpaceOnly = False
                break
            
        if whiteSpaceOnly:
            return res

        # Find prefixes:
        for prefix in self._prefixes:

            token = prefix.createToken(text)

            if token:

                right = prefix.getRemainingRight(text) or ""

                if right:
                    res = self._getTokens(right, endPos)

                prefixEnd = endPos.clone()
                prefixEnd.backward(right)
                prefixStart = prefixEnd.clone()
                prefixStart.backward(token.getText())
                token.setStartPosition(prefixStart)
                token.setEndPosition(prefixEnd)
                
                res.append(token)

                return res

        # Find postfixes:
        for postfix in self._postfixes:

            token = postfix.createToken(text)

            if token:
                
                left = postfix.getRemainingLeft(text) or ""
                
                postfixEnd = endPos.clone()
                postfixStart = postfixEnd.clone()
                postfixStart.backward(left)
                
                token.setStartPosition(postfixStart)
                token.setEndPosition(postfixEnd)
                res = [token]

                if left:
                    res += self._getTokens(left, postfixStart)

                return res

        # Find (key)words:

        matchingWords = []

        if text in self._keywords:
            matchingWords = [self._keywords[text]]
        else:
            # perhaps case insensitive keyword?
            tmp = text.upper()
            if tmp in self._keywords:
                kw = self._keywords[tmp]
                if not kw.isCaseSensitive():
                    matchingWords = [kw]

        for word in self._words:
            if word.matches(text):
                matchingWords.append(word)

        if matchingWords:
            
            token = Token(text, matchingWords)
            
            wordEnd = endPos.clone()
            wordStart = wordEnd.clone()
            wordStart.backward(text) 
            
            token.setStartPosition(wordStart)
            token.setEndPosition(wordEnd)
            return [token]

        msg = "Unknown token '%s'" % text
        msg += " ending at line %d, column %d" % (endPos.line, endPos.column)

        raise Exception(msg)

    def _isLiteralDelim(self, ch):

        return ch in self._literalDelims
    
    def _isWhiteSpace(self, ch):
        
        if not self._currentLitDelim:
            return ord(ch) in self._wsCharCodes
        else:
            return False

#        if self._isLiteralDelim(ch):
#
#            if self._currentLitDelim:
#                if ch == self._currentLitDelim:
#                    self._currentLitDelim = ''
#            else:
#                self._currentLitDelim = ch
#                
#            return False
#
#        elif self._currentLitDelim:
#            
#            return False
#
#        else:
#            
#            return ord(ch) in self._wsCharCodes
