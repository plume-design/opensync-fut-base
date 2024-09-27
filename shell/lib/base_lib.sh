#!/bin/sh
#
# Base library of shared functions with minimal prerequisites:
#   [
#   basename
#   date
#   echo
#   printf
#
echo "${FUT_TOPDIR}/shell/lib/base_lib.sh sourced"

###############################################################################
# DESCRIPTION:
#   Function is used to log errors or failures and exit with a non-zero code.
#
#   Note that exit is used and not return, which prevents calling functions
#   from doing their own error handling.
# INPUT PARAMETER(S):
#   $1  Message to be logged to stdout (string, optional)
#   Supported flags:
#       -arg: Invalid or missing argument
#       -ds:  Error during device setup
#       -ec:  Define custom exit code
#       -fc:  Error during function call
#       -l:   Location of error instead of this file
#       -ofm: Missing shell override file
#       -s:   Propagate skip condition to framework
#       -tc:  Testcase failure
# USAGE EXAMPLE(S):
#   raise <message> -s
#   raise <message> -l <raise location> -tc
#   raise <message> -ec 42 -ds
###############################################################################
raise()
{
    exception_type="BROKEN"
    exception_name="FutShellException"
    exception_location=$(basename "$0")
    exception_msg=${1:-"Unknown error"}
    shift 1
    exit_code=1

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -arg)
                exception_name="InvalidOrMissingArgument"
                ;;
            -ds)
                exception_name="DeviceSetup"
                exception_type="FAIL"
                ;;
            -ec)
                exit_code=${1}
                shift
                ;;
            -fc)
                exception_name="FunctionCall"
                ;;
            -l)
                exception_location=${1}
                shift
                ;;
            -ofm)
                exception_name="OverrideFileMissing"
                exception_type="FAIL"
                exception_msg="Missing *_OVERRIDE_FILE=${exception_msg} file. Check *_OVERRIDE_FILE and file existence"
                ;;
            -s)
                exit_code=3
                exception_type="SKIP"
                ;;
            -tc)
                exception_name="TestFailure"
                exception_type="FAIL"
                ;;
        esac
    done

    echo "$(date +%T) [${exception_type}] [${exception_name}] ${exception_location} - ${exception_msg}"
    exit ${exit_code}
}

###############################################################################
# DESCRIPTION:
#   Function is used to mark test as passed.
# INPUT PARAMETER(S):
#   $1  pass message (string, optional)
# EXITS:
#   0   Always.
# USAGE EXAMPLE(S):
#   pass
###############################################################################
pass()
{
    echo
    log ${*:-TEST PASSED}
    exit 0
}

###############################################################################
# DESCRIPTION:
#   Function is used to print titles decorated by separate rows of asterisks.
# INPUT PARAMETER(S):
#   $1  message (string, required)
#   $2  single decorator character (string, optional, default="*")
# USAGE EXAMPLE(S):
#   log_title <log title>
###############################################################################
log_title()
{
    c=${2:-"*"}
    v=$(printf "%0.s$c" $(seq 1 $((${#1}+2))))
    echo -ne "${v}\n ${1} \n${v}\n"
}

###############################################################################
# DESCRIPTION:
#   Function is used to log messages to stdout, prefixed with a time mark.
#   Supported flags:
#       -deb    mark log message as debug
#       -err    mark log message as error
# INPUT PARAMETER(S):
#   $1  log type, setting debug, warning or error log type (string, optional)
# RETURNS:
#   0   When logging regular or -deb messages.
#   1   When logging -err messages.
# USAGE EXAMPLE(S):
#   log <log message>
#   log -deb <log message>
#   log -err <log message>
###############################################################################
log()
{
    return_val=0
    case "$1" in
        -deb)
            msg_type="[DEBUG]"
            shift
            ;;
        -err)
            msg_type="[ERROR]"
            return_val=1
            shift
            ;;
        *)
            msg_type="[SHELL]"
            ;;
    esac
    echo -e "$(date +%T) $msg_type $*"
    return ${return_val}
}
