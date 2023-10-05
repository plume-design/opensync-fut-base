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
#   Function is used to raise an exception, usually during test execution.
# INPUT PARAMETER(S):
#   The function has 5 parameters for the user to customize and 2 modes:
#   Parameters:
#       exception_msg: Message to be displayed in terminal
#       exception_location: Where did the error happen
#       exception_name: Error name to report to framework:
#                   "FunctionCall"
#                   "DeviceSetup"
#                   "OvsdbWait"
#                   "OvsdbException"
#                   "NativeFunction"
#                   "TestFailure"
#                   "InvalidOrMissingArgument"
#       exception_type: Type of error to report to framework: ERROR|BROKEN
#       exit_code: actual process exit code to return to calling function
#   Modes:
#       is_skip=true: propagate skip condition to framework (exit_code=3)
#       is_skip=false: an error occurred
# EXITS:
#   With exit code:
#       - 1, default
#       - 3, -s, skipped test
#       - custom, use -ec flag
# USAGE EXAMPLE(S):
#   raise <raise message> -l <raise location> -tc
#   raise <raise message> -l <raise location> -ds
###############################################################################
raise()
{
    exception_msg=${1:-"Unknown error"}
    shift 1
    exception_location=$(basename "$0")
    exception_name="CommonShellException"
    exception_type="BROKEN"
    is_skip=false
    exit_code=1

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            # Use for generic failures
            -f)
                exception_type="FAIL"
                ;;
            # Use to define custom exit code
            -ec)
                exit_code=${1}
                shift
                ;;
            # Use to propagate "skip" condition to framework
            -s)
                exit_code=3
                is_skip=true
                ;;
            # Customize location of error, instead of this library
            -l)
                exception_location=${1}
                shift
                ;;
            # Use when error occurred during function call
            -fc)
                exception_name="FunctionCall"
                ;;
            # Use when error occurred during device setup
            -ds)
                exception_name="DeviceSetup"
                exception_type="FAIL"
                ;;
            # Use when error occurred during ovsdb-wait
            -ow)
                exception_name="OvsdbWait"
                exception_type="FAIL"
                ;;
            # Use when error occurred due to ovsdb issue
            -oe)
                exception_name="OvsdbException"
                ;;
            # Use when error occurred due to native function issue
            -nf)
                exception_name="NativeFunction"
                exception_type="FAIL"
                ;;
            # Use for detection of down-ed / crashed ovsdb-server
            -osc)
                exception_name="OVSDBServerCrashed"
                exception_type="FAIL"
                ;;
            # Use for testcase failures
            -tc)
                exception_name="TestFailure"
                exception_type="FAIL"
                ;;
            # Use for testcase failures
            -ofm)
                exception_name="OverrideFileMissing"
                exception_type="FAIL"
                exception_msg="Missing *_OVERRIDE_FILE=${exception_msg} file. Check *_OVERRIDE_FILE and file existence"
                ;;
            # Use when error occurred due to invalid or missing argument
            -arg)
                exception_name="InvalidOrMissingArgument"
                ;;
        esac
    done

    echo "$(date +%T) [ERROR] ${exception_location} - ${exception_msg}"
    if [ "$is_skip" = 'false' ]; then
        echo "FutShellException|FES|${exception_type}|FES|${exception_name}|FES|${exception_msg} AT ${exception_location}"
    else
        echo "${exception_msg} AT ${exception_location}"
    fi
    exit "$exit_code"
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
    if [ $# -ge 1 ]; then
        echo -e "\n$(date +%T) [SHELL] $*"
    else
        echo -e "\n$(date +%T) [SHELL] TEST PASSED"
    fi
    exit 0
}

###############################################################################
# DESCRIPTION:
#   Function is used to log title.
# INPUT PARAMETER(S):
# RETURNS:
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
#   Function is used to log test event.
#   Echoes log message prefixed with time mark.
#   Supported flags:
#       -deb    mark log message as debug
#       -wrn    mark log message as warning
#       -err    mark log message as error
#   If called without flag, message is shell log.
# INPUT PARAMETER(S):
#   $1  log type, setting debug, warning or error log type (string, optional)
# RETURNS:
#   0   DEBUG or SHELL message logged.
#   1   ERROR message logged.
# USAGE EXAMPLE(S):
#   log <log message>
#   log -deb <log message>
#   log -wrn <log message>
#   log -err <log message>
###############################################################################
log()
{
    msg_type="[SHELL]"
    exit_code=0
    if [ "$1" = "-deb" ]; then
        msg_type="[DEBUG]"
        shift
    elif [ "$1" = "-wrn" ]; then
        msg_type="[WARNING]"
        shift
    elif [ "$1" = "-err" ]; then
        msg_type="[ERROR]"
        exit_code=1
        shift
    fi

    echo -e "$(date +%T) $msg_type $*"

    return $exit_code
}

contains_element()
{
    local match="$1"
    shift
    while [ -n "${1}" ]; do
        value="${1}"
        [ "${value}" == "${match}" ] && echo 0 && return 0
        shift
    done
    echo 1 && return 1
}

get_index_in_list()
{
    local index_for="$1"
    shift
    index=0
    values="$@"
    while [ -n "${1}" ]; do
        value="${1}"
        [ "${value}" == "${index_for}" ] && echo $index && return 0
        index=$((index + 1))
        shift
    done
    return 1
}

get_by_index_from_list()
{
    local index="$1"
    shift
    check_index=0
    values="$@"
    while [ -n "${1}" ]; do
        value="${1}"
        [ "${check_index}" == "${index}" ] && echo "$value" && return 0
        check_index=$((check_index+1))
        shift
    done
    return 1
}
