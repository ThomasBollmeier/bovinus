AC_INIT(bovinus, 1.6.6)

AM_INIT_AUTOMAKE([1.11])

AM_SILENT_RULES([yes])

AM_PATH_PYTHON([3.2])

AC_ARG_ENABLE(
[javascript],
[AS_HELP_STRING([--enable-javascript], [Build JavaScript runtime (default=no)])],
[
if test "x$enableval" = xyes; then
    build_js=yes
else
    build_js=no
fi
],
[build_js=no]
)
AM_CONDITIONAL([BUILD_JS], [test "x$build_js" = xyes])

AC_ARG_ENABLE(
[js-compression],
[AS_HELP_STRING([--enable-js-compression], [Create compressed JavaScript library (default=yes)])],
[
if test "x$enableval" = xyes; then
    compression=yes
else
    compression=no
fi
],
[compression=yes]
)
AM_CONDITIONAL([WITH_COMPRESSION], [test "x$compression" = xyes])

AC_ARG_ENABLE(
[php],
[AS_HELP_STRING([--enable-php], [Build PHP runtime (default=no)])],
[
if test "x$enableval" = xyes; then
    build_php=yes
else
    build_php=no
fi
],
[build_php=no]
)
AM_CONDITIONAL([BUILD_PHP], [test "x$build_php" = xyes])

AC_ARG_VAR([PHP_LIBDIR], [installation directory for BovinusPHP library]) 
if test -z "$PHP_LIBDIR"; then
    PHP_LIBDIR=${prefix}/lib/php
fi
AC_SUBST([PHP_LIBDIR])

# Checks for programs.
if test "x$build_js" = xyes; then
	if test "x$compression" = xyes; then
    	AC_CHECK_PROG([JAVA], [java], [java], [not found],)
	    if test "x$JAVA" != xjava; then
			AC_MSG_ERROR([No java interpreter could be found. \
Run configure with option --disable-compression to suppress this check])
    	fi
	fi
fi

AC_OUTPUT([
Makefile
data/Makefile
src/Makefile
src/runtime/Makefile
src/runtime/javascript/Makefile
src/runtime/php/Makefile
src/runtime/python/__init__.py
unittests/Makefile
unittests/php/Makefile
unittests/python/Makefile
])
