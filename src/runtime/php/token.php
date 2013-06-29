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

class Bovinus_Token {

    function __construct($text, $types) {

        $this->_text = $text;
        $this->_types = $types;
    }

    public function getText() {

        return $this->_text;
    }

    public function getTypes() {

        return $this->_types;
    }

    public function getTypeIds() {

        $res = array();

        foreach ($this->_types as $type) {
            array_push($res, $type->getId());
        }

        return $res;
    }

    public function setStartPosition($line, $column) {

        $this->_lineStart = $line;
        $this->_columnStart = $column;
    }

    public function getStartPosition() {

        return array(
            'line' => $this->_lineStart,
            'column' => $this->_columnStart
        );
    }

    public function setEndPosition($line, $column) {

        $this->_lineEnd = $line;
        $this->_columnEnd = $column;
    }

    public function getEndPosition() {

        return array(
            'line' => $this->_lineEnd,
            'column' => $this->_columnEnd
        );
    }

    private $_text;
    private $_types;
    private $_lineStart = 0;
    private $_columnStart = 0;
    private $_lineEnd = 0;
    private $_columnEnd = 0;

}

abstract class Bovinus_TokenType {

    protected function __construct() {

        $this->_id = Bovinus_TokenType::$_currentId;
        Bovinus_TokenType::$_currentId++;
    }

    public function getId() {

        return $this->_id;
    }

    public abstract function createToken($text);

    public static function escape($text) {

        $pattern = '/([\+\*\.\[\]\)\(])/';
        $replace = '\\\\${1}';

        return preg_replace($pattern, $replace, $text);
    }

    protected function _escape($text) {
        
        return Bovinus_TokenType::escape($text);
    }

    private $_id;
    private static $_currentId = 1;

}

class Bovinus_Word extends Bovinus_TokenType {

    function __construct($pattern) {

        parent::__construct();

        $this->_regex = '/^(' . $pattern . ')$/';
    }

    public function createToken($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return new Bovinus_Token($matches[0], array($this));
        } else {
            return null;
        }
    }

    public function matches($text) {

        return preg_match($this->_regex, $text) > 0;
    }

    private $_regex;

}

class Bovinus_Keyword extends Bovinus_TokenType {

    function __construct($keyword, $caseSensitive = TRUE) {

        parent::__construct();

        $this->_caseSensitive = $caseSensitive;
        if ($this->_caseSensitive) {
            $this->_keyword = $keyword;
        } else {
            $this->_keyword = strtoupper($keyword);
        }
    }

    public function createToken($text) {

        $tmp = $this->_caseSensitive ? $text : strtoupper($text);
        if ($this->_keyword == $tmp) {
            return new Bovinus_Token($text, array($this));
        } else {
            return null;
        }
    }

    public function getKeyword() {
        return $this->_keyword;
    }

    public function isCaseSensitive() {
        return $this->_caseSensitive;
    }

    private $_caseSensitive;
    private $_keyword;

}

class Bovinus_Literal extends Bovinus_TokenType {

    function __construct() {

        if (Bovinus_Literal::$_single != null) {
            throw new Exception('Instance of Literal must not be created');
        }

        parent::__construct();

        Bovinus_Literal::$_single = $this;
    }

    static function get() {

        if (!Bovinus_Literal::$_single) {
            Bovinus_Literal::$_single = new Bovinus_Literal();
        }

        return Bovinus_Literal::$_single;
    }

    public function createToken($text) {

        if ($this->isLiteral($text)) {
            return new Bovinus_Token($text, array($this));
        } else {
            return null;
        }
    }

    public function isLiteral($text) {

        if (strlen($text) < 2)
            return FALSE;

        $firstChar = substr($text, 0, 1);
        $lastChar = substr($text, -1, 1);

        return ( in_array($firstChar, Bovinus_Literal::$DELIMITERS) )
                and
                ( $firstChar == $lastChar );
    }

    static public $DELIMITERS = array('\'', '"');
    static public $ESCAPE_CHAR = '\\';
    static private $_single = null;

}

class Bovinus_Prefix extends Bovinus_TokenType {

    function __construct($tokenText, $escape = TRUE) {

        parent::__construct();

        $tmp = $escape ? $this->_escape($tokenText) : $tokenText;
        $this->_regex = '/(' . $tmp . ')(\S.*)/';
    }

    public function createToken($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return new Bovinus_Token($matches[1], array($this));
        } else {
            return null;
        }
    }

    public function getRemainingRight($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return $matches[2];
        } else {
            return "";
        }
    }

    private $_regex;

}

class Bovinus_Postfix extends Bovinus_TokenType {

    function __construct($tokenText, $escape = TRUE) {

        parent::__construct();

        $tmp = $escape ? $this->_escape($tokenText) : $tokenText;
        $this->_regex = '/(.*\S)(' . $tmp . ')/';
    }

    public function createToken($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return new Bovinus_Token($matches[2], array($this));
        } else {
            return null;
        }
    }

    public function getRemainingLeft($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return $matches[1];
        } else {
            return "";
        }
    }

    private $_regex;

}

class Bovinus_Separator extends Bovinus_TokenType {

    function __construct($tokenText, $whiteSpaceAllowed = TRUE, $escape = TRUE) {

        parent::__construct();

        $tmp = $escape ? $this->_escape($tokenText) : $tokenText;

        if ($whiteSpaceAllowed) {
            $this->_regex = '/(.*)(' . $tmp . ')(.*)/';
        } else {
            $this->_regex = '/(.*\S)(' . $tmp . ')(\S.*)/';
        }
    }

    public static function create($pattern) {

        $sep = new Bovinus_Separator('dummy');
        $sep->_regex = '/' . $pattern . '/';

        return $sep;
    }

    public function createToken($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return new Bovinus_Token($matches[2], array($this));
        } else {
            return null;
        }
    }

    public function getRemainingLeft($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return $matches[1];
        } else {
            return "";
        }
    }

    public function getRemainingRight($text) {

        preg_match($this->_regex, $text, $matches);

        if ($matches) {
            return $matches[3];
        } else {
            return "";
        }
    }

    public function getRegex() {

        return $this->_regex;
    }

    private $_regex;

}
