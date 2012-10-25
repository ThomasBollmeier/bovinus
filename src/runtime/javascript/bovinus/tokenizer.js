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

(function(imports, exports) {
	
	"use strict";

	var oop = imports.OOPtimus;
	var bov = imports.bovinus;

	var Tokenizer = oop.defClass(function() {

        this._literal = null;
        this._literalDelims = ['"', "'"];
        this._literalEscChar = '\\';
        this._separators = [];

	});

	Tokenizer.addMember("set_literal", function(literal) {

        this._literal = literal;
        this._literalDelims = bov.Literal.DELIMITERS;
        this._literalEscChar = bov.Literal.ESCAPE_CHAR;

	});

	Tokenizer.addMember("add_separator", function(sep) {

		this._separators.push(sep);

	});

    Tokenizer.addMember("split_at_separators", function(text) {

        var worklist = [{text:text, sep:null}];

		for (var i=0, ii=this._separators.length; i<ii; i++) {
			
			var tmp = [];
			var sep = this._separators[i];

			for (var j=0, jj=worklist.length; j<jj; j++) {
				var item = worklist[j];
				if (item.sep != null) {
					tmp.push(item);
				} else {
					tmp = tmp.concat(this._split_at_sep(item.text, sep));
				}
			}

			worklist = tmp;

		}

		return worklist;

	});


	Tokenizer.addMember("_split_at_sep", function(text, sep) {

		var res = [];

		var worklist = [{text: text, sep: null, checked: false}];
		var regex = sep.getRegex();

		while (true) {

			var tmp = []
			var doNextStep = false;
			var i, ii;
			var item;

			for (i=0, ii=worklist.length; i<ii; i++) {

				item = worklist[i];

				if (item.checked) {
					tmp.push(item);
					continue;
				}

				var m = item.text.match(regex);
				var num_match_groups = m != null ? m.length - 1 : -1;
				if ( num_match_groups == 0 || num_match_groups == 1 || num_match_groups == 3 ) {
					doNextStep = true;
					if (num_match_groups == 0) {
						tmp.push({text: m[0], sep: sep, checked: true});
					} else if (num_match_groups == 1) {
						tmp.push({text: m[1], sep: sep, checked: true});
					} else {
						if (m[1].length > 0) {
							tmp.push({text: m[1], sep: null, checked: false});
						}
						tmp.push({text: m[2], sep: sep, checked: true});
						if (m[3].length > 0) {
							tmp.push({text: m[3], sep: null, checked: false});
						}
					}
				} else {
					item.checked = true;
					tmp.push(item);
				}

			}

			if (!doNextStep) {
				for (i=0, ii=tmp.length; i<ii; i++) {
					res.push({text: tmp[i].text, sep: tmp[i].sep});
				}
				res = this._unsplit_if_in_literal(res);
				break;
			} else {
				worklist = tmp;
			}
				
		}

		return res;

	});

	Tokenizer.addMember("_is_in_literal", function(left, right) {

		for (var i=0, ii=this._literalDelims.length; i<ii; i++) {
	
			var delim = this._literalDelims[i];

			var nleft = this._num_delim_occurrences(delim, left);
			if (nleft % 2 == 0) {
				continue;
			}

			var nright = this._num_delim_occurrences(delim, right);
			if (nright % 2 != 0) {
				return true;
			}

		}

		return false;

	});

    Tokenizer.addMember("_unsplit_if_in_literal", function(split_result) {

		if (this._literal == null) {
			return split_result;
		}

		var tmp = [];
		var item;
		var i, ii, j;

		for (i=0, ii=split_result.length; i<ii; i++) {

			item = split_result[i];
			
			if (item.sep == null) {
				tmp.push(item);
				continue;
			}

			if (i>0 && i<ii-1) {
				var left = "";
				for (j=0; j<i; j++) {
					left += split_result[j].text;
				}
				var right = "";
				for (j=i+1; j<ii; j++) {
					right += split_result[j].text;
				}
				if (!this._is_in_literal(left, right)) {
					tmp.push(item);
				} else {
					tmp.push({text: item.text, sep: null});
				}
			} else {
				tmp.push(item);
			}

		}

		var res = [];
		var buffer = "";

		for (i=0; i<ii; i++) {
			if (tmp[i].sep == null) {
				buffer += tmp[i].text;
			} else {
				if (buffer.length > 0) {
					res.push({text: buffer, sep: null});
					buffer = "";
				}
				res.push(tmp[i]);
			}
		}

		if (buffer.length > 0) {
			res.push({text: buffer, sep: null});
		}

		return res;

	});

	Tokenizer.addMember("_num_delim_occurrences", function(delim, text) {

		var res = 0;
		var prev = null;

		for (var i=0, ii=text.length; i<ii; i++) {
			var ch = text.charAt(i);
			if (ch == delim && (prev == null || prev != this._literalEscChar)) {
				res++;
			}
			prev = ch;
		}

		return res;

	});

	exports.Tokenizer = Tokenizer;

}({"OOPtimus": OOPtimus, "bovinus": bovinus}, bovinus));
