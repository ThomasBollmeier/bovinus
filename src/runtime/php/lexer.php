<?php

/*
 * Copyright 2012 Thomas Bollmeier <tbollmeier@web.de>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

require_once 'Bovinus/tokenizer.php';
require_once 'Bovinus/token.php';
require_once 'Bovinus/input_buffer.php';

class Bovinus_Lexer {

    public function __construct() {

        $this->_tokenizer = new Bovinus_Tokenizer();
        $this->_wsCharCodes = array(
            Bovinus_WSCharCode::TAB,
            Bovinus_WSCharCode::LINEBREAK,
            Bovinus_WSCharCode::VTAB,
            Bovinus_WSCharCode::FORMFEED,
            Bovinus_WSCharCode::SPACE
        );
    }

    public function setInputStream($instream) {

        $this->_instream = $instream;
        $this->_reset();
    }

    public function addTokenType($tt) {

        if ($tt instanceof Bovinus_Keyword) {
            $this->_keywords[$tt->getKeyword()] = $tt;
        } else if ($tt instanceof Bovinus_Word) {
            array_push($this->_words, $tt);
        } else if ($tt instanceof Bovinus_Prefix) {
            array_push($this->_prefixes, $tt);
        } else if ($tt instanceof Bovinus_Postfix) {
            array_push($this->_postfixes, $tt);
        } else if ($tt instanceof Bovinus_Separator) {
            $this->_tokenizer->addSeparator($tt);
        } else if ($tt instanceof Bovinus_Literal) {
            $this->_literal = $tt;
            $this->_literalDelims = Bovinus_Literal::$DELIMITERS;
            $this->_literalEscChar = Bovinus_Literal::$ESCAPE_CHAR;
            $this->_tokenizer->setLiteral($tt);
        } else {
            throw new Exception('Unknown token type!');
        }
    }

    public function enableLineComments($lineCommentStart = '//') {

        $this->_lineCommentEnabled = TRUE;
        $this->_lineCommentStart = $lineCommentStart;
    }

    public function enableBlockComments($blockCommentStart = '/*', $blockCommentEnd = '*/') {

        $this->_blockCommentEnabled = TRUE;
        $this->_blockCommentStart = $blockCommentStart;
        $this->_blockCommentEnd = $blockCommentEnd;
    }

    public function getNextToken() {

        if ($this->_instream == null) {
            return null;
        }

        if (count($this->_stack) > 0) {
            return array_pop($this->_stack);
        }

        if ($this->_inputBuffer == null) {
            $this->_initBuffer();
        }

        $hlp = $this->_getNextChars();

        if ($hlp != null) {
            $tokenStr = $hlp->text;
            $endLine = $hlp->line;
            $endColumn = $hlp->column;
        } else {
            return null;
        }

        $this->_stack = $this->_getTokens($tokenStr, $endLine, $endColumn);

        if (count($this->_stack) > 0) {
            return array_pop($this->_stack);
        } else {
            $message = "Unknown token '" . $tokenStr . "'";
            $message .= " at line " . $endLine . ", column " . $endColumn;
            throw new Exception($message);
        }
    }

    private function _reset() {

        $this->_stack = array();
        $this->_inputBuffer = null;
        $this->_mode = Bovinus_LexerMode::NORMAL;
    }

    private function _initBuffer() {

        $fillSize = 2; // <-- needed to detect escape chars in literals

        if ($this->_lineCommentEnabled) {
            if (strlen($this->_lineCommentStart) > $fillSize) {
                $fillSize = strlen($this->_lineCommentStart);
            }
        }

        if ($this->_blockCommentEnabled) {
            if (strlen($this->_blockCommentStart) > $fillSize) {
                $fillSize = strlen($this->_blockCommentStart);
            }
            if (strlen($this->_blockCommentEnd) > $fillSize) {
                $fillSize = strlen($this->_blockCommentEnd);
            }
        }

        $this->_inputBuffer = new Bovinus_InputBuffer($this->_instream, $fillSize);
        $this->_consumed = "";
    }

    private function _getNextChars() {

        $res = null;

        while (TRUE) {

            $content = $this->_inputBuffer->getContent();

            if (strlen($content) == 0) {
                if (strlen($this->_consumed) > 0) {
                    $res = new Bovinus_CharInfo();
                    $posInfo = $this->_inputBuffer->getPositionInfo();
                    $res->line = $posInfo->line;
                    $res->column = $posInfo->column;
                    $res->text = $this->_consumed;
                }
                $this->_consumed = "";
                break;
            }

            $newMode = $this->_getNewMode($content);

            if ($newMode > 0) {
                $res = $this->_onNewMode($newMode);
                if ($res != null) {
                    break;
                }
            } else {
                $this->_consumeContent($content);
            }
        }

        return $res;
    }

    private function _getTokens($text, $endLine, $endColumn) {

        $res = array();
        $parts = $this->_tokenizer->splitAtSeparators($text);
        // Reverse order to fit into stack logic:
        $parts = array_reverse($parts);

        $col_end = $endColumn;

        foreach ($parts as $item) {

            $txt = $item['text'];
            $sep = $item['sep'];

            if ($sep != null) {
                $token = new Bovinus_Token($txt, array($sep));
                $col_start = $col_end - strlen($txt) + 1;
                $token->setStartPosition($endLine, $col_start);
                $token->setEndPosition($endLine, $col_end);
                array_push($res, $token);
            } else {
                $res = array_merge($res, $this->_getNonSepTokens($txt, $endLine, $col_end));
            }

            $col_end -= strlen($txt);
        }

        return $res;
    }

    private function _getNonSepTokens($text, $endLine, $endColumn) {

        // Handle literals:
        if ($this->_literal != null) {

            $token = $this->_literal->createToken($text);
            if ($token != null) {
                $token->setStartPosition($endLine, $endColumn - strlen($text) + 1);
                $token->setEndPosition($endLine, $endColumn);
                return array($token);
            }
        }

        $res = array();

        // Find prefixes:
        foreach ($this->_prefixes as $prefix) {

            $token = $prefix->createToken($text);
            if ($token != null) {

                $right = $prefix->getRemainingRight($text);
                if (strlen($right) > 0) {
                    $res = $this->_getTokens($right, $endLine, $endColumn);
                }
                $col = $endColumn - strlen($right);
                $txt = $token->getText();
                $token->setStartPosition($endLine, $col - strlen($txt) + 1);
                $token->setEndPosition($endLine, $col);
                array_push($res, $token);

                return $res;
            }
        }

        // Find postfixes:
        foreach ($this->_postfixes as $postfix) {

            $token = $postfix->createToken($text);
            if ($token != null) {

                $left = $postfix->getRemainingLeft($text);
                $txt = $token->getText();
                $token->setStartPosition($endLine, $endColumn - strlen($txt) + 1);
                $token->setEndPosition($endLine, $endColumn);
                $res = array($token);

                if (strlen($left) > 0) {
                    $col = $endColumn - strlen($txt);
                    $res = array_merge($res, $this->_getTokens($left, $endLine, $col));
                }

                return $res;
            }
        }

        // Find (key)words:

        $matchingWords = array();

        if (array_key_exists($text, $this->_keywords)) {
            array_push($matchingWords, $this->_keywords[$text]);
        } else {
            // perhaps case insensitive keyword?
            $tmp = strtoupper($text);
            if (array_key_exists($tmp, $this->_keywords)) {
                $kw = $this->_keywords[$tmp];
                if (!$kw->isCaseSensitive()) {
                    array_push($matchingWords, $kw);
                }
            }
        }

        foreach ($this->_words as $word) {
            if ($word->matches($text)) {
                array_push($matchingWords, $word);
            }
        }

        if (count($matchingWords) > 0) {

            $token = new Bovinus_Token($text, $matchingWords);
            $token->setStartPosition($endLine, $endColumn - strlen($text) + 1);
            $token->setEndPosition($endLine, $endColumn);

            return array($token);
        }

        $message = "Unknown token '" . $text . "'";
        $message .= " ending at line " . $endLine . ", column " . $endColumn;

        throw new Exception($message);
    }

    private function _getNewMode($content) {

        $res = -1;

        switch ($this->_mode) {

            case Bovinus_LexerMode::NORMAL:
                if ($this->_startsWS($content)) {
                    $res = Bovinus_LexerMode::WSPACE;
                } else if ($this->_startsLineComment($content)) {
                    $res = Bovinus_LexerMode::LINE_COMMENT;
                } else if ($this->_startsBlockComment($content)) {
                    $res = Bovinus_LexerMode::BLOCK_COMMENT;
                }
                break;

            case Bovinus_LexerMode::WSPACE:
                if (!$this->_isWhiteSpace($content[0])) {
                    if ($this->_startsLineComment($content)) {
                        $res = Bovinus_LexerMode::LINE_COMMENT;
                    } else if ($this->_startsBlockComment($content)) {
                        $res = Bovinus_LexerMode::BLOCK_COMMENT;
                    } else {
                        $res = Bovinus_LexerMode::NORMAL;
                    }
                }
                break;

            case Bovinus_LexerMode::LINE_COMMENT:
                if ($this->_endsLineComment($content)) {
                    $res = Bovinus_LexerMode::NORMAL;
                }
                break;

            case Bovinus_LexerMode::BLOCK_COMMENT:
                if ($this->_endsBlockComment($content)) {
                    $res = Bovinus_LexerMode::NORMAL;
                }
                break;
        }

        return $res;
    }

    private function _onNewMode($newMode) {

        $res = null;

        switch ($this->_mode) {

            case Bovinus_LexerMode::NORMAL:
                $pos = $this->_inputBuffer->getPositionInfo();
                $line = $pos->line;
                $column = $pos->column;
                switch ($newMode) {
                    case Bovinus_LexerMode::WSPACE:
                        $len = 1;
                        break;
                    case Bovinus_LexerMode::LINE_COMMENT:
                        $len = strlen($this->_lineCommentStart);
                        break;
                    case Bovinus_LexerMode::BLOCK_COMMENT:
                        $len = strlen($this->_blockCommentStart);
                        break;
                }
                $this->_inputBuffer->consumeNChars($len);
                if (strlen($this->_consumed) > 0) {
                    $res = new Bovinus_CharInfo();
                    $res->line = $line;
                    $res->column = $column;
                    $res->text = $this->_consumed;
                    $this->_consumed = "";
                }
                break;

            case Bovinus_LexerMode::WSPACE:
                switch ($newMode) {
                    case Bovinus_LexerMode::NORMAL:
                        $this->_consumed .= $this->_inputBuffer->consumeChar();
                        break;
                    case Bovinus_LexerMode::LINE_COMMENT:
                        $this->_inputBuffer->consumeNChars(strlen($this->_lineCommentStart));
                        break;
                    case Bovinus_LexerMode::BLOCK_COMMENT:
                        $this->_inputBuffer->consumeNChars(strlen($this->_blockCommentStart));
                        break;
                }
                break;

            case Bovinus_LexerMode::LINE_COMMENT:
                // can only change to normal mode:
                $this->_inputBuffer->consumeChar(); // <-- consume linebreak
                break;

            case Bovinus_LexerMode::BLOCK_COMMENT:
                // can only change to normal mode:
                $this->_inputBuffer->consumeNChars(strlen($this->_blockCommentEnd));
                break;
        }

        $this->_mode = $newMode;

        return $res;
    }

    private function _consumeContent($content) {

        if ($this->_mode != Bovinus_LexerMode::NORMAL) {
            $this->_inputBuffer->consumeChar();
            return;
        }

        if ($this->_literal != null) {

            $escaped = FALSE;

            if (strlen($this->_currentLitDelim) == 0) {
                foreach ($this->_literalDelims as $delim) {
                    if ($content[0] == $delim) {
                        $this->_currentLitDelim = $content[0];
                        break;
                    }
                }
            } else {
                // Currently inside literal
                // Check for escape characters and treat them separately:
                if ($this->_literalEscChar != null) {
                    $pattern = '/(\\\\)/';
                    $replace = '\\\\${1}';
                    $escChar = preg_replace($pattern, $replace, $this->_literalEscChar);
                    foreach ($this->_literalDelims as $delim) {
                        $regex = "/^" . $escChar . $delim . ".*/";
                        if (preg_match($regex, $content) > 0) {
                            $escaped = TRUE;
                            break;
                        }
                    }
                }

                if ($content[0] == $this->_currentLitDelim) {
                    $this->_currentLitDelim = "";
                }
            }

            if ($escaped) {
                $this->_inputBuffer->consumeChar();
            }

            $this->_consumed .= $this->_inputBuffer->consumeChar();
        } else {
            // No literal defined
            $this->_consumed .= $this->_inputBuffer->consumeChar();
        }
    }

    private function _startsWS($content) {

        if (strlen($this->_currentLitDelim) == 0) {

            foreach ($this->_wsCharCodes as $code) {
                if ($code == ord($content[0])) {
                    return TRUE;
                }
            }

            return FALSE;
        } else {
            return FALSE;
        }
    }

    private function _startsWith($comment, $start) {

        $regex = '/^' . Bovinus_TokenType::escape($start) . '/';

        return ( preg_match($regex, $comment) > 0 );
    }

    private function _startsLineComment($content) {

        $res = FALSE;

        if ($this->_lineCommentEnabled && strlen($this->_currentLitDelim) == 0) {
            $res = $this->_startsWith($content, $this->_lineCommentStart);
        }

        return $res;
    }

    private function _startsBlockComment($content) {

        $res = FALSE;

        if ($this->_blockCommentEnabled && strlen($this->_currentLitDelim) == 0) {
            $res = $this->_startsWith($content, $this->_blockCommentStart);
        }

        return $res;
    }

    private function _endsLineComment($content) {

        $res = FALSE;

        if ($this->_lineCommentEnabled && strlen($this->_currentLitDelim) == 0) {
            $res = ( ord($content[0]) == Bovinus_WSCharCode::LINEBREAK );
        }

        return $res;
    }

    private function _endsBlockComment($content) {

        $res = FALSE;

        if ($this->_blockCommentEnabled && strlen($this->_currentLitDelim) == 0) {
            $res = $this->_startsWith($content, $this->_blockCommentEnd);
        }

        return $res;
    }

    private function _isWhiteSpace($ch) {

        $res = FALSE;

        if ($this->_isLiteralDelim($ch)) {

            if (strlen($this->_currentLitDelim) > 0) {
                if ($ch == $this->_currentLitDelim) {
                    $this->_currentLitDelim = '';
                }
            } else {
                $this->_currentLitDelim = $ch;
            }
            $res = FALSE;
        } else if (strlen($this->_currentLitDelim) > 0) {

            $res = FALSE;
        } else {

            $res = FALSE;
            foreach ($this->_wsCharCodes as $code) {
                if ($code == ord($ch)) {
                    $res = TRUE;
                    break;
                }
            }
        }

        return $res;
    }

    private function _isLiteralDelim($ch) {

        foreach ($this->_literalDelims as $delim) {
            if ($delim == $ch) {
                return TRUE;
            }
        }

        return FALSE;
    }

    private $_instream = null;
    private $_inputBuffer = null;
    private $_consumed = "";
    private $_tokenizer;
    private $_stack = array();
    private $_keywords = array(); // <-- Dictionary
    private $_words = array();
    private $_prefixes = array();
    private $_postfixes = array();
    private $_literal = null;
    private $_literalDelims = array();
    private $_literalEscChar = null;
    private $_currentLitDelim = '';
    private $_wsCharCodes;
    private $_mode = Bovinus_LexerMode::NORMAL;
    private $_lineCommentEnabled = FALSE;
    private $_lineCommentStart = '';
    private $_blockCommentEnabled = FALSE;
    private $_blockCommentStart = '';
    private $_blockCommentEnd = '';

}

class Bovinus_WSCharCode {

    const TAB = 9;
    const LINEBREAK = 10;
    const VTAB = 11;
    const FORMFEED = 12;
    const SPACE = 32;

}

class Bovinus_LexerMode {

    const NORMAL = 1;
    const LINE_COMMENT = 2;
    const BLOCK_COMMENT = 3;
    const WSPACE = 4;

}

class Bovinus_CharInfo {

    public $text;
    public $line;
    public $column;

}
