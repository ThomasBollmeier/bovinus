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

( function(imports, exports) {
    "use strict";

    var OOPtimus = imports.OOPtimus;
    var bovinus = imports.bovinus;

    var Node = OOPtimus.defClass(function(category, tokenType) {

        this._catg = category;
        this._tokenType = tokenType || null;
        this._techId = Node._nextTechId;
        Node._nextTechId += 1;

    });

    Node.addMember("getTokenType", function() {
        return this._tokenType;
    });

    Node.addMember("getTokenTypeId", function() {
        return this._tokenType && this._tokenType.getId() || -1;
    });

    Node.addMember("isRuleStart", function() {
        return this._catg === Node.RULE_START;
    });

    Node.addMember("isRuleEnd", function() {
        return this._catg === Node.RULE_END;
    });

    Node.addMember("isTokenNode", function() {
        return this._catg === Node.TOKEN;
    });

    Node.addMember("isTechnicalNode", function() {
        return this._catg === Node.TECHNICAL;
    });

    Node.addMember("getSocket", function() {
        return this;
    });

    Node.addMember("getTechnicalId", function() {
        return this._techId;
    });
    // Node categories:
    Node.addStaticMember("RULE_START", 1);
    Node.addStaticMember("RULE_END", 2);
    Node.addStaticMember("TOKEN", 3);
    Node.addStaticMember("TECHNICAL", 4);

    // Other static members:
    Node.addStaticMember("_nextTechId", 1);

    var PlugNode = OOPtimus.defClass(Node, function(category, tokenType) {

        this.superInit(category, tokenType);

        this._successors = [];

    });

    PlugNode.addMember("getSuccessors", function(context) {

        return this._successors;

    });

    PlugNode.addMember("getPlug", function() {

        return this;

    });

    PlugNode.addMember("connectTo", function(socket) {

        if(!bovinus.util.inArray(socket, this._successors)) {
            this._successors.push(socket);
        }

    });

    PlugNode.addMember("connect", function(successorElem) {

        this.connectTo(successorElem.getSocket());

        return successorElem;

    });

    var IdNode = {
        _id : "",
        getId : function() {
            return this._id;
        }
    };

    var RuleStartNode = OOPtimus.defClass(Node, function(ruleAccess, name, ident) {

        this.superInit(Node.RULE_START);

        this._ruleAccess = ruleAccess;
        this._name = name;
        this._id = ident;

    });

    RuleStartNode.realize(IdNode);

    RuleStartNode.addMember("getSuccessors", function(context) {

        var start = new PlugNode(Node.TECHNICAL);
        var end = new PlugNode(Node.TECHNICAL);

        this._ruleAccess.expand(start, end, context);
        end.connectTo(this._ruleAccess.getEndNode());

        return [start];

    });

    RuleStartNode.addMember("getEnvVars", function() {
        return this._ruleAccess.getEnvVars();
    });

    RuleStartNode.addMember("getName", function() {
        return this._name;
    });

    var RuleEndNode = OOPtimus.defClass(PlugNode, function(ruleAccess) {

        this.superInit(Node.RULE_END, null);

        this._ruleAccess = ruleAccess;

    });

    RuleEndNode.addMember("transform", function(astNode) {

        return this._ruleAccess.transform(astNode);

    });

    var TokenNode = OOPtimus.defClass(PlugNode, function(tokenType, ident) {

        this.superInit(Node.TOKEN, tokenType);

        this._id = ident;
        this._envVarChangeFunc = null;
        this._envVarUndoFunc = null;

    });

    TokenNode.realize(IdNode);

    TokenNode.addMember("setEnvChange", function(changeFunc, undoFunc) {

        this._envVarChangeFunc = changeFunc;
        this._envVarUndoFunc = undoFunc;

    });

    TokenNode.addMember("changesEnv", function() {

        return this._envVarChangeFunc && this._envVarUndoFunc ? true : false;

    });

    TokenNode.addMember("changeEnv", function(envVars, token) {

        if(this._envVarChangeFunc) {
            this._envVarChangeFunc(envVars, token, this);
        }

    });

    TokenNode.addMember("undoEnvChange", function(envVars, token) {

        if(this._envVarUndoFunc) {
            this._envVarUndoFunc(envVars, token, this);
        }

    });
	
    var ConditionalNode = OOPtimus.defClass(Node, function (conditionFunc, end) {
		
        this.superInit(Node.TECHNICAL);
		
        this._conditionFunc = conditionFunc;
        this._end = end;
		
    });
	
    ConditionalNode.addMember("getSuccessors", function (context) {
		
        if (this._conditionFunc(context)) {
            return [this._end];
        } else {
            throw new Error("No valid successor");
        }
		
    });
	
    var SwitchNode = OOPtimus.defClass(Node, function (branches, end) {
		
        this.superInit(Node.TECHNICAL);
		
        this._branches = branches;
        this._end = end;
		
    });
	
    SwitchNode.addMember("getSuccessors", function (context) {
		
        var keyword = context.getCurKeyword();
		
        if (!keyword) {
            return [];
        }
		
        var branch = this._branches[keyword.getKeyword()];
		
        if (branch !== undefined) {
            var start = new PlugNode(Node.TECHNICAL);
            start.connect(branch).connect(this._end);
            return [start];
        } else {
            return [];
        }
		
    });
	
    var Rule = OOPtimus.defClass(function(name, ident) {

        if(this.constructor === Rule) {
            throw new Error("Cannot instantiate abstract class!");
        }

        this._start = new RuleStartNode(this, name, ident);
        this._end = new RuleEndNode(this);
        this._envVars = {};

    });

    Rule.addMember("expand", function(start, end, context) {
        throw new Error("Abstract method 'expand' must be implemented");
    });

    Rule.addMember("transform", function(astNode) {
        return astNode;
    });

    Rule.addMember("getName", function() {
        return this._start.getName();
    });

    Rule.addMember("getEndNode", function() {
        return this._end;
    });

    Rule.addMember("getEnvVars", function() {
        return this._envVars;
    });

    Rule.addMember("setEnvVar", function(name, value) {
        this._envVars[name] = value;
    });

    Rule.addMember("getSocket", function() {
        return this._start;
    });

    Rule.addMember("getPlug", function() {
        return this._end;
    });

    Rule.addMember("connect", function(succElem) {

        this._end.connectTo(succElem.getSocket());

        return succElem;

    });

    var defineRule = function(ruleName, methods) {

        var init = methods["init"] || null;
        var expand = methods["expand"];
        var transform = methods["transform"] || null;

        var constructor = function(ident) {

            this.superInit(ruleName, ident);

            if (init !== null) {
                init.call(this, this._envVars);
            }

            this.expand = function(start, end, context) {
                expand.call(this, start, end, context);
            };
	    
            if (transform !== null) {
                this.transform = function(astNode) {
                    return transform.call(this, astNode);
                };
            }

        };
        return OOPtimus.defClass(Rule, constructor);

    };
    
    var Grammar = OOPtimus.defClass(Rule, function(tokenTypes) {

        this.superInit('', '');

        var _tokenTypes = tokenTypes;

        this.getTokenTypes = function() {
            return _tokenTypes;
        };
    });
    
    var defineGrammar = function (tokenTypes, methods) {
        
        var init = methods["init"] || null;
        var expand = methods["expand"];
        var transform = methods["transform"] || null;

        var constructor = function() {

            this.superInit(tokenTypes);

            if (init !== null) {
                init.call(this, this._envVars);
            }

            this.expand = function(start, end, context) {
                expand.call(this, start, end, context);
            };
            
            if (transform !== null) {
                this.transform = function(astNode) {
                    return transform.call(this, astNode);
                };
            }

        };

        return OOPtimus.defClass(Grammar, constructor);
            
    };


    var Multiplier = OOPtimus.defClass(function(element, mult) {

        this._start = new PlugNode(Node.TECHNICAL);
        this._end = new PlugNode(Node.TECHNICAL);

        switch (mult) {

            case Multiplier.ZERO_TO_ONE:
                this._start.connect(element).connect(this._end);
                this._start.connect(this._end);
                break;

            case Multiplier.ZERO_TO_MANY:
                this._start.connect(element).connect(this._start);
                this._start.connect(this._end);
                break;

            case Multiplier.ONE_TO_MANY:
                this._start.connect(element).connect(this._end);
                element.connect(element);
                break;

        }

    });

    Multiplier.addStaticMember("ZERO_TO_ONE", 1);
    Multiplier.addStaticMember("ZERO_TO_MANY", 2);
    Multiplier.addStaticMember("ONE_TO_MANY", 3);

    Multiplier.addMember("getSocket", function() {
        return this._start;
    });

    Multiplier.addMember("getPlug", function() {
        return this._end;
    });

    Multiplier.addMember("connect", function(succElem) {
        return this._end.connect(succElem);
    });
    
    var Sequence = OOPtimus.defClass(function(elements) {

        var i, current;

        this._start = new PlugNode(Node.TECHNICAL);
        this._end = new PlugNode(Node.TECHNICAL);
        current = this._start;
        for( i = 0; i < elements.length; i += 1) {
            current.connect(elements[i]);
            current = elements[i];
        }
        current.connect(this._end);

    });

    Sequence.addMember("getSocket", function() {
        return this._start;
    });

    Sequence.addMember("getPlug", function() {
        return this._end;
    });

    Sequence.addMember("connect", function(succElem) {
        return this._end.connect(succElem);
    });
	
    var Fork = OOPtimus.defClass(function(branches) {

        var i, current;

        this._start = new PlugNode(Node.TECHNICAL);
        this._end = new PlugNode(Node.TECHNICAL);
		
        for( i = 0; i < branches.length; i += 1) {
            this._start.connect(branches[i]).connect(this._end);
        }

    });

    Fork.addMember("getSocket", function() {
        return this._start;
    });

    Fork.addMember("getPlug", function() {
        return this._end;
    });

    Fork.addMember("connect", function(succElem) {
        return this._end.connect(succElem);
    });
	
    var Switch = OOPtimus.defClass(function (branches) {
		
        this._end = new PlugNode(Node.TECHNICAL);
        this._start = new SwitchNode(branches, this._end);
				
    });
	
    Switch.addMember("getSocket", function () {
        return this._start;
    });

    Switch.addMember("getPlug", function () {
        return this._end;
    });

    Switch.addMember("connect", function(succElem) {
        return this._end.connect(succElem);
    });
	
    var Condition = OOPtimus.defClass(function (conditionFunc) {
		
        this._end = new PlugNode(Node.TECHNICAL);
        this._start = new ConditionalNode(conditionFunc, this._end);
		
    });
	
    Condition.addMember("getSocket", function () {
        return this._start;
    });
	
    Condition.addMember("getPlug", function () {
        return this._end;
    });
	
    Condition.addMember("connect", function (succElem) {
        return this._end.connect(succElem);
    });

    var connector = function() {
	return new PlugNode(Node.TECHNICAL);
    };
	
    var tNode = function(tokenType, ident) {
        return new TokenNode(tokenType, ident);
    };
    var zeroToOne = function(element) {
        return new Multiplier(element, Multiplier.ZERO_TO_ONE);
    };
    var zeroToMany = function(element) {
        return new Multiplier(element, Multiplier.ZERO_TO_MANY);
    };
    var oneToMany = function(element) {
        return new Multiplier(element, Multiplier.ONE_TO_MANY);
    };
	
    var sequence = function() {
        var elements = [];
        for (var i=0; i<arguments.length; i+=1) {
            elements.push(arguments[i]);
        }
        return new Sequence(elements);
    };

    var fork = function() {
        var branches = [];
        for (var i=0; i<arguments.length; i+=1) {
            branches.push(arguments[i]);
        }
        return new Fork(branches);
    };
	
    var switchByKey = function(branches) {
        return new Switch(branches);
    };
        
    /* Exports: */
    exports.bovinus.define_grammar = defineGrammar;
    exports.bovinus.define_rule = defineRule;
    exports.bovinus.tnode = tNode;
	exports.bovinus.connector = connector;
    exports.bovinus.zero_to_one = zeroToOne;
    exports.bovinus.zero_to_many = zeroToMany;
    exports.bovinus.one_to_many = oneToMany;
    exports.bovinus.sequence = sequence;
    exports.bovinus.fork = fork;
    exports.bovinus.switch_by_key = switchByKey;
    exports.bovinus.guard = function(condFunc) { 
        return new Condition(condFunc);
    };

}( {
    "OOPtimus" : OOPtimus,
    "bovinus" : bovinus
}, {
    "bovinus" : bovinus
}) );

