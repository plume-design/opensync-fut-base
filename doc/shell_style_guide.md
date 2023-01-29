# FUT Shell Style Guide

## Introduction

This document is intended to define the coding style and the rules that need to
be applied to shell test scripts used by the FUT. Scripts written for the FUT
are part of libraries and testcases, and contain command sequences executed on
devices that are part of OSRT.

Following a style or rules helps programmers to read and understand the source
code better, and helps avoiding errors. Also the goal is to have
POSIX-compliant scripts so that the scripts are as portable as possible.

Style and rules are derived from other already established rules which can be
found online.

## General Rules

General rules are the rules that are not specific to the shell scripts only,
and can be applied to other programming languages, or in this case are derived
from other code styles. In our case from the OpenSync Coding Style in
particular. Links to the online resources can be found at the bottom of this
document in the Links and References sections. It is highly advisable for all
testcase writers to check this section.

## Indentations and Spacing

### Avoiding tabs

No tabs are allowed. Use spaces instead.
As a good practice, configure your editor to use spaces instead of tabs.

```bash
if [   ]; then
    some_function    # OK. Indented correctly, 4 spaces.
fi

if [   ]; then
  some_function      # Not OK. Not indented correctly, only 2 spaces.
fi
```

Indent size is 4 spaces.
Configure your editor to use 4 spaces instead of tabs.

### Vertical Spacing

Use blank lines between blocks of code performing one thought or action to
improve readability.

### Maximum line length

Maximum line length is allowed is 120 characters, although 80 is preferable.

**Note:**\
Some lines used for logging can exceed the 120 characters line length rule as a
consequence of rather lengthy function names. This can hardly be avoided, but
is advisable nonetheless.

### Control Sentences

Put `; do` and `; then` on the same line as `while`, `for` and `if`.\
Use one space between `;` and `then` control keywords.

Loops in "shell" are a bit different, but follow the same principles as with
braces when declaring functions.

That is: `; then` and `; do` should be on the same line as `if`, `for`,
`while`.

Examples:

```bash
if [   ]; then    # OK
    ...
fi

if [[   ]];       # Not OK (besides, the ';' is not needed here)
then
    ...
fi


if [[   ]]        # Not OK
then
    ...
fi
```

### The `if...then...else` Statement

`else` should be in its own line. Closing statement `fi` should be in its own
line, vertically aligned with the opening statement.

```bash
if [   ]; then    # OK
    ...
else
    ...
fi
```

Use single square brackets for conditions.

```bash
if [   ]; then      # Preferred
    ...
```

```bash
if [[   ]]; then    # Not preferred
    ...
```

## Comparisons

### Comparing Strings

Use quotes rather than filler characters where possible. Use tests for
empty/non-empty strings or empty strings rather than filler characters.

```bash
# Do this:
if [ "${my_var}" == "some_string" ]; then
    do_something
fi
```

```bash
# -z (string length is zero) and -n (string length is not zero) are
# preferred over testing for an empty string
if [ -z "${my_var}" ]; then
    do_something
fi

# This is OK (ensure quotes on the empty side), but not preferred:
if [ "${my_var}" == "" ]; then
    do_something
fi

# Not this:
if [ ${my_var}X == some_stringX ]; then
    do_something
fi
```

### Comparing Booleans

It is preferred to define booleans as strings to make code more readable.

```bash
failed="true"

if [ "$failed" == "true" ] then
    echo "Something failed";
fi
```

### Comparing Numbers

Integers are best compared with these operators:

```bash
-eq  # Equal
-ne  # Not equal
-lt  # Less than
-le  # Less than or equal
-gt  # Greater than
-ge  # Greater than or equal
```

```bash
if [ "$a" -eq "$b" ]; then
    echo "Numbers are equal"
fi
```

### The `case` Statement

Use `case` statement instead of multiple `if-elif` statements.

Follow the rules:

- Indent case alternatives by 4 spaces.
- A one-line alternative needs a space after the close parenthesis of the
  pattern and before the `;;`.
- Long or multi-command alternatives should be split over multiple lines with
  the pattern, actions, and `;;` on separate lines.
