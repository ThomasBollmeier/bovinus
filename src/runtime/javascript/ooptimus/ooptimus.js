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

var OOPtimus = {

	/** Creates a new Class 
	 * -> SuperClass (optional): Constructor of super class
	 * -> initMethod: Initialization method (to be called by constructor)
	 * <- Constructor for new Class
	 */
	defClass : function(SuperClass, initMethod) {

		var superCls = null;
		var init = null;
		var clone = function(obj) {
			
			var Helper = function(){};
			Helper.prototype = obj;
			
			return new Helper();
			
		};

		switch (arguments.length) {
			case 1:
				superCls = null;
				init = arguments[0];
				break;
			case 2:
				superCls = arguments[0];
				init = arguments[1];
				break;
			default:
				throw "Number of arguments must be 1 or 2!";
		}

		var constructor = function() {
			
			init.apply(this, arguments);

		};
		
		if(superCls) {
			constructor.prototype = clone(superCls.prototype);
			constructor.prototype.constructor = constructor;
		}
		
		constructor.prototype.superClass = superCls;

		function superMeth(name) {
			
			// Get current level:
			var current = superMeth._stack[superMeth._stack.length - 1];
			var cls = current.prototype.superClass;
			
			// Find implementation:
			while (!cls.prototype.hasOwnProperty(name)) {
				cls = cls.prototype.superClass;
				if (!cls) {
					throw new Error("Method '" + name + "' not found");
				}
			}
			
			// Adjust level info:
			superMeth._stack.push(cls);
			
			// Call implementation:
			var args = [];
			for (var i=1; i<arguments.length; i+=1) {
				args.push(arguments[i]);
			}
			
			var res = cls.prototype[name].apply(this, args);
			
			// Return to previous level:
			superMeth._stack.pop();
			
			return res;
			
		}
		
		superMeth._stack = [constructor];
		
		constructor.prototype.superMethod = superMeth;
		constructor.prototype.superInit = function () {
			var args = ['constructor'];
			for (var i=0; i<arguments.length; i+=1) {
				args.push(arguments[i]);
			}
			return superMeth.apply(this, args);
		};
		
		constructor.prototype.proxy = function(method) {
			var that = this;
			var meth = typeof method == "string" ? that[method] : method;
			return function() {
				return meth.apply(that, arguments);	
			};
		};
		
		constructor.addMember = function(name, value) {
			constructor.prototype[name] = value;
			return constructor;	
		};

		constructor.addStaticMember = function(name, value) {
			constructor[name] = value;
			return constructor;	
		};
		
		constructor.realize = function (intf) {
			
			for (memberName in intf) {
				if (intf.hasOwnProperty(memberName)) {
					constructor.prototype[memberName] = intf[memberName];					
				}
			}
			
			return constructor;
		};
		
		return constructor;

	},
	
	/**
	 * Creates a decorator class
	 */
	defDecorator: function(wrapped, initMethod) {
		
		var _init = function() {
			
			this._wrapped = wrapped;
						
			if (initMethod) {
				initMethod.apply(this, arguments);
			}
			
		};
		
		var constructor = OOPtimus.defClass(_init);
		
		for (propName in wrapped) {
			
			(function(){
				
			var name = propName;
			
			if (typeof wrapped[name] == "function") { // define delegates
				
				constructor.addMember(name, function () {
					return wrapped[name].apply(wrapped, arguments);	
				});
				
			} else { // define setters and getters for non-function properties:
				
				var capitalized = name[0].toUpperCase() + name.slice(1);
				
				constructor.addMember("get" + capitalized, function () {
					return wrapped[name];
				});

				constructor.addMember("set" + capitalized, function (value) {
					wrapped[name] = value;
				});
				
			}
			
			}());
							
		}
				
		return constructor;
		
	}
	
};
