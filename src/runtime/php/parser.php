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

require_once 'Bovinus/lexer.php';
require_once 'Bovinus/grammar.php';
require_once 'Bovinus/path.php';
require_once 'Bovinus/context.php';
require_once 'Bovinus/file_input.php';
require_once 'Bovinus/string_input.php';
require_once 'Bovinus/ast.php';

class Bovinus_Parser {

    public function __construct($grammar) {

        $this->grammar = $grammar;

        $this->lexer = new Bovinus_Lexer();
        foreach ($grammar->getTokenTypes() as $tokenType) {
            $this->lexer->addTokenType($tokenType);
        }

        $this->curFile = "";
        $this->fullBacktracking = FALSE;
        $this->tokenBuffer = array();
    }

    public function enableLineComments($lineCommentStart = '//') {
        $this->lexer->enableLineComments($lineCommentStart);
    }

    public function enableBlockComments($blockCommentStart = '/*', $blockCommentEnd = '*/') {

        $this->lexer->enableBlockComments($blockCommentStart, $blockCommentEnd);
    }

    public function enableFullBacktracking($fullBacktracking) {

        $this->fullBacktracking = $fullBacktracking;
    }

    public function parse($inStream) {

        $this->lexer->setInputStream($inStream);

        $path = new Bovinus_Path();
        $path->push($this->grammar->getSocket(), null);
        $error = FALSE;
        $done = FALSE;
        $searchRes = null;

        while (!$done) {

            $token = $this->getNextToken();

            if ($searchRes != null) {
                $path = $searchRes->path;
            }

            if ($token == null) {

                $searchRes = $this->findPathToEnd($path);

                if ($searchRes->found) {
                    $done = TRUE;
                } else {
                    $searchRes = $this->findNextSibling($path);
                    if (!$searchRes->found) {
                        $error = TRUE;
                        $done = TRUE;
                    }
                }

                continue;
            }

            $searchRes = $this->findNextMatchingNode($token, $path);

            if ($searchRes->found) {
                array_pop($this->tokenBuffer);
            } else {
                $searchRes = $this->findNextSibling($path);
                if (!$searchRes->found) {
                    $done = TRUE;
                    $error = TRUE;
                }
            }
        }

        if (!$error) {
            return $this->createAst($path);
        } else {
            if (count($this->tokenBuffer) > 0) {
                $token = $this->tokenBuffer[0];
                $text = $token->getText();
                $pos = $token->getStartPosition();
                $line = $pos['line'];
                $column = $pos['column'];
                throw new Bovinus_ParseError($this->curFile, $line, $column, $text);
            } else {
                throw new Exception("Parsing error");
            }
        }
    }

    public function parseFile($filePath) {

        $this->curFile = $filePath;
        $input = new Bovinus_FileInput($filePath);

        $res = $this->parse($input);

        $this->curFile = "";

        return $res;
    }

    public function parseString($string) {

        return $this->parse(new Bovinus_StringInput($string));
    }

    public function getLexer() {

        return $this->lexer;

    }

    private function getNextToken() {

        if (count($this->tokenBuffer) == 0) {
            $token = $this->lexer->getNextToken();
            if ($token != null) {
                array_push($this->tokenBuffer, $token);
            }
        }

        $cnt = count($this->tokenBuffer);

        if ($cnt > 0) {
            return $this->tokenBuffer[$cnt - 1];
        } else {
            return null;
        }
    }

    private function findPathToEnd($path) {

        $node = $path->getElement(-1)->getGrammarNode();
        try {
            $ctx = new Bovinus_Context($path);
            $successors = $node->getSuccessors($ctx);
        } catch (Bovinus_SuccessorError $error) {
            return new Bovinus_PathSearchResult(FALSE, $path);
        }

        if (count($successors) == 0) {
            return new Bovinus_PathSearchResult(TRUE, $path);
        }

        foreach ($successors as $succ) {

            if ($succ->isTokenNode()) {
                continue;
            }

            $path->push($succ, null);

            $searchRes = $this->findPathToEnd($path);
            if ($searchRes->found) {
                return $searchRes;
            } else {
                $path->pop();
            }
        }

        return new Bovinus_PathSearchResult(FALSE, $path);
    }

    private function findNextSibling($path) {

        $removed = array();

        while (TRUE) {

            if ($path->getLength() < 2) {
                // Restore original path:
                while (count($removed) > 0) {
                    $elem = array_pop($removed);
                    $token = $elem->getToken();
                    if ($token != null) {
                        array_pop($this->tokenBuffer);
                    }
                    $path->push($elem->getGrammarNode(), $token);
                }

                return new Bovinus_PathSearchResult(FALSE, $path);
            }

            $siblingSearchRes = $this->gotoNextSibling($path);

            if ($siblingSearchRes->found) {

                return $siblingSearchRes;
            } else {

                if (!$this->fullBacktracking) {
                    // A backward navigation must not exit the current rule:
                    $grammarNode = $path->getElement(-1)->getGrammarNode();
                    if ($grammarNode->isRuleEnd()) {
                        return new Bovinus_PathSearchResult(FALSE, $path);
                    }
                }

                $elem = $path->pop();
                $token = $elem->getToken();
                array_push($removed, $elem);
                if ($token != null) {
                    array_push($this->tokenBuffer, $token);
                }
            }
        }

        return new Bovinus_PathSearchResult(FALSE, $path);
    }

