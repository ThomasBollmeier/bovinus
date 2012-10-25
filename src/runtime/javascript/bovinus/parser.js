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
     * Parser
     */
	
    var Parser = OOPtimus.defClass(function(grammar) {
		
        this._grammar = grammar;
	
        this._lexer = new bovinus.Lexer();
		
        var tokenTypes = this._grammar.getTokenTypes();
        var i;
		
        for (i=0; i<tokenTypes.length; i+=1) {
            this._lexer.addTokenType(tokenTypes[i]);
        }

		this._fullBacktracking = false;
		
    });
        
    Parser.addMember("enableLineComments", 
        function (lineCommentStart) {
            
            var _start = lineCommentStart || "//";
            
            this._lexer.enableLineComments(_start);
            
        });
        
    Parser.addMember("enableBlockComments",
        function (blockCommentStart, blockCommentEnd) {
            
            var _start = blockCommentStart || "/*";
            var _end = blockCommentEnd || "*/";
            
            this._lexer.enableBlockComments(_start, _end);
            
        });

	Parser.addMember("enableFullBacktracking", function(fullBacktracking) {

		this._fullBacktracking = fullBacktracking;

	});
        
    Parser.addMember("parse", function (inStream) {
            
        this._lexer.setInputStream(inStream);
        this._tokenBuffer = [];
        
        var path = new bovinus.Path();
        path.push(this._grammar.getSocket(), null);
        
        var 
        error = false,
		errorMsg = "", 
        done = false,
        findResult;
        
        while (!done) {
            
            var token = this._getNextToken();
            
            if (!token) {
            
                findResult = this._findPathToEnd(path);
                path = findResult.path;
                if (findResult.found) {
                    done = true;
                } else {
                    findResult = this._findNextSibling(path);
                    path = findResult.path;
                    if (!findResult.found) {
                        done = true;
                        error = true;
			errorMsg = "Unexpected end of input";
                    }
                }
                
                continue;

            }
            
            findResult = this._findNextMatchingNode(token, path);
            path = findResult.path;
            
            if (findResult.found) {
                this._tokenBuffer.pop();
            } else {
                findResult = this._findNextSibling(path);
                path = findResult.path;
                if (!findResult.found) {
                    done = true;
                    error = true;
                }
            }
            
        }
        
        if (!error) {
            return this._createAst(path);
        } else {
            this._throwError(errorMsg);
        }
            
    });
    
    Parser.addMember("parseString", function (text) {
	return this.parse(new bovinus.StringInput(text));
    });
    
    Parser.addMember("_getNextToken", function () {
        
        if (this._tokenBuffer.length === 0) {
            var token = this._lexer.getNextToken();
            if (token) {
                this._tokenBuffer.push(token);
            }
        }
        
        if (this._tokenBuffer.length > 0) {
            return this._tokenBuffer[this._tokenBuffer.length-1];
        } else {
            return null;
        }
        
    });
    
    Parser.addMember("_findPathToEnd", function (path) {
        
        var node = path.getElement(-1).getGrammarNode();
        var context = new bovinus.Context(path);
        var error = null;
        
        try {
            var successors = node.getSuccessors(context);
        } catch(error) {
            return {
                "found": false, 
                "path": path
            };
        }
        
        if (successors.length === 0) {
            // we are done...
            return {
                "found": true, 
                "path": path
            };
        }
        
        for (var i=0; i<successors.length; i++) {
            
            var succ = successors[i];
            
            if (succ.isTokenNode()) {
                continue;
            }
            
            path.push(succ, null);
            
            var findResult = this._findPathToEnd(path);
            if (findResult.found) {
                return findResult;
            } else {
                path.pop();
            }
            
        }
        
        return {
            "found": false, 
            "path": path
        };
        
    });
    
    Parser.addMember("_findNextSibling", function (path) {
        
        var removed = [];
        var elem, token;
        var siblingResult;
        
        while (true) {
            
            if (path.getLength() < 2) {
                // restore original path before return:
                while (removed.length > 0) {
                    elem = removed.pop();
                    token = elem.getToken();
                    if (token) {
                        this._tokenBuffer.pop();
                    }
                    path.push(elem.getGrammarNode(), token);
                }
                
                return {
                    "found": false, 
                    "path": path
                };
                
            }
            
            siblingResult = this._gotoNextSibling(path);
            path = siblingResult.path;
            
            if (siblingResult.found) {
                return {
                    "found": true, 
                    "path": path
                };
            } else {
		
				if (this._fullBacktracking === false) {
				
					// A backward navigation must not exit the current rule:
					var grammarNode = path.getElement(-1).getGrammarNode();
					if (grammarNode != null && grammarNode.isRuleEnd()) {
						return {
							"found": false,
							"path": path
							};
					}

				}

                elem = path.pop();
                removed.push(elem);
                token = elem.getToken();
                if (token) {
                    this._tokenBuffer.push(token);
                }
            }
            
        }
        
    });
    
    Parser.addMember("_gotoNextSibling", function (path) {
        
        if (path.getLength() < 2) {
            return {
                "found": false,
                "path": path
            };
        }
        
        var elem = path.pop();
        var start = elem.getGrammarNode();
        var token = elem.getToken();
        var prev = path.getElement(-1).getGrammarNode();
        var context = new bovinus.Context(path, token);
        var error;
        
        try {
            var successors = prev.getSuccessors(context);
        } catch (error) {
            path.push(start, token);
            return {
                "found": false,
                "path": path
            };
        }
        
        var idx = bovinus.util.indexOf(start, successors);
        
        if (idx < 0 || idx === successors.length - 1) {
            path.push(start, token);
            return {
                "found": false, 
                "path": path
            };
        }
        
        var sibling = successors[idx+1];
        path.push(sibling, null);
        
        if (token) {
            this._tokenBuffer.push(token);
        }
        
        return {
            "found": true, 
            "path": path
        };
        
    });
    
    Parser.addMember("_findNextMatchingNode", function (token, path) {
        
        var elem = path.getElement(-1);
        var startNode = elem.getGrammarNode();
        var startToken = elem.getToken();
        var findResult;
        var error;
        
        if (startNode.isTokenNode() && !startToken) {
            
            var ttypeId = startNode.getTokenTypeId();
            
            if (bovinus.util.inArray(ttypeId, token.getTypeIds())) {
				// combination of pop and push necessary to ensure 
				// that method "changeEnv" is called on token nodes:
				path.pop();
				path.push(elem.getGrammarNode(), token);
                return {
                    "found": true,
                    "path": path
                };
            } else {
                return {
                    "found": false,
                    "path": path
                };
            }
            
        }
        
        try {
            var context = new bovinus.Context(path, token);
            var successors = startNode.getSuccessors(context);
        } catch (error) {
            return {
                "found": false,
                "path": path
            };
        }
        
        for (var idx in successors) {
            
            path.push(successors[idx], null);
            findResult = this._findNextMatchingNode(token, path);
            path = findResult.path;
            if (findResult.found) {
                return {
                    "found": true,
                    "path": path
                };
                
            } else {
                path.pop();
            }
            
        }
        
        return {
            "found": false,
            "path": path
        };
        
    });
    
    Parser.addMember("_throwError", function (message) {
        
        var errorMsg = message;

		if (errorMsg.length === 0) {
        
		    if (this._tokenBuffer.length > 0) {
            
			var token = this._tokenBuffer[0];
			var startPos = token.getStartPosition();
	           	var endPos = token.getEndPosition();
            
		        errorMsg = "Unexpected token '" + token.getText() + "'";
		        errorMsg += " at Ln: " + startPos.line + ", Col: " + startPos.column;
 
	            } else {
            
			errorMsg = "Parsing error";
            
		    }

		}
        
        throw new Error(errorMsg);
        
    });
    
    Parser.addMember("_createAst", function (path) {
        
        var stack = [];
        var current = null;
        var numElements = path.getLength();
        var element, node, token, text;
        
        for (var i=0; i<numElements; i++) {
            
            element = path.getElement(i);
            node = element.getGrammarNode();
            token = element.getToken();
            
            if (node.isRuleStart()) {
                
                if (current) {
                    stack.push(current);
                }
                
                text = token && token.getText() || "";
                
                current = new bovinus.AstNode(node.getName(), text, node.getId());
                            
            } else if (node.isRuleEnd()) {
                
                // -> call tree refactoring (keep ID)
                var tmp = current;
                current = node.transform(current);
                if (tmp !== current) {
                    current.setId(tmp.getId());
                }
                
                var parent = stack && stack.pop() || null;
                
                if (parent) {
                    parent.addChild(current);
                    current = parent;
                } else {
                    break; // we are done
                }
                                
            } else if (node.isTokenNode()) {
                
                text = token && token.getText() || "";
                current.addChild(new bovinus.AstNode('token', text, node.getId()));
                
            }
            
        }
        
        return current;
                
    });
    
    exports.bovinus.Parser = Parser;
        	
}({
    "OOPtimus" : OOPtimus,
    "bovinus" : bovinus
}, {
    "bovinus" : bovinus
}));
