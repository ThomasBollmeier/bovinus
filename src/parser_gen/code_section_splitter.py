#! /usr/bin/env python3
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

class CodeSectionSplitter(object):
	"""
	Splits code sections from grammar file
	"""
	def __init__(self):
		
		self._regex_code_begin = re.compile(r'\s*%\s+([a-z_]([a-zA-Z0-9_])*)\s+\{')
		self._regex_code_end = re.compile(r'\s*%\s+\}')

	def split_grammar_file(self, grammar_file):
		"""
		Split grammar_file into pure grammar and embedded code sections
		in : <- grammar_file
		out: -> (grammar_string, code_sections)
		"""

		grammar_string = ""
		code_sections = {}
		
		f = open(grammar_file, "r")
		grammar_lines = [line.rstrip() for line in f.readlines()]
		f.close()

		current_section = False
		code_lines = []

		for line in grammar_lines:
			if not current_section:
				match = self._regex_code_begin.match(line)
				if not match:
					grammar_string += line + "\n"
				else:
					current_section = match.group(1)
					code_lines = []
			else:
				match = self._regex_code_end.match(line)
				if not match:
					code_lines.append(line)
				else:
					code_sections[current_section + '-transform'] = self._left_align(code_lines)
					current_section = ""
					code_lines = []

		return grammar_string, code_sections

	def _left_align(self, code_lines):

		res = []

		num_tabs_min = -1

		for line in code_lines:
			num_tabs = 0
			for ch in line:
				if ch == '\t':
					num_tabs += 1
				else:
					break
			if num_tabs < num_tabs_min or num_tabs_min == -1:
				num_tabs_min = num_tabs

		for line in code_lines:
			res.append(line[num_tabs_min:])

		return res