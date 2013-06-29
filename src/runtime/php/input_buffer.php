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

class Bovinus_InputBuffer {

    public function __construct($stream, $fillSize = 1) {

        $this->_stream = $stream;
        $this->_fillSize = $fillSize;
        $this->_positionInfo = new Bovinus_PositionInfo(1, 0);
    }

    public function setFillSize($fillSize) {

        $this->_fillSize = $fillSize;
    }

    public function getContent() {

        $this->fillContent();

        return substr($this->_content, 0, $this->_fillSize);
    }

    public function getPositionInfo() {

        return $this->_positionInfo;
    }

    public function consumeChar() {

        $ch = '';

        $len = strlen($this->_content);

        if ($len > 0) {
            $ch = $this->_content[0];
            if ($len > 1) {
                $this->_content = substr($this->_content, 1);
            } else {
                $this->_content = "";
            }
        }

        $this->fillContent();

        if ($ch !== "\n") {
            $this->_positionInfo->column++;
        } else {
            $this->_positionInfo->line++;
            $this->_positionInfo->column = 0;
        }

        return $ch;
    }

    public function consumeNChars($n) {

        $res = "";

        for ($i = 0; $i < $n; $i++) {
            $res .= $this->consumeChar();
        }

        return $res;
    }

    public function consumeAll() {

        $res = "";

        if (strlen($this->_content) <= $this->_fillSize) {
            $res = $this->_content;
            $this->_content = "";
        } else {
            $res = substr($this->_content, 0, $this->_fillSize);
            $this->_content = substr($this->_content, $this->_fillSize);
        }

        for ($i = 0; $i < strlen($res); $i++) {
            $ch = $res[$i];
            if ($ch !== "\n") {
                $this->_positionInfo->column++;
            } else {
                $this->_positionInfo->line++;
                $this->_positionInfo->column = 0;
            }
        }

        return $res;
    }

    private function fillContent() {

        while (strlen($this->_content) < $this->_fillSize) {
            if ($this->_stream->endOfInput())
                break;
            $this->_content .= $this->_stream->getNextChar();
        }
    }

    private $_stream;
    private $_fillSize;
    private $_content = "";
    private $_positionInfo;

}

class Bovinus_PositionInfo {

    public $line;
    public $column;

    public function __construct($line, $column) {

        $this->line = $line;
        $this->column = $column;
    }

}
