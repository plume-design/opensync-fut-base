#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "${fut_topdir}"/lib/unit_lib.sh

usage() {
    cat << usage_string
tools/client/fsm/make_curl_agent_req.sh [-h] arguments
Description:
    - Script makes curl request to url with specified user_agent
Arguments:
    -h  show this help message
    \$1 (namespace_enter_cmd) : Command to enter interface namespace : (string)(required)
    \$2 (user_agent)          : User agent to pass with curl request : (string)(required)
    \$3 (url)                 : URL to make curl request             : (string)(required)
Script usage example:
    ./tools/client/fsm/make_curl_agent_req.sh "custom_user_agent_name" "www.google.com"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/client/fsm/make_curl_agent_req.sh" -arg
namespace_enter_cmd=$1
user_agent=$2
url=$3

${namespace_enter_cmd} -c "curl -S -s --output /dev/null -A '${user_agent}' '${url}'" || $(exit 1)
if [[ "$?" != 0 ]]; then
    raise "Failed to make curl request to ${url} with user_agent ${user_agent}" -l "tools/client/fsm/make_curl_agent_req.sh"
else
    log "tools/client/fsm/make_curl_agent_req.sh: curl request made to ${url} with user_agent ${user_agent}"
fi
