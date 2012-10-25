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

	var InputBuffer = OOPtimus.defClass(function(stream, fillSize) {

		var _stream = stream, _fillSize = fillSize || 1, _content = "";
		var _positionInfo = { line: 1, column: 0 };

		var fillContent = function() {

			while(_content.length < _fillSize) {
				if(_stream.endOfInput()) {
					break;
				}
				_content += _stream.getNextChar();
			}

		};

		this.setFillSize = function(newFillSize) {

			_fillSize = newFillSize;

		};

		this.getContent = function() {

			fillContent();

			return _content.slice(0, _fillSize);

		};

		this.getPositionInfo = function () {
			
			return _positionInfo;

		};

		this.consumeChar = function() {

			if(_content.length > 0) {

				var ch = _content[0];

				if(_content.length > 1) {
					_content = _content.slice(1);
				} else {
					_content = "";
				}

				fillContent();

				if (ch !== "\n") {
					_positionInfo.column++;
				} else {
					_positionInfo.line++;
					_positionInfo.column = 0;
				}

				return ch;

			} else {
				return '';
			}

		};

		this.consumeAll = function() {

			var res;

			if ( _content.length <= _fillSize ) {
				res = _content;
				_content = "";
			} else {
				res = _content.slice(0, _fillSize);
				_content = _content.slice(_fillSize);
			}

			for (var i=0, len=res.length; i<len; i++) {
				if (res[i] !== "\n") {
					_positionInfo.column++;
				} else {
					_positionInfo.line++;
					_positionInfo.column = 0;
				}
			}

			return res;

		};
	});

	bovinus.InputBuffer = InputBuffer;

}());
