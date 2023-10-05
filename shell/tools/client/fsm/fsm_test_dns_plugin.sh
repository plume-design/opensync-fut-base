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
tools/client/fsm/fsm_test_dns_plugin.sh [-h] arguments
Description:
    - Script resolves url using 'dig' and it checks url final destination
Arguments:
    -h  show this help message
    \$1 (namespace_enter_cmd) : Command to enter interface namespace : (string)(required)
    \$2 (url)                 : URL to dig                           : (string)(required)
    \$3 (url_resolve)         : Address of resolved URL              : (string)(required)
Script usage example:
    ./tools/client/fsm/fsm_test_dns_plugin.sh "ip netns exec nswifi1 bash" "google.com" "1.2.3.4"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/client/fsm/fsm_test_dns_plugin.sh" -arg

namespace_enter_cmd=$1
url=$2
url_resolve=$3

${namespace_enter_cmd} -c "dig +short ${url}" | grep -q "${url_resolve}" || $(exit 1)
if [[ "$?" != 0 ]];then
    ${namespace_enter_cmd} -c "dig ${url}"
    raise "${url} not resolved to ${url_resolve}" -l "tools/client/fsm/fsm_test_dns_plugin.sh"
else
    log "tools/client/fsm/fsm_test_dns_plugin.sh: ${url} resolved to ${url_resolve}"
fi