    private function gotoNextSibling($path) {

        if ($path->getLength() < 2) {
            return new Bovinus_PathSearchResult(FALSE, $path);
        }

        $elem = $path->pop();
        $start = $elem->getGrammarNode();
        $token = $elem->getToken();

        $prev = $path->getElement(-1)->getGrammarNode();
        $context = new Bovinus_Context($path, $token);

        try {
            $successors = $prev->getSuccessors($context);
        } catch (Bovinus_SuccessorError $err) {
            $path->push($start, $token);
            return new Bovinus_PathSearchResult(FALSE, $path);
        }

        // Get start index:
        $idx = 0;
        $startIdx = -1;
        foreach ($successors as $succ) {
            if ($succ->getTechnicalId() == $start->getTechnicalId()) {
                $startIdx = $idx;
                break;
            }
            $idx++;
        }

        if ($startIdx < 0 || $startIdx == count($successors) - 1) {
            $path->push($start, $token);
            return new Bovinus_PathSearchResult(FALSE, $path);
        }

        $sibling = $successors[$startIdx + 1];
        if ($token != null) {
            array_push($this->tokenBuffer, $token);
        }
        $path->push($sibling, null);

        return new Bovinus_PathSearchResult(TRUE, $path);
    }

    private function findNextMatchingNode($token, $path) {

        $elem = $path->getElement(-1);
        $startNode = $elem->getGrammarNode();
        $startToken = $elem->getToken();

        if ($startNode->isTokenNode() && $startToken == null) {

            $tokenTypeId = $startNode->getTokenTypeId();
            $typeIds = $token->getTypeIds();

            foreach ($typeIds as $typeId) {
                if ($typeId == $tokenTypeId) {
                    $path->pop();
                    $path->push($startNode, $token);
                    return new Bovinus_PathSearchResult(TRUE, $path);
                }
            }

            return new Bovinus_PathSearchResult(FALSE, $path);
        }

        try {
            $ctx = new Bovinus_Context($path, $token);
            $successors = $startNode->getSuccessors($ctx);
        } catch (Bovinus_SuccessorError $error) {
            return new Bovinus_PathSearchResult(FALSE, $path);
        }

        foreach ($successors as $succ) {

            $path->push($succ, null);

            $searchRes = $this->findNextMatchingNode($token, $path);
            if ($searchRes->found) {
                return $searchRes;
            } else {
                $path->pop();
            }
        }

        return new Bovinus_PathSearchResult(FALSE, $path);
    }

    private function createAst($path) {

        $stack = array();
        $current = null;

        $numElements = $path->getLength();

        for ($i = 0; $i < $numElements; $i++) {

            $element = $path->getElement($i);
            $node = $element->getGrammarNode();
            $token = $element->getToken();

            if ($node->isRuleStart()) {

                if ($current != null) {
                    array_push($stack, $current);
                }
                $name = $node->getName();
                $id = $node->getId();
                $text = $token != null ? $token->getText() : "";
                $current = new Bovinus_AstNode($name, $text, $id);
            } else if ($node->isRuleEnd()) {

                // Ggf. Transformation. Dabei ID aus Regel bewahren:
                $orig = $current;
                $current = $node->transform($current);
                if ($current != $orig) {
                    $current->setId($orig->getId());
                }

                $parent = count($stack) > 0 ? array_pop($stack) : null;
                if ($parent != null) {
                    $parent->addChild($current);
                    $current = $parent;
                } else {
                    break;
                }
            } else if ($node->isTokenNode()) {

                $id = $node->getId();
                $text = $token != null ? $token->getText() : '';
                $current->addChild(new Bovinus_AstNode('token', $text, $id));
            } else {
                continue;
            }
        }

        return $current;
    }

    private $grammar;
    private $lexer;
    private $curFile;
    private $fullBacktracking;
    private $tokenBuffer;

}

class Bovinus_PathSearchResult {

    public $found;
    public $path;

    public function __construct($found, $path) {
        $this->found = $found;
        $this->path = $path;
    }

}

class Bovinus_ParseError extends Exception {

    public function __construct($filename, $line, $column, $text) {

        $message = sprintf("Line:%d, Column:%d -> Unexpected token '%s'", $line, $column, $text);
        if ($filename != "") {
            $message = "File:\"" . $filename . "\", " . $message;
        }

        parent::__construct($message);
    }

}
?>



