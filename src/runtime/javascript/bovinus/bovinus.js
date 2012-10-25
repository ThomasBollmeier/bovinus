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

bovinus = { util: {} };

bovinus.importNames = function(target) {
    
    for (var i=1; i<arguments.length; i++) {
	
	var name = arguments[i];
	target[name] = bovinus[name];
	
    }
        
};

bovinus.importAll = function(target) {
    
    for (var name in bovinus) {

	if (bovinus.hasOwnProperty(name)) {
	    target[name] = bovinus[name];
	}	

    }
    
};

bovinus.declareNames = function() {
    
    var res = "";
    
    for (var i=0; i<arguments.length; i++) {
	
	var name = arguments[i];
	var cmd = "var " + name + " = bovinus[\"" + name + "\"];";
	
	if (res !== "") {
	    res += "\n";
	}
	res += cmd;
	
    }
    
    return res;
        
};

bovinus.declareAll = function() {
    
    var res = "";
    
    for (var name in bovinus) {

	if (bovinus.hasOwnProperty(name)) {

	    var cmd = "var " + name + " = bovinus[\"" + name + "\"];";

            if (res !== "") {
	        res += "\n";
	    }
	    res += cmd;
	    
	}	

    }
    
    return res;
    
};