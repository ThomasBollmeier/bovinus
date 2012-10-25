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

( function() {"use strict";

	/*global OOPtimus, bovinus */

	var WSCharCode = {
		TAB : 9,
		LINEBREAK : 10,
		VTAB : 11,
		FORMFEED : 12,
		SPACE : 32
	};

	var LexerMode = {
		NORMAL : 1,
		LINE_COMMENT : 2,
		BLOCK_COMMENT : 3,
		WSPACE: 4
	};

	var Lexer = OOPtimus.defClass(function() {

		this._instream = null;
		this._tokenizer = new bovinus.Tokenizer();
		this._stack = [];
		this._keywords = {};
		this._words = [];
		this._prefixes = [];
		this._postfixes = [];
		this._separators = [];
		this._literal = null;
		this._literalDelims = [];
		this._literalEscChar = null;
		this._currentLitDelim = '';
		this._wsCharCodes = [WSCharCode.TAB, WSCharCode.LINEBREAK, WSCharCode.VTAB, WSCharCode.FORMFEED, WSCharCode.SPACE];
		this._mode = LexerMode.NORMAL;
		this._lineCommentEnabled = false;
		this._lineCommentStart = '';
		this._blockCommentEnabled = false;
		this._blockCommentStart = '';
		this._blockCommentEnd = '';

	});

	Lexer.addMember("setInputStream", function(instream) {

		this._instream = instream;
		this._reset();

	});

	Lexer.addMember("_reset", function() {

		this._stack = [];
		this._inputBuffer = null;
		this._mode = LexerMode.NORMAL;

	});

	Lexer.addMember("addTokenType", function(tt) {

		switch (tt.constructor) {
			case bovinus.Keyword:
				this._keywords[tt.getKeyword()] = tt;
				break;
			case bovinus.Word:
				this._words.push(tt);
				break;
			case bovinus.Prefix:
				this._prefixes.push(tt);
				this._prefixes.sort(bovinus.TokenType.compare);
				break;
			case bovinus.Postfix:
				this._postfixes.push(tt);
				this._postfixes.sort(bovinus.TokenType.compare);
				break;
			case bovinus.Separator:
				this._separators.push(tt);
				this._separators.sort(bovinus.TokenType.compare);
				this._tokenizer.add_separator(tt);
				break;
			case bovinus.Literal:
				this._literal = tt;
				this._literalDelims = bovinus.Literal.DELIMITERS;
				this._literalEscChar = bovinus.Literal.ESCAPE_CHAR;
				this._tokenizer.set_literal(tt);
				break;
			default:
				throw new Error("Unknown token type");
		}

	});

	Lexer.addMember("enableLineComments", function(lineCommentStart) {

		this._lineCommentEnabled = true;
		this._lineCommentStart = lineCommentStart || "//";

	});

	Lexer.addMember("enableBlockComments", function(blockCommentStart, blockCommentEnd) {

		this._blockCommentEnabled = true;
		this._blockCommentStart = blockCommentStart || "/*";
		this._blockCommentEnd = blockCommentEnd || "*/";

	});

	Lexer.addMember("getNextToken", function() {

		if(!this._instream) {
			return null;
		}

		if(this._stack.length > 0) {
			return this._stack.pop();
		}

		if (!this._inputBuffer) {
			this._initBuffer();
		}

		var hlp = this._getNextChars();

		if (hlp) {
			var tokenStr = hlp.text;
			var endLine = hlp.line;
			var endColumn = hlp.column;
		} else {
			return null;
		}

		this._stack = this._getTokens(tokenStr, endLine, endColumn);
		
		if(this._stack.length > 0) {
			return this._stack.pop();
		} else {
			var msg = "Unknown token '" + tokenStr + "'";
			msg += " at line " + endLine + ", column " + endColumn;
			throw new Error(msg);
		}

	});

	Lexer.addMember("_getNextChars", function () {

		var res = null;

		while (true) {

			var content = this._inputBuffer.getContent();

			if (content.length === 0) {
				if (this._consumed) {
					res = {};
					var pos = this._inputBuffer.getPositionInfo();
					res.line = pos.line;
					res.column = pos.column;
					res.text = this._consumed;
				}
				this._consumed = "";
				break;
			}

			var newMode = this._getNewMode(content); 

			if (newMode  > 0) {

				res = this._onNewMode(newMode);
				if (res) {
					break;
				}

			} else {

				this._consumeContent(content);

			}

		}

		return res;

	});

	Lexer.addMember("_initBuffer", function () {
			
		var fillSize = 2; // <-- needed to detect escape chars in literals
			
		if (this._lineCommentEnabled) {
			if (this._lineCommentStart.length > fillSize) {
				fillSize = this._lineCommentStart.length;
			}
		}

		if (this._blockCommentEnabled) {
			if (this._blockCommentStart.length > fillSize) {
				fillSize = this._blockCommentStart.length;
			}	
			if (this._blockCommentEnd.length > fillSize) {
				fillSize = this._blockCommentEnd.length;
			}	
		}

		this._inputBuffer = new bovinus.InputBuffer(this._instream, fillSize);
		this._consumed = "";

	});

	Lexer.addMember("_getNewMode", function (content) {

		var res = -1;
		
		switch (this._mode) {

		case LexerMode.NORMAL:
			if (this._startsWS(content)) {
				res = LexerMode.WSPACE;
			} else if (this._startsLineComment(content)) {
				res = LexerMode.LINE_COMMENT;
			} else if (this._startsBlockComment(content)) {
				res = LexerMode.BLOCK_COMMENT;
			} 	
			break;
		case LexerMode.WSPACE:
			if (!this._isWhiteSpace(content[0])) {
				if (this._startsLineComment(content)) {
					res = LexerMode.LINE_COMMENT;
				} else if (this._startsBlockComment(content)) {
					res = LexerMode.BLOCK_COMMENT;
				} else {
					res = LexerMode.NORMAL;
				} 	
			}
			break;
		case LexerMode.LINE_COMMENT:
			if (this._endsLineComment(content)) {
				res = LexerMode.NORMAL;
			}
			break;
		case LexerMode.BLOCK_COMMENT:
			if (this._endsBlockComment(content)) {
				res = LexerMode.NORMAL;
			}
			break;

		}

		return res;

	});

	Lexer.addMember("_startsWith", function (content, start) {

		var tmp = start.replace('*', '\\*');
		var regex = new RegExp("^" + tmp );

		return regex.exec(content) ? true : false;

	});

	Lexer.addMember("_startsWS", function (content) {
		
		if (this._currentLitDelim === "") {

			var code = content.charCodeAt(0);

			for (var i=0, len=this._wsCharCodes.length; i<len; i++) {
				if (code === this._wsCharCodes[i]) {
					return true;
				}		
			}

			return false;

		} else {
			return false;
		}

	});

	Lexer.addMember("_startsLineComment", function (content) {

		var res = false;

		if (this._lineCommentEnabled && this._currentLitDelim === "") {
			res = this._startsWith(content, this._lineCommentStart);
		}

		return res;

	});

	Lexer.addMember("_startsBlockComment", function (content) {

		var res = false;

		if (this._blockCommentEnabled && this._currentLitDelim === "") {
			res = this._startsWith(content, this._blockCommentStart);
		}

		return res;

	});

	Lexer.addMember("_endsLineComment", function (content) {

		var res = false;

		if (this._lineCommentEnabled && this._currentLitDelim === "") {
			res = content[0] === "\n";
		}

		return res;
		
	});

	Lexer.addMember("_endsBlockComment", function (content) {

		var res = false;

		if (this._blockCommentEnabled && this._currentLitDelim === "") {
			res = this._startsWith(content, this._blockCommentEnd);
		}

		return res;
		
	});

	Lexer.addMember("_onNewMode", function (newMode) {

		var res = null;
		var i, len;

		switch (this._mode) {

		case LexerMode.NORMAL:
			var pos = this._inputBuffer.getPositionInfo();
			var line = pos.line;
			var column = pos.column;
			switch (newMode) {
			case LexerMode.WSPACE:
				len = 1;
				break;
			case LexerMode.LINE_COMMENT:
				len = this._lineCommentStart.length;
				break;
			case LexerMode.BLOCK_COMMENT:
				len = this._blockCommentStart.length;
				break;
			}
			for (i=0; i<len; i++) {
				this._inputBuffer.consumeChar();
			}
			if (this._consumed) {
				res = {};
				res.line = line;
				res.column = column;
				res.text = this._consumed;
			}
			this._consumed = "";
			break;

		case LexerMode.WSPACE:
			switch (newMode) {
			case LexerMode.NORMAL:
				var ch = this._inputBuffer.consumeChar();
				this._consumed += ch;
				break;
			case LexerMode.LINE_COMMENT:
				len = this._lineCommentStart.length;
				for (i=0; i<len; i++) {
					this._inputBuffer.consumeChar();
				}
				break;	
			case LexerMode.BLOCK_COMMENT:
				len = this._blockCommentStart.length;
				for (i=0; i<len; i++) {
					this._inputBuffer.consumeChar();
				}
				break;	
			}
			break;

		case LexerMode.LINE_COMMENT:
			// can only change to normal mode:
			this._inputBuffer.consumeChar(); // <-- consume '\n'
			break;

		case LexerMode.BLOCK_COMMENT:
			// can only change to normal mode:
			len = this._blockCommentEnd.length;
			for (i=0; i<len; i++) {
				this._inputBuffer.consumeChar(); 
			}
			break;

		}

		this._mode = newMode;

		return res;

	});

	Lexer.addMember("_consumeContent", function (content) {

		var ch;

		if (this._mode === LexerMode.NORMAL) {

			if (this._literal !== null) {

				var escaped = false;
 
				if (this._currentLitDelim === "") {
					if (bovinus.util.inArray(content[0], this._literalDelims)) {
						this._currentLitDelim = content[0];
					}
				} else {

					// Currently inside literal
					// Check for escape characters and treat them separately:
					if (this._literalEscChar) {
						var escChar = this._literalEscChar.replace("\\", "\\\\");
						for (var i=0, len=this._literalDelims.length; i<len; i++) {
							var regex = new RegExp("^" + escChar + this._literalDelims[i] + ".*");
							if (content.match(regex)) {
								escaped = true;
								break;							
							}
						}
					} 

					if (content[0] === this._currentLitDelim) {
						this._currentLitDelim = "";
					}

				}

				if (escaped) {
					this._inputBuffer.consumeChar();
				}

				ch = this._inputBuffer.consumeChar();
				this._consumed += ch; 

			} else {

				ch = this._inputBuffer.consumeChar();
				this._consumed += ch; 

			}

		} else {
			ch = this._inputBuffer.consumeChar();
		}

	});

	Lexer.addMember("_getTokens", function(text, endLine, endColumn) {

		var res = [];
	
		var parts = this._tokenizer.split_at_separators(text);
		// Reverse order to fit into stack logic:
		parts.reverse();

		var col_end = endColumn;

		for (var i=0, ii=parts.length; i<ii; i++) {

			var item = parts[i];

			if (item.sep != null) {
				var token = new bovinus.Token(item.text, [item.sep]);
				token.setStartPosition(endLine, col_end - item.text.length + 1);
				token.setEndPosition(endLine, col_end);
				res.push(token);
			} else {
				res = res.concat(this._getNonSepTokens(item.text, endLine, col_end));
			}

			col_end -= item.text.length;

		}

		return res;

	});

	Lexer.addMember("_getNonSepTokens", function(text, endLine, endColumn) {

		var token;

		// Handle literals:
		if(this._literal) {
			token = this._literal.createToken(text);
			if(token) {
				token.setStartPosition(endLine, endColumn - text.length + 1);
				token.setEndPosition(endLine, endColumn);
				return [token];
			}

		}

		var res = [], i, col, left, right;

		// Find prefixes:
		for( i = 0; i < this._prefixes.length; i += 1) {

			var prefix = this._prefixes[i];
			token = prefix.createToken(text);

			if(token) {

				right = prefix.getRemainingRight(text);

				if(right) {
					res = this._getTokens(right, endLine, endColumn);
				}

				col = endColumn - right.length;
				token.setStartPosition(endLine, col - token.getText().length + 1);
				token.setEndPosition(endLine, col);
				res.push(token);

				return res;

			}

		}

		// Find postfixes:
		for( i = 0; i < this._postfixes.length; i += 1) {

			var postfix = this._postfixes[i];
			token = postfix.createToken(text);

			if(token) {
				
				left = postfix.getRemainingLeft(text);
				token.setStartPosition(endLine, endColumn - token.getText().length + 1);
				token.setEndPosition(endLine, endColumn);
				res = [token];

				if(left) {
					col = endColumn - token.getText().length;
					res = res.concat(this._getTokens(left, endLine, col));
				}

				return res;

			}

		}

		// Find (key)words:

		var matchingWords = [];

		if(this._keywords[text] !== undefined) {
			matchingWords = [this._keywords[text]];
		} else {
			// perhaps case insensitive keyword?
			var kw = this._keywords[text.toUpperCase()];
			if(kw !== undefined && !kw.isCaseSensitive()) {
				matchingWords = [kw];
			}
		}

		for( i = 0; i < this._words.length; i += 1) {
			if(this._words[i].matches(text)) {
				matchingWords.push(this._words[i]);
			}
		}

		if(matchingWords.length > 0) {
			token = new bovinus.Token(text, matchingWords);
			token.setStartPosition(endLine, endColumn - text.length + 1);
			token.setEndPosition(endLine, endColumn);
			return [token];
		}

		var msg = "Unknown token '" + text + "'";
		msg += " ending at line " + endLine + ", column " + endColumn;

		throw new Error(msg);

	});

	Lexer.addMember("_isLiteralDelim", function(ch) {

		var res = false, i;

		for( i = 0; i < this._literalDelims.length; i += 1) {
			if(this._literalDelims[i] === ch) {
				res = true;
				break;
			}
		}

		return res;

	});

	Lexer.addMember("_isWhiteSpace", function(ch) {

		var res, i;

		if(this._isLiteralDelim(ch)) {

			if(this._currentLitDelim !== '') {
				if(ch === this._currentLitDelim) {
					this._currentLitDelim = '';
				}
			} else {
				this._currentLitDelim = ch;
			}
			res = false;

		} else if(this._currentLitDelim !== '') {
			res = false;

		} else {
			res = false;

			for( i = 0; i < this._wsCharCodes.length; i += 1) {
				if(ch.charCodeAt(0) === this._wsCharCodes[i]) {
					res = true;
					break;
				}
			}

		}

		return res;

	});

	bovinus.Lexer = Lexer;

}());
