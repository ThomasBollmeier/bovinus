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
    
    var AstNode = OOPtimus.defClass(function(name, text, ident) {
        
        this._name = name || "";
        this._text = text || "";
        this._id = ident || "";
        
        this._parent = null;
        this._children = [];
        
    });
    
    AstNode.addMember("copy", function () {
        
        var res = new AstNode(this._name, this._text, this._id);
        
        for (var i=0; i<this._children.length; i++) {
            var child = this._children[i].copy();
            res.addChild(child);
        }
        
        return res;
        
    });
    
    AstNode.addMember("addChild", function (child) {
       
        this._children.push(child);
        child._parent = this;
       
    });
    
    AstNode.addMember("removeChildren", function () {
        
        for (var i=0; i<this._children.length; i++) {
            this._children[i]._parent = null;
        }
        
        this._children = [];
        
    });
    
    AstNode.addMember("replaceChild", function (oldChild, newChild) {
        
        for (var i=0; i<this._children.length; i++) {
            if (this._children[i] === oldChild) {
                this._children[i] = newChild;
            }
        }
                
    });
    
    AstNode.addMember("setName", function (name) {
        this._name = name;
    });
    
    AstNode.addMember("getName", function () {
        return this._name;
    });
    
    AstNode.addMember("getText", function () {
        return this._text;
    });

    AstNode.addMember("getParent", function () {
        return this._parent;
    });

    AstNode.addMember("getChildren", function () {
        return this._children;
    });
    
    AstNode.addMember("getChildrenByName", function (name) {
        
        var res = [];
        
        for (var i=0; i<this._children.length; i++) {
            if (this._children[i]._name === name) {
                res.push(this._children[i]);
            }
        }
        
        return res;
        
    });
    
    AstNode.addMember("getChild", function (name) {
        
        for (var i=0; i<this._children.length; i++) {
            if (this._children[i]._name === name) {
                return this._children[i];
            }
        }
        
        return null;
        
    });
    
    AstNode.addMember("setId", function (ident) {
        this._id = ident;
    });
    
    AstNode.addMember("getId", function () {
        return this._id;
    });

    AstNode.addMember("clearId", function() {
        this._id = "";
    });
    
    AstNode.addMember("getChildById", function (ident) {
        
        for (var i=0; i<this._children.length; i++) {
            if (this._children[i]._id === ident) {
                return this._children[i];
            }
        }
        
        return null;
        
    });
    
    AstNode.addMember("getChildrenById", function (ident) {
        
        var res = [];
        
        for (var i=0; i<this._children.length; i++) {
            if (this._children[i]._id === ident) {
                res.push(this._children[i]);
            }
        }
        
        return res;
        
    });
    
    AstNode.addMember("hasChildren", function() {
        return ( this._children.length > 0 );
    });

	AstNode.addMember("toJSON", function(indentLevel) {

		var level = indentLevel || 0;
		var indent = "";
		var i;

		for (i=0; i<level; i++) {
			indent += "\t";
		}
		var indent2 = indent + "\t";

		var res = indent + "{";
		res += "\n" + indent2 + "\"name\": \"" + this._name + "\"";
		res += ",\n" + indent2 + "\"text\": \"" + this._text + "\"";
		res += ",\n" + indent2 + "\"id\": \"" + this._id + "\"";

		res += ",\n" + indent2 + "\"children\": [";
		var hlp = "";
		for (i=0; i<this._children.length; i++) {
			if (hlp.length) {
				hlp += ",";
			}
			hlp += "\n" + this._children[i].toJSON(level+1);
		}
		res += hlp;
		res += "\n" + indent2 + "]";
		
		res += "\n" + indent + "}";

		return res;

	});
    
    exports.bovinus.AstNode = AstNode;
        
} ({
    "OOPtimus" : OOPtimus,
    "bovinus" : bovinus
}, {
    "bovinus" : bovinus
}) );    
