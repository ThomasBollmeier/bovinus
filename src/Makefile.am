SUBDIRS = runtime

dist_bin_SCRIPTS = parser_gen/bovinus

bovinusdir = $(pythondir)/bovinus

dist_bovinus_DATA = \
	runtime/python/grammar.py \
	runtime/python/input_buffer.py \
	runtime/python/instream.py \
	runtime/python/lexer.py \
	runtime/python/parser.py \
	runtime/python/token.py \
	runtime/python/tokenizer.py \
	runtime/python/util.py

nodist_bovinus_DATA = \
	runtime/python/__init__.py
	
parsergendir = $(bovinusdir)/parsergen

dist_parsergen_DATA = \
	parser_gen/__init__.py \
	parser_gen/ast.py \
	parser_gen/code_section_splitter.py \
	parser_gen/edit_sections.py \
	parser_gen/js_codegen.py \
	parser_gen/meta_grammar.py \
	parser_gen/meta_objects.py \
	parser_gen/meta_parser.py \
	parser_gen/output.py \
	parser_gen/php_codegen.py \
	parser_gen/python_codegen.py

EXTRA_DIST = \
	runtime/python/__init__.py.in

uninstall-local:
	-rm -rf $(bovinusdir)
