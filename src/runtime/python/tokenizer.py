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

class Tokenizer(object):

    def __init__(self):

        self._literal = None
        self._literalDelims = ['"', "'"]
        self._literalEscChar = '\\'
        self._separators = []

    def set_literal(self, literal):

        self._literal = literal
        self._literalDelims = literal.DELIMITERS
        self._literalEscChar = literal.ESCAPE_CHAR

    def add_separator(self, sep):

        self._separators.append(sep)

    def split_at_separators(self, text):

        worklist = [(text, None)]

        for sep in self._separators:

            tmp = []
            for text_, sep_ in worklist:
                if sep_:
                    tmp.append((text_, sep_))
                else:
                    tmp += self._split_at_sep(text_, sep)

            worklist = tmp

        return worklist

    def _split_at_sep(self, text, sep):

        regex = sep.getRegexIgnoreWS()

        sep_positions = []
        for m in regex.finditer(text):
            sep_positions.append((m.start(),m.end()))

        tmp = []
        current = 0
        for start, end in sep_positions:
            substr = text[current:start]
            if substr:
                tmp.append((substr, None)) # None --> not a separator
            tmp.append((text[start:end], sep))
            current = end

        substr = text[current:]
        if substr:
            tmp.append((substr, None))

        res = self._unsplit_if_in_literal(tmp)

        return res

    def _unsplit_if_in_literal(self, split_result):

        if not self._literal:
            return split_result

        tmp = []
        last_idx = len(split_result) - 1

        for idx, item in enumerate(split_result):

            substr, sep = item

            if sep is None:
                tmp.append((substr, sep))
                continue
            
            if idx > 0 and idx < last_idx:
                left = "".join([el[0] for el in split_result[:idx]])
                right = "".join([el[0] for el in split_result[idx+1:]])
                if not self._is_in_literal(left, right):
                    tmp.append((substr, sep))
                else:
                    tmp.append((substr, None))
            else:
                tmp.append((substr, sep))

        res = []
        buffer = ""
        for substr, sep in tmp:
            if sep is None:
                buffer += substr
            else:
                if buffer:
                    res.append((buffer, None))
                    buffer = ""
                res.append((substr, sep))
        if buffer:
            res.append((buffer, None))

        return res

    def _is_in_literal(self, left, right):

        for delim in self._literalDelims:
            nleft = self._num_delim_occurrences(delim, left)
            if nleft % 2 == 0:
                continue
            nright = self._num_delim_occurrences(delim, right)
            if nright % 2 != 0:
                return True

        return False

    def _num_delim_occurrences(self, delim, text):

        res = 0
        prev = ''
        for ch in text:
            if ch == delim and (not prev or prev != self._literalEscChar):
                res += 1
            prev = ch

        return res