- Add the default option `*)` to catch any unsupported options.

Matching expressions are indented one level from the `case` and `esac`.

Multiline actions are indented for additional level. In general, there is no
need to quote the match expressions. Pattern expressions should not be preceded
by an open parenthesis.

Avoid the `;&` and `;;&` notations.

```bash
case "${option}" in
    a) ...
       ...
       ;;
    b) ...
       ...
       ;;
    *) error "Unexpected option '${option}'"
       ;;
esac
```

### The `for` Loop

The `; do` should be on the same line as `for`.

```bash
for count in $(seq 1 3); do
    ...
done
```

## Naming

Everything must be named in English. No other languages are allowed.

All names must only consist of lowercase letters and numbers if needed.

Use underscore (`_`) to separate words.

Do not use hyphen character (`-`).

### Naming the Files

All shell testcase scripts names must end with `.sh`

All library file names should end with `.sh`.

No uppercase letters are allowed to be used in file names. All names must only
consist of lowercase letters and numbers if needed.

Word boundaries is the underscore character (`_`) and must be used to separate
words in names.

Do not use hyphen character (`-`).

For each test suite, start the file name with an indicator to which test suite
the test script or testcase script belongs. Examples are: `brv_`, `dm_`,
`cm2_`, `nm2_`, `onbrd_`, etc.

Example:

```bash
onbrd_verify_number_of_params.sh   # OK

onbrdverifynumberofparams.sh       # Not OK
onbrdVerifyNumberOfParams.sh       # Not OK
OnbrdVerifyNumberOfParams.sh       # Not OK
```

### Naming the Functions

Function names consist of lower case letters.

No uppercase letters are allowed to be used in file names.

All names must only consist of lowercase letters and numbers if needed.

Word boundaries is the underscore character (`_`) and must be used to separate
words in names.

Do not use hyphen character (`-`).

It is advisable for function names to start with a verb describing what the
functions does.

Continue with underscore and a subject describing the object on which the
action is performed.

```bash
some_function()    # OK
get_channel()      # OK
set_channel()      # OK

somefunction()     # Not OK
someFunction()     # Not OK
SomeFunction()     # Not OK
```

If a function uses a system tool to perform an action, the name of this tool
can be a part of the function name.

```bash
block_traffic_iptables()    # OK
```

### Naming the Variables

To avoid shadowing or clobbering the system variables, follow these rules:

- Names of variables only consist of lower case letters. Similar to naming the
  files.
- Word boundaries are marked using the underscore character (`_`).
- For local variables, short names are allowed.
- For variables used with broader scope, use longer names to improve
  description what these variables are used for, or use a specific prefix.

```bash
count      # OK

Count      # Not OK
COUNT()    # Not OK
```

### Naming Constants and Environment Variables

Constants are to be named with all capital letters.

Word boundaries are marked using the underscore characters.

Constants and anything exported to the environment should be capitalized.

```bash
FUT_TOPDIR       # OK

Fut_Top_Dir      # Not OK
fut_top_dir()    # Not OK
```

## Comments

Everything must be commented in English. No other languages are allowed.

Comment tricky, non-obvious, interesting, or important parts of your code.

Do not comment everything. If there is a complex algorithm or if you are doing
something out of the ordinary, put a short comment in.

Examples:

Not a necessary comment, function name provides the same info:

```bash
# Perform a firmware test
test_firmware
```

Comment that is too long:

```bash
# Perform firmware test with a really long description about why and how this is done and what the consequences will be, etc.
test_firmware
```

Nicely done comment on a function that needs more info, reasoning the function
call:

```bash
# Needs to be tested before upgrade.
test_firmware
```

### File Header

Start each file with a "shebang" line:

```bash
    #!/bin/sh
```

or:

```bash
    #!/bin/bash
```

Every file must have a top-level comment including a brief overview of its
contents.

A copyright notice and author information are forbidden.

Example:

```bash
#!/bin/sh

# Perform a firmware test.
# Check if the firmware name field is populated and has a proper format.
```

## Function Header

Any function that is not both obvious and short must be commented.

Any function in a library must be commented regardless of length or complexity.

It should be possible for anyone to learn on how to use your program or use a
function in your library by reading the comments (or "help" if provided)
without actually reading the code.

All function comments should describe the intended function behavior by:

- Description of the function.
- Globals: list of global variables used and modified.
- Arguments: arguments of a function.
- Outputs: output to STDOUT or STDERR.
- Returns: return values other than the default exit status of the last
  executed command.

Examples:

```bash
###############################################################################
# DESCRIPTION:
#   Function does something. Describe.
# INPUT PARAMETER(S):
#   $1  option_1, describe, add (type, optional|mandatory, default value)
#   $2  option_2, describe, add (type, optional|mandatory, default value)
# RETURNS:
#   None.
# USAGE EXAMPLE(S):
#   do_something block 192.168.200.10
###############################################################################
do_something()
{
    option_1=$1
    option_2=$2
    ...
}
```

```bash
###############################################################################
# DESCRIPTION:
#   Get configuration directory.
# Globals:
#   SOMEDIR
# INPUT PARAMETER(S):
#   None
# RETURNS:
#   Echoes location to stdout
# USAGE EXAMPLE(S):
#   get_dir
###############################################################################
get_dir()
{
  echo "${SOMEDIR}"
}
```

```bash
###############################################################################
# DESCRIPTION:
#   Function deletes a file in a very sophisticated manner.
# INPUT PARAMETER(S):
#   $1  File to delete, a path (string, mandatory).
# RETURNS:
#   0 if file was deleted, non-zero on error.
# USAGE EXAMPLE(S):
#   delete_file file_x
###############################################################################
delete_file()
{
  rm "$1"
}
```

## Commenting the Code

For line comments, use `#` followed by a space and then the text describing
what the part of the code below does, and especially why this part of the code
is needed.

```bash
# This a good comment. OK.

#This is not as readable as above. Not OK.
```

Indent line comments at the same level as the code that is commented.

For end-of-line comments make two spaces before `#` to improve readability,
then apply the same rule as for the line comments.

Make sure that "end-of-line" comments do not expand too much to the right since
maximum line length rule should be followed.

### TODO Comments

Use `TODO:` word in the comments for the code that is temporary, or a
short-term solution, or good-enough, but not perfect.

TODOs should include a string `TODO:` in all caps, to be easily searchable if
needed.

A `TODO:` should be followed by the name, email address, or other identifier of
the person with the best context about the issue referenced by the TODO.

The main purpose here is to have a consistent TODOs that can be searched to
find out how to get more details upon a request and be easily deleted for the
release of the code. A TODO is not a commitment that the person referenced will
fix the issue. Thus, when you create a TODO, it is almost always your name that
is given.

```bash
# OK example:

# TODO: Rework this function. Currently is not doing what it should.
# The function performs only when the parameter fed into it is A or B, but not C.
# This should be addressed.
# john.doe@somewhere.com.

# Not OK example (todo written wrong, not enough info after todo):
# todo: Rework.
```

### The Good and the Bad Practices

**Use Local Variables**\
Declare function-specific variables with `local`. Declaration and assignment
should be on different lines.

Ensure that local variables are only seen inside a function and its children by
using `local` when declaring these variables. This avoids polluting the global
name space and inadvertently setting the variables that may have significance
outside the function.

**Flow control using `&&` and `||` is deprecated**\
Logical operators with `A && B || C` is allowed, although deprecated.\
It is advisable to use `if-then-else-fi` instead.

Example:

```bash
get_something &&
    echo "Success: got something" ||
    echo "FAIL: unable to get something"
```

## Logging

In FUT shell scripts logging is used extensively to enable understanding and
analysis of the testcase execution. Without logging, the testcase cannot be
declared passed or failed and it is hardly debugged.

When a testcase fails, logging can help testers to communicate the problem to
the developer. So, it is of great importance to follow certain rules regarding
the level and type of each log and its contents.

Log messages are used in testcase scripts and in the supporting library
functions.

Although the message itself cannot be strictly defined, there are still some
recommendations that need to be followed:

