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
    
    var Context = OOPtimus.defClass(function (path, token) {
        
        this._path = path;
        this._token = token || null;
        
    });
    
    Context.addMember("setToken", function (token) {
       this._token = token; 
    });

    Context.addMember("getToken", function () {
       return this._token; 
    });
    
    Context.addMember("getEnvVar", function(name) {
        return this._path.getEnvVar(name);
    });
    
    Context.addMember("getCurKeyword", function() {
        
        if (!this._token) {
            return null;
        }
        
        var tokenTypes = this._token.getTypes();
        for (var idx in tokenTypes) {
            if (tokenTypes[idx] instanceof bovinus.Keyword) {
                return tokenTypes[idx];
            }
        }
        
        return null;
        
    });

    exports.bovinus.Context = Context;
    
} ({
    "OOPtimus" : OOPtimus,
    "bovinus" : bovinus
}, {
    "bovinus" : bovinus
}) );