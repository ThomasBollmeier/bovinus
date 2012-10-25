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
    
    /*
     * PathElement
     */
    
    var PathElement = OOPtimus.defClass(
        function (grammarNode, token) {
        
            this._grammarNode = grammarNode;
            this._token = token;
        
        });
    
    PathElement.addMember("getGrammarNode", function () {
        return this._grammarNode;
    });

    PathElement.addMember("setToken", function (token) {
        this._token = token;
    });

    PathElement.addMember("getToken", function () {
        return this._token;
    });
    
    PathElement.addMember("getMatchedTokenType", function() {
        return this._grammarNode.getTokenType();
    });
    
    /*
     * Path
     */ 
    var Path = OOPtimus.defClass(function () {
        
        this._elements = [];
        this._envStack = []; // <-- environments stack
        
    });
    
    Path.addMember("push", function (grammarNode, token) {
        
        var element = new PathElement(grammarNode, token);
        
        this._elements.push(element);
        
        if (grammarNode.isRuleStart()) {
            this._envStack.push(grammarNode.getEnvVars());
        } else if (grammarNode.isRuleEnd()) {
            this._envStack.push(false);
        } else if (grammarNode.isTokenNode() && grammarNode.changesEnv()) {
            var envVars = this._getCurEnvVars();
            if (envVars) {
                grammarNode.changeEnv(envVars, token);
            }
        }
                
    });
    
    Path.addMember("pop", function () {
        
        var res = this._elements.pop();
        var node = res.getGrammarNode();
        
        if (node.isRuleStart() || node.isRuleEnd() ) {
            this._envStack.pop();
        } else if (node.isTokenNode() && node.changesEnv()) {
            var envVars = this._getCurEnvVars();
            if (envVars) {
                node.undoEnvChange(envVars, res.getToken());
            }
        }
        
        return res;
        
    });
    
    Path.addMember("popToken", function () {
        return this.pop().getToken();
    });
    
    Path.addMember("getLength", function () {
        return this._elements.length;
    });
    
    Path.addMember("getElement", function (index) {
        
        var numElems = this._elements.length;
        var idx = index >= 0 ? index : index + numElems;
        
        if (idx < 0 || idx >= numElems) {
            throw new Error("Invalid path element index");
        }
        
        return this._elements[idx];
        
    });
    
    Path.addMember("getEnvVar", function (name) {
        
        var envVarStack = [];
        var i;
        
        for (i=0; i<this._envStack.length; i+=1) {
            var envVars = this._envStack[i];
            if (typeof envVars !== "boolean") {
                envVarStack.push(envVars);
            } else {
                envVarStack.pop();
            }
        }
        
        i = envVarStack.length - 1;
        while (i>=0) {
            if (envVarStack[i][name] !== undefined) {
                return envVarStack[i][name];
            }
            i -= 1;
        }
        
        return null;
        
    });
    
    Path.addMember("toString", function (technical) {
        
        var _technical = technical || false;
        var token, i, node;
        var res = "";
        
        if (!_technical) {
            
            for (i=0; i<this._elements.length; i++) {
                token = this._elements[i].getToken();
                if (token) {
                    if (res !== "") {
                        res += ".";
                    }
                    res += token.getText();
                }
            }
            
        } else {
            
            for (i=0; i<this._elements.length; i++) {
                node = this._elements[i].getGrammarNode();
                if (res !== "") {
                    res += ":";
                }
                res += node.getTechnicalId();
            }
            
        }
        
        return res;
        
    });
    
    Path.addMember("_getCurEnvVars", function () {
        
        var idx = this._envStack.length - 1;
        var level = 0;
        var envVars;
                
        while (idx >= 0) {
            envVars = this._envStack[idx];
            if (typeof envVars !== "boolean") {
                if (level === 0) {
                    return envVars;
                }
                level += 1;
            } else {
                level -= 1;
            }
        }
        
        return null;
        
    });
    
    exports.bovinus.Path = Path;
    exports.bovinus.PathElement = PathElement;

}({
    "OOPtimus" : OOPtimus,
    "bovinus" : bovinus
}, {
    "bovinus" : bovinus
}) );
