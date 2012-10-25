#!/bin/bash
# script to run unittests

grammar_file=godl.bovg
parser_file=godl_parser.php

# Create parser file:
rm -f $parser_file
bovinus --target=php -o $parser_file $grammar_file

# Run
phpunit tokenizertest.php
phpunit lexertest.php
phpunit parsertest.php

# Cleanup
rm $parser_file
