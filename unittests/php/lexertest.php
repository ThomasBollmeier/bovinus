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

ini_set('include_path', "..:" . ini_get('include_path'));

//require_once 'PHPUnit/Autoload.php';

require_once 'Bovinus/lexer.php';
require_once 'Bovinus/file_input.php';
require_once 'Bovinus/string_input.php';

class LexerTest extends PHPUnit_Framework_TestCase {

    public function setUp() {

        $this->hyphen = new Bovinus_Separator('-');
        $this->semicolon = new Bovinus_Separator(';');
        $this->id = new Bovinus_Word('[a-zA-Z_][a-zA-Z_0-9]*');
        $this->dataKeyw = new Bovinus_Keyword("data");
        $this->literal = Bovinus_Literal::get();
        $this->colon = new Bovinus_Separator(':');
        $this->coloncolon = new Bovinus_Separator('::');

        $lexer = new Bovinus_Lexer();
        $lexer->addTokenType($this->hyphen);
        $lexer->addTokenType($this->semicolon);
        $lexer->addTokenType($this->id);
        $lexer->addTokenType($this->dataKeyw);
        $lexer->addTokenType($this->literal);
        $lexer->addTokenType($this->coloncolon);
        $lexer->addTokenType($this->colon);

        $this->lexer = $lexer;
    }

    public function tearDown() {

        $this->lexer = null;
    }

    public function testSimple() {

        $input = new Bovinus_StringInput("data mydata-address1-country");
        $this->lexer->setInputStream($input);

        $tokens = array();

        $token = $this->lexer->getNextToken();
        while ($token != null) {

            $tokens[] = $token;
            $token = $this->lexer->getNextToken();
        }
        
        $this->assertEquals(6, count($tokens));
        $ttypes = $tokens[2]->getTypes();
        $this->assertEquals(1, count($ttypes));
        $this->assertEquals($this->hyphen, $ttypes[0]);

    }
    
    public function testSimpleFileInput() {

        $input = new Bovinus_FileInput("input.txt");
        $this->lexer->setInputStream($input);

        $tokens = array();

        $token = $this->lexer->getNextToken();
        while ($token != null) {

            $tokens[] = $token;
            $token = $this->lexer->getNextToken();
        }

        $this->assertEquals(7, count($tokens));

    }

    public function testLiteral() {

        $input = new Bovinus_StringInput("'do-not-split-this-literal'");
        $this->lexer->setInputStream($input);

        $tokens = array();

        $token = $this->lexer->getNextToken();
        while ($token != null) {

            $tokens[] = $token;
            $token = $this->lexer->getNextToken();
        }
        
        $this->assertEquals(1, count($tokens));
        $ttypes = $tokens[0]->getTypes();
        $this->assertEquals(1, count($ttypes));
        $this->assertEquals($this->literal, $ttypes[0]);

    }

    public function testSepPrecedence() {

        $input = new Bovinus_StringInput("::split::correctly");
        $this->lexer->setInputStream($input);

        $tokens = array();

        $token = $this->lexer->getNextToken();
        while ($token != null) {
            $tokens[] = $token;
            $token = $this->lexer->getNextToken();
        }


        $ttypes = $tokens[0]->getTypes();
        $this->assertEquals(1, count($ttypes));
        $this->assertEquals($this->coloncolon, $ttypes[0]);        

    }
    
    private $lexer;
    private $hyphen;
    private $semicolon;
    private $id;
    private $dataKeyw;
    private $literal;

}

?>
