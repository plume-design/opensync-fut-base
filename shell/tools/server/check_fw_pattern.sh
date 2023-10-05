#!/bin/bash

current_dir=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
export FUT_TOPDIR="$(realpath "$current_dir"/../../..)"

# FUT environment loading
source "${FUT_TOPDIR}/shell/config/default_shell.sh"
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"

usage()
{
cat << usage_string
tools/server/check_fw_pattern.sh [-h] [-file FILENAME] [-fw FW_STRING]
Description:
    Check fw version pattern validity
    The script is a development tool that is intended for execution on RPI
    server or local PC within the framework directory structure, not on DUT!
Arguments:
    -h              : show this help message
    -file FILENAME  : verify FW version string(s) from FILENAME
    -fw FW_STRING   : verify FW version string FW_STRING
Testcase procedure: execute on RPI server or local PC, not DUT
    - Export environment variable FUT_TOPDIR:
        export FUT_TOPDIR=~/git/device/core/src/fut
    - Run tool
Script usage example:
    ./tools/server/check_fw_pattern.sh -file files/fw_patterns
    ./tools/server/check_fw_pattern.sh -fw 2.4.3-72-g65b961c-dev-debug
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/server/check_fw_pattern.sh" -arg

in_file=""
fw_string=""

while [ -n "$1" ]; do
    option=$1
    shift
    case "$option" in
        -file)
            in_file="${1}"
            shift
            ;;
        -fw)
            fw_string="${1}"
            shift
            ;;
        *)
            raise "Unknown argument" -l "tools/server/check_fw_pattern.sh" -arg
            ;;
    esac
done

# TEST EXECUTION:
if [ -n "$in_file"  ]; then
    log "tools/server/check_fw_pattern.sh: Verifying FW version string(s) from file '${in_file}'."
    while IFS= read line
    do
        # Discard empty lines and comments
        echo "$line" | grep -q -e "^$" -e "^#"
        if [ "$?" = "0" ]; then
            echo "${line}"
            continue
        fi
        # Use subprocess to not exit upon error
        rv=$(check_fw_pattern "${line}")
        rc=$?
        [ $rc -eq 0 ] &&
            log -deb "tools/server/check_fw_pattern.sh: FW version string ${line} is valid" ||
            log -err "tools/server/check_fw_pattern.sh: FW version string ${line} is not valid\n${rv}"
    done <"$in_file"
elif [ -n "$fw_string" ]; then
    log "tools/server/check_fw_pattern.sh: Verifying FW version string '${fw_string}'."
    rv=$(check_fw_pattern "${fw_string}")
    [ $? -eq 0 ] &&
        log -deb "tools/server/check_fw_pattern.sh: FW version string ${fw_string} is valid" ||
        raise "FW version string ${fw_string} is not valid" -l "tools/server/check_fw_pattern.sh" -tc
else
    log -err "tools/server/check_fw_pattern.sh: Something went wrong..."
    usage && exit 1
fi
