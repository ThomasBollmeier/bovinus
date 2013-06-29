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

class Bovinus_PathElement {

    public function __construct($grammarNode, $token) {

        $this->grammarNode = $grammarNode;
        $this->token = $token;
    }

    public function getGrammarNode() {

        return $this->grammarNode;
    }

    public function getToken() {

        return $this->token;
    }

    public function getMatchedTokenType() {

        return $this->grammarNode->getTokenType();
    }

    private $grammarNode;
    private $token;

}

class Bovinus_Path {

    public function __construct() {

        $this->elements = array();
        $this->envStack = array();
    }

    public function push($grammarNode, $token) {

        $element = new Bovinus_PathElement($grammarNode, $token);
        array_push($this->elements, $element);

        if ($grammarNode->isRuleStart()) {
            array_push($this->envStack, $grammarNode->getEnvVars());
        } else if ($grammarNode->isRuleEnd()) {
            array_push($this->envStack, FALSE);
        } else if ($grammarNode->isTokenNode() && $grammarNode->changesEnvVars()) {
            $envVars = $this->getCurEnvVars();
            if ($envVars != null) {
                $grammarNode->changeEnv($envVars, $token);
            }
        }
    }

    public function pop() {

        $res = array_pop($this->elements);

        $node = $res->getGrammarNode();
        if ($node->isRuleStart() || $node->isRuleEnd()) {
            array_pop($this->envStack);
        } else if ($node->isTokenNode() && $node->changesEnvVars()) {
            $envVars = $this->getCurEnvVars();
            if ($envVars != null) {
                $node->undoEnvChange($envVars, $res->getToken());
            }
        }

        return $res;
    }

    public function popToken() {

        $element = $this->pop();

        return $element->getToken();
    }

    public function getLength() {

        return count($this->elements);
    }

    public function getElement($index) {

        $numElements = count($this->elements);

        if ($index < 0) {
            $index = $numElements + $index;
        }

        if ($index < 0 || $index > $numElements - 1) {
            throw new Exception('Invalid path element index');
        }

        return $this->elements[$index];
    }

    public function getEnvVar($name) {

        $envVarStack = array();

        foreach ($this->envStack as $env) {
            if (!is_bool($env)) {
                array_push($envVarStack, $env);
            } else {
                array_pop($envVarStack);
            }
        }

        $idx = count($envVarStack) - 1;
        while ($idx > -1) {
            if (array_key_exists($name, $envVarStack[$idx])) {
                return $envVarStack[$idx][$name];
            }
            $idx--;
        }

        return null;
    }

    private function getCurEnvVars() {

        $idx = count($this->envStack) - 1;
        $level = 0;

        while ($idx >= 0) {
            $envVars = $this->envStack[$idx];
            if (!is_bool($envVars)) {
                if ($level == 0)
                    return $envVars;
                $level++;
            } else {
                $level--;
            }
            $idx--;
        }

        return null;
    }

    private $elements;
    private $envStack; // stack of environments  

}
