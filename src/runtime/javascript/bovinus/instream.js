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
	 * Interface InStream
	 * 		Methods
	 * 			getNextChar() -> returns next character from input stream
	 * 			endOfInput() -> returns true if end of input reached
	 */

	/*
	 * StringInput
	 */
	var StringInput = OOPtimus.defClass(function(text) {

		var _text = text, _idx = 0;

		this.getNextChar = function() {

			if(!this.endOfInput()) {
				var nextChar = _text.slice(_idx, _idx + 1);
				_idx += 1;
				return nextChar;
			} else {
				return '';
			}

		};

		this.endOfInput = function() {
			return _idx >= _text.length;
		};
	});
	/*
	 * Export:
	 */

	bovinus.StringInput = StringInput;

}());
