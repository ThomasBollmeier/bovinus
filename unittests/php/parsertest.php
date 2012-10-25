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

ini_set('include_path', ".:" . ini_get('include_path'));

require_once 'godl_parser.php';
require_once 'Bovinus/file_input.php';

class ParserTest extends PHPUnit_Framework_TestCase {

    public function setUp() {

        $this->parser = new GodlParser();
    }

    public function tearDown() {

        $this->parser = null;
    }

    public function testTokens() {

        $lexer = $this->parser->getLexer();
        $lexer->setInputStream(new Bovinus_FileInput('test.godl'));

        $tokens = array();
        $token = $lexer->getNextToken();
        while ($token != null) {
            $tokens[] = $token;
            $token = $lexer->getNextToken();
        }

    }

    public function testSimple() {

        try {
            $ast = $this->parser->parseFile("test.godl");
        } catch (Bovinus_ParseError $err) {
            $ast = null;
            echo "\n" . $err->getMessage();
        }

        $this->assertTrue($ast != null);

        if ($ast != null) {
            echo "\n" . $ast->toXml();
        }
    }

    private $parser;

}

?>
