if BUILD_JS

BOVINUS_JS_FILES = \
	bovinus/ast.js \
	bovinus/bovinus.js \
	bovinus/context.js \
	bovinus/grammar.js \
	bovinus/input_buffer.js \
	bovinus/instream.js \
	bovinus/lexer.js \
	bovinus/parser.js \
	bovinus/path.js \
	bovinus/token.js \
	bovinus/tokenizer.js \
	bovinus/util.js \
	ooptimus/ooptimus.js

if WITH_COMPRESSION

BUILD_TARGET = bovinus-runtime-@PACKAGE_VERSION@.min.js
BUILD_OPTS = -c

else

BUILD_TARGET = bovinus-runtime-@PACKAGE_VERSION@.js
BUILD_OPTS =

endif

jsdir = $(libdir)/js

nodist_js_DATA = \
$(BUILD_TARGET)

$(BUILD_TARGET): build-scripts/create_bovinus.sh $(BOVINUS_JS_FILES)
	$< $(BUILD_OPTS) -o $(BUILD_TARGET)
    	
clean-local:
	rm -f $(BUILD_TARGET)

endif

EXTRA_DIST = \
	bovinus/ast.js \
	bovinus/bovinus.js \
	bovinus/context.js \
	bovinus/grammar.js \
	bovinus/input_buffer.js \
	bovinus/instream.js \
	bovinus/lexer.js \
	bovinus/parser.js \
	bovinus/path.js \
	bovinus/token.js \
	bovinus/tokenizer.js \
	bovinus/util.js \
	ooptimus/ooptimus.js \
	build-scripts/create_bovinus.sh \
	build-scripts/license_comment.txt \
	external-tools/yuicompressor-2.4.7.jar

