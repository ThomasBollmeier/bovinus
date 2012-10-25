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

require_once 'Bovinus/token.php';

class Bovinus_Tokenizer {

    public function __construct() {

        $this->_literal = null;
        $this->_literalDelims = array('"', "'");
        $this->_literalEscChar = '\\';
        $this->_separators = array();
    }

    public function setLiteral($literal) {

        $this->_literal = $literal;
        $this->_literalDelims = Bovinus_Literal::$DELIMITERS;
        $this->_literalEscChar = Bovinus_Literal::$ESCAPE_CHAR;
    }

    public function addSeparator($separator) {

        array_push($this->_separators, $separator);
    }

    public function splitAtSeparators($text) {

        $worklist = array(array("text" => $text, "sep" => null));

        foreach ($this->_separators as $sep) {

            $tmp = array();

            foreach ($worklist as $item) {

                if ($item['sep'] != null) {
                    array_push($tmp, $item);
                } else {
                    $tmp = array_merge($tmp, $this->_splitAtSep($item["text"], $sep));
                }
            }

            $worklist = $tmp;
        }

        return $worklist;
    }

    private function _splitAtSep($text, Bovinus_Separator $sep) {

        $res = array();

        $worklist = array(array("text" => $text, "sep" => null, "checked" => FALSE));
        $regex = $sep->getRegex();

        while (TRUE) {

            $tmp = array();
            $doNextStep = FALSE;

            foreach ($worklist as $item) {

                if ($item["checked"]) {
                    array_push($tmp, $item);
                    continue;
                }

                preg_match($regex, $item["text"], $matches);
                $numGroups = count($matches) - 1;

                switch ($numGroups) {

                    case 0:
                    case 1:

                        $doNextStep = TRUE;

                        $newItem = array("text" => $matches[$numGroups], "sep" => $sep, "checked" => TRUE);
                        array_push($tmp, $newItem);
                        break;

                    case 3:

                        $doNextStep = TRUE;

                        $m1 = $matches[1];
                        if (strlen($m1) > 0) {
                            $newItem = array("text" => $m1, "sep" => null, "checked" => FALSE);
                            array_push($tmp, $newItem);
                        }

                        $newItem = array("text" => $matches[2], "sep" => $sep, "checked" => TRUE);
                        array_push($tmp, $newItem);

                        $m3 = $matches[3];
                        if (strlen($m3) > 0) {
                            $newItem = array("text" => $m3, "sep" => null, "checked" => FALSE);
                            array_push($tmp, $newItem);
                        }

                        break;

                    default:

                        $item["checked"] = TRUE;
                        array_push($tmp, $item);
                        break;
                }
            }

            if (!$doNextStep) {
                foreach ($tmp as $el) {
                    array_push($res, array("text" => $el["text"], "sep" => $el["sep"]));
                }
                $res = $this->_unsplitIfInLiteral($res);
                break;
            } else {
                $worklist = $tmp;
            }
        }

        return $res;
    }

    private function _unsplitIfInLiteral($splitResult) {

        if ($this->_literal == null) {
            return $splitResult;
        }

        $res = array();
        $tmp = array();
        $len = count($splitResult);

        for ($i = 0; $i < $len; $i++) {

            $item = $splitResult[$i];

            if ($item["sep"] == null) {
                array_push($tmp, $item);
                continue;
            }

            if ($i > 0 && $i < $len - 1) {

                $left = "";
                for ($j = 0; $j < $i; $j++) {
                    $left .= $splitResult[$j]["text"];
                }

                $right = "";
                for ($j = $i + 1; $j < $len; $j++) {
                    $right .= $splitResult[$j]["text"];
                }

                if (!$this->_isInLiteral($left, $right)) {
                    array_push($tmp, $item);
                } else {
                    array_push($tmp, array("text" => $item["text"], "sep" => null));
                }
            } else {
                array_push($tmp, $item);
            }
        }

        $buffer = "";

        for ($i = 0; $i < $len; $i++) {

            if ($tmp[$i]["sep"] == null) {
                $buffer .= $tmp[$i]["text"];
            } else {
                if (strlen($buffer) > 0) {
                    array_push($res, array("text" => $buffer, "sep" => null));
                    $buffer = "";
                }
                array_push($res, $tmp[$i]);
            }
        }

        if (strlen($buffer) > 0) {
            array_push($res, array("text" => $buffer, "sep" => null));
        }

        return $res;
    }

    private function _isInLiteral($left, $right) {

        foreach ($this->_literalDelims as $delim) {

            $nleft = $this->_numDelimOccurrences($delim, $left);
            if ($nleft % 2 == 0)
                continue;

            $nright = $this->_numDelimOccurrences($delim, $right);
            if ($nright % 2 != 0) {
                return TRUE;
            }
        }

        return FALSE;
    }

    private function _numDelimOccurrences($delim, $text) {

        $res = 0;
        $len = strlen($text);
        $prev = null;

        for ($i = 0; $i < $len; $i++) {
            $ch = $text[$i];
            if ($ch == $delim && ($prev == null || $prev != $this->_literalEscChar)) {
                $res++;
            }
            $prev = $ch;
        }

        return $res;
    }

    private $_literal;
    private $_literalDelims;
    private $_literalEscChar;
    private $_separators;

}

?>
