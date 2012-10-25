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
require_once 'Bovinus/instream.php';

class Bovinus_FileInput implements Bovinus_InStream {

    public function __construct($filePath) {

        $this->filePath = $filePath;
    }

    public function __destruct() {

        if (!$this->closed) {
            fclose($this->file);
        }
    }

    public function endOfInput() {

        if ($this->opened) {
            return $this->endOfFile;
        } else {
            return false;
        }
    }

    public function getNextChar() {

        if (!$this->opened) {

            $handle = fopen($this->filePath, "r");
            if ($handle) {
                $this->file = $handle;
                $this->opened = true;
                $this->endOfFile = false;
            } else {
                throw new Exception("Cannot open file '$this->filePath'");
            }
        }

        $ch = fgetc($this->file);

        if ($ch !== false) {
            return $ch;
        } else {
            $this->endOfFile = true;
            $this->closed = true;
            fclose($this->file);
            return '';
        }
    }

    private $filePath;
    private $file = NULL;
    private $opened = false;
    private $closed = false;
    private $endOfFile = false;

}

?>