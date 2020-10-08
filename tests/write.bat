:: Writes a message to stdout
:: (which in the parent is piped to stdout.log)
echo message

:: Now I want to write a message to stderr
:: (which in the parent is piped to stderr.log)
echo message 1>&2