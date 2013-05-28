<?php

/*
 * Copyright 2012-2013 Thomas Bollmeier <tbollmeier@web.de>
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

class Bovinus_AstNode {

    public function __construct($name, $text = '', $identifier = '') {

        $this->name = $name;
        $this->text = $text;
        $this->identifier = $identifier;
    }

    public function copy() {

        $res = new Bovinus_AstNode($this->name, $this->text, $this->identifier);
        foreach ($this->children as $child) {
            array_push($res->children, $child->copy());
        }

        return $res;
    }

    public function addChild($child) {

        array_push($this->children, $child);
        $child->parent = $this;
        
        if ($child->identifier != '') {
			$this->addChildToIndex($child);
		}
			        
    }

    public function removeChildren() {

        foreach ($this->children as $child) {
            $child->parent = null;
        }

        $this->children = array();
        $this->childrenIndex = array();
    }

    public function replaceChild($old, $new) {

        for ($i = 0; $i < count($this->children); $i++) {

            if ($this->children[$i] == $old) {
                $old->parent = null;
                if ($old->identifier != '') {
					$this->removeChildFromIndex($old);
				}
                $new->parent = $this;
                $this->children[$i] = $new;
                if ($new->identifier != '') {
					$this->addChildToIndex($new);
				}
                break;
            }
        }
    }

    public function setName($name) {

        $this->name = $name;
    }

    public function getName() {

        return $this->name;
    }

    public function getText() {

        return $this->text;
    }

    public function getParent() {

        return $this->parent;
    }

    public function getChildren() {

        return $this->children;
    }

    public function getChildrenByName($name) {

        $children = array();

        foreach ($this->children as $child) {
            if ($child->name == $name) {
                array_push($children, $child);
            }
        }

        return $children;
    }

    public function getChild($name) {

        foreach ($this->children as $child) {
            if ($child->name == $name) {
                return $child;
            }
        }

        return null;
    }

    public function setId($identifier) {
		
		if ($this->identifier == $identifier) return;
		
		if ($this->parent != null) {
			$this->parent->removeChildFromIndex($this);
		}

        $this->identifier = $identifier;

		if ($this->parent != null) {
			$this->parent->addChildToIndex($this);
		}

    }

    public function getId() {

        return $this->identifier;
    }

    public function getChildById($identifier) {
		
		if (array_key_exists($identifier, $this->childrenIndex)) {
			$children = $this->childrenIndex[$identifier];
			return $children[0];
		} else {
			return null;
		}
	
    }

    public function getChildrenById($identifier) {

		if (array_key_exists($identifier, $this->childrenIndex)) {
			return $this->childrenIndex[$identifier];
		} else {
			return array();
		}

    }
    
    public function getChildAccess() {
		
		return new Bovinus_AstNodeChildAccess($this);
		
	}

    public function hasChildren() {

        return (count($this->children) > 0);
    }

    public function toXml($indent = 0) {

        $res = "";

        $line = "<" . $this->name;

        if ($this->identifier != "") {
            $line .= ' id="' . $this->identifier . '"';
        }

        if (count($this->children) > 0) {
            if ($this->text == "") {
                $line .= ">";
            } else {
                $line .= ">" . $this->text;
            }
        } else {
            if ($this->text == "") {
                $line .= " />";
            } else {
                $line .= ">" . $this->text . "</" . $this->name . ">";
            }
        }

        $line = $this->indent($line, $indent);
        $res = $line . "\n";

        if (count($this->children) > 0) {

            foreach ($this->children as $child) {
                $res .= $child->toXml($indent + 1);
            }

            $line = "</" . $this->name . ">";
            $line = $this->indent($line, $indent);
            $res .= $line . "\n";
        }

        return $res;
    }
    
    public function toJSON() {
		
		$res = '{';
		$res .= ' "name" : "' . $this->name . '"';
		$res .= ', "text" : "' . $this->text . '"';
		$res .= ', "identifier" : "' . $this->identifier . '"';
		$res .= ', "children" : [';
		
		$tmp = '';
		foreach ($this->children as $child) {
			if (strlen($tmp) != 0) {
				$tmp .= ', ';
			}
			$tmp .= $child->toJSON();
		}
		if (strlen($tmp) > 0) {
			$res .= ' ' . $tmp;
		}
		
		$res .= '] }';
		
		return $res;
		
	}
	
	private function indent($line, $level) {
		
		$res = $line;
		
		for ($i=0; $i<$level; $i++) {
			$res = "\t" . $res;
		}
		
		return $res;
		
	}
	
	private function addChildToIndex($child) {
	
		if ($child->identifier == '') return;
		
		if (!array_key_exists($child->identifier, $this->childrenIndex)) {
			$this->childrenIndex[$child->identifier] = array($child);
		} else {
			array_push($this->childrenIndex[$child->identifier], $child);
		}
		
	}
	
	private function removeChildFromIndex($child) {
	
		if ($child->identifier == '' || !array_key_exists($child->identifier, $this->childrenIndex)) {
			// Nothing to do
			return;
		}		
		
		$children = $this->childrenIndex[$child->identifier];
		$idx = 0;
		$changed = FALSE;
		foreach ($children as $c) {
			if ($c === $child) {
				unset($children[$idx]);
				$changed = TRUE;
			}
			$idx++;
		}
		
		if (!$changed) return;
		
		if (count($children) > 0) {
			$this->childrenIndex[$child->identifier] = array_values($children);
		} else {
			unset($this->childrenIndex[$child->identifier]);
		}
	
	}
    
    private $name;
    private $text;
    private $identifier;
    private $parent = null;
    private $children = array();
    private $childrenIndex = array();

}

class Bovinus_AstNodeChildAccess {
	
	public function __construct($astNode) {
	
		$this->astNode = $astNode;

	}

    public function __get($identifier) {
		
		if ($identifier != "astNode") {

			$children = $this->astNode->getChildrenById($identifier);

			if (count($children) == 1) {
				return $children[0];
			} else {
				return $children;
			}

		} else {

			return $this->astNode;

		}
		
	}
	
	private $astNode;
}

?>
