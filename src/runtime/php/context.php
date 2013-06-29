<?php

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

require_once 'Bovinus/token.php';

class Bovinus_Context {

    public function __construct($path, $token = null) {

        $this->path = $path;
        $this->token = $token;
    }

    public function setToken($token) {

        $this->token = $token;
    }

    public function getToken() {

        return $this->token;
    }

    public function getEnvVar($name) {

        return $this->path->getEnvVar($name);
    }

    public function getCurKeyword() {

        if ($this->token == null) {
            return null;
        }

        foreach ($this->token->getTypes() as $tokenType) {
            if ($tokenType instanceof Bovinus_Keyword) {
                return $tokenType;
            }
        }

        return null;
    }

    private $path;
    private $token;

}
