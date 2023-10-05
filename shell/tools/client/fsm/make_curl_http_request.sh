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
tools/client/fsm/make_curl_http_request.sh [-h] arguments
Description:
    - Script makes curl request to url
Arguments:
    -h  show this help message
    \$1 (namespace_enter_cmd) : Command to enter interface namespace : (string)(required)
    \$2 (url)                 : URL to make curl request             : (string)(required)
Script usage example:
    ./tools/client/fsm/make_curl_http_request.sh "custom_user_agent_name" "www.google.com"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/client/fsm/make_curl_http_request.sh" -arg

namespace_enter_cmd=$1
url=$2

${namespace_enter_cmd} -c "curl --max-time 20 '${url}'"
if [[ "$?" != 0 ]]; then
    raise "Failed to make curl request to ${url}" -l "tools/client/fsm/make_curl_http_request.sh"
else
    log "tools/client/fsm/make_curl_http_request.sh: curl request made to ${url}"
fi
