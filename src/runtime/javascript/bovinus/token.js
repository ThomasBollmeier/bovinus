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

( function() {
	
	"use strict";

	/*global OOPtimus, bovinus */

	/*
	 * Token
	 */
	var Token = OOPtimus.defClass(function(text, types) {

		var _text = text, _types = types;
		var _lineStart = 0, _columnStart = 0;
		var _line = 0, _column = 0;

		this.getText = function() {
			return _text;
		};

		this.getTypes = function() {
			return _types;
		};
		
		this.getTypeIds = function() {
			
			var res = [];
			for (var i in _types) {
				res.push(_types[i].getId());
			}
			
			return res;
			
		};
		
		this.setStartPosition = function(line, column) {
			_lineStart = line;
			_columnStart = column;
		};
		
		this.getStartPosition = function () {
			return {
				line: _lineStart,
				column: _columnStart
			};
		};
		
		this.setPosition = function(line, column) {
			_line = line;
			_column = column;
		};
		
		this.getPosition = function() {
			return {
				line : _line,
				column : _column
			};
		};
		
		this.setEndPosition = this.setPosition;
		this.getEndPosition = this.getPosition;
		
	});
	/*
	 * TokenType
	 */

	var TokenType = OOPtimus.defClass(function() {

		var _id;

		if(this.constructor === TokenType) {
			throw new Error("Cannot instantiate abstract class!");
		}

		TokenType._currentId += 1;
		_id = TokenType._currentId;
		this._len = 0;

		this.getId = function() {
			return _id;
		};
	});

	TokenType.addStaticMember("compare", function(tokenType1, tokenType2) {

		if(tokenType1._len > tokenType2._len) {
			return -1;
		} else if(tokenType1._len < tokenType2._len) {
			return 1;
		} else {
			return 0;
		}

	});

	TokenType.addMember("createToken", function(text) {

		throw new Error("Method createToken is abstract!");

	});

	TokenType.addStaticMember("_currentId", 0);

	TokenType.addMember("_escape", function(text) {

		var regex = /([\+\*\.\[\]\(\)\^])/g;

		return text.replace(regex, "\\$1");

	});
	/*
	 * Word
	 */

	var Word = OOPtimus.defClass(TokenType, function(pattern) {

		this.superClass.call(this);

		var _regex = new RegExp("^(" + pattern + ")$");

		this._len = pattern.length;

		this.createToken = function(text) {

			var match = text.match(_regex);

			return match ? new Token(match[1], [this]) : null;

		};

		this.matches = function(text) {
			return text.match(_regex) ? true : false;
		};
	});
	/*
	 * Keyword
	 */

	var Keyword = OOPtimus.defClass(TokenType, function(keyword, caseSensitive) {

		var caseSens, keyw;

		this.superClass.call(this);

		if(caseSensitive !== undefined) {
			caseSens = caseSensitive;
		} else {
			caseSens = true;
		}
		keyw = keyword;
		if(!caseSens) {
			keyw = keyw.toUpperCase();
		}

		this.getKeyword = function() {
			return keyw;
		};

		this.isCaseSensitive = function() {
			return caseSens;
		};

		this.createToken = function(text) {

			var tmp = caseSens ? text : text.toUpperCase();

			return tmp === keyw ? new Token(text, [this]) : null;

		};
	});
	/*
	 * Literal
	 */

	var Literal = OOPtimus.defClass(TokenType, function() {

		if(Literal._creationNotAllowed) {
			throw new Error("Instance of Literal must not be created");
		}

		this.superClass.call(this);

	});

	Literal.addStaticMember("DELIMITERS", ['\'', '\"']);
	Literal.addStaticMember("ESCAPE_CHAR", '\\');

	Literal.addMember("createToken", function(text) {

		if(this.isLiteral(text)) {
			return new Token(text, [this]);
		} else {
			return null;
		}

	});

	Literal.addMember("isLiteral", function(text) {

		if(text.length < 2) {
			return false;
		}

		var firstChar = text.slice(0, 1), lastChar = text.slice(text.length - 1), firstIsDelim = false, i;

		for( i = 0; i < Literal.DELIMITERS.length; i += 1) {

			if(firstChar === Literal.DELIMITERS[i]) {
				firstIsDelim = true;
				break;
			}

		}

		return firstIsDelim && lastChar === firstChar;

	});

	Literal.addStaticMember("get", function() {

		if(!Literal._single) {

			Literal._creationNotAllowed = false;

			Literal._single = new Literal();

			Literal._creationNotAllowed = true;

		}

		return Literal._single;

	});

	Literal.addStaticMember("_single", null);
	Literal.addStaticMember("_creationNotAllowed", true);

	/*
	 * Prefix
	 */

	var Prefix = OOPtimus.defClass(TokenType, function(tokenText, escape) {

		this.superClass.call(this);

		if(escape === undefined) {
			escape = true;
		}

		var tmp = escape ? this._escape(tokenText) : tokenText;
		var regex = new RegExp("^(" + tmp + ")(\\S+)$");

		this._len = tokenText.length;

		this.createToken = function(text) {

			var match = text.match(regex);

			if(match) {
				return new Token(match[1], [this]);
			} else {
				return null;
			}

		};

		this.getRemainingRight = function(text) {

			var match = text.match(regex);

			if(match) {
				return match[2];
			} else {
				return "";
			}

		};
	});
	/*
	 * Postfix
	 */

	var Postfix = OOPtimus.defClass(TokenType, function(tokenText, escape) {

		this.superClass.call(this);

		if(escape === undefined) {
			escape = true;
		}

		var tmp = escape ? this._escape(tokenText) : tokenText;
		var regex = new RegExp("^(\\S+)(" + tmp + ")$");

		this._len = tokenText.length;

		this.createToken = function(text) {

			var match = text.match(regex);

			if(match) {
				return new Token(match[2], [this]);
			} else {
				return null;
			}

		};

		this.getRemainingLeft = function(text) {

			var match = text.match(regex);

			if(match) {
				return match[1];
			} else {
				return "";
			}

		};
	});
	/*
	 * Separator
	 */

	var Separator = OOPtimus.defClass(TokenType, function(tokenText, whiteSpaceAllowed, escape) {

		this.superClass.call(this);

		var wsYes = whiteSpaceAllowed === undefined ? true : whiteSpaceAllowed;
		var tmp;
		var regex;
                
                if (typeof escape !== "boolean") {
                    tmp = this._escape(tokenText);
                } else if (escape) {
                    tmp = this._escape(tokenText);
                } else {
                    tmp = tokenText;
                }

		if(wsYes) {
			regex = new RegExp("^(.*)(" + tmp + ")(.*)$");
		} else {
			regex = new RegExp("^(\\S+)(" + tmp + ")(\\S+)$");
		}

		this._len = tokenText.length;

		this.createToken = function(text) {

			var match = text.match(this._getRegex());

			if(match) {
				return new Token(match[2], [this]);
			} else {
				return null;
			}

		};

		this.getRemainingLeft = function(text) {

			var match = text.match(this._getRegex());

			if(match) {
				return match[1];
			} else {
				return "";
			}

		};

		this.getRemainingRight = function(text) {

			var match = text.match(this._getRegex());

			if(match) {
				return match[3];
			} else {
				return "";
			}

		};

		this._getRegex = function() {
			return regex;
		};

		this.getRegex = this._getRegex;

	});

	Separator.addStaticMember("create", function(pattern) {

		var sep = new Separator("");
		var regex = new RegExp(pattern);

		sep._len = pattern.length;

		sep._getRegex = function() {
			return regex;
		};

		sep.getRegex = sep._getRegex;

		return sep;

	});
	/*
	 * Export:
	 */

	bovinus.Token = Token;
	bovinus.TokenType = TokenType;
	bovinus.Word = Word;
	bovinus.Keyword = Keyword;
	bovinus.Literal = Literal;
	bovinus.Prefix = Prefix;
	bovinus.Postfix = Postfix;
	bovinus.Separator = Separator;

}());
