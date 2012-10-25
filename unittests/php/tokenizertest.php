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

require_once 'Bovinus/token.php';
require_once 'Bovinus/tokenizer.php';

class ParserTest extends PHPUnit_Framework_TestCase {

    public function setUp() {

    }

    public function tearDown() {

    }

    public function testPrecedence() {

        $testInput = "This::is:a::test";

        $colon = new Bovinus_Separator(':');
        $coloncolon = new Bovinus_Separator('::');

        $tokenizer = new Bovinus_Tokenizer();
        $tokenizer->addSeparator($colon);
        $tokenizer->addSeparator($coloncolon);
        
        $splitted = $tokenizer->splitAtSeparators($testInput);
        $this->assertEquals(count($splitted), 9);

        $tokenizer = new Bovinus_Tokenizer();
        $tokenizer->addSeparator($coloncolon);
        $tokenizer->addSeparator($colon);
        
        $splitted = $tokenizer->splitAtSeparators($testInput);
        $this->assertEquals(count($splitted), 7);

    }

}

?>