- In the testcase script logs, use keywords "Success" and "FAIL" to mark
  successful and unsuccessful actions.
- Always make an indicator where the message is logged using the location flag
  (`-l`) or add the file or function name in the log message.
- Use log flags (`-deb`, `-l`, `-tc`, etc.) to mark the type of log message, so
  the framework and Jenkins can sort the messages into groups.
- In the functions that are part of libraries, use the same rules as above, but
  try to avoid "Success" and "FAIL" keywords, not to confuse the tester that
  the testcase has executed successfully or failed.

Below is a typical use of logging. "Success" is logged for a successful action
and "FAIL" when the action fails:

```bash
log "abc/abc_verify_channel: Checking if channel is valid"  # Information log
check_channel_type "$channel" "$if_name" "$channel_type" &&
    log "abc/abc_verify_channel: check_channel_type - Channel $channel is valid - Success" ||  # Success log
    raise "FAIL: check_channel_type - Channel $channel is not valid" -l "abc/abc_verify_channel" -tc  # Something went wrong log
```

## The Shell Checker

Besides rules found on this page, it is very useful to check the testcase
scripts with an online available tool such as ShellCheck. The tool can also be
added to a development editor as a plugin if not already built-in.

## Example of an Empty Shell Script

Below is an example of how a typical testcase script is organized:

- The script should start with a shebang.
- A copyright notice and author information are forbidden.
- The script should have a short description of what it does. No more than one
  line is needed. Consider answering the "why" question, providing the
  reasoning for the script.
- The script should have a help or usage section.
- Within the help section, a detailed description of what script does and how
  it is used should be included.
- The help section should describe all input parameters needed for script to
  work.
- The script can have a trap section if needed.
- The script should have a parameter handler to process the arguments, loading
  all input parameters into the script variables. In case input parameters are
  incorrect, or if the number does not match the usage, the script should
  report usage or help notes.
- The script should have an initial log that reports the start of execution of
  the script.

```bash
#!/bin/sh

# Short description of the file...

# SOURCING section (example for DM suite testcase):
# FUT environment loading
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/dm_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

# TRAP section (if needed):
trap '
    ...
' EXIT SIGINT SIGTERM

# USAGE section:
usage="
$(basename "$0") [-h] \$1 \$2 \$3

Detailed description of the testcase...

where options are:
    -h  show this help message

where arguments are:
    arg_1_name=\$1 -- used as ... - (string)(required)
    arg_2_name=\$1 -- used as ... - (string)(required)
    arg_3_name=\$1 -- used as ... - (string)(required)

this script is dependent on following:
    - running ... manager
    - running ... manager

example of usage:
   ...
"

# OPTIONS section:
while getopts h option; do
    case "$option" in
        h)
            echo "$usage"
            exit 1
            ;;
    esac
done

# ARGUMENTS processing section:
NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires at least '${NARGS}' input argument(s)" -l "${tc_name}" -arg

arg_1=$1
arg_2=$2
arg_3=$3

# LOG TITLE:
log_title "$tc_name: Say Hello!"

# TESTCASE EXECUTION section:
...
...
pass

```

## Conclusion

Be consistent and use common sense. Consistency brings readability.

This means that it is better to add or edit your code in the same code style as
already present, even if the style does not conform to these standards.

But if styling needs to be changed, do it as a separate step. Do not mix
styling changes and changes to the contents of the code. The same would apply
for adding comments, usage notes, etc.

## Links and References

[https://www.shellcheck.net/](https://www.shellcheck.net/)
[http://ronaldbradford.com/blog/scripting-standards/](http://ronaldbradford.com/blog/scripting-standards/)
[https://google.github.io/styleguide/shellguide.html](https://google.github.io/styleguide/shellguide.html)
[http://queirozf.com/entries/posix-shell-tests-and-conditionals-examples-and-reference](http://queirozf.com/entries/posix-shell-tests-and-conditionals-examples-and-reference)
[https://engineering.vokal.io/Systems/sh.md.html](https://engineering.vokal.io/Systems/sh.md.html)
