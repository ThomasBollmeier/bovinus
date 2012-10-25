#! coding=UTF-8

# Copyright 2012 Thomas Bollmeier <tbollmeier@web.de>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

class EditableSections(object):
    """
    user editable code sections
    """

    SECTION_INITIALIZED_FROM_FILE = 1
    SECTION_SET_EXTERNALLY = 2
    
    def __init__(
        self,
        regex_begin_str,
        regex_end_str
        ):

        self._regex_begin = re.compile(regex_begin_str)
        self._regex_end = re.compile(regex_end_str)
        
        self._sections = {} # {(content, origin)}

    def init_from_file(self, file_path):
        
        self._sections = {} 
        
        try:
            input_file = open(file_path, "r")
        except IOError:
            return
        lines = input_file.readlines()
        input_file.close()
        
        in_user_section = False
        read_from_file = True
        
        for line in lines:
            
            line = line[:-1] # remove line break
            
            if not in_user_section:
                section_begin, section_name = self._check_for_section_begin(line)
                if section_begin:
                    in_user_section = True
                    content = []
            else:
                if not self._is_section_end(line):
                    content.append(line)
                else:
                    self._sections[section_name] = (content, self.SECTION_INITIALIZED_FROM_FILE)
                    in_user_section = False
                    section_name = ""

    def set_section(
        self,
        section_name,
        lines
        ):

        self._sections[section_name] = (lines, self.SECTION_SET_EXTERNALLY)

    def get_section(
        self,
        section_name,
        default_lines=[]
        ):

        res = []
        
        res.append(self._create_section_begin(section_name))

        try:
            res += self._sections[section_name][0]
        except KeyError:
            res += default_lines

        res.append(self._create_section_end(section_name))

        return res

    def is_section_set_externally(self, section_name):

        try:
            return self._sections[section_name][1] == self.SECTION_SET_EXTERNALLY
        except KeyError:
            return False

    def _create_section_begin(self, section_name):

        raise NotImplementedError

    def _create_section_end(self, section_name):

        raise NotImplementedError

    def _check_for_section_begin(self, line):

        match = self._regex_begin.match(line)
        if match:
            return True, match.group(1)
        else:
            return False, ""
        
    def _is_section_end(self, line):

        return bool(self._regex_end.match(line))
