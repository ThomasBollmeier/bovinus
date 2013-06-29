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

abstract class Bovinus_Rule implements Bovinus_Connectable, Bovinus_Pluggable, Bovinus_GrammarElement, Bovinus_RuleInternalAccess {

    public function __construct($name, $identifier = "") {

        $this->_start = new Bovinus_RuleStartNode($this, $name, $identifier);
        $this->_end = new Bovinus_RuleEndNode($this);
        $this->_envVars = array();
    }

    public function getName() {

        return $this->_start->getName();
    }

    public function getEndNode() {

        return $this->_end;
    }

    public function getEnvVars() {

        return $this->_envVars;
    }

    public function setEnvVar($name, $value = TRUE) {

        $this->_envVars[$name] = $value;
    }

    public function onSuccRequested($start, $end, $context) {

        $this->expand($start, $end, $context);
    }

    abstract public function expand($start, $end, $context);

    public function transform($astNode) {

        return $astNode;
    }

    public function connect(Bovinus_Connectable $successorElement) {

        $this->_end->connectTo($successorElement->getSocket());

        return $successorElement;
    }

    public function getPlug() {

        return $this->_end;
    }

    public function getSocket() {

        return $this->_start;
    }

    private $_start;
    private $_end;
    private $_envVars;

}

abstract class Bovinus_Grammar extends Bovinus_Rule {

    public function __construct($name, $tokenTypes) {

        parent::__construct($name);

        $this->tokenTypes = $tokenTypes;
    }

    public function getTokenTypes() {

        return $this->tokenTypes;
    }

    private $tokenTypes;

}

function bovinus_tokenNode($tokenType, $identifier = "") {

    return new Bovinus_TokenNode($tokenType, $identifier);
}

function bovinus_sequence() {

    $elements = func_get_args();

    return new Bovinus_Sequence($elements);
}

function bovinus_fork() {

    $branches = func_get_args();

    return new Bovinus_Fork($branches);
}

function bovinus_zero_to_one($element) {
    
    return new Bovinus_Multiplier($element, Bovinus_Multiplier::ZERO_TO_ONE);
}

function bovinus_zero_to_many($element) {
    
    return new Bovinus_Multiplier($element, Bovinus_Multiplier::ZERO_TO_MANY);
}

function bovinus_one_to_many($element) {
    
    return new Bovinus_Multiplier($element, Bovinus_Multiplier::ONE_TO_MANY);
}

interface Bovinus_Connectable {

    function getSocket();
}

interface Bovinus_Socket {

    function getSuccessors($context);
}

interface Bovinus_Pluggable {

    function getPlug();
}

interface Bovinus_Plug {

    function connectTo($socket);
}

interface Bovinus_GrammarElement {

    function connect(Bovinus_Connectable $successorElement);
}

interface Bovinus_IdNode {

    function getId();
}

interface Bovinus_RuleInternalAccess {

    function getName();

    function getEndNode();

    function getEnvVars();

    function onSuccRequested($start, $end, $context);

    function transform($astNode);
}

abstract class Bovinus_Node implements Bovinus_Connectable, Bovinus_Socket {
// Node categories:

    const RULE_START = 1;
    const RULE_END = 2;
    const TOKEN = 3;
    const TECHNICAL = 4;

    public function __construct($category, $tokenType = null) {

        $this->catg = $category;
        $this->tokenType = $tokenType;
        $this->techId = Bovinus_Node::$nextTechId++;
    }

    public function getTokenType() {

        return $this->tokenType;
    }

    public function getTokenTypeId() {

        if ($this->tokenType != null) {
            return $this->tokenType->getId();
        } else {
            return -1;
        }
    }

    public function isRuleStart() {

        return $this->catg == Bovinus_Node::RULE_START;
    }

    public function isRuleEnd() {

        return $this->catg == Bovinus_Node::RULE_END;
    }

    public function isTokenNode() {

        return $this->catg == Bovinus_Node::TOKEN;
    }

    public function isTechnicalNode() {

        return $this->catg == Bovinus_Node::TECHNICAL;
    }

    public function getSocket() {

        return $this;
    }

    public function getTechnicalId() {

        return $this->techId;
    }

    static private $nextTechId = 1;
    private $catg;
    private $tokenType;
    private $techId;

}

class Bovinus_PlugNode extends Bovinus_Node implements Bovinus_Pluggable, Bovinus_Plug, Bovinus_GrammarElement {

    public static function createConnector() {

        return new Bovinus_PlugNode(Bovinus_Node::TECHNICAL);
    }

    public function __construct($category, $tokenType = null) {

        parent::__construct($category, $tokenType);

        $this->successors = array();
    }

    public function getSuccessors($context) {

        return $this->successors;
    }

    public function getPlug() {

        return $this;
    }

    public function connectTo($socket) {

        if (array_search($socket, $this->successors, TRUE) === FALSE) {
            array_push($this->successors, $socket);
        }
    }

    public function connect(Bovinus_Connectable $successorElement) {

        $this->connectTo($successorElement->getSocket());

        return $successorElement;
    }

    private $successors;

}

class Bovinus_RuleStartNode extends Bovinus_Node implements Bovinus_IdNode {

    public function __construct(Bovinus_RuleInternalAccess $ruleAccess, $name, $identifier) {

        parent::__construct(Bovinus_Node::RULE_START);

        $this->ruleAccess = $ruleAccess;
        $this->name = $name;
        $this->ident = $identifier;
    }

    public function getId() {

        return $this->ident;
    }

    public function getSuccessors($context) {

        $start = Bovinus_PlugNode::createConnector();
        $end = Bovinus_PlugNode::createConnector();

        $this->ruleAccess->onSuccRequested($start, $end, $context);

        $end->connectTo($this->ruleAccess->getEndNode());

        return array($start);
    }

