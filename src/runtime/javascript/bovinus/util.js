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

( function(exports) {

    exports.inArray = function(item, items, compareFunc) {

        var i;
        var cmp = compareFunc ||
        function(a, b) {
            return a === b;
        };

        for( i = 0; i < items.length; i += 1) {
            if(cmp(item, items[i])) {
                return true;
            }
        }

        return false;

    };
        
    exports.indexOf = function(item, items, compareFunc) {

        var i;
        var cmp = compareFunc ||
        function(a, b) {
            return a === b;
        };

        for( i = 0; i < items.length; i += 1) {
            if(cmp(item, items[i])) {
                return i;
            }
        }

        return -1;
        
    };
	
}(bovinus.util));