    public function getEnvVars() {

        return $this->ruleAccess->getEnvVars();
    }

    public function getName() {

        return $this->name;
    }

    private $ruleAccess;
    private $name;
    private $ident;

}

class Bovinus_RuleEndNode extends Bovinus_PlugNode {

    public function __construct(Bovinus_RuleInternalAccess $ruleAccess) {

        parent::__construct(Bovinus_Node::RULE_END);

        $this->ruleAccess = $ruleAccess;
    }

    public function transform($astNode) {

        return $this->ruleAccess->transform($astNode);
    }

    private $ruleAccess;

}

interface Bovinus_EnvVarChanger {

    function change($envVars, $token, $node);

    function undo($envVars, $token, $node);
}

class Bovinus_TokenNode extends Bovinus_PlugNode implements Bovinus_IdNode {

    public function __construct($tokenType, $identifier = "") {

        parent::__construct(Bovinus_Node::TOKEN, $tokenType);

        $this->ident = $identifier;
    }

    public function getId() {

        return $this->ident;
    }

    public function setEnvChanger(Bovinus_EnvVarChanger $changer) {

        $this->envVarChanger = $changer;
    }

    public function changesEnvVars() {

        return ($this->envVarChanger != null);
    }

    public function changeEnv($envVars, $token) {

        if ($this->envVarChanger != null) {
            $this->envVarChanger->change($envVars, $token, $this);
        }
    }

    public function undoEnvChange($envVars, $token) {

        if ($this->envVarChanger != null) {
            $this->envVarChanger->undo($envVars, $token, $this);
        }
    }

    private $ident = "";
    private $envVarChanger = null;

}

class Bovinus_Sequence implements Bovinus_Connectable, Bovinus_Pluggable, Bovinus_GrammarElement {

    public function __construct($elements) {

        $this->start = Bovinus_PlugNode::createConnector();
        $this->end = Bovinus_PlugNode::createConnector();

        $prev = $this->start;

        foreach ($elements as $element) {
            $prev->connect($element);
            $prev = $element;
        }

        $prev->connect($this->end);
    }

    public function connect(Bovinus_Connectable $successorElement) {

        $this->end->connectTo($successorElement->getSocket());

        return $successorElement;
    }

    public function getPlug() {

        return $this->end;
    }

    public function getSocket() {

        return $this->start;
    }

    private $start = null;
    private $end = null;

}

class Bovinus_Fork implements Bovinus_Connectable, Bovinus_Pluggable, Bovinus_GrammarElement {

    public function __construct($branches) {

        $this->start = Bovinus_PlugNode::createConnector();
        $this->end = Bovinus_PlugNode::createConnector();

        foreach ($branches as $branch) {
            $this->start->connect($branch)->connect($this->end);
        }
    }

    public function connect(Bovinus_Connectable $successorElement) {

        $this->end->connectTo($successorElement->getSocket());

        return $successorElement;
    }

    public function getPlug() {

        return $this->end;
    }

    public function getSocket() {

        return $this->start;
    }

    private $start;
    private $end;

}

class Bovinus_Multiplier implements Bovinus_Connectable, Bovinus_Pluggable, Bovinus_GrammarElement {

    const ZERO_TO_ONE = 1;
    const ZERO_TO_MANY = 2;
    const ONE_TO_MANY = 3;

    public function __construct($element, $multiplicity) {

        $this->start = Bovinus_PlugNode::createConnector();
        $this->end = Bovinus_PlugNode::createConnector();

        switch ($multiplicity) {

            case Bovinus_Multiplier::ZERO_TO_ONE:
                $this->start->connect($element)->connect($this->end);
                $this->start->connect($this->end);
                break;

            case Bovinus_Multiplier::ZERO_TO_MANY:
                $this->start->connect($element)->connect($this->start);
                $this->start->connect($this->end);
                break;

            case Bovinus_Multiplier::ONE_TO_MANY:
                $this->start->connect($element);
                $element->connect($this->end);
                $element->connect($element);
                break;

            default:
                throw new Exception("Unknown multiplicity '" . $multiplicity . "'");
                break;
        }
    }

    public function connect(Bovinus_Connectable $successorElement) {

        $this->end->connectTo($successorElement->getSocket());

        return $successorElement;
    }

    public function getPlug() {

        return $this->end;
    }

    public function getSocket() {

        return $this->start;
    }

    private $start;
    private $end;

}

class Bovinus_Condition implements Bovinus_Connectable, Bovinus_Pluggable, Bovinus_GrammarElement {

    public function __construct($conditionFunc) {

        $this->start = null;
        $this->end = Bovinus_PlugNode::createConnector();
    }

    public function connect(Bovinus_Connectable $successorElement) {

        $this->end->connectTo($successorElement->getSocket());

        return $successorElement;
    }

    public function getPlug() {

        return $this->end;
    }

    public function getSocket() {

        return $this->start;
    }

    private $start;
    private $end;

}

class Bovinus_ConditionalNode extends Bovinus_Node {

    public function __construct(Bovinus_ConditionChecker $checker, $endNode) {

        parent::__construct(Bovinus_Node::TECHNICAL);

        $this->checker = $checker;
        $this->end = $endNode;
    }

    public function getSuccessors($context) {

        if ($this->checker->isFulfilled($context)) {
            return $this->end;
        } else {
            throw new Bovinus_SuccessorError();
        }
    }

    private $checker;
    private $end;

}

class Bovinus_SuccessorError extends Exception {

    public function __construct() {

        parent::__construct("Unexpected successor!");
    }

}

interface Bovinus_ConditionChecker {

    function isFulfilled($context);
}
