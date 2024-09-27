#!/bin/sh

# Include basic environment config
export FUT_UNIT_LIB_SRC=true
[ "${FUT_BASE_LIB_SRC}" != true ] && source "${FUT_TOPDIR}/shell/lib/base_lib.sh"
echo "${FUT_TOPDIR}/shell/lib/unit_lib.sh sourced"

###############################################################################
# DESCRIPTION:
#   Function adds port with provided name the network bridge.
#   Procedure:
#       - check if bridge exists
#       - check if port with provided name already exists on bridge
#       - if port does not exist add port
#   Raises an exception if bridge does not exist, port already in bridge ...
#   Raises an exception if
#       - bridge does not exist,
#       - port cannot be added.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   add_port_to_bridge br-home patch-h2w
###############################################################################
add_port_to_bridge()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:add_port_to_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1
    port_name=$2

    if linux_native_bridge_enabled; then
        nb_add_port_to_bridge "${bridge}" "${port_name}"
    else
        ovs_add_port_to_bridge "${bridge}" "${port_name}"
    fi
}

###############################################################################
# DESCRIPTION:
#   Function creates tap interface on bridge with selected Openflow port.
#   Raises an exception if not in the path.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Interface name (string, required)
#   $3  Open flow port (string, required)
# RETURNS:
#   0   On success.
# USAGE EXAMPLE(S):
#   add_tap_interface br-home br-home.tdns 3001
#   add_tap_interface br-home br-home.tx 401
###############################################################################
add_tap_interface()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:add_tap_interface requires ${NARGS} input arguments, $# given" -arg
    bridge=$1
    iface=$2
    ofport=$3

    log -deb "unit_lib:add_tap_interface - Generating tap interface '${iface}' on bridge '${bridge}'"

    add_port_to_bridge "${bridge}" "${iface}"
    set_interface_option "${iface}"  "type" "internal"
    set_interface_option "${iface}"  "ofport_request" "${ofport}"

}

###############################################################################
# DESCRIPTION:
#   Function checks if beacon interval is applied at OS - LEVEL2.
#   Function raises an exception if beacon interval is not applied.
# STUB:
#   This function is a stub. It always raises an exception and needs
#   a function with the same name and usage in platform or device overrides.
# INPUT PARAMETER(S):
#   $1  Beacon interval (int, required)
#   $2  VIF interface name (string, required)
# RETURNS:
#   0   Beacon interval on system matches expected value
# USAGE EXAMPLE(S):
#   check_beacon_interval_at_os_level 600 home-ap-U50
###############################################################################
check_beacon_interval_at_os_level()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_beacon_interval_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    bcn_int=$1
    vif_if_name=$2

    log -deb "unit_lib:check_beacon_interval_at_os_level - Checking Beacon interval for interface '$vif_if_name' at OS - LEVEL2"
    # Provide override in platform specific file
    raise "This is a stub function. Override implementation needed." -l "unit_lib:check_beacon_interval_at_os_level" -fc
}

###############################################################################
# DESCRIPTION:
#   Function compares CN (Common Name) of the certificate to
#   several parameters:
#       - device model string,
#       - device id,
#       - WAN eth port MAC address.
#   NOTE: CN verification is optional, this function just echoes these
#         parameters. If the validation should be required, please overload the
#         function in the device shell library overload file.
# INPUT PARAMETER(S):
#   $1  Common Name stored in the certificate (string, required)
#   $2  Device model string (string, optional)
#   $3  Device id (string, optional)
#   $4  MAC address of device WAN eth port (string, optional)
# RETURNS:
#   0   Always.
# USAGE EXAMPLE(S):
#   check_certificate_cn 1A2B3C4D5E6F 1A2B3C4D5E6F PP203X 00904C324057
###############################################################################
check_certificate_cn()
{
    local NARGS=1
    [ $# -lt ${NARGS} ] &&
        raise "unit_lib:check_certificate_cn requires at least ${NARGS} input argument(s), $# given" -arg

    local comm_name=${1}
    echo "Common Name of the certificate: $comm_name"
    local device_model=${2}
    echo "Device model: $device_model"
    local device_id=${3}
    echo "Device ID: $device_id"
    local wan_eth_mac=${4}
    echo "WAN eth port MAC address: $wan_eth_mac"

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if channel is applied at OS - LEVEL2.
#   Raises exception if actual channel does not match expected value
# INPUT PARAMETER(S):
#   $1  Channel (int, required)
#   $2  VIF interface name (string, required)
# RETURNS:
#   0  if actual channel matches expected value
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_channel_at_os_level 1 home-ap-24
###############################################################################
check_channel_at_os_level()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_channel_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    # shellcheck disable=SC2034
    channel=$1
    # shellcheck disable=SC2034
    vif_if_name=$2

    log -deb "unit_lib:check_channel_at_os_level - Checking channel '$channel' at OS - LEVEL2"
    wait_for_function_output $channel "get_channel_from_os $vif_if_name" &&
        log -deb "unit_lib:check_channel_at_os_level - channel '$channel' is set at OS - LEVEL2 - Success" ||
        raise "channel '$channel' is not set at OS - LEVEL2" -l "unit_lib:check_channel_at_os_level" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if default gateway route exists for LTE.
# INPUT PARAMETER(S):
#   $1  LTE Interface name (string, required)
#   $2  metric value (int, required)
#   $3  route tool path (string, required)
# RETURNS:
#   0   Default route exists.
#   1   Default route does not exist.
# USAGE EXAMPLE(S):
#   check_default_route_gw wwan0 100 /sbin/route
###############################################################################
check_default_lte_route_gw()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_default_lte_route_gw requires ${NARGS} input argument(s), $# given" -arg
    if_name=${1}
    metric=${2}
    tool_path=${3}

    # Show route
    ${tool_path} -n

    default_gw=$(${tool_path} -n | grep -i $if_name | grep -i 'UG' | awk '{print $5}' | grep -i $metric;)
    if [ -z "$default_gw" ]; then
        return 1
    else
        log -deb "unit_lib:check_default_lte_route_gw - Default GW for $if_name set to $default_gw"
        return 0
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if default gateway route exists.
#   Function uses route tool. Must be installed on device.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   Default route exists.
#   1   Default route does not exist.
# USAGE EXAMPLE(S):
#   check_default_route_gw
###############################################################################
check_default_route_gw()
{
    default_gw=$(route -n | tr -s ' ' | grep -i UG | awk '{printf $2}';)
    if [ -z "$default_gw" ]; then
        return 1
    else
        return 0
    fi
}

###############################################################################
# DESCRIPTION:
#   Function verifies if dhcp for interface is configured at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
#   $2  Start pool (string, required)
#   $3  End pool (string, required)
# RETURNS:
#   0   dhcp is configured on interface.
#   1   dhcp is not configured on interface.
# USAGE EXAMPLE(S):
#   check_dhcp_from_dnsmasq_conf wifi0 10.10.10.16 10.10.10.32
###############################################################################
check_dhcp_from_dnsmasq_conf()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_dhcp_from_dnsmasq_conf requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1
    start_pool=$2
    end_pool=$3

    grep "dhcp-range=$if_name,$start_pool,$end_pool" /var/etc/dnsmasq.conf &&
        return 0 ||
        return 1
}

###############################################################################
# DESCRIPTION:
#   Function returns state of the ethernet interface provided in parameter.
#   Uses and requires ifconfig tool to be installed on device.
#   Provide adequate function in overrides otherwise.
# INPUT PARAMETER(S):
#   $1  Ethernet interface name (string, required)
# RETURNS:
#   0   If ethernet interface state is UP, non zero otherwise.
# USAGE EXAMPLE(S):
#   check_eth_interface_state_is_up eth0
###############################################################################
check_eth_interface_state_is_up()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_eth_interface_state_is_up requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    ifconfig "$if_name" 2>/dev/null | grep Metric | grep UP
    return $?
}

###############################################################################
# DESCRIPTION:
#   Function checks if provided firmware version string is a valid pattern.
#   Raises an exception if firmware version string has invalid pattern.
# FIELDS OF INTEREST:
#             (optional) build description
#            (optional) version patch    |
#        (required) minor version   |    |
#                               |   |    |
#   For the FW version string 2.0.2.0-70-gae540fd-dev-academy
#                             |   |   |
#      (required) major version   |   |
#       (optional) version revision   |
#               (optional) build number
# INPUT PARAMETER(S):
#   $1  FW version (string, required)
# RETURNS:
#   0   Firmware version string is valid
#   See DESCRIPTION.
#   Function will send an exit signal upon error, use subprocess to avoid this
# USAGE EXAMPLE(S):
#   check_fw_pattern 3.0.0-29-g100a068-dev-debug
#   check_fw_pattern 2.0.2.0-70-gae540fd-dev-academy
###############################################################################
check_fw_pattern()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_fw_pattern requires ${NARGS} input argument(s), $# given" -arg
    fw_version="${1}"

    [ -n "${fw_version}" ] ||
        raise "Firmware version string '${fw_version}' is empty!" -l "unit_lib:check_fw_pattern"

    ### Split by delimiter '-' to separate version and build information
    # only three elements are of interest
    fw_segment_0="$(echo "$fw_version" | cut -d'-' -f1)"
    fw_segment_1="$(echo "$fw_version" | cut -d'-' -f2)"
    fw_segment_2="$(echo "$fw_version" | cut -d'-' -f3-)"
    # If delimiter is not present, segment is empty, not equal to previous
    [ "${fw_segment_2}" == "${fw_segment_1}" ] && fw_segment_2=''
    [ "${fw_segment_1}" == "${fw_segment_0}" ] && fw_segment_1=''
    # Determine build number, if present
    build_number="${fw_segment_1}"
    if [ -n "${build_number}" ]; then
        # If not empty, must be integer between 1 and 6 numerals
        [ ${#build_number} -ge 1 ] && [ ${#build_number} -le 6 ] ||
            raise "Build number '${build_number}' must contain 1-6 numerals, not ${#build_number}" -l "unit_lib:check_fw_pattern"
        echo ${build_number} | grep -E "^[0-9]*$" ||
            raise "Build number '${build_number}' contains non numeral characters!" -l "unit_lib:check_fw_pattern"
    fi

    # Verify the version segment before splitting
    [ -n "${fw_segment_0}" ] ||
        raise "Firmware version segment '${fw_segment_0}' is empty!" -l "unit_lib:check_fw_pattern"
    echo "${fw_segment_0}" | grep -E "^[0-9.]*$" ||
        raise "Firmware version segment '${fw_segment_0}' contains invalid characters!" -l "unit_lib:check_fw_pattern"
    # At least major and minor versions are needed, so one dot "." is required
    echo "${fw_segment_0}" | grep [.] ||
        raise "Firmware version segment '${fw_segment_0}' does not contain the delimiter '.'" -l "unit_lib:check_fw_pattern"
    ### Split by delimiter '.' to get version segments
    ver_major="$(echo "$fw_segment_0" | cut -d'.' -f1)"
    ver_minor="$(echo "$fw_segment_0" | cut -d'.' -f2)"
    ver_revision="$(echo "$fw_segment_0" | cut -d'.' -f3)"
    ver_patch="$(echo "$fw_segment_0" | cut -d'.' -f4)"
    ver_overflow="$(echo "$fw_segment_0" | cut -d'.' -f5-)"
    # Allow 2 to 4 elements, else fail
    [ -n "${ver_major}" ] ||
        raise "Major version ${ver_major} is empty!" -l "unit_lib:check_fw_pattern"
    [ -n "${ver_minor}" ] ||
        raise "Minor version ${ver_minor} is empty!" -l "unit_lib:check_fw_pattern"
    [ -z "${ver_overflow}" ] ||
        raise "Firmware version ${fw_segment_0} has too many segments (2-4), overflow: '${ver_overflow}'" -l "unit_lib:check_fw_pattern"
    # Non-empty segments must have 1-4 numerals
    [ ${#ver_major} -ge 1 ] && [ ${#ver_major} -le 3 ] ||
        raise "Major version '${ver_major}' must contain 1-3 numerals, not ${#ver_major}" -l "unit_lib:check_fw_pattern"
    [ ${#ver_minor} -ge 1 ] && [ ${#ver_minor} -le 3 ] ||
        raise "Minor version '${ver_minor}' must contain 1-3 numerals, not ${#ver_minor}" -l "unit_lib:check_fw_pattern"
    if [ -n "${ver_revision}" ]; then
        [ ${#ver_revision} -ge 1 ] && [ ${#ver_revision} -le 3 ] ||
            raise "Micro version '${ver_revision}' must contain 1-3 numerals, not ${#ver_revision}" -l "unit_lib:check_fw_pattern"
    fi
    if [ -n "${ver_patch}" ]; then
        [ ${#ver_patch} -ge 1 ] && [ ${#ver_patch} -le 3 ] ||
            raise "Nano version '${ver_patch}' must contain 1-3 numerals, not ${#ver_patch}" -l "unit_lib:check_fw_pattern"
    fi

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if HT mode for interface on selected channel is
#   applied at OS - LEVEL2.
#   Raises exception if actual HT mode does not match expected value
# INPUT PARAMETER(S):
#   $1  HT mode (string, required)
#   $2  VIF interface name (string, required)
#   $3  Channel (int, required)
# RETURNS:
#   0  if actual HT mode matches expected value
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_ht_mode_at_os_level HT40 home-ap-24 2
#   check_ht_mode_at_os_level HT20 home-ap-50 36
###############################################################################
check_ht_mode_at_os_level()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_ht_mode_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    # shellcheck disable=SC2034
    ht_mode=$1
    vif_if_name=$2
    channel=$3

    log -deb "unit_lib:check_ht_mode_at_os_level - Checking HT mode for channel '$channel' at OS - LEVEL2"
    wait_for_function_output "$ht_mode" "get_ht_mode_from_os $vif_if_name $channel" &&
        log -deb "unit_lib:check_ht_mode_at_os_level - HT Mode '$ht_mode' set at OS - LEVEL2 - Success" ||
        raise "HT Mode '$ht_mode' is not set at OS - LEVEL2" -l "unit_lib:check_ht_mode_at_os_level" -tc

    return 0
}

##################################################################################
# DESCRIPTION:
#   Function validates the 'id' field of the AWLAN_Node table and raises an
#   exception if
#   1. length of 'id' > 81 characters
#   2. id pattern contains invalid characters.
#   Note that Node ID should also pass below rules but FUT does not verify this:
#   1. Node ID should be unique across all devices.
#   2. Node ID has to match either of Serial Number or MAC address of the device,
#       BLE and QR code.
#   3. ID length cannot be greater than 12 characters for devices claimed via BLE.
#       FUT just throws warning if length exceeds 12 characters in any case.
# INPUT PARAMETER(S):
#   $1  Node ID (string, required)
#   $2  MAC address of the device (string, required)
#   $3  Serial number of the device (string, required)
# RETURNS:
#   0   Node ID string is valid
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_id_pattern A12B34CD5678 11:22:33:44:55:66 A12B34CD5678
###################################################################################
check_id_pattern()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_id_pattern requires ${NARGS} input argument(s), $# given" -arg
    node_id=${1}
    mac_addr=${2}
    serial_num=${3}

    [ -n "${node_id}" ] ||
        raise "Node ID string is empty!" -l "unit_lib:check_id_pattern"

    # If not empty, must not exceed 81 chars
    [ ${#node_id} -gt 81 ] &&
        raise "Length of Node ID '${node_id}' is invalid" -l "unit_lib:check_id_pattern"
    # Length must not exceed 12 chars for devices claimed via bluetooth
    [ ${#node_id} -gt 12 ] &&
        log "unit_lib:check_id_pattern - Node ID '${node_id}' is longer than 12 characters and can not be used for claiming the device via bluetooth!"

    # Allowed alphanumerics, colon and underscore characters.
    echo ${node_id} | grep -E "[A-Za-z0-9:_]" ||
        raise "Node ID '${node_id}' contains invalid characters!" -l "unit_lib:check_id_pattern"

    # Logged if Node ID matches MAC address or Serial Number.
    [ "${node_id}" == "${mac_addr}" ] &&
        log -deb "unit_lib:check_id_pattern - Node ID '${node_id}' matches MAC address of the device"
    [ "${node_id}" == "${serial_num}" ] &&
        log -deb "unit_lib:check_id_pattern - Node ID '${node_id}' matches serial number of the device"

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if port with provided name is in the network bridge.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   0   Port is in bridge.
#   1   Port is not in bridge.
# USAGE EXAMPLE(S):
#   check_if_port_in_bridge br-lan eth0
###############################################################################
check_if_port_in_bridge()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_if_port_in_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1
    port_name=$2

    if linux_native_bridge_enabled; then
        brctl show ${bridge} | grep -wF "${port_name}"
    else
        ovs-vsctl list-ports "$bridge" | grep -wF "$port_name"
    fi
    if [ "$?" = 0 ]; then
        log -deb "unit_lib:check_if_port_in_bridge - Port '$port_name' exists on bridge '$bridge'"
        return 0
    else
        log -deb "unit_lib:check_if_port_in_bridge - Port '$port_name' does not exist on bridge '$bridge'"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function verifies if broadcast address for interface is set at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   Broadcast address set on interface.
#   1   Broadcast address not set on interface.
# USAGE EXAMPLE(S):
#   check_interface_broadcast_set_on_system eth0
###############################################################################
check_interface_broadcast_set_on_system()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_interface_broadcast_set_on_system requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    ifconfig "$if_name" | tr -s ' :' '@' | grep -e '^@inet@' | cut -d '@' -f 6
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:check_interface_broadcast_set_on_system - Broadcast set for interface '${if_name}'"
        return 0
    else
        log -deb "unit_lib:check_interface_broadcast_set_on_system - Broadcast not set for interface '${if_name}'"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if interface exists on system.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   Interface exists.
#   1   Interface does not exist.
# USAGE EXAMPLE(S):
#   check_interface_exists test1
###############################################################################
check_interface_exists()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_interface_exists requires ${NARGS} input argument(s), $# given" -arg
    local if_name=$1

    log -deb "unit_lib:check_interface_exists - Checking if interface '${if_name}' exists on OS - LEVEL2"

    ifconfig | grep -wE "$if_name"
    if [ "$?" -eq 0 ]; then
        log -deb "unit_lib:check_interface_exists - Interface '${if_name}' exists on OS - LEVEL2"
        return 0
    else
        log -deb "unit_lib:check_interface_exists - Interface '${if_name}' does not exist on OS - LEVEL2"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function returns IP address of interface provided in parameter.
#   Uses and requires ifconfig tool to be installed on device.
#   Provide adequate function in overrides otherwise.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   IP address of an interface
# USAGE EXAMPLE(S):
#   check_interface_ip_address_set_on_system eth0
###############################################################################
check_interface_ip_address_set_on_system()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_interface_ip_address_set_on_system requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    ifconfig "$if_name" | tr -s ' :' '@' | grep -e '^@inet@' | cut -d '@' -f 4
}

###############################################################################
# DESCRIPTION:
#   Function verifies if MTU for interface is set at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   MTU set on interface.
#   1   MTU not set on interface.
# USAGE EXAMPLE(S):
#   check_interface_mtu_set_on_system eth0
###############################################################################
check_interface_mtu_set_on_system()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_interface_mtu_set_on_system requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    ifconfig "$if_name" | tr -s ' ' | grep "MTU" | cut -d ":" -f2 | awk '{print $1}'
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:check_interface_mtu_set_on_system - MTU set for interface '${if_name}'"
        return 0
    else
        log -deb "unit_lib:check_interface_mtu_set_on_system - MTU not set for interface '${if_name}'"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if NAT is enabled for interface at OS - LEVEL2.
#   Uses iptables tool.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   NAT is enabled on interface.
#   1   NAT is not enabled on interface.
# USAGE EXAMPLE(S):
#   check_interface_nat_enabled eth0
###############################################################################
check_interface_nat_enabled()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_interface_nat_enabled requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    iptables -t nat --list -v  | tr -s ' ' / | grep '/MASQUERADE/' | grep "$if_name"
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:check_interface_nat_enabled - Interface '${if_name}' NAT enabled"
        return 0
    else
        log -deb "unit_lib:check_interface_nat_enabled - Interface '${if_name}' NAT disabled"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function verifies if netmask for interface is set at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   Netmask set on interface.
#   1   Netmask not set on interface.
# USAGE EXAMPLE(S):
#   check_interface_netmask_set_on_system eth0
###############################################################################
check_interface_netmask_set_on_system()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_interface_netmask_set_on_system requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    ifconfig "$if_name" | tr -s ' :' '@' | grep -e '^@inet@' | cut -d '@' -f 8
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:check_interface_netmask_set_on_system - Netmask set for interface '${if_name}'"
        return 0
    else
        log -deb "unit_lib:check_interface_netmask_set_on_system - Netmask not set for interface '${if_name}'"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if IP port forwarding is enabled on given interface.
#   Uses iptables tool.
# INPUT PARAMETER(S):
#   $1  interface name (required)
# RETURNS:
#   0   Port forwarding enabled on interface.
#   1   Port forwarding not enabled on interface.
# USAGE EXAMPLE(S):
#   check_ip_port_forwarding eth0
###############################################################################
check_ip_port_forwarding()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_ip_port_forwarding requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    iptables -t nat --list -v  | tr -s ' ' / | grep '/DNAT/' | grep "$if_name"
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:check_ip_port_forwarding - IP port forward set for interface '${if_name}'"
        return 0
    else
        log -deb "unit_lib:check_ip_port_forwarding - IP port forward not set for interface '${if_name}'"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if CAC (Channel Availability Check) on selected channel and
#   interface is started.
#   State is established by inspecting the Wifi_Radio_State table.
#   Raises exception if CAC is not started.
# INPUT PARAMETER(S):
#   $1  Channel (int, required)
#   $2  Interface name (string, required)
# RETURNS:
#   0   CAC started for channel.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_is_cac_started 120 wifi2
#   check_is_cac_started 100 wifi2
###############################################################################
check_is_cac_started()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_is_cac_started requires ${NARGS} input argument(s), $# given" -arg
    channel=$1
    if_name=$2

    log -deb "unit_lib:check_is_cac_started - Checking if CAC is started on channel $channel"
    if ${OVSH} s Wifi_Radio_State channels -w if_name=="$if_name" -r | grep -F '["'$channel'","{\"state\": \"cac_started\"}"]'; then
        log -deb "unit_lib:check_is_cac_started - CAC started on channel '$channel'"
        return 0
    fi
    log -err "unit_lib:check_is_cac_started - CAC is not started on channel '$channel'"
    return 1
}

###############################################################################
# DESCRIPTION:
#   Function checks if requested channel is available on selected radio interface.
#   It does not check if the channel is available for immediate use.
#   Raises exception if Wifi_Radio_State::allowed_channels is not populated or
#   if selected channel is not found in the list of allowed channels.
# INPUT PARAMETER(S):
#   $1  Channel (int, required)
#   $2  Radio interface name (string, required)
# RETURNS:
#   0   Channel is available on selected radio interface.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_is_channel_allowed 2 wifi0
#   check_is_channel_allowed 144 wifi2
###############################################################################
check_is_channel_allowed()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_is_channel_allowed requires ${NARGS} input argument(s), $# given" -arg
    channel=$1
    if_name=$2

    log -deb "unit_lib:check_is_channel_allowed - Waiting for Wifi_Radio_State::allowed_channels to be populated"
    wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_Radio_State allowed_channels -w if_name ${if_name}" &&
        log -deb "unit_lib:check_is_channel_allowed - Wifi_Radio_State::allowed_channels populated - Success" ||
        raise "Wifi_Radio_State::allowed_channels not populated" -l "unit_lib:check_is_channel_allowed" -ds

    log -deb "unit_lib:check_is_channel_allowed - Checking if channel '$channel' is allowed for '$if_name'"
    allowed_channels=$(get_ovsdb_entry_value Wifi_Radio_State allowed_channels -w if_name "$if_name" -r)
    if [ -z "${allowed_channels}" ]; then
        ${OVSH} s Wifi_Radio_State
        raise "Wifi_Radio_State::allowed_channels for '$if_name' is empty" -l "unit_lib:check_is_channel_allowed" -ds
    fi
    log -deb "unit_lib:check_is_channel_allowed - allowed_channels: ${allowed_channels}"
    contains_element "${channel}" $(echo ${allowed_channels} | sed 's/\[/ /g; s/\]/ /g; s/,/ /g;') &&
        log -deb "unit_lib:check_is_channel_allowed - Channel '$channel' is allowed on radio '$if_name' - Success" ||
        raise "Wifi_Radio_State::allowed_channels for '$if_name' does not contain '$channel'" -l "unit_lib:check_is_channel_allowed" -ds

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if requested channel is ready to use on radio interface.
#   Even if the channel changes in Wifi_Radio_State table, this might mean that
#   the channel was DFS and is currently undergoing CAC. The channel is actually
#   ready for use, only once the state is equal to "allowed" or "cac_completed".
# INPUT PARAMETER(S):
#   $1  Channel (required)
#   $2  Radio interface name (required)
# RETURNS:
#   0   Channel is ready use.
#   1   Channel is not ready to use.
# USAGE EXAMPLE(S):
#   check_is_channel_ready_for_use 2 wifi0
###############################################################################
check_is_channel_ready_for_use()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_is_channel_ready_for_use requires ${NARGS} input argument(s), $# given" -arg
    channel=$1
    if_name=$2
    is_empty=false

    log -deb "unit_lib:check_is_channel_ready_for_use - Checking if channel '$channel' is ready for immediate use"
    wait_for_function_response "notempty" "get_ovsdb_entry_value Wifi_Radio_State channels -w if_name $if_name" || is_empty=true

    if [ "$is_empty" = "true" ]; then
        log -deb "unit_lib:check_is_channel_ready_for_use - Table Wifi_Radio_State dump"
        ${OVSH} s Wifi_Radio_State || true
        raise "Wifi_Radio_State::channels is empty for '$if_name'" -l "unit_lib:check_is_channel_ready_for_use" -ds
    fi

    check_is_channel_allowed "$channel" "$if_name" &&
        log -deb "unit_lib:check_is_channel_ready_for_use - channel $channel is allowed on radio $if_name" ||
        raise "Channel $channel is not allowed on radio $if_name" -l "unit_lib:check_is_channel_ready_for_use" -ds

    state="$(get_radio_channel_state "$channel" "$if_name")"
    if [ "$state" == "cac_completed" ] || [ "$state" == "allowed" ]; then
        log -deb "unit_lib:check_is_channel_ready_for_use - Channel '$channel' is ready for use - $state"
        return 0
    fi

    log -deb "unit_lib:check_is_channel_ready_for_use - Channel '$channel' is not ready for use: $state"
    return 1
}

###############################################################################
# DESCRIPTION:
#   Function checks if NOP (No Occupancy Period) on the desired interface for
#   the channel in question is not in effect. This means that there are no
#   active radar events detected and the channel is eligible to start CAC
#   (channel availability check).
#   The information is parsed from the Wifi_Radio_State table.
# INPUT PARAMETER(S):
#   $1  Channel (int, required)
#   $2  Interface name (string, required)
# RETURNS:
#   0   channel status is "nop_finished"
#   1   channel status is not "nop_finished"
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_is_nop_finished 120 wifi2
###############################################################################
check_is_nop_finished()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_is_nop_finished requires ${NARGS} input argument(s), $# given" -arg
    channel=$1
    if_name=$2

    if ${OVSH} s Wifi_Radio_State channels -w if_name=="$if_name" -r | grep -F '["'$channel'","{\"state\": \"nop_finished\"}"]'; then
        return 0
    fi

    return 1
}

###############################################################################
# DESCRIPTION:
#   Function checks kconfig value from ${OPENSYNC_ROOTDIR}/etc/kconfig
#   if it matches given value.
#   Raises an exception if kconfig field is missing from given path.
# INPUT PARAMETER(S):
#   $1  kconfig option name (string, required)
#   $2  kconfig option value to check (string, required)
# RETURNS:
#   0   value matches to the one in kconfig path
#   1   value does not match to the one in kconfig path
# USAGE EXAMPLE(S):
#   check_kconfig_option "CONFIG_PM_ENABLE_LED" "y"
###############################################################################
check_kconfig_option()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_kconfig_option requires ${NARGS} input argument(s), $# given" -arg
    kconfig_option_name=${1}
    kconfig_option_value=${2}

    kconfig_path="${OPENSYNC_ROOTDIR}/etc/kconfig"
    if ! [ -f "${kconfig_path}" ]; then
        raise "kconfig file is not present on ${kconfig_path}" -l "unit_lib:check_kconfig_option" -ds
    fi
    cat "${kconfig_path}" | grep -q "${kconfig_option_name}=${kconfig_option_value}"
    return $?
}

###############################################################################
# DESCRIPTION:
#   Function checks kconfig option exists in ${OPENSYNC_ROOTDIR}/etc/kconfig
#   Raises an exception if kconfig file is missing on device.
# INPUT PARAMETER(S):
#   $1  kconfig option name (string, required)
# RETURNS:
#   0   option present in kconfig file
#   1   option not present in kconfig file
# USAGE EXAMPLE(S):
#   check_kconfig_option_exists "CONFIG_TARGET_PATH_DISABLE_FATAL_STATE"
###############################################################################
check_kconfig_option_exists()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_kconfig_option_exists requires ${NARGS} input argument(s), $# given" -arg
    kconfig_option_name=${1}

    kconfig_path="${OPENSYNC_ROOTDIR}/etc/kconfig"
    if ! [ -f "${kconfig_path}" ]; then
        raise "kconfig file is not present on ${kconfig_path}" -l "unit_lib:check_kconfig_option" -ds
    fi
    grep -qw "${kconfig_option_name}" "${kconfig_path}"
    return $?
}

##################################################################################
# DESCRIPTION:
#   Function validates the 'model' field of the AWLAN_Node table and raises an
#   exception if the pattern contains invalid characters.
#   Allowed characters: uppercase and lowercase alphanumerics, hyphen, underscore.
# INPUT PARAMETER(S):
#   $1  Model string (string, required)
# RETURNS:
#   0   Model string is valid
# USAGE EXAMPLE(S):
#   check_model_pattern A12-B34_cd5678
###################################################################################
check_model_pattern()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_model_pattern requires ${NARGS} input argument(s), $# given" -arg
    model_string=${1}
    echo ${node_id} | grep -E "^[A-Za-z0-9_-]*$" ||
        raise "Model string '${model_string}' contains invalid characters!" -l "unit_lib:check_model_pattern"
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if number of radios for device is as expected in parameter.
# INPUT PARAMETER(S):
#   $1  number of expected radios (int, required)
# RETURNS:
#   0   Number of radios is as expected.
#   1   Number of radios is not as expected.
# USAGE EXAMPLE(S):
#   check_number_of_radios 3
###############################################################################
check_number_of_radios()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_number_of_radios requires ${NARGS} input argument(s), $# given" -arg
    num_of_radios_1=$1
    num_of_radios_2=$(get_number_of_radios)

    log -deb "unit_lib:check_number_of_radios - Number of radios is $num_of_radios_2"

    if [ "$num_of_radios_1" = "$num_of_radios_2" ]; then
        return 0
    else
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if the actual values of the requested fields in the
#   specified table are equal to the expected ones. Fields and values are
#   specified with the -w (where) flag:
#     -w field value
#   If -w option is used then two additional parameters must follow to
#   define the condition string. Several -w options are possible.
#   The underlying command used is 'ovsh select'.
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  option, supported options: -w (string, optional, see DESCRIPTION)
#   $3  ovsdb field in ovsdb table (string, optional, see DESCRIPTION)
#   $4  ovsdb field value (string, optional, see DESCRIPTION)
#
# RETURNS:
#   0   Query finds at least one existing entry with the given conditions.
#   1   Query does not find any existing entry with the given conditions.
# USAGE EXAMPLE(S):
#   check_ovsdb_entry AWLAN_Node -w model <model>
###############################################################################
check_ovsdb_entry()
{
    ovsdb_table=$1
    shift 1
    conditions_string=""
    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -w)
                echo ${2} | grep -e "[ \"]" -e '\\' &&
                    conditions_string="$conditions_string -w $1==$(single_quote_arg "${2}")" ||
                    conditions_string="$conditions_string -w $1==$2"
                shift 2
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:check_ovsdb_entry" -arg
                ;;
        esac
    done
    check_cmd="${OVSH} s $ovsdb_table $conditions_string"
    log -deb "unit_lib:check_ovsdb_entry - Checking if entry exists:\n\t$check_cmd"
    eval "$check_cmd"
    if [ "$?" == 0 ]; then
        log -deb "unit_lib:check_ovsdb_entry - Entry $ovsdb_table $conditions_string exists"
        return 0
    else
        log -deb "unit_lib:check_ovsdb_entry - Entry $ovsdb_table $conditions_string does not exist"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if the actual values of the requested fields in the
#   specified table are equal to the expected ones. Fields and values are
#   specified with the -w (where) flag:
#     -w field value
#   If -w option is used then two additional parameters must follow to
#   define the condition string. Several -w options are possible.
#   The underlying command used is 'ovsdb-client transact'.
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  option, supported options: -w (string, optional, see DESCRIPTION)
#   $3  ovsdb field in ovsdb table (string, optional, see DESCRIPTION)
#   $4  ovsdb field value (string, optional, see DESCRIPTION)
#
# RETURNS:
#   0   Query finds at least one existing entry with the given conditions.
#   1   Query does not find any existing entry with the given conditions.
# USAGE EXAMPLE(S):
#   check_ovsdb_entry AWLAN_Node -w model <model>
###############################################################################
check_ovsdb_entry_transact()
{
    ovsdb_table=$1
    shift 1
    transact_string='["Open_vSwitch",{"op": "select","table": "'$ovsdb_table'","where":['
    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -w)
                echo ${2} | grep -e "[ \"]" -e '\\' &&
                    val_str="$2"
                    echo "$2" | grep -q "map"
                    if [ "$?" != "0" ]; then
                        echo "$2" | grep -q "false\|true"
                        if [ "$?" != "0" ]; then
                            echo "$2" | grep -q "\""
                            if [ "$?" != "0" ]; then
                                [ "$2" -eq "$2" ] 2>/dev/null && is_number="0" || is_number="1"
                                if [ "${is_number}" == "1" ]; then
                                    val_str='"'$2'"'
                                fi
                            fi
                        fi
                    fi
                    transact_string=$transact_string'["'$1'","==",'$val_str'],'
                shift 2
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:check_ovsdb_entry" -arg
                ;;
        esac
    done
    transact_string="$transact_string]}]"
    # remove last , from where statement ],]}]
    transact_string=${transact_string//],]/]]}

    log -deb "unit_lib:check_ovsdb_entry - Transact string: ovsdb-client transact \'${transact_string}\'"
    res=$(eval ovsdb-client transact \'${transact_string}\')
    if [ "$?" == "0" ]; then
        echo "${res}" | grep '\[{"rows":\[\]}\]'
        if [ "$?" == "0" ]; then
            log -deb "unit_lib:check_ovsdb_entry - Entry does not exist"
            return 1
        else
            log -deb "unit_lib:check_ovsdb_entry - Entry exists"
            return 0
        fi
    else
        log -deb "unit_lib:check_ovsdb_entry - Entry does not exist"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if the OVSDB table exists or not.
#   Function uses ovsdb-client tool.
# INPUT PARAMETER(S):
#   $1  OVSDB table name (string, required).
# RETURNS:
#   0 if the OVSDB table exist.
#   1 if the OVSDB table does not exist.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_ovsdb_table_exist AWLAN_Node
###############################################################################
check_ovsdb_table_exist()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_ovsdb_table_exist requires ${NARGS} input argument(s), $# given" -arg
    ovsdb_table_name=${1}
    check=$(ovsdb-client list-tables | grep ${ovsdb_table_name})
    if [ -z "$check" ]; then
        return 1
    else
        return 0
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if field exists in the specific table.
# INPUT PARAMETER(S):
#   $1  ovsdb table name (string, required)
#   $2  field name in the ovsdb table (string, required)
# RETURNS:
#   0   If field exists in ovsdb table.
#   1   If field does not exist in ovsdb table.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_ovsdb_table_field_exists AWLAN_Node device_mode
###############################################################################
check_ovsdb_table_field_exists()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_ovsdb_table_field_exists requires ${NARGS} input argument(s), $# given" -arg
    ovsdb_table=$1
    field_name=$2

    $(${OVSH} s "$ovsdb_table" "$field_name" &> /dev/null)
    if [ $? -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
# INPUT PARAMETER(S):
#   $1  process status type (string, required)
#   $2  process file (string, required)
# RETURNS:
#   0   process file does not exist and process should be dead
#   0   process file exists and process is alive
#   1   process file does not exist and process should be alive
#   1   process file exists and process should be dead
# USAGE EXAMPLE(S):
#   check_pid_file alive \"/var/run/udhcpc-$if_name.pid\"
#   check_pid_file dead \"/var/run/udhcpc-$if_name.pid\"
###############################################################################
check_pid_file()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_pid_file requires ${NARGS} input argument(s), $# given" -arg
    type=$1
    file=$2

    if [ "$type" = "dead" ] && [ ! -f "$file" ]; then
        log -deb "unit_lib:check_pid_file - Process '$file' is dead"
        return 0
    elif [ "$type" = "alive" ] && [ -f "$file" ]; then
        log -deb "unit_lib:check_pid_file - Process '$file' is alive"
        return 0
    elif [ "$type" = "dead" ] && [ -f "$file" ]; then
        log -deb "unit_lib:check_pid_file - Process is alive"
        return 1
    else
        log -deb "unit_lib:check_pid_file - Process is dead"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if udhcps service (DHCP client) on provided interface is
#   running. It does so by checking existence of PID of DHCP client service.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   PID found, udhcpc service is running
#   1   PID not found, udhcpc service is not running
# USAGE EXAMPLE(S):
#   check_pid_udhcp eth0
###############################################################################
check_pid_udhcp()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_pid_udhcp requires ${NARGS} input argument(s), $# given" -arg
    local if_name="${1}"

    PID=$($(get_process_cmd) | grep -e udhcpc | grep -e "${if_name}" | grep -v 'grep' | awk '{ print $1 }')
    if [ -z "$PID" ]; then
        log -deb "unit_lib:check_pid_udhcp - DHCP client not running on '${if_name}'"
        return 1
    else
        log -deb "unit_lib:check_pid_udhcp - DHCP client running on '${if_name}', PID=${PID}"
        return 0
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if the "LM: Run log-pull procedure" message is
#   present in the log messages, which indicates that the logpull
#   procedure started.
#   Raises exception on fail:
#       - logs not found
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_pm_report_log
###############################################################################
check_pm_report_log()
{
    log_msg="LM: Run log-pull procedure"
    pm_log_grep="$LOGREAD | grep -i '$log_msg'"

    log "unit_lib:check_pm_report_log - $log_msg"
    wait_for_function_response 0 "${pm_log_grep}" &&
        log -deb "unit_lib:check_pm_report_log - Found '$log_msg' - Success" ||
        raise "Could not find '$log_msg' in logs" -l "unit_lib:check_pm_report_log" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
# INPUT PARAMETER(S):
# RETURNS:
# USAGE EXAMPLE(S):
###############################################################################
check_radio_vif_state()
{
    vif_args_c=""
    vif_args_w=""
    radio_args=""
    replace="func_arg"
    retval=0

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -if_name | -radio_if_name)
                radio_args="$radio_args $replace if_name $1"
                if_name=$1
                shift
                ;;
            -vif_if_name)
                vif_args="$vif_args $replace if_name $1"
                vif_if_name=$1
                shift
                ;;
            -vif_radio_idx)
                vif_args="$vif_args $replace vif_radio_idx $1"
                shift
                ;;
            -ssid)
                vif_args="$vif_args $replace ssid $(single_quote_arg "$1")"
                shift
                ;;
            -channel)
                radio_args="$radio_args $replace channel $1"
                vif_args="$vif_args $replace channel $1"
                shift
                ;;
            -ht_mode)
                radio_args="$radio_args $replace ht_mode $1"
                shift
                ;;
            -hw_mode)
                radio_args="$radio_args $replace hw_mode $1"
                shift
                ;;
            -mode)
                vif_args="$vif_args $replace mode $1"
                shift
                ;;
            -security)
                vif_args="$vif_args $replace security $(single_quote_arg "$1")"
                shift
                ;;
            -country)
                radio_args="$radio_args $replace country $1"
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:check_radio_vif_state" -arg
                ;;
        esac
    done

    log -deb "unit_lib:check_radio_vif_state - Checking if interface $if_name is up"
    check_vif_interface_state_is_up "$if_name"
    if [ "$?" -eq 0 ]; then
        log -deb "unit_lib:check_radio_vif_state - Interface '$if_name' is up"
    else
        log -deb "unit_lib:check_radio_vif_state - Interface '$if_name' is not up"
        return 1
    fi

    func_params=${radio_args//$replace/-w}
    # shellcheck disable=SC2086
    check_ovsdb_entry Wifi_Radio_State $func_params
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:check_radio_vif_state - Wifi_Radio_State is valid for given configuration"
    else
        log -deb "unit_lib:check_radio_vif_state - Entry with required radio arguments in Wifi_Radio_State does not exist"
        retval=1
    fi

    func_params=${vif_args//$replace/-w}
    eval check_ovsdb_entry Wifi_VIF_State $func_params
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:check_radio_vif_state - Wifi_VIF_State is valid for given configuration"
    else
        log -deb "unit_lib:check_radio_vif_state - Entry with required VIF arguments in Wifi_VIF_State does not exist"
        retval=1
    fi

    return $retval
}

###############################################################################
# DESCRIPTION:
#   Function verifies if DNS is configured at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  primary DNS IP (string, required)
# RETURNS:
#   0   DNS is configured.
#   1   DNS is not configured.
# USAGE EXAMPLE(S):
#   check_resolv_conf 1.2.3.4
###############################################################################
check_resolv_conf()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_resolv_conf requires ${NARGS} input argument(s), $# given" -arg
    primary_dns=$1

    cat /tmp/resolv.conf | grep "nameserver $primary_dns" &&
        return 0 ||
        return 1
}

###############################################################################
# DESCRIPTION:
#   Function checks if the radio TX chainmask is applied at OS - LEVEL2.
# STUB:
#   This function is a stub. It always raises an exception and needs
#   a function with the same name and usage in platform or device overrides.
# INPUT PARAMETER(S):
#   $1  Radio TX Chainmask (int, required)
#   $2  Radio interface name (string, required)
# RETURNS:
#   0   Radio TX Chainmask on system matches expected value.
# USAGE EXAMPLE(S):
#   check_tx_chainmask_at_os_level 3 IF_NAME
###############################################################################
check_tx_chainmask_at_os_level()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_tx_chainmask_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    tx_chainmask=$1
    if_name=$2

    log "unit_lib:check_tx_chainmask_at_os_level - Checking Radio TX Chainmask for interface '$if_name' at OS - LEVEL2"
    # Provide override in platform specific file
    raise "This is a stub function. Override implementation needed." -l "unit_lib:check_tx_chainmask_at_os_level" -fc
}

###############################################################################
# DESCRIPTION:
#   Function checks if Tx Power is applied at OS - LEVEL2.
#   Raises exception if actual Tx Power does not match expected value
# INPUT PARAMETER(S):
#   $1  Tx Power (int, required)
#   $2  VIF interface name (string, required)
#   $3  Radio interface name (string, required)
# RETURNS:
#   0  if actual Tx Power matches expected value
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_tx_power_at_os_level 21 home-ap-24 wifi0
#   check_tx_power_at_os_level 14 wl0.2 wl0
###############################################################################
check_tx_power_at_os_level()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_tx_power_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    # shellcheck disable=SC2034
    tx_power=$1
    # shellcheck disable=SC2034
    vif_if_name=$2
    # shellcheck disable=SC2034
    if_name=$3

    log -deb "unit_lib:check_tx_power_at_os_level - Checking Tx Power for interface '$if_name' at OS - LEVEL2"
    wait_for_function_output $tx_power "get_tx_power_from_os $vif_if_name" &&
        log -deb "unit_lib:check_tx_power_at_os_level - Tx Power '$tx_power' is set at OS - LEVEL2 - Success" ||
        raise "Tx Power '$tx_power' is not set at OS - LEVEL2" -l "unit_lib:check_tx_power_at_os_level" -tc
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function returns state of the wireless interface provided in parameter.
#   Uses and requires ifconfig tool to be installed on device.
#   Provide adequate function in overrides otherwise.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
# RETURNS:
#   0   If VIF interface state is up, non zero otherwise.
# USAGE EXAMPLE(S):
#   check_vif_interface_state_is_up home-ap-24
###############################################################################
check_vif_interface_state_is_up()
{
    check_eth_interface_state_is_up "$@"
}

###############################################################################
# DESCRIPTION:
#   Function checks if vlan interface exists at OS level - LEVEL2.
# STUB:
#   This function is a stub. It always raises an exception and needs
#   a function with the same name and usage in platform or device overrides.
# INPUT PARAMETER(S):
#   $1  Parent interface name (string, required)
#   $2  VLAN ID (int, required)
# RETURNS:
#   0   vlan interface exists on system.
# USAGE EXAMPLE(S):
#  check_vlan_iface eth0 100
###############################################################################
check_vlan_iface()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_vlan_iface requires ${NARGS} input argument(s), $# given" -arg
    parent_ifname=$1
    vlan_id=$2

    log "unit_lib:check_vlan_iface - Checking vlan interface at OS - LEVEL2"
    # Provide override in platform specific file
    raise "This is a stub function. Override implementation needed for each platform." -l "unit_lib:check_vlan_iface" -fc
}

###############################################################################
# DESCRIPTION:
#   Function checks if inet_addr at OS - LEVEL2 is the same as
#   in test case config.
# INPUT PARAMETER(S):
#   $1  WAN interface name (string, required)
#   $2  Expected WAN IP (string, required)
# RETURNS:
#   0   IP is as expected.
#   1   WAN interface has no IP assigned or IP not equal to OS LEVEL2 IP address.
# USAGE EXAMPLE(S):
#   check_wan_ip_l2 eth0 192.168.200.10
###############################################################################
check_wan_ip_l2()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_wan_ip_l2 requires ${NARGS} input argument(s), $# given" -arg
    wan_if_name=$1
    inet_addr_in=$2

    # LEVEL2
    inet_addr=$(ifconfig "$wan_if_name" | grep 'inet addr' | awk '/t addr:/{gsub(/.*:/,"",$2); print $2}')
    if [ -z "$inet_addr" ]; then
        log -deb "unit_lib:check_wan_ip_l2 - inet_addr is empty"
        return 1
    fi

    if [ "$inet_addr_in" = "$inet_addr" ]; then
        log -deb "unit_lib:check_wan_ip_l2 - OVSDB inet_addr '$inet_addr_in' equals LEVEL2 inet_addr '$inet_addr' - Success"
        return 0
    else
        log -deb "unit_lib:check_wan_ip_l2 - FAIL: OVSDB inet_addr '$inet_addr_in' not equal to LEVEL2 inet_addr '$inet_addr'"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if device supports WPA3
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   1   Always.
# NOTE:
#   This is a stub function. Provide function for each device in overrides.
#   Defaults to 1 WPA3 incompatible
# USAGE EXAMPLE(S):
#   check_wpa3_compatibility
###############################################################################
check_wpa3_compatibility()
{
    log -deb "unit_lib:check_wpa3_compatibility - This is STUB function, provide override for device. Default to WPA3 incompatible"
    return 1
}

###############################################################################
# DESCRIPTION:
#   Function clears the DNS cache.
# STUB:
#   This function is a stub. It always raises an exception and needs
#   a function with the same name and usage in platform or device overrides.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   If DNS cache on the device was cleared.
# USAGE EXAMPLE(S):
#   clear_dns_cache
###############################################################################
clear_dns_cache()
{
    log "unit_lib:clear_dns_cache - Clearing DNS cache on the device."
    # Provide override in platform specific file
    raise "This is a stub function. Override implementation needed." -l "unit_lib:clear_dns_cache" -fc
}

###############################################################################
# DESCRIPTION:
#   Function populates DNS settings for given interface to Wifi_Inet_Config.
#   It waits for Wifi_Inet_Config to reflect in Wifi_Inet_State.
#   Raises an exception on fail.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
#   $2  Primary DNS IP (string, optional)
#   $3  Secondary DNS IP (string, optional)
# RETURNS:
#   0   On Success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   configure_custom_dns_on_interface eth0 16.17.18.19 20.21.22.23
#   configure_custom_dns_on_interface eth0
###############################################################################
configure_custom_dns_on_interface()
{
    NARGS_MIN=1
    NARGS_MAX=3
    [ $# -eq ${NARGS_MIN} ] || [ $# -eq ${NARGS_MAX} ] ||
        raise "unit_lib:configure_custom_dns_on_interface requires ${NARGS_MIN} or ${NARGS_MAX} input arguments, $# given" -arg
    if_name=$1
    primary_dns=$2
    secondary_dns=$3

    dns='["map",[["primary","'$primary_dns'"],["secondary","'$secondary_dns'"]]]'
    if [ -z "$primary_dns" ] && [ -z "$secondary_dns" ]; then
        dns=''
    fi

    log -deb "unit_lib:configure_custom_dns_on_interface - Creating DNS on interface '$if_name'"

    update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" \
        -u enabled true \
        -u network true \
        -u ip_assign_scheme static \
        -u dns $dns ||
            raise "Could not update Wifi_Inet_Config" -l "unit_lib:configure_custom_dns_on_interface" -fc

    wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" \
        -is enabled true \
        -is network true \
        -is dns $dns ||
            raise "Wifi_Inet_Config not reflected to Wifi_Inet_State" -l "unit_lib:configure_custom_dns_on_interface" -fc

    log -deb "unit_lib:configure_custom_dns_on_interface - DNS created on interface '$if_name' - Success"

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function enables or disables DHCP server on interface.
#   It waits for Wifi_Inet_Config to reflect in Wifi_Inet_State.
#   Raises exception if DHCP server is not configured.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
#   $2  IP address start pool (string, optional)
#   $3  IP address end pool (string, optional)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   configure_dhcp_server_on_interface eth1 10.10.10.20 10.10.10.50
#   configure_dhcp_server_on_interface eth1
###############################################################################
configure_dhcp_server_on_interface()
{
    NARGS_MIN=1
    NARGS_MAX=3
    [ $# -eq ${NARGS_MIN} ] || [ $# -eq ${NARGS_MAX} ] ||
        raise "unit_lib:configure_dhcp_server_on_interface requires ${NARGS_MIN} or ${NARGS_MAX} input arguments, $# given" -arg
    if_name=$1
    start_pool=$2
    end_pool=$3

    if [ -z "$start_pool" ] && [ -z "$end_pool" ]; then
        # One or both arguments are missing.
        dhcpd=''
    else
        dhcpd='["start","'$start_pool'"],["stop","'$end_pool'"]'
    fi

    log -deb "unit_lib:configure_dhcp_server_on_interface - Configuring DHCP server on interface '$if_name'"

    update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" \
        -u enabled true \
        -u network true \
        -u dhcpd '["map",['$dhcpd']]' ||
            raise "Could not update Wifi_Inet_Config" -l "unit_lib:configure_dhcp_server_on_interface" -fc

    wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" \
        -is enabled true \
        -is network true \
        -is dhcpd '["map",['$dhcpd']]' ||
            raise "Wifi_Inet_Config not reflected to Wifi_Inet_State" -l "unit_lib:configure_dhcp_server_on_interface" -fc

    log -deb "unit_lib:configure_dhcp_server_on_interface - DHCP server created on interface '$if_name' - Success"

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function configures STA VIF by populating the Wifi_VIF_Config OVSDB  table.
#
# INPUT PARAMETER(S):
#   Parameters are fed into function as key-value pairs. Only 'vif_if_name',
#   and 'ssid' arguments are mandatory, however those arguments alone might
#   not be enough to achieve the desired VIF configuration.
#   Function supports the following keys for parameter values:
#   -mac_list, -mac_list_type, -mode, -multi_ap, -parent, -ssid,
#   -vif_if_name, -wpa, -wpa_key_mgmt, -wpa_oftags, -wpa_psks,
#   -clear_wcc, -wait_ip
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
# Backhaul configuration on leaf node:
#   configure_sta_interface \
#   -vif_if_name bhaul-sta-24 \
#   -ssid bhaul_ssid \
###############################################################################
configure_sta_interface()
{
    vif_args_c=""
    vif_args_w=""
    wcc_args_c=""
    replace="func_arg"
    while [ -n "${1}" ]; do
        option=${1}
        shift
        case "${option}" in
            -if_name | -vif_if_name)
                # special variable name chosen to avoid overriding upstream variables
                vif_if_name=${1}
                vif_args_c="${vif_args_c} ${replace} if_name ${1}"
                vif_args_w="${vif_args_w} ${replace} if_name ${1}"
                shift
                ;;
            -ssid)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                wcc_args_c="${wcc_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ${option#?} $(single_quote_arg "$1")"
                ssid="${1}"
                shift
                ;;
            -clear_wcc)
                clear_wcc=${1}
                shift
                ;;
            -wait_ip)
                wait_ip=${1}
                shift
                ;;
            -mac_list | \
            -mac_list_type | \
            -mode | \
            -multi_ap | \
            -parent | \
            -wpa_oftags | \
            -wpa_key_mgmt | \
            -wpa)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -wpa_psks)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:configure_sta_interface" -arg
                ;;
        esac
    done

    [ -z "${vif_if_name}" ] &&
        raise "Interface name argument empty" -l "unit_lib:configure_sta_interface" -arg
    [ -z "${ssid}" ] &&
        raise "SSID name argument empty" -l "unit_lib:configure_sta_interface" -arg

    if [ "${clear_wcc}" = "true" ]; then
        log -deb "unit_lib:configure_sta_interface - Clearing Wifi_Credential_Config table"
        empty_ovsdb_table Wifi_Credential_Config &&
            log -deb "unit_lib:configure_sta_interface - Wifi_Credential_Config table is cleared" ||
            raise "empty_ovsdb_table Wifi_Credential_Config" -l "unit_lib:configure_sta_interface" -fc
    fi


    log -deb "unit_lib:configure_sta_interface - WPA is used, will not set Wifi_Credential_Config"
    update_ovsdb_entry Wifi_VIF_Config -w if_name "${vif_if_name}" -u security "[\"map\",[]]" &&
        log "unit_lib:configure_sta_interface update_ovsdb_entry - Wifi_VIF_Config::security is [\"map\",[]] - Success" ||
        raise "update_ovsdb_entry - Failed to update Wifi_VIF_Config::security is not [\"map\",[]]" -l "unit_lib:configure_sta_interface" -tc
    wait_ovsdb_entry Wifi_VIF_State -w if_name "${vif_if_name}" -is security "[\"map\",[]]" &&
        log "unit_lib:configure_sta_interface wait_ovsdb_entry - Wifi_VIF_State::security is [\"map\",[]] - Success" ||
        raise "wait_ovsdb_entry - Failed to update Wifi_VIF_State::security is not [\"map\",[]]" -l "unit_lib:configure_sta_interface" -tc

    # Check if entry for if_name already exists in Wifi_VIF_Config table
    # Update if entry exists, insert otherwise
    check_ovsdb_entry Wifi_VIF_Config -w if_name "${vif_if_name}"
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:configure_sta_interface - Updating existing VIF entry"
        function_to_call="update_ovsdb_entry"
        function_arg="-u"
    else
        raise "STA VIF entry does not exist" -l "unit_lib:configure_sta_interface" -ds
    fi

    # Perform action update/insert VIF
    func_params=${vif_args_c//$replace/$function_arg}
    # shellcheck disable=SC2086
    eval $function_to_call Wifi_VIF_Config -w if_name "$vif_if_name" $func_params &&
        log -deb "unit_lib:configure_sta_interface - $function_to_call Wifi_VIF_Config -w if_name $vif_if_name $func_params - Success" ||
        raise "$function_to_call Wifi_VIF_Config -w if_name $vif_if_name $func_params" -l "unit_lib:configure_sta_interface" -fc

    wait_for_function_response "notempty" "get_ovsdb_entry_value Wifi_VIF_State parent -w if_name $vif_if_name" &&
        parent_bssid=0 ||
        parent_bssid=1

    if [ "$parent_bssid" -eq 0 ]; then
        parent_bssid=$(get_ovsdb_entry_value Wifi_VIF_State parent -w if_name "$vif_if_name")
        update_ovsdb_entry Wifi_VIF_Config -w if_name "$vif_if_name" \
            -u parent "$parent_bssid" &&
                log -deb "unit_lib:configure_sta_interface - VIF_State parent was associated" ||
                raise "Failed to update Wifi_VIF_Config with parent MAC address" -l "unit_lib:configure_sta_interface" -ds
    fi

    # Validate action insert/update VIF
    func_params=${vif_args_w//$replace/-is}
    # shellcheck disable=SC2086
    eval wait_ovsdb_entry Wifi_VIF_State -w if_name "$vif_if_name" $func_params &&
        log -deb "unit_lib:configure_sta_interface - wait_ovsdb_entry Wifi_VIF_State -w if_name $vif_if_name $func_params - Success" ||
        raise "wait_ovsdb_entry Wifi_VIF_State -w if_name $vif_if_name $func_params" -l "unit_lib:configure_sta_interface" -fc

    if [ "${wait_ip}" == "true" ]; then
        log -deb "unit_lib:configure_sta_interface - Waiting for ${vif_if_name} Wifi_Inet_State address"
        wait_for_function_response "notempty" "get_ovsdb_entry_value Wifi_Inet_State inet_addr -w if_name ${vif_if_name}"
        wait_ovsdb_entry Wifi_Inet_State -w if_name "${vif_if_name}" -is_not inet_addr "0.0.0.0" &&
            log -deb "unit_lib:configure_sta_interface - ${vif_if_name} inet_addr in Wifi_Inet_State is $(get_ovsdb_entry_value Wifi_Inet_State inet_addr -w if_name $vif_if_name)" ||
            raise "${vif_if_name} inet_addr in Wifi_Inet_State is empty" -l "unit_lib:configure_sta_interface" -fc
    fi
    log -deb "unit_lib:configure_sta_interface: STA VIF entry successfully configured"
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function connects device to simulated FUT cloud.
#   Procedure:
#       - test if certificate file in provided folder exists
#       - update SSL table with certificate location and file name
#       - remove redirector address so it will not interfere
#       - set inactivity probe to 30s
#       - set manager address to FUT cloud
#       - set target in Manager table (it should be resolved by CM)
#       - wait for cloud state to become ACTIVE
#   Raises an exception on fail.
# INPUT PARAMETER(S):
#   $1  Cloud IP (string, optional, defaults to 192.168.200.1)
#   $2  Port (int, optional, defaults to 65000)
#   $3  Certificates folder (string, optional, defaults to $FUT_TOPDIR/utility/files)
#   $4  Certificate file (string, optional, defaults to fut_ca.pem)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   connect_to_fut_cloud
#   connect_to_fut_cloud 192.168.200.1 65000 fut-base/utility/files fut_ca.pem
###############################################################################
connect_to_fut_cloud()
{
    target="fut.opensync.io"
    port=65000
    server_cert_dir="${FUT_TOPDIR}/shell/tools/server/certs"
    cert_dir="/var/certs"

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -t)
                target="${1}"
                shift
                ;;
            -p)
                port="${1}"
                shift
                ;;
            -cd)
                cert_dir="${1}"
                shift
                ;;
            *)
              ;;
        esac
    done
    log -deb "unit_lib:connect_to_fut_cloud - Configure certificates, check if file exists"
    fut_server_cert_path="${server_cert_dir}/ca.pem"
    log -deb "unit_lib:connect_to_fut_cloud - Setting ${fut_server_cert_path} to ${cert_dir}/ca.pem"
    cat "${fut_server_cert_path}" >> "${cert_dir}/ca.pem"  &&
        log -deb "unit_lib:connect_to_fut_cloud - Certificate ca.pem loaded - Success" ||
        raise "Failed to load Certificate ca.pem" -l "unit_lib:connect_to_fut_cloud" -ds

    # Remove redirector, to not interfere with the flow
    update_ovsdb_entry AWLAN_Node -u redirector_addr '' &&
        log -deb "unit_lib:connect_to_fut_cloud - AWLAN_Node redirector_addr set to '' - Success" ||
        raise "AWLAN_Node::redirector_addr not set to ''" -l "unit_lib:connect_to_fut_cloud" -ds

    # Remove manager_addr, to not interfere with the flow
    update_ovsdb_entry AWLAN_Node -u manager_addr '' &&
        log -deb "unit_lib:connect_to_fut_cloud - AWLAN_Node manager_addr set to '' - Success" ||
        raise "AWLAN_Node::manager_addr not set to ''" -l "unit_lib:connect_to_fut_cloud" -ds

    # Clear Manager::target before starting
    update_ovsdb_entry Manager -u target '' &&
        log -deb "unit_lib:connect_to_fut_cloud - Manager target set to '' - Success" ||
        raise "Manager::target not set to ''" -l "unit_lib:connect_to_fut_cloud" -ds
    # Wait for CM to settle
    sleep 2
    update_ovsdb_entry AWLAN_Node -u redirector_addr "ssl:$target:$port" &&
        log -deb "unit_lib:connect_to_fut_cloud - AWLAN_Node redirector_addr set to ssl:$target:$port - Success" ||
        raise "AWLAN_Node::redirector_addr not set to ssl:$target:$port" -l "unit_lib:connect_to_fut_cloud" -ds

    log -deb "unit_lib:connect_to_fut_cloud - Waiting for FUT cloud status to go to ACTIVE"
    wait_cloud_state ACTIVE &&
        log -deb "unit_lib:connect_to_fut_cloud - Manager::status is set to ACTIVE. Connected to FUT cloud. - Success" ||
        raise "Manager::status is not ACTIVE. Not connected to FUT cloud." -l "unit_lib:connect_to_fut_cloud" -ds
}

###############################################################################
# DESCRIPTION:
#   Function searches a list of values for a provided value.
# INPUT PARAMETER(S):
#   $1  Value to look for in the list
#   $@  the values consisting the list from which to match the value
# RETURNS:
#   0   Value is found in the list
#   1   Value is not found in the list
# USAGE EXAMPLE(S):
#   contains_element baz foo bar baz
###############################################################################
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

###############################################################################
# DESCRIPTION:
#   Function creates entry to Wifi_Inet_Config table.
#   It then waits for config to reflect in Wifi_Inet_State table.
#   Raises exception on fail.
# INPUT PARAMETER(S):
#   See fields in table Wifi_Inet_Config.
#   Mandatory parameter: if_name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   create_inet_entry -if_name "eth1" -if_type "eth" -enabled "true"
###############################################################################
create_inet_entry()
{
    args=""
    add_cfg_args=""
    replace="func_arg"

    # Parse parameters
    while [ -n "$1" ]; do
        option=${1}
        shift
        case "${option}" in
            -if_name | -inet_if_name | -network_if_name)
                # special variable name chosen to avoid overriding upstream variables
                inet_if_name_val="${1}"
                args="${args} ${replace} if_name ${1}"
                shift
                ;;
            -enabled | -inet_enabled)
                args="${args} ${replace} enabled ${1}"
                shift
                ;;
            -network | \
            -if_type | \
            -inet_addr | \
            -bridge | \
            -dns | \
            -gateway | \
            -broadcast | \
            -ip_assign_scheme | \
            -mtu | \
            -NAT | \
            -upnp_mode | \
            -dhcpd | \
            -vlan_id | \
            -parent_ifname | \
            -gre_ifname | \
            -gre_remote_inet_addr | \
            -gre_local_inet_addr)
                args="${args} ${replace} ${option#?} ${1}"
                shift
                ;;
            -dhcp_sniff)
                add_cfg_args="${add_cfg_args} ${replace} ${option#?} ${1}"
                shift
                ;;
            -no_flood)
                add_cfg_args="${add_cfg_args} ${replace} ${option#?} ${1}"
                shift
                ;;
            -collect_stats)
                add_cfg_args="${add_cfg_args} ${replace} ${option#?} ${1}"
                shift
                ;;
            -broadcast_n)
                broadcast_n="${1}"
                shift
                ;;
            -inet_addr_n)
                inet_addr_n="${1}"
                shift
                ;;
            -subnet)
                subnet="${1}"
                shift
                ;;
            -netmask)
                netmask="${1}"
                args="${args} ${replace} ${option#?} ${1}"
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:create_inet_entry" -arg
                ;;
        esac
    done

    # Make sure inet_if_name_val parameter is set
    [ -z "${inet_if_name_val}" ] &&
        raise "Interface name argument empty" -l "unit_lib:create_inet_entry" -arg

    if [ -n "${broadcast_n}" ] && [ -n "${inet_addr_n}" ] && [ -n "${netmask}" ] && [ -n "${subnet}" ]; then
        log -deb "unit_lib:create_inet_entry - Setting additional parameters from partial info: broadcast, dhcpd_start, dhcpd_stop, inet_addr"
        broadcast="${subnet}.${broadcast_n}"
        dhcpd_start="${subnet}.$((inet_addr_n + 1))"
        dhcpd_stop="${subnet}.$((broadcast_n - 1))"
        inet_addr="${subnet}.${inet_addr_n}"
        dhcpd='["map",[["dhcp_option","26,1600"],["force","false"],["lease_time","12h"],["start","'${dhcpd_start}'"],["stop","'${dhcpd_stop}'"]]]'
        args="${args} ${replace} broadcast ${broadcast}"
        args="${args} ${replace} inet_addr ${inet_addr}"
        args="${args} ${replace} dhcpd ${dhcpd}"
    fi

    # Check if entry for given interface already exists, and if exists perform update action instead of insert
    check_ovsdb_entry Wifi_Inet_Config -w if_name "${inet_if_name_val}"
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:create_inet_entry - Updating existing interface in Wifi_Inet_Config"
        function_to_call="update_ovsdb_entry"
        function_arg="-u"
    else
        log -deb "unit_lib:create_inet_entry - Creating interface in Wifi_Inet_Config"
        function_to_call="insert_ovsdb_entry"
        function_arg="-i"
    fi

    # Perform action insert/update
    func_params=${args//$replace/$function_arg}
    func_params_add=${add_cfg_args//$replace/$function_arg}
    # shellcheck disable=SC2086
    $function_to_call Wifi_Inet_Config -w if_name "$inet_if_name_val" $func_params $func_params_add &&
        log -deb "unit_lib:create_inet_entry - $function_to_call Wifi_Inet_Config -w if_name $inet_if_name_val $func_params $func_params_add - Success" ||
        raise "$function_to_call Wifi_Inet_Config -w if_name $inet_if_name_val $func_params $func_params_add" -l "unit_lib:create_inet_entry" -fc

    # Validate action insert/update
    func_params=${args//$replace/-is}
    # shellcheck disable=SC2086
    wait_ovsdb_entry Wifi_Inet_State -w if_name "$inet_if_name_val" $func_params &&
        log -deb "unit_lib:create_inet_entry - wait_ovsdb_entry Wifi_Inet_State -w if_name $inet_if_name_val $func_params - Success" ||
        raise "wait_ovsdb_entry Wifi_Inet_State -w if_name $inet_if_name_val $func_params" -l "unit_lib:create_inet_entry" -fc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function creates and configures an AP VIF and makes sure the required
#   radio interface is created and configured as well.
# NOTE:
#   This function does not verify that the channel is ready for immediate
#   use, only that the channel was set, which means that DFS channels are
#   likely performing CAC, and a timeout and check needs to be done in
#   the calling function. See function: check_is_channel_ready_for_use()
# INPUT PARAMETER(S):
#   Parameters are fed into function as key-value pairs. Only 'radio_if_name',
#   'vif_if_name' and 'channel' arguments are mandatory, however those arguments
#   alone might not be enough to achieve the desired VIF configuration.
#   Function supports the following keys for parameter values:
#   -channel, -channel_mode, -ht_mode, -radio_if_name, -ap_bridge, -bridge,
#   -enabled, -mac_list, -mac_list_type, -mode, -multi_ap, -ssid, -ssid_broadcast,
#   -hw_mode, -vif_if_name, -vif_radio_idx, -wpa, -wpa_key_mgmt, -wpa_oftags, -wpa_psks,
#   -broadcast, -dhcpd, -if_type, -inet_addr, -inet_enabled, -ip_assign_scheme,
#   -mtu, -NAT, -netmask, -network, -network_if_name, -perform_network_config,
#   -perform_cac
# RETURNS:
#   0   On success.
# USAGE EXAMPLE(S):
#   create_radio_vif_interface -channel 1 \
#       -if_name wifi0 \
#       -vif_if_name home-ap-24 \
###############################################################################
create_radio_vif_interface()
{
    vif_args_c=""
    vif_args_w=""
    radio_args=""
    replace="func_arg"
    channel_change_timeout=""
    perform_cac="false"
    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -ht_mode)
                radio_ht_mode="$replace ${option#?} ${1}"
                shift
                ;;
            -channel_mode | \
            -tx_power | \
            -tx_chainmask)
                radio_args="$radio_args $replace ${option#?} ${1}"
                shift
                ;;
            -vif_radio_idx | \
            -ssid_broadcast | \
            -parent | \
            -mac_list_type | \
            -bridge | \
            -vlan_id | \
            -radius_srv_secret | \
            -radius_srv_addr)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -mac_list)
                vif_args_c="${vif_args_c} ${replace} mac_list $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} mac_list $(single_quote_arg "$1")"
                shift
                ;;
            -credential_configs)
                vif_args_c="${vif_args_c} ${replace} credential_configs $(single_quote_arg "$1")"
                shift
                ;;
            -ssid)
                vif_args_c="${vif_args_c} ${replace} ssid $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ssid $(single_quote_arg "$1")"
                shift
                ;;
            -ap_bridge)
                vif_args_c="$vif_args_c $replace ap_bridge $1"
                vif_args_w="$vif_args_w $replace ap_bridge $1"
                shift
                ;;
            -wpa_oftags)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -wpa | \
            -wpa_key_mgmt | \
            -wpa_psks)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -mode)
                vif_args_c="$vif_args_c $replace mode $1"
                vif_args_w="$vif_args_w $replace mode $1"
                mode=$1
                shift
                ;;
            -multi_ap)
                vif_args_c="$vif_args_c $replace multi_ap $1"
                vif_args_w="$vif_args_w $replace multi_ap $1"
                shift
                ;;
            -enabled)
                radio_args="$radio_args $replace enabled $1"
                vif_args_c="$vif_args_c $replace enabled $1"
                vif_args_w="$vif_args_w $replace enabled $1"
                shift
                ;;
            -country)
                radio_args="$radio_args $replace country $1"
                country_arg="$replace country $1"
                shift
                ;;
            -hw_mode)
                radio_args="$radio_args $replace hw_mode $1"
                shift
                ;;
            -channel)
                radio_args="$radio_args $replace channel $1"
                vif_args_w="$vif_args_w $replace channel $1"
                channel=$1
                shift
                ;;
            -radio_if_name)
                radio_args="$radio_args $replace if_name $1"
                radio_if_name=$1
                shift
                ;;
            -vif_if_name)
                vif_args_c="$vif_args_c $replace if_name $1"
                vif_args_w="$vif_args_w $replace if_name $1"
                vif_if_name=$1
                shift
                ;;
            -timeout)
                channel_change_timeout="-t ${1}"
                shift
                ;;
            -perform_cac)
                perform_cac=${1}
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:create_radio_vif_interface" -arg
                ;;
        esac
    done

    # Mandatory parameters
    [ -z "${radio_if_name}" ] &&
        raise "'radio_if_name' argument empty" -l "unit_lib:create_radio_vif_interface" -arg
    [ -z "${vif_if_name}" ] &&
        raise "'vif_if_name' argument empty" -l "unit_lib:create_radio_vif_interface" -arg
    [ -z "${channel}" ] &&
        raise "'channel' argument empty" -l "unit_lib:create_radio_vif_interface" -arg

    # Only check if channel is allowed, need not be ready for immediate use
    check_is_channel_allowed "$channel" "$radio_if_name" &&
        log -deb "unit_lib:create_radio_vif_interface - Channel '$channel' is allowed on interface '$radio_if_name'" ||
        raise "Channel '$channel' is not allowed on interface '$radio_if_name'" -l "unit_lib:create_radio_vif_interface" -ds

    log -deb "unit_lib:create_radio_vif_interface - Bringing up radio/VIF interface"

    func_params="${radio_args//$replace/-u} ${radio_ht_mode//$replace/-u}"
    # shellcheck disable=SC2086
    update_ovsdb_entry Wifi_Radio_Config -w if_name "$radio_if_name" $func_params &&
        log -deb "unit_lib:create_radio_vif_interface - Table Wifi_Radio_Config updated - Success" ||
        raise "Could not update Wifi_Radio_Config table" -l "unit_lib:create_radio_vif_interface" -tc

    if [ "$mode" = "sta" ]; then
        remove_sta_connections "$vif_if_name"
    fi

    function_to_call="insert_ovsdb_entry"
    function_arg="-i"

    ${OVSH} s Wifi_VIF_Config -w if_name=="$vif_if_name" &&
        update=0 ||
        update=1
    if [ "$update" -eq 0 ]; then
        log -deb "unit_lib:create_radio_vif_interface - VIF entry exists, updating Wifi_VIF_Config instead of inserting"
        function_to_call="update_ovsdb_entry"
        function_arg="-u"
    fi

    func_params=${vif_args_c//$replace/$function_arg}
    # shellcheck disable=SC2086
    eval $function_to_call Wifi_VIF_Config -w if_name "$vif_if_name" $func_params &&
        log -deb "unit_lib:create_radio_vif_interface - $function_to_call Wifi_VIF_Config - Success" ||
        raise "Could not $function_to_call to Wifi_VIF_Config" -l "unit_lib:create_radio_vif_interface" -fc

    # Associate VIF and radio interfaces
    uuids=$(get_ovsdb_entry_value Wifi_VIF_Config _uuid -w if_name "$vif_if_name") ||
        raise "Could not get _uuid for '$vif_if_name' from Wifi_VIF_Config: get_ovsdb_entry_value" -l "unit_lib:create_radio_vif_interface" -fc

    vif_configs_set="[\"set\",[[\"uuid\",\"$uuids\"]]]"

    func_params=${radio_args//$replace/-u}
    # shellcheck disable=SC2086
    update_ovsdb_entry Wifi_Radio_Config -w if_name "$radio_if_name" $func_params &&
            log -deb "unit_lib:create_radio_vif_interface - Table Wifi_Radio_Config updated - Success" ||
            raise "Could not update table Wifi_Radio_Config" -l "unit_lib:create_radio_vif_interface" -fc

    ${OVSH} u Wifi_Radio_Config -w if_name=="$radio_if_name" vif_configs:ins:"$vif_configs_set" &&
            log -deb "unit_lib:create_radio_vif_interface - Table Wifi_Radio_Config vif_configs updated - Success" ||
            raise "Could not update table Wifi_Radio_Config vif_configs" -l "unit_lib:create_radio_vif_interface" -fc

    # shellcheck disable=SC2086
    func_params=${vif_args_w//$replace/-is}
    eval wait_ovsdb_entry Wifi_VIF_State -w if_name "$vif_if_name" $func_params ${channel_change_timeout} &&
        log -deb "unit_lib:create_radio_vif_interface - Wifi_VIF_Config reflected to Wifi_VIF_State - Success" ||
        raise "Could not reflect Wifi_VIF_Config to Wifi_VIF_State" -l "unit_lib:create_radio_vif_interface" -fc

    if [ "$mode" = "sta" ]; then
        wait_for_function_response "notempty" "get_ovsdb_entry_value Wifi_VIF_State parent -w if_name $vif_if_name" &&
            parent_mac=0 ||
            parent_mac=1
        if [ "$parent_mac" -eq 0 ]; then
            parent_mac=$(get_ovsdb_entry_value Wifi_VIF_State parent -w if_name "$vif_if_name")
            update_ovsdb_entry Wifi_VIF_Config -w if_name "$vif_if_name" \
                -u parent "$parent_mac" &&
                    log -deb "unit_lib:create_radio_vif_interface - VIF_State parent was associated" ||
                    log -deb "unit_lib:create_radio_vif_interface - VIF_State parent was not associated"
        fi
    fi

    if [ -n "$country_arg" ]; then
        radio_args=${radio_args//$country_arg/""}
    fi

    func_params="${radio_args//$replace/-is} ${radio_ht_mode//$replace/-is}"

    if [ "$mode" = "sta" ]; then
        func_params="${radio_args//$replace/-is}"
    fi
    # Check nop_started
    channel_status="$(get_radio_channel_state "${channel}" "${if_name}")"
    if [ "${channel_status}" == "nop_started" ]; then
        raise "SKIP: Channel ${check_channel} NOP time started, channel  unavailable" -l "unit_lib:create_radio_vif_interface" -s
    fi
    # shellcheck disable=SC2086
    wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" $func_params ${channel_change_timeout} &&
      if_created="true" ||
      if_created="false"

    if [ "${if_created}" == "true" ]; then
        log -deb "unit_lib:create_radio_vif_interface - Wifi_Radio_Config reflected to Wifi_Radio_State - Success"
    else
        channel_status="$(get_radio_channel_state "${channel}" "${radio_if_name}")"
        if [ "${channel_status}" == "nop_started" ]; then
            raise "SKIP: Channel ${check_channel} NOP time started, channel  unavailable" -l "unit_lib:create_radio_vif_interface" -s
        fi
        raise "Could not reflect Wifi_Radio_Config to Wifi_Radio_State" -l "unit_lib:create_radio_vif_interface" -fc
    fi
    if [ "${perform_cac}" == "true" ]; then
        # Even if the channel is set in Wifi_Radio_State, it is not
        # necessarily available for immediate use if CAC is in progress.
        validate_cac "${radio_if_name}" &&
            log "unit_lib:create_radio_vif_interface - CAC time elapsed or not needed" ||
            raise "CAC failed. Channel is not usable" -l "unit_lib:create_radio_vif_interface" -ds
    else
        log -deb "unit_lib:create_radio_vif_interface - CAC explicitly disabled"
    fi

    log -deb "unit_lib:create_radio_vif_interface - Wireless interface created"
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function creates VIF interface.
#   Raises exception on fail.
# INPUT PARAMETER(S):
#   ...
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
# Backhaul configuration on root node:
#   create_vif_interface \
#   -radio_if_name wifi1 \
#   -if_name bhaul-ap-l50 \
#   -mac_list '["set",["aa:bb:cc:dd:ee:ff"]]' \
#   -mac_list_type whitelist \
#   -mode ap \
#   -ssid bhaul_ssid \
#   -ssid_broadcast "disabled" \
#   -vif_radio_idx 1 \
#   -enabled true
# Wifi Security arguments(choose one or the other):
#   If 'wifi_security_type' == 'wpa' (preferred)
#   -wifi_security_type wpa \
#   -wpa "true" \
#   -wpa_key_mgmt "wpa-psk" \
#   -wpa_psks '["map",[["key","FutTestPSK"]]]' \
#   -wpa_oftags '["map",[["key","home--1"]]]' \
#   (OR)
#   If 'wifi_security_type' == 'legacy' (deprecated)
#   -wifi_security_type legacy \
#   -security '["map",[["encryption","WPA-PSK"],["key","PSK"],["mode","2"]]]' \
# Backhaul configuration on leaf node:
#   create_vif_interface \
#   -if_name bhaul-sta-l50 \
#   -wifi_security_type legacy \
#   -ssid bhaul_ssid
# Wifi Security arguments(choose one or the other):
#   If 'wifi_security_type' == 'wpa' (preferred)
#   -wifi_security_type wpa \
#   -wpa "true" \
#   -wpa_key_mgmt "wpa-psk" \
#   -wpa_psks '["map",[["key","FutTestPSK"]]]' \
#   -wpa_oftags '["map",[["key","home--1"]]]' \
#   (OR)
#   If 'wifi_security_type' == 'legacy' (deprecated)
#   -wifi_security_type legacy \
#   -security '["map",[["encryption","WPA-PSK"],["key","PSK"],["mode","2"]]]' \
###############################################################################
create_vif_interface()
{
    vif_args_c=""
    vif_args_w=""
    replace="func_arg"

    while [ -n "${1}" ]; do
        option=${1}
        shift
        case "${option}" in
            -radio_if_name)
                radio_if_name=${1}
                shift
                ;;
            -if_name)
                vif_if_name=${1}
                vif_args_c="${vif_args_c} ${replace} ${option#?} ${1}"
                vif_args_w="${vif_args_w} ${replace} ${option#?} ${1}"
                shift
                ;;
            -ap_bridge | \
            -bridge | \
            -dynamic_beacon | \
            -mac_list_type | \
            -mac_list | \
            -parent | \
            -ssid_broadcast | \
            -vif_radio_idx | \
            -vlan_id)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -wifi_security_type)
                wifi_security_type=${1}
                shift
                ;;
            -wpa_oftags)
                [ "${wifi_security_type}" != "wpa" ] && raise "Incorrect combination of WPA and legacy wifi security type provided" -l "unit_lib:create_vif_interface" -arg
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -wpa | \
            -wpa_key_mgmt | \
            -wpa_psks)
                [ "${wifi_security_type}" != "wpa" ] && raise "Incorrect combination of WPA and legacy wifi security type provided" -l "unit_lib:create_vif_interface" -arg
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -security)
                [ "${wifi_security_type}" != "legacy" ] && raise "Incorrect combination of WPA and legacy wifi security type provided" -l "unit_lib:create_vif_interface" -arg
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -enabled)
                vif_args_c="${vif_args_c} ${replace} ${option#?} ${1}"
                vif_args_w="${vif_args_w} ${replace} ${option#?} ${1}"
                shift
                ;;
            -ssid)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                vif_args_w="${vif_args_w} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            -mode)
                mode=${1}
                vif_args_c="${vif_args_c} ${replace} ${option#?} ${1}"
                vif_args_w="${vif_args_w} ${replace} ${option#?} ${1}"
                shift
                ;;
            -credential_configs)
                vif_args_c="${vif_args_c} ${replace} ${option#?} $(single_quote_arg "$1")"
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:create_vif_interface" -arg
                ;;
        esac
    done

    [ "$mode" = "sta" ] &&
        remove_sta_connections "$vif_if_name"

    [ -z "${vif_if_name}" ] &&
        raise "Interface name argument empty" -l "unit_lib:create_vif_interface" -arg

    # Check if entry for if_name already exists in Wifi_VIF_Config table
    # Update if entry exists, insert otherwise
    check_ovsdb_entry Wifi_VIF_Config -w if_name "${vif_if_name}"
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:create_vif_interface - Updating existing VIF entry"
        function_to_call="update_ovsdb_entry"
        function_arg="-u"
    else
        log -deb "unit_lib:create_vif_interface - Creating VIF entry"
        function_to_call="insert_ovsdb_entry"
        function_arg="-i"
    fi

    # Perform action update/insert VIF
    func_params=${vif_args_c//$replace/$function_arg}
    # shellcheck disable=SC2086
    eval $function_to_call Wifi_VIF_Config -w if_name "$vif_if_name" $func_params &&
        log -deb "unit_lib:create_vif_interface - $function_to_call Wifi_VIF_Config -w if_name $vif_if_name $func_params - Success" ||
        raise "$function_to_call Wifi_VIF_Config -w if_name $vif_if_name $func_params" -l "unit_lib:create_vif_interface" -fc

    # Mutate radio entry with VIF uuid
    if [ "${function_to_call}" == "insert_ovsdb_entry" ]; then
        vif_uuid=$(get_ovsdb_entry_value Wifi_VIF_Config _uuid -w if_name "$vif_if_name" ) ||
            raise "get_ovsdb_entry_value" -l "unit_lib:create_vif_interface" -fc
        ${OVSH} u Wifi_Radio_Config -w if_name=="${radio_if_name}" vif_configs:ins:'["set",[["uuid","'${vif_uuid//" "/}'"]]]'
    fi

    # Validate action insert/update VIF
    func_params=${vif_args_w//$replace/-is}
    # shellcheck disable=SC2086
    eval wait_ovsdb_entry Wifi_VIF_State -w if_name "$vif_if_name" $func_params &&
        log -deb "unit_lib:create_vif_interface - wait_ovsdb_entry Wifi_VIF_State -w if_name $vif_if_name $func_params - Success" ||
        raise "wait_ovsdb_entry Wifi_VIF_State -w if_name $vif_if_name $func_params" -l "unit_lib:create_vif_interface" -fc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function deletes entry values in Wifi_Inet_Config table.
#   It then waits for config to reflect in Wifi_Inet_State table.
#   It checks if configuration is reflected to system.
#   Raises exception if interface is not removed and then forces deletion.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   delete_inet_interface eth0
###############################################################################
delete_inet_interface()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:delete_inet_interface requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    log -deb "unit_lib:delete_inet_interface - Removing interface '$if_name'"

    remove_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" ||
        raise "Could not remove Wifi_Inet_Config::if_name" -l "unit_lib:delete_inet_interface" -fc

    wait_ovsdb_entry_remove Wifi_Inet_State -w if_name "$if_name" ||
        raise "Could not remove Wifi_Inet_State::if_name" -l "unit_lib:delete_inet_interface" -fc

    wait_for_function_response 1 "ip link show $if_name" &&
        log -deb "unit_lib:delete_inet_interface - LEVEL2: Interface $if_name removed - Success" ||
        raise "Interface $if_name still present on system" -l "unit_lib:delete_inet_interface" -ds

    log -deb "unit_lib:delete_inet_interface - Interface '$if_name' deleted from ovsdb and OS - LEVEL2"

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function initializes device for use in FUT.
#   It calls a function that instructs CM to prevent the device from rebooting.
#   Does not stop healthcheck service. Consider disabling the service in
#   platform or device overrides to prevent the device from rebooting.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   device_init
###############################################################################
device_init()
{
    disable_fatal_state &&
        log -deb "unit_lib:device_init - CM fatal state disabled - Success" ||
        raise "Could not disable CM fatal state" -l "unit_lib:device_init" -ds
}

###############################################################################
# DESCRIPTION:
#   Function prevents CM fatal state thus prevents restarting managers or
#   rebooting device. In normal operation CM would be constantly performing
#   connectivity tests to the Cloud and without connection it would perform
#   device reboot. In FUT environment device has no connection to the Cloud,
#   so restarts and reboots must be prevented. If device is missing the kconfig
#   option CONFIG_TARGET_PATH_DISABLE_FATAL_STATE, this function does nothing.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Last exit code of file creation, if file path is specified, 0 otherwise.
# DEPENDENCY:
# - Function is dependent on tool dirname, if file path is specified.
# USAGE EXAMPLE(S):
#   disable_fatal_state
###############################################################################
disable_fatal_state()
{
    check_kconfig_option_exists "CONFIG_TARGET_PATH_DISABLE_FATAL_STATE" || return 0

    log -deb "unit_lib:disable_fatal_state - Disabling CM manager restart procedure"

    is_tool_on_system dirname || raise "Tool dirname required on system" -l "unit_lib:disable_fatal_state" -ds
    fatal_state_inhibit_path=$(get_kconfig_option_value "CONFIG_TARGET_PATH_DISABLE_FATAL_STATE" | tr -d '"' "'")
    fatal_state_inhibit_dir=$(dirname "${fatal_state_inhibit_path:?}")

    if [ ! -d "${fatal_state_inhibit_dir:?}" ]; then
        mkdir -p "${fatal_state_inhibit_dir:?}"
    fi
    touch "${fatal_state_inhibit_path:?}"
    if [ $? != 0 ]; then
        log -deb "unit_lib:disable_fatal_state - ${fatal_state_inhibit_dir} is not writable, mount a tmpfs over it."
        mount -t tmpfs tmpfs "${fatal_state_inhibit_dir:?}"
        touch "${fatal_state_inhibit_path:?}"
    fi
}

###############################################################################
# DESCRIPTION:
#   Function ensures the logpull directory is empty.
###############################################################################
empty_logpull_dir()
{
    rm -rf /tmp/logpull/*
}

###############################################################################
# DESCRIPTION:
#   Function deletes all entries in ovsdb table.
#   Raises an exception if table entries cannot be deleted.
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   empty_ovsdb_table AW_Debug
#   empty_ovsdb_table Wifi_Stats_Config
###############################################################################
empty_ovsdb_table()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:empty_ovsdb_table requires ${NARGS} input argument(s), $# given" -arg
    ovsdb_table=$1

    log -deb "unit_lib:empty_ovsdb_table - Clearing $ovsdb_table table"
    ${OVSH} d "$ovsdb_table" ||
        raise "Could not delete table $ovsdb_table" -l "unit_lib:empty_ovsdb_table" -fc
}

###############################################################################
# DESCRIPTION:
#   Function deletes port forwarding on interface by force.
#   Uses iptables tool.
#   Raises exception.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
#   $2  table type in iptables list (string, required)
#   $3  IP:Port (string, required)
# RETURNS:
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   force_delete_ip_port_forward_raise bhaul-sta-24 <tabletype> 10.10.10.123:80
###############################################################################
force_delete_ip_port_forward_raise()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:force_delete_ip_port_forward_raise requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1
    ip_table_type=$2
    ip_port_forward_ip=$3

    log -deb "unit_lib:force_delete_ip_port_forward_raise - iptables not empty. Force delete"

    port_forward_line_number=$(iptables -t nat --list -v --line-number | tr -s ' ' | grep "$ip_table_type" | grep "$if_name" | grep  "$ip_port_forward_ip" | cut -d ' ' -f1)
    if [ -z "$port_forward_line_number" ]; then
        log -deb "unit_lib:force_delete_ip_port_forward_raise - Could not get iptables line number, skipping..."
        return 0
    fi

    wait_for_function_response 0 "iptables -t nat -D $ip_table_type $port_forward_line_number" &&
        raise "IP port forward forcefully removed from iptables" -l "unit_lib:force_delete_ip_port_forward_raise" -tc ||
        raise "Could not to remove IP port forward from iptables" -l "unit_lib:force_delete_ip_port_forward_raise" -tc
}

###############################################################################
# DESCRIPTION:
#   Function prints a line used as a separator in allure report.
# INPUT PARAMETER(S):
#   None
# RETURNS:
#   None
# USAGE EXAMPLE(S):
#   fut_info_dump_line
###############################################################################
fut_info_dump_line()
{
    echo "************* FUT-INFO-DUMP: $(basename $0) *************"
}

###############################################################################
# DESCRIPTION:
#   Function marks interface as no-flood.
#   So, only the traffic matching the flow filter will hit the plugin.
# INPUT PARAMETER(S):
#   $1 Bridge name (string, required)
#   $2 Interface name (string, required)
# RETURNS:
#   None.
# USAGE EXAMPLE(S):
#   gen_no_flood_cmd br-home br-home.tdns
###############################################################################
gen_no_flood_cmd()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:gen_no_flood_cmd requires ${NARGS} input arguments, $# given" -arg
    bridge=$1
    iface=$2

    log -deb "unit_lib:gen_no_flood_cmd: Mark interface '${iface}' as 'no-flood'"

    if linux_native_bridge_enabled; then
        ip link set "$iface" type bridge_slave flood "off"
    else
        ovs-ofctl mod-port "${bridge}" "${iface}" no-flood
    fi
}

###############################################################################
# DESCRIPTION:
#   Function echoes chainmask of the radio.
#   This function actually echoes chainmask without performing
#   any action on the received value. An override function can
#   be implemented for any target to change this behavior.
# INPUT PARAMETER(S):
#   $1  Chainmask of the radio (int, required)
#   $2  Frequency band of the radio (string, required)
# RETURNS:
#   Transformed/actual chainmask of the radio.
# USAGE EXAMPLE(S):
#   get_actual_chainmask 15 5GU
###############################################################################
get_actual_chainmask()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_actual_chainmask requires ${NARGS} input argument(s), $# given" -arg
    chainmask=${1}
    freq_band=${2}

    echo "${chainmask}"
}

###############################################################################
# DESCRIPTION:
#   Function echoes allowed channels for an interface.
# INPUT PARAMETER(S):
#   $1  Chainmask of the radio (int, required)
#   $2  Frequency band of the radio (string, required)
# RETURNS:
#   Allowed channels for the interface.
# USAGE EXAMPLE(S):
#   get_actual_chainmask 15 5GU
###############################################################################
get_allowed_channels_for_interface()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:check_is_channel_allowed requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    allowed_channels=$(get_ovsdb_entry_value Wifi_Radio_State allowed_channels -w if_name "$if_name" -r)
    channels=$(echo ${allowed_channels} | sed 's/\[/ /g; s/\]/ /g; s/,/ /g;')
    clear_channels=${channels/\"set\"/}
    echo ${clear_channels}
}

###############################################################################
# DESCRIPTION:
#   Function returns IP address of leaf device based on LEAF MAC address.
#   Uses /tmp/dhcp.leases file as default for acquirement of leased LEAF IP address.
#   Provide adequate function in overrides otherwise.
# INPUT PARAMETER(S):
#   $1  leaf MAC address (string, required)
# RETURNS:
#   IP address of associated leaf device
# USAGE EXAMPLE(S):
#   get_associated_leaf_ip ff:ff:ff:ff:ff:ff
###############################################################################
get_associated_leaf_ip()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_associated_leaf_ip requires ${NARGS} input argument(s), $# given" -arg

    cat /tmp/dhcp.leases | grep "${1}" | awk '{print $3}'
}

###############################################################################
# DESCRIPTION:
#   Function returns the element in the list designated by the provided index.
#   This is needed as all devices are not guaranteed to support indexed arrays.
# INPUT PARAMETER(S):
#   $1  index in the list from which to retrieve the value
#   $@  the values consisting the list from which to retrieve the value
# RETURNS:
#   0   The value is retrieved
#   1   The value is not retrieved
# USAGE EXAMPLE(S):
#   get_by_index_from_list 2 foo bar baz
###############################################################################
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

###############################################################################
# DESCRIPTION:
#   Function returns channel set at OS - LEVEL2.
# STUB:
#   This function is a stub. It always raises an exception and needs
#   a function with the same name and usage in platform or device overrides.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
# RETURNS:
#   Echoes channel set for interface
# USAGE EXAMPLE(S):
#   get_channel_from_os home-ap-24
###############################################################################
get_channel_from_os()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_channel_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1

    log "unit_lib:get_channel_from_os - Getting channel from OS - LEVEL2"
    # Provide override in platform specific file
    raise "This is a stub function. Override implementation needed." -l "unit_lib:get_channel_from_os" -fc
}

get_channels_to_check_for_cac()
{
    # First validate presence of regulatory.txt file
    regulatory_file_path="${FUT_TOPDIR}/shell/config/regulatory.txt"
    if [ ! -f "${regulatory_file_path}" ]; then
        log -deb "unit_lib:get_channels_to_check_for_cac - Regulatory file ${regulatory_file_path} does not exist, nothing to do."
        return 0
    fi

    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_channels_to_check_for_cac requires ${NARGS} input argument(s), $# given" -arg
    # shellcheck disable=SC2034
    if_name="${1}"

    # Check if channel is set in Wifi_Radio_State
    state_channel=$(get_ovsdb_entry_value Wifi_Radio_State channel -w if_name "${if_name}")
    if [ "${state_channel}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:get_channels_to_check_for_cac - Channel is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi
    state_ht_mode=$(get_ovsdb_entry_value Wifi_Radio_State ht_mode -w if_name "${if_name}")
    if [ "${state_ht_mode}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:get_channels_to_check_for_cac - ht_mode is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi
    state_freq_band=$(get_ovsdb_entry_value Wifi_Radio_State freq_band -w if_name "${if_name}" | tr '[A-Z]' '[a-z]' | tr -d '.')
    if [ "${state_freq_band}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:get_channels_to_check_for_cac - freq_band is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi

    # Retrieve device regulatory domain
    state_country=$(get_iface_regulatory_domain "${if_name}")
    echo "${state_country}"
    state_country=$(echo "${state_country}" | tail -1)

    log -deb "unit_lib:get_channels_to_check_for_cac - Acquiring channels to validate CAC for ${state_channel} in range of ${state_ht_mode}"
    channels_to_check=""
    lower_limit="0"
    upper_limit="300"
    # If HT20, we do not need to wait for any other channel except the one given
    if [ "${state_ht_mode}" == "HT20" ]; then
        channels_to_check="${state_channel}"
    else
        # Retrieve channel placement for given channel width
        lower_placement_match=$(cat "${regulatory_file_path}" | grep -i "CHAN_PLACE_${state_freq_band}_${state_ht_mode}_LOWER")
        check_is_lower=$(contains_element "${state_channel}" ${lower_placement_match})
        upper_placement_match=$(cat "${regulatory_file_path}" | grep -i "CHAN_PLACE_${state_freq_band}_${state_ht_mode}_UPPER")
        check_is_upper=$(contains_element "${state_channel}" ${upper_placement_match})
        if [ "${check_is_lower}" == "0" ]; then
            chan_placement="LOWER"
            chan_placement_invert="UPPER"
        elif [ "${check_is_upper}" == "0" ]; then
            chan_placement="UPPER"
            chan_placement_invert="LOWER"
        else
            chan_placement="MIDDLE"
        fi
        log -deb "unit_lib:get_channels_to_check_for_cac - Channel ${state_channel} placement in range ${state_ht_mode} is ${chan_placement}"
        if [ "${chan_placement}" != "MIDDLE" ]; then
            chan_placement_match=$(cat "${regulatory_file_path}" | grep -i "CHAN_PLACE_${state_freq_band}_${state_ht_mode}_${chan_placement}")
            placement_index=$(get_index_in_list "${state_channel}" ${chan_placement_match})
            if [ "$?" != "0" ]; then
                raise "Failed to retrieve placement of ${state_channel} in ${chan_placement_match}" -l "unit_lib:get_channels_to_check_for_cac" -tc
            fi
            log -deb "unit_lib:get_channels_to_check_for_cac - Placement index is ${placement_index} of ${state_channel} in ${chan_placement_match}"
            chan_placement_match_invert=$(cat "${regulatory_file_path}" | grep -i "CHAN_PLACE_${state_freq_band}_${state_ht_mode}_${chan_placement_invert}")
            invert_channel=$(get_by_index_from_list "${placement_index}" ${chan_placement_match_invert})
            if [ "$?" != "0" ]; then
                raise "Failed to retrieve invert placement of ${placement_index} in ${chan_placement_match_invert}" -l "unit_lib:get_channels_to_check_for_cac" -tc
            fi
            log -deb "unit_lib:get_channels_to_check_for_cac - Channel ${state_channel} invert ${chan_placement_invert} channel is ${invert_channel}"
        fi
        # If channel placement is LOWER, we need to traverse all channels until first UPPER channel for given HT range
        if [ "${chan_placement}" == "LOWER" ]; then
            channels_to_check="${state_channel}"
            next_channel="${state_channel}"
            while [ "${next_channel}" != "${invert_channel}" ] && [ "${next_channel}" -lt "${upper_limit}" ]; do
                next_channel=$((next_channel + 4))
                channels_to_check="${channels_to_check} ${next_channel}"
            done
        # If channel placement is UPPER, we need to traverse all channels until first LOWER channel for given HT range
        elif [ "${chan_placement}" == "UPPER" ]; then
            prev_channel="${state_channel}"
            while [ "${prev_channel}" != "${invert_channel}" ] && [ "${prev_channel}" -gt "${lower_limit}" ]; do
                prev_channel=$((prev_channel - 4))
                channels_to_check="${channels_to_check} ${prev_channel}"
            done
            channels_to_check="${channels_to_check} ${state_channel}"
        else
            # Channel placement is in the MIDDLE of the range
            # We need to acquire previous lower channels, and next upper channels
            # For example, in HT80 channel 108 is in the middle, his LOWER channel is 100, and his upper channel is 112
            # We need to get all channels, since we are in the MIDDLE of the range, we will first find range LOWER channel
            # And traverse to range UPPER channel - identical as in chan_placement==LOWER condition
            chan_placement_match=$(cat "${regulatory_file_path}" | grep -i "CHAN_PLACE_${state_freq_band}_${state_ht_mode}_LOWER")
            chan_placement_match_invert=$(cat "${regulatory_file_path}" | grep -i "CHAN_PLACE_${state_freq_band}_${state_ht_mode}_UPPER")
            for check_channel in ${chan_placement_match}; do
                lower_channel="${state_channel}"
                # Only channels lower than the current state channel can be their lower channel
                if [ "${check_channel}" -lt "${state_channel}" ]; then
                    chan_num_in_range="1"
                    case ${state_ht_mode} in
                        "HT40")
                            chan_num_in_range="1 2"
                            ;;
                        "HT80")
                            chan_num_in_range="1 2 3 4"
                            ;;
                        "HT160")
                            chan_num_in_range="1 2 3 4 5 6 7 8"
                            ;;
                    esac
                    for i in ${chan_num_in_range}; do
                        lower_channel=$((lower_channel - 4))
                        [ "${check_channel}" == "${lower_channel}" ] && break
                    done
                    [ "${check_channel}" == "${lower_channel}" ] && break
                fi
            done
            log -deb "unit_lib::get_channels_to_check_for_cac - Lower channel for ${state_channel} in ${state_ht_mode} is ${lower_channel}"
            lower_placement_index=$(get_index_in_list "${lower_channel}" ${chan_placement_match})
            if [ "$?" != "0" ]; then
                raise "Failed to retrieve lower placement of ${lower_channel} in ${chan_placement_match}" -l "unit_lib:get_channels_to_check_for_cac" -tc
            fi
            upper_channel=$(get_by_index_from_list "${lower_placement_index}" ${chan_placement_match_invert})
            log -deb "unit_lib::get_channels_to_check_for_cac - Upper channel for ${state_channel} in ${state_ht_mode} is ${upper_channel}"
            channels_to_check="${lower_channel}"
            next_channel="${lower_channel}"
            while [ "${next_channel}" != "${upper_channel}" ] && [ "${next_channel}" -lt "${upper_limit}" ]; do
                next_channel=$((next_channel + 4))
                channels_to_check="${channels_to_check} ${next_channel}"
            done
        fi
    fi
    echo "${channels_to_check}"
}

###############################################################################
# DESCRIPTION:
#   Function returns HT mode set at OS - LEVEL2.
# STUB:
#   This function is a stub. It always raises an exception and needs
#   a function with the same name and usage in platform or device overrides.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
#   $2  channel (int, not used, but still required, do not optimize)
# RETURNS:
#   Echoes HT mode set for interface
# USAGE EXAMPLE(S):
#   get_ht_mode_from_os home-ap-24 1
###############################################################################
get_ht_mode_from_os()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_ht_mode_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1
    channel=$2

    log "unit_lib:check_ht_mode_at_os_level - Getting HT mode for channel '$channel' at OS - LEVEL2"
    # Provide override in platform specific file
    raise "This is a stub function. Override implementation needed." -l "unit_lib:get_ht_mode_from_os" -fc
}

###############################################################################
# DESCRIPTION:
#   Function retrieves regulatory domain of radio interface.
# INPUT PARAMETER(S):
#   $1  Radio interface name  (string, required)
# RETURNS:
#   Radio interface regulatory domain - defaults to US
# NOTE:
#   Function first checks Wifi_Radio_State interface 'country' field, if not
#   populated checks Wifi_Radio_State 'hw_params' and looks for 'reg_domain'
# USAGE EXAMPLE(S):
#   get_iface_regulatory_domain wifi0
###############################################################################
get_iface_regulatory_domain()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_iface_regulatory_domain requires ${NARGS} input argument(s), $# given" -arg
    if_name="${1}"

    country_found=1
    country=$(get_ovsdb_entry_value Wifi_Radio_State country -w if_name "${if_name}")
    if [ "${country}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:get_iface_regulatory_domain - Country is not set in Wifi_Radio_State."
        hw_params_reg_domain=$(get_ovsdb_entry_value Wifi_Radio_State hw_params -w if_name "${if_name}" -json_value reg_domain)
        log -deb "unit_lib:get_iface_regulatory_domain - Trying to acquire country region trough hw_params: ${hw_params_reg_domain}"
        # 58 (3a hex) US | 55 (37 hex) EU
        if [ ${?} == 0 ]; then
            if [ ${hw_params_reg_domain} == '"58"' ]; then
                country='US'
            elif [ ${hw_params_reg_domain} == '"55"' ]; then
                country='EU'
            else
                log -deb "unit_lib:get_iface_regulatory_domain - Failed to retrieve device regulatory domain. Defaulting to US regulatory rules!"
                country='US'
            fi
        else
            log -deb "unit_lib:get_iface_regulatory_domain - Failed to retrieve device regulatory domain. Defaulting to US regulatory rules!"
            country='US'
        fi
        country_found=0
    else
        country_found=0
    fi
    if [ "${country_found}" == 1 ]; then
        log -deb "unit_lib:get_iface_regulatory_domain - Failed to retrieve device regulatory domain. Defaulting to US regulatory rules!"
        country='US'
    fi
    echo "${country}"
}

###############################################################################
# DESCRIPTION:
#   Function echoes the index of the value in the list.
# INPUT PARAMETER(S):
#   $1  Value to look for in the list
#   $@  the values consisting the list from which to retrieve the index
# RETURNS:
#   0   Value is found in the list and the index provided
#   1   Value is not found in the list
# USAGE EXAMPLE(S):
#   get_index_in_list baz foo bar baz
###############################################################################
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

###############################################################################
# DESCRIPTION:
#   Function echoes kconfig value from ${OPENSYNC_ROOTDIR}/etc/kconfig which matches value name
#   Raises an exception if kconfig field is missing from given path.
# INPUT PARAMETER(S):
#   $1  kconfig option name (string, required)
# RETURNS:
#   None.
#   See description
# NOTE:
#   If the value of the kconfig option has quotes, this will not remove them.
# USAGE EXAMPLE(S):
#   get_kconfig_option_value "CONFIG_PM_ENABLE_LED" <- return y or n
###############################################################################
get_kconfig_option_value()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_kconfig_option_value requires ${NARGS} input argument(s), $# given" -arg
    kconfig_option_name=${1}

    kconfig_path="${OPENSYNC_ROOTDIR}/etc/kconfig"
    if ! [ -f "${kconfig_path}" ]; then
        raise "kconfig file is not present on ${kconfig_path}" -l "unit_lib:get_kconfig_option_value" -ds
    fi
    cat "${kconfig_path}" | grep "${kconfig_option_name}" |  cut -d "=" -f2
}

###############################################################################
# DESCRIPTION:
#   Function echoes locationId from AWLAN_Node mqtt_headers field
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   get_location_id
###############################################################################
get_location_id()
{
    ${OVSH} s AWLAN_Node mqtt_headers |
        awk -F'"' '{for (i=1;i<NF;i++) {if ($(i)=="locationId"){print $(i+2)}}}'
}

###############################################################################
# DESCRIPTION:
#  Function returns interface MAC address at OS - LEVEL2.
# INPUT PARAMETER(S):
#  $1  VIF interface name (string, required)
# RETURNS:
#  Echoes MAC address for interface
# USAGE EXAMPLE(S):
#   get_mac_from_os wifi0
###############################################################################
get_mac_from_os()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_mac_from_os requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    mac_address=$(ip -o link show dev "$if_name" | awk '{print $(NF-2)}')
    echo "$mac_address"
}

###############################################################################
# DESCRIPTION:
#   Function returns path to the script manipulating OpenSync managers.
#   Function assumes one of the two manager scripts exist on system;
#       - opensync
#       - manager
#   Raises exception if manager script does not exist.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Echoes path to manager script.
# USAGE EXAMPLE(S):
#   get_managers_script
###############################################################################
get_managers_script()
{
    if [ -e /etc/init.d/opensync ]; then
        echo "/etc/init.d/opensync"
    elif [ -e /etc/init.d/manager ]; then
        echo "/etc/init.d/manager"
    else
        raise "Missing the script to start OS managers" -l "unit_lib:get_managers_script" -ds
    fi
}

###############################################################################
# DESCRIPTION:
#   Function echoes nodeId from AWLAN_Node mqtt_headers field
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   get_node_id
###############################################################################
get_node_id()
{
    ${OVSH} s AWLAN_Node mqtt_headers |
        awk -F'"' '{for (i=1;i<NF;i++) {if ($(i)=="nodeId"){print $(i+2)}}}'
}

###############################################################################
# DESCRIPTION:
#   Function echoes number of radio interfaces present in Wifi_Radio_State table.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Echoes number of radios.
# USAGE EXAMPLE(S):
#   get_number_of_radios
###############################################################################
get_number_of_radios()
{
    num=$(${OVSH} s Wifi_Radio_State if_name -r | wc -l)
    echo "$num"
}

###############################################################################
# DESCRIPTION:
#   Function returns filename of the script manipulating openvswitch.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Echoes path to openvswitch script.
# USAGE EXAMPLE(S):
#   get_openvswitch_script
###############################################################################
get_openvswitch_script()
{
    echo "/etc/init.d/openvswitch"
}

###############################################################################
# DESCRIPTION:
#   Function echoes current ovs version.
#   Raises an exception if cannot obtain actual ovs version.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Echoes ovs version.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   get_ovs_version
###############################################################################
get_ovs_version()
{
    local OVS_NAME="ovs-vswitchd"
    local OVS_CMD

    OVS_CMD=$(command -v $OVS_NAME)
    # try which if command utility is not available
    [ -z "${OVS_CMD}" ] &&
        OVS_CMD=$(which $OVS_NAME)
    [ -z "${OVS_CMD}" ] &&
        raise "Can not call ${OVS_NAME}" -l "unit_lib:get_ovs_version" -fc

    OVS_ACTUAL_VER=$(${OVS_CMD} -V | head -n1 | cut -d' ' -f4)
    ec=$?
    [ ${ec} -ne 0 ] &&
        raise "Error calling ${OVS_CMD}" -l "unit_lib:get_ovs_version" -ec ${ec} -fc
    [ -z "${OVS_ACTUAL_VER}" ] &&
        raise "Could not get ovs version" -l "unit_lib:get_ovs_version" -tc

    echo "${OVS_ACTUAL_VER}"
}

###############################################################################
# DESCRIPTION:
#   Function echoes field value from ovsdb table.
#   It can be used with supported option(s):
#   -w (where)  field value used as a condition to select ovsdb table column
#
#   If -w option is used then two additional parameters must follow to
#   define condition string. Several -w options are possible, but for any
#   additional -w option used, there must always be 2 additional parameters.
#   In short, optional parameters come in groups of 3.
#
#   -r (raw)    output value is echoed without formatting
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  ovsdb field in ovsdb table (string, required)
#   $3  option, supported options: -w, -raw (string, optional, see DESCRIPTION)
#   $4  ovsdb field in ovsdb table (string, optional, see DESCRIPTION)
#   $5  ovsdb field value (string, optional, see DESCRIPTION)
#   ...
# RETURNS:
#   Echoes field value.
# USAGE EXAMPLE(S):
#   get_ovsdb_entry_value AWLAN_Node firmware_version
#   get_ovsdb_entry_value Manager target -r
###############################################################################
get_ovsdb_entry_value()
{
    ovsdb_table=$1
    ovsdb_field=$2
    shift 2
    conditions_string=""
    raw="false"
    json_value="false"

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -w)
                conditions_string="$conditions_string -w $1==$2"
                shift 2
                ;;
            -r)
                raw="true"
                shift
                ;;
            -json_value)
                json_value=$1
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:get_ovsdb_entry_value" -arg
                ;;
        esac
    done

    # shellcheck disable=SC2086
    if [ "$json_value" == "false" ]; then
        raw_field_value=$(${OVSH} s "$ovsdb_table" $conditions_string "$ovsdb_field" -r) ||
            return 1
    else
        raw_field_value=$(${OVSH} s "$ovsdb_table" $conditions_string "$ovsdb_field" -j) ||
            return 1
    fi

    echo "$raw_field_value" | grep -q '"uuid"'
    uuid_check_res="$?"
    if [ "$json_value" == "false" ] && [ "$raw" == "false" ] && [ "$uuid_check_res" == "0" ]; then
        value=$(echo "$raw_field_value" | cut -d ',' -f 2 | cut -d '"' -f 2)
    elif [ "$json_value" != "false" ]; then
        value=$(echo "$raw_field_value" | sed -n "/${json_value}/{n;p;}")
        if [ ${?} != 0 ]; then
            value=$(echo "$raw_field_value" | awk "/${json_value}/{getline; print}")
        fi
        # Remove leading whitespaces from json output
        value=$(echo "${value}" | sed 's/^ *//g')
    else
        value="$raw_field_value"
    fi

    echo -n "$value"
}

###############################################################################
# DESCRIPTION:
#   Function echoes PID of provided process.
# INPUT PARAMETER(S):
#   $1 process name (string, required)
# RETURNS:
#   PID value.
# USAGE EXAMPLE(S):
#   get_pid "healthcheck"
###############################################################################
get_pid()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_pid requires ${NARGS} input argument(s), $# given" -arg
    process_name=$1

    # Match parameter string, but exclude lines containing 'grep'.
    PID=$($(get_process_cmd) | grep -e "$process_name" | grep -v 'grep' | awk '{ print $1 }')
    echo "$PID"
}

###############################################################################
# DESCRIPTION:
#   Function echoes processes print-out in wide format.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Echoes list of processes.
# USAGE EXAMPLE(S):
#   get_process_cmd
###############################################################################
get_process_cmd()
{
    echo "ps -w"
}

###############################################################################
# DESCRIPTION:
#   Function echoes the radio channel state description in channels field of
#   table Wifi_Radio_State.
# INPUT PARAMETER(S):
#   $1  Channel (int, required)
#   $2  Radio interface name (string, required)
# RETURNS:
#   0   A valid channel state was echoed to stdout.
#   1   Channel is not allowed or state is not recognized.
# ECHOES:
#   (on return 0):
#   "allowed"       : non-dfs channel
#   "nop_finished"  : dfs channel, requires cac finished before usable
#   "cac_completed" : dfs channel, cac completed, usable
#   "nop_started"   : dfs channel, radar was detected and it must not be used
# USAGE EXAMPLE(S):
#   ch_state=$(get_radio_channel_state 2 wifi0)
###############################################################################
get_radio_channel_state()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_radio_channel_state requires ${NARGS} input argument(s), $# given" -arg
    channel=$1
    if_name=$2

    # Ensure channel is allowed.
    # Redirect output to ensure clean echo to stdout
    check_is_channel_allowed "$channel" "$if_name" >/dev/null 2>&1 ||
        return 1

    state_raw=$(get_ovsdb_entry_value Wifi_Radio_State channels -w if_name "$if_name" -r | tr ']' '\n' | grep "$channel")
    state="$(echo "${state_raw##*state}" | tr -d ' \":}' | tr -d ' ')"
    if [ "$state" == "allowed" ]; then
        echo "allowed"
    elif [ "$state" == "nop_finished" ]; then
        echo "nop_finished"
    elif [ "$state" == "cac_completed" ]; then
        echo "cac_completed"
    elif [ "$state" == "nop_started" ]; then
        echo "nop_started"
    else
        # Undocumented state, return 1
        echo "${state_raw##*state}" | tr -d '\":}' | tr -d ' '
        return 1
    fi

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function returns MAC of radio interface from Wifi_Radio_State table.
#   Using condition string interface can be selected by name, channel,
#   frequency band etc. See USAGE EXAMPLE(S).
# INPUT PARAMETER(S):
#   $1 condition string (string, required)
# RETURNS:
#   Radio interface MAC address.
# USAGE EXAMPLES(S):
#   get_radio_mac_from_ovsdb "freq_band==5GL"
#   get_radio_mac_from_ovsdb "if_name==wifi1"
#   get_radio_mac_from_ovsdb "channel==44"
###############################################################################
get_radio_mac_from_ovsdb()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_radio_mac_from_ovsdb requires ${NARGS} input argument(s), $# given" -arg
    local where_clause=$1

    # No logging, this function echoes the requested value to caller!
    ${OVSH} s Wifi_Radio_State -w ${where_clause} mac -r
    return $?

}

###############################################################################
# DESCRIPTION:
#   Function gets MAC address of a provided interface.
#   Function supports ':' delimiter only.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   HW address of an interface.
# USAGE EXAMPLE(S):
#   get_radio_mac_from_system eth0
###############################################################################
get_radio_mac_from_system()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_radio_mac_from_system requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    # Match two hex chars and a ':' five times, followed by two hex chars at the end
    ifconfig "$if_name" | grep -o -E '([A-F0-9]{2}:){5}[A-F0-9]{2}'
}

###############################################################################
# DESCRIPTION:
#   Function echoes the path to the syslog rotate script.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Echoes path to the syslog rotate script.
# USAGE EXAMPLE(S):
#   get_syslog_rotate_cmd
###############################################################################
get_syslog_rotate_cmd()
{
    find ${OPENSYNC_ROOTDIR} -name "*_syslog_rotate.sh"
}

###############################################################################
# DESCRIPTION:
#   Function returns Radio TX Power set at OS - LEVEL2.
# STUB:
#   This function is a stub. It always raises an exception and needs
#   a function with the same name and usage in platform or device overrides.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
# RETURNS:
#   Echoes Radio TX Power set for interface
# USAGE EXAMPLE(S):
#   get_tx_power_from_os home-ap-24
###############################################################################
get_tx_power_from_os()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_tx_power_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1

    log "unit_lib:check_ht_mode_at_os_level - Getting Radio TX Power for interface '$vif_if_name' at OS - LEVEL2"
    # Provide override in platform specific file
    raise "This is a stub function. Override implementation needed." -l "unit_lib:get_tx_power_from_os" -fc
}

###############################################################################
# DESCRIPTION:
#   Function echoes upgrade manager's numerical code of identifier.
#   It translates the identifier's string to its numerical code.
#   Raises exception if identifier not found.
# INPUT PARAMETER(S):
#   $1  upgrade_identifier (string, required)
# RETURNS:
#   Echoes upgrade status code.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   get_um_code UPG_ERR_DL_FW
#   get_um_code UPG_STS_FW_DL_END
###############################################################################
get_um_code()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:get_um_code requires ${NARGS} input argument(s), $# given" -arg
    upgrade_identifier=$1

    case "$upgrade_identifier" in
        "UPG_ERR_ARGS")
            echo  "-1"
            ;;
        "UPG_ERR_URL")
            echo  "-3"
            ;;
        "UPG_ERR_DL_FW")
            echo  "-4"
            ;;
        "UPG_ERR_DL_MD5")
            echo  "-5"
            ;;
        "UPG_ERR_MD5_FAIL")
            echo  "-6"
            ;;
        "UPG_ERR_IMG_FAIL")
            echo  "-7"
            ;;
        "UPG_ERR_FL_ERASE")
            echo  "-8"
            ;;
        "UPG_ERR_FL_WRITE")
            echo  "-9"
            ;;
        "UPG_ERR_FL_CHECK")
            echo  "-10"
            ;;
        "UPG_ERR_BC_SET")
            echo  "-11"
            ;;
        "UPG_ERR_APPLY")
            echo  "-12"
            ;;
        "UPG_ERR_BC_ERASE")
            echo  "-14"
            ;;
        "UPG_ERR_SU_RUN ")
            echo  "-15"
            ;;
        "UPG_ERR_DL_NOFREE")
            echo  "-16"
            ;;
        "UPG_STS_FW_DL_START")
            echo  "10"
            ;;
        "UPG_STS_FW_DL_END")
            echo  "11"
            ;;
        "UPG_STS_FW_WR_START")
            echo  "20"
            ;;
        "UPG_STS_FW_WR_END")
            echo  "21"
            ;;
        "UPG_STS_FW_BC_START")
            echo  "30"
            ;;
        "UPG_STS_FW_BC_END")
            echo  "31"
            ;;
        *)
            raise "Unknown upgrade_identifier {given:=$upgrade_identifier}" -l "unit_lib:get_um_code" -arg
            ;;
    esac
}

###############################################################################
# DESCRIPTION:
#   Function echoes interface name used by CM for WAN uplink.
#   No checks are made for number of echoed elements in case none, one or
#   multiple interfaces are used.
# INPUT PARAMETER(S):
#   None
# RETURNS:
#   Used WAN interface
# USAGE EXAMPLES(S):
#   var=$(get_wan_uplink_interface_name)
###############################################################################
get_wan_uplink_interface_name()
{
    # No logging, this function echoes the requested value to caller!
    ${OVSH} s Connection_Manager_Uplink -w is_used==true if_name -r
    return $?
}

###############################################################################
# DESCRIPTION:
#   Function echoes the name of the wireless manager present on the device.
# INPUT PARAMETER(S):
#   None
# RETURNS:
#   Wireless manager name
# USAGE EXAMPLES(S):
#   var=$(get_wireless_manager_name)
###############################################################################
get_wireless_manager_name()
{
    if check_kconfig_option "CONFIG_MANAGER_OWM" "y"; then
        if [ "$(get_ovsdb_entry_value Node_Services status -w service owm)" == "enabled" ]; then
            wireless_manager=owm
        elif [ "$(get_ovsdb_entry_value Node_Services status -w service wm)" == "enabled" ]; then
            wireless_manager=wm
        else
            raise "No OpenSync wireless manager enabled on the device" -l "unit_lib.sh" -ds
        fi
    elif [ "$(get_ovsdb_entry_value Node_Services status -w service wm)" == "enabled" ]; then
        wireless_manager=wm
    else
        raise "WM disabled on the device" -l "unit_lib.sh" -ds
    fi

    echo "${wireless_manager}"
}

###############################################################################
# DESCRIPTION:
#   Function inserts entry to provided table. Raises an exception if
#   selected entry cannot be inserted.
#   It can be used with supported option(s):
#   -w (where)  field value used as a condition to select ovsdb table column
#
#   If -w option is used then two additional parameters must follow to
#   define condition string. Several -w options are possible, but for any
#   additional -w option used, there must always be 2 additional parameters.
#   In short, optional parameters come in groups of 3.
#
#   -i (insert)         Insert requires 2 additional parameters: field and
#                       value forming insert string.
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  option, supported options: -i
#   $3  ovsdb field in ovsdb table
#   $4  ovsdb field value
# RETURNS:
#   0   On success.
#   See DESCRIPTION:
# USAGE EXAMPLE(S):
#   insert_ovsdb_entry Wifi_Master_State -i if_type eth
###############################################################################
insert_ovsdb_entry()
{
    local ovsdb_table=$1
    shift
    local insert_string=""
    local conditions_string=""
    local insert_method=":="

    while [ -n "${1}" ]; do
        option=${1}
        shift
        case "$option" in
            -i)
                echo ${2} | grep -e "[ \"]" -e '\\' -e '(' &&
                    insert_string="${insert_string} "${1}"${insert_method}"$(single_quote_arg "${2}") ||
                    insert_string="${insert_string} "${1}"${insert_method}"${2}
                insert_method=":="
                shift 2
                ;;
            -m)
                insert_method="$1"
                shift
                ;;
            -w)
                conditions_string="$conditions_string -w $1==$2"
                shift 2
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:insert_ovsdb_entry" -arg
                ;;
        esac
    done

    entry_command="${OVSH} i $ovsdb_table $insert_string $conditions_string"
    log -deb "unit_lib:insert_ovsdb_entry - Executing ${entry_command}"
    eval ${entry_command}
    if [ $? -eq 0 ]; then
        log -deb "unit_lib:insert_ovsdb_entry - Entry inserted to $ovsdb_table - Success"
        ${OVSH} s "$ovsdb_table"
        return 0
    else
        ${OVSH} s "$ovsdb_table"
        raise  "Could not insert entry to $ovsdb_table" -l "unit_lib:insert_ovsdb_entry" -fc
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if tool is built into busybox.
# INPUT PARAMETER(S):
#   $1 command/tool name (string, required)
# ECHOES:
#   Verbose description of the outcome (output of the `type` command)
# RETURNS:
#   0   Successful completion.
#   >0  The command_name could not be found or an error occurred.
# USAGE EXAMPLE(S):
#   is_busybox_builtin arping
#   is_busybox_builtin chmod
###############################################################################
is_busybox_builtin()
{
    log -deb "unit_lib:is_busybox_builtin - Checking if tool is built into busybox"
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:is_busybox_builtin requires ${NARGS} input argument(s), $# given" -arg
    cmd_name=$1

    type "${cmd_name}"
    return $?
}

###############################################################################
# DESCRIPTION:
#   Function checks if the given ebtables rule is configured on the device.
#   Raise exception it the rule is not configured.
# INPUT PARAMETER(S):
#   \$1 (table_name)      : table to use (filter, nat or broute)                         : (string)(required)
#   \$2 (chain_name)      : chain to use (eg. INPUT, FORWARD etc.)                       : (string)(required)
#   \$3 (ebtable_rule)    : condition to be matched                                      : (string)(required)
#   \$4 (ebtable_target)  : action to take when the rule match (ACCEPT, DROP, CONTINUE)  : (string)(required)
# RETURNS:
#   0 If the ebtables rule is configured.
#   See DESCRIPTION
# USAGE EXAMPLE(S):
#   is_ebtables_rule_configured "filter" "INPUT" "-d 11:11:11:11:11:11" "DROP"
###############################################################################
is_ebtables_rule_configured()
{
    local NARGS=4
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:is_ebtables_rule_configured requires ${NARGS} input argument(s), $# given" -arg

    table_name="${1}"
    chain_name="${2}"
    ebtable_rule="${3}"
    ebtable_target="${4}"

    wait_for_function_response 0 "ebtables -t $table_name -L $chain_name | grep "${ebtable_target}" | grep -i -e \"$ebtable_rule\" " 10 &&
        log "nfm_lib/is_ebtables_rule_configured: ebtables rule \"$ebtable_rule\" configured on the device " ||
        raise "ebtables rule \"$ebtable_rule\" not configured on the device" -l "nfm_lib/is_ebtables_rule_configured" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if the given ebtables rule is removed from the device.
#   Raise exception it the rule is present and not removed.
# INPUT PARAMETER(S):
#   \$1 (table_name)      : table to use (filter, nat or broute)                         : (string)(required)
#   \$2 (chain_name)      : chain to use (eg. INPUT, FORWARD etc.)                       : (string)(required)
#   \$3 (ebtable_rule)    : condition to be matched                                      : (string)(required)
#   \$4 (ebtable_target)  : action to take when the rule match (ACCEPT, DROP, CONTINUE)  : (string)(required)
# RETURNS:
#   0 If the rule is removed from the device
#   See DESCRIPTION
# USAGE EXAMPLE(S):
#   is_ebtables_rule_removed "filter" "INPUT" "-d 11:11:11:11:11:11" "DROP"
###############################################################################
is_ebtables_rule_removed()
{
    local NARGS=4
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:is_ebtables_rule_removed requires ${NARGS} input argument(s), $# given" -arg

    table_name="${1}"
    chain_name="${2}"
    ebtable_rule="${3}"
    ebtable_target="${4}"

    wait_for_function_response 1 "ebtables -t $table_name -L $chain_name | grep "${ebtable_target}" | grep -i -e \"$ebtable_rule\" " 10 &&
        log "nfm_lib/is_ebtables_rule_removed: ebtables rule \"$ebtable_rule\" removed from the device " ||
        raise "ebtables rule \"$ebtable_rule\" not removed from the device" -l "nfm_lib/is_ebtables_rule_configured" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if logpull directory is empty.
# INPUT PARAMETER(S):
#   None
# RETURNS:
#   0   Directory is empty
#   1   Directory is not empty
# USAGE EXAMPLE(S):
#   is_logpull_dir_empty
###############################################################################
is_logpull_dir_empty()
{
    [ -z "$(ls -A /tmp/logpull/)" ]
}

###############################################################################
# DESCRIPTION:
#   Function checks if script is present in filesystem.
# INPUT PARAMETER(S):
#   $1  script path, can be relative or absolute (string, required)
# RETURNS:
#   0   Script found on system
#   >0  Script NOT found on system or in PATH if relative path is provided
# USAGE EXAMPLE(S):
#   is_script_on_system /tmp/resolv.conf
#   is_script_on_system /sbin/udhcpc
#   is_script_on_system /etc/init.d/opensync
#   is_script_on_system /dev/null
###############################################################################
is_script_on_system()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:is_script_on_system requires ${NARGS} input argument(s), $# given" -arg
    script_path=$1

    log -deb "unit_lib:is_script_on_system - Checking script ${script_path} presence"
    test -e "${script_path}"
    rc=$?
    return ${rc}
}

###############################################################################
# DESCRIPTION:
#   Function checks if tool is installed on system.
# INPUT PARAMETER(S):
#   $1  command/tool name (string, required)
# RETURNS:
#   0   Successful completion.
#   126 The utility specified by command name was found but could not be invoked.
#   >0  The command name could not be found or an error occurred.
# USAGE EXAMPLE(S):
#   is_tool_on_system arping
#   is_tool_on_system cat
###############################################################################
is_tool_on_system()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:is_tool_on_system requires ${NARGS} input argument(s), $# given" -arg
    cmd_name=$1

    log -deb "unit_lib:is_tool_on_system - Checking tool presence on system"
    command -v "$cmd_name"
    rc=$?
    if [ $rc -gt 0 ] && [ $rc -ne 126 ]; then
        which "$cmd_name"
        rc=$?
    fi
    if [ $rc -gt 0 ] && [ $rc -ne 126 ]; then
        type "$cmd_name"
        rc=$?
    fi
    return ${rc}
}

###############################################################################
# DESCRIPTION:
#   Function kills process of given name.
#   Requires binary/tool pidof installed on system.
# INPUT PARAMETER(S):
#   $1 process name (string, required)
# RETURNS:
#   None.
# USAGE EXAMPLE(S):
#   killall_process_by_name <process name>
###############################################################################
killall_process_by_name()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:killall_process_by_name requires ${NARGS} input argument(s), $# given" -arg
    process_name=$1
    local PROCESS_PID

    PROCESS_PID="$(pidof "${process_name}")"
    if [ -n "$PROCESS_PID" ]; then
        # In case of several returned values
        for P in $PROCESS_PID; do
            for S in TERM INT HUP KILL; do
                kill -s "${S}" "${P}"
                kill -0 "${P}"
                if [ $? -ne 0 ]; then
                    break
                fi
            done
            if [ $? -eq 0 ]; then
                log -deb "unit_lib:killall_process_by_name - killed process: ${P} with signal: ${S}"
            else
                log -deb "unit_lib:killall_process_by_name - killall_process_by_name - could not kill process: ${P}"
            fi
        done
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if the device is running in Native Linux Bridge configuration.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0 - CONFIG_TARGET_USE_NATIVE_BRIDGE is enabled
#   1 - CONFIG_TARGET_USE_NATIVE_BRIDGE is disabled or not set
# USAGE EXAMPLE(S):
#   linux_native_bridge_enabled
###############################################################################
linux_native_bridge_enabled()
{
    check_kconfig_option "CONFIG_TARGET_USE_NATIVE_BRIDGE" "y"
}

###############################################################################
# DESCRIPTION:
#   Function adds port with provided name to native bridge.
#   Procedure:
#       - check if native bridge exists
#       - check if port with provided name already exists on bridge
#       - if port does not exist add port
#   Raises an exception if bridge does not exist, port already in bridge ...
#   Raises an exception if
#       - bridge does not exist,
#       - port cannot be added.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   nb_add_port_to_bridge br-home patch-h2w
###############################################################################
nb_add_port_to_bridge()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:nb_add_port_to_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1
    port_name=$2

    log "unit_lib:nb_add_port_to_bridge - checking if '${bridge}' bridge is configured"
    ${OVSH} s Bridge name | grep -w "${bridge}" &&
        log -deb "unit_lib:nb_add_port_to_bridge - ${bridge} bridge is configured - Success" ||
        raise "Bridge '${bridge}' does not exist" -l "unit_lib:nb_add_port_to_bridge" -ds

    log "unit_lib:nb_add_port_to_bridge - checking if port '${port_name}' is configured to '${bridge}' bridge"
    brctl show "${bridge}" | grep -w "${port_name}"
    if [ $? = 0 ]; then
        log -deb "unit_lib:nb_add_port_to_bridge - Port '${port_name}' already in bridge '${bridge}'"
        return 0
    fi

    log "unit_lib:nb_add_port_to_bridge - adding '${port_name}' to Port, Interface and Bridge table"
    ovsdb_client_command=$(nb_gen_add_port_to_br_config "${bridge}" "${port_name}")
    ovsdb-client transact "$ovsdb_client_command" &&
        log -deb "unit_lib:nb_add_port_to_bridge - adding '${port_name}' to Port, Interface and Bridge table - Success" ||
        raise "Could not add port '${port_name}' to bridge '${bridge}'" -l "unit_lib:nb_add_port_to_bridge" -ds

    check_field=$(${OVSH} s Wifi_Inet_Config -w if_name=="$port_name")
    if [ -z "$check_field" ]; then
        insert_ovsdb_entry Wifi_Inet_Config -w if_name "$port_name" -i if_name "$port_name" \
            -i if_type "tap" \
            -i enabled "true" \
            -i network "true" \
            -i collect_stats "false" \
            -i no_flood "true" &&
                log -deb "unit_lib:nb_add_port_to_bridge - Insert entry for $port_name interface in Wifi_Inet_Config - Success" ||
                raise "Insert was not done for the entry of $port_name interface in Wifi_Inet_Config " -l "unit_lib:nb_add_port_to_bridge" -ds
    else
        log -deb "unit_lib:nb_add_port_to_bridge - Entry for $port_name in Wifi_Inet_Config already exists, skipping..."
    fi

    sleep 5

    check_if_port_in_bridge "${bridge}" "${port_name}"
    if [ $? = 0 ]; then
        log -deb "unit_lib:nb_add_port_to_bridge - adding port $port_name to $bridge - Success"
    else
        raise "Could not add port '${port_name}' to bridge '${bridge_name}'" -l unit_lib:nb_add_port_to_bridge -ds
    fi
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function enables/disables hairpin mode on the interface.
# INPUT PARAMETER(S):
#   $1 interface name (string, required)
#   $2 "on/off" (string, required)
# RETURNS:
#   0 - hairpin configuration is successful
#   1 - when hairpin configuration fails
# USAGE EXAMPLE(S):
#   nb_configure_hairpin br-home.dns "on"
#   nb_configure_hairpin br-home.dns "off"
###############################################################################
nb_configure_hairpin()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:nb_configure_hairpin requires ${NARGS} input argument(s), $# given" -arg

    ifname=$1
    hairpin=$2

    port=$(${OVSH} s Port -w name=="$ifname" -r | wc -l)
    if [ "${port}" -ne 0 ]; then
        # delete existing hairpin configuration if present
        nb_del_hairpin_config_if_present "$ifname"
        log -deb "unit_lib:nb_configure_hairpin - configuring hairpin '$hairpin' on interface '$ifname'"
        ${OVSH} U Port -w name=="$ifname" other_config:ins:"[\"map\",[[\"hairpin_mode\", \"${hairpin}\"]]]"
    fi

    sleep 2
    # verify if the configuration is applied
    hairpin_config=$(nb_get_current_hairpin_mode "$ifname")
    log -deb "unit_lib:nb_configure_hairpin - hairpin configuration is $hairpin_config "
    if [ -z "${hairpin_config}" ]; then
        log -deb "unit_lib:nb_configure_hairpin - Failed to configure hairpin mode on interface '$ifname'"
        return 1
    else
        log -deb "unit_lib:nb_configure_hairpin - Configured hairpin mode on interface '$ifname' - Success"
        return 0
    fi
}

###############################################################################
# DESCRIPTION:
#   Function checks if the hairpin configuration is present for the interface.
#   If configured, the hairpin configuration is removed from Ports table.
# INPUT PARAMETER(S):
#   $1  interface name (string, required)
# RETURNS:
#   None
# USAGE EXAMPLE(S):
#   nb_del_hairpin_config_if_present br-home.dns
###############################################################################
nb_del_hairpin_config_if_present()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib.sh:nb_del_hairpin_config_if_present requires ${NARGS} input argument(s), $# given" -arg

    ifname=$1
    curr_hairpin_mode=$(nb_get_current_hairpin_mode "$ifname")
    log -deb "curr_hairpin_mode: $curr_hairpin_mode"

    # remove hairpin mode if present
    if [ -n "${curr_hairpin_mode}" ]; then
        ${OVSH} -v U Port -w name=="$ifname" other_config:del:"[\"map\",[[\"hairpin_mode\", \"${curr_hairpin_mode}\"]]]"
    fi
}

###############################################################################
# DESCRIPTION:
#   Function creates the configuration for adding port to the bridge.  This
#   function is used as a helper function to add port to the bridge.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   NONE
# USAGE EXAMPLE(S):
#   nb_gen_add_port_to_br_config br-home br-home.dns
###############################################################################
nb_gen_add_port_to_br_config()
{
    bridge=$1
    port=$2
    cat <<EOF
    [
        "Open_vSwitch",
        {
            "op": "insert",
            "table": "Interface",
            "row": {
                "name": "${port}",
                "type": "internal",
                "ofport_request": 401
            },
            "uuid-name": "iface"
        },
        {
            "op": "insert",
            "table": "Port",
            "row": {
                "name": "${port}",
                "interfaces": ["set", [["named-uuid","iface"]]]
            },
            "uuid-name": "port"
        },
        {
            "op": "mutate",
            "table": "Bridge",
            "where": [["name", "==", "${bridge}" ]],
            "mutations": [["ports", "insert", ["set", [["named-uuid", "port"]]]]]
        }
    ]
EOF
}

###############################################################################
# DESCRIPTION:
#   When the device runs in Linux Native Bridge configuration, the function
#   parses the other_config in the Ports table for hairpin configuration and
#   returns the hairpin configuration.
# INPUT PARAMETER(S):
#   $1  interface name (string, required)
# RETURNS:
#   hairpin configuration
# USAGE EXAMPLE(S):
#   nb_get_current_hairpin_mode br-home.dns
###############################################################################
nb_get_current_hairpin_mode()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib.sh:nb_get_current_hairpin_mode requires ${NARGS} input argument(s), $# given" -arg

    ifname=$1
    ${OVSH} -M s Port -w name=="$ifname" other_config | \
        awk -F'"' '{for (i=1;i<NF;i++) {if ($(i)=="hairpin_mode"){print $(i+2)}}}'
}

###############################################################################
# DESCRIPTION:
#   Function checks if the Traffic Control rule of the given type (ingress or egress)
#   is configured on the device - LEVEL2. Linux TC command should be available on
# . the device.
# INPUT PARAMETER(S):
#   $1  interface name (string, required)
#   $2  expected value to check (string, required)
#   $3  rule type whether ingress or egress (string, required)
# RETURNS:
#   0   if the Traffic Control rule is configured on the device
# USAGE EXAMPLE(S):
#  nb_is_tc_rule_configured "br-home" "8080" "ingress"
###############################################################################
nb_is_tc_rule_configured()
{
    ifname=$1
    expected_str=$2
    rule_type=$3

    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:nb_is_tc_rule_configured requires ${NARGS} input argument(s), $# given" -arg

    log "unit_lib:nb_is_tc_rule_configured - Checking if $rule_type Traffic Control rule is applied on the device - LEVEL2"

    if [ $rule_type = "ingress" ]; then
        cmd="tc filter show dev ${ifname} parent ffff: | grep \"${expected_str}\" "
    else
        cmd="tc filter show dev ${ifname} | grep \"${expected_str}\" "
    fi
    log "unit_lib:nb_is_tc_rule_configured - Executing ${cmd}"
    wait_for_function_response 0 "${cmd}" 10 &&
        log -deb "unit_lib:nb_is_tc_rule_configured -$rule_type Traffic Control rule is applied on the device - Success" ||
        raise "$rule_type Traffic Control rule is not applied on the device" -l "unit_lib:nb_is_tc_rule_configured" -ds

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if the Traffic Control rule of the given type (ingress or egress)
#   is removed from the device - LEVEL2. Linux TC command should be available on
# . the device.
# INPUT PARAMETER(S):
#   $1  interface name (string, required)
#   $2  expected value to check (string, required)
#   $3  rule type whether ingress or egress (string, required)
# RETURNS:
#   0   if the Traffic Control rule is removed from the device
# USAGE EXAMPLE(S):
#  nb_is_tc_rule_removed "br-home" "8080" "ingress"
###############################################################################
nb_is_tc_rule_removed()
{
    ifname=$1
    expected_str=$2
    rule_type=$3

    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:nb_is_tc_rule_removed requires ${NARGS} input argument(s), $# given" -arg

    log "unit_lib:nb_is_tc_rule_removed - Checking if $rule_type Traffic Control rule is removed from the device - LEVEL2"

    if [ $rule_type = "ingress" ]; then
        cmd="tc filter show dev ${ifname} parent ffff: | grep \"${expected_str}\" "
    else
        cmd="tc filter show dev ${ifname} | grep \"${expected_str}\" "
    fi
    log "unit_lib:nb_is_tc_rule_removed - Executing ${cmd}"
    wait_for_function_response 1 "${cmd}" 10 &&
        log -deb "unit_lib:nb_is_tc_rule_removed -$rule_type Traffic Control rule is removed from the device - Success" ||
        raise "$rule_type Traffic Control rule is not removed from the device" -l "unit_lib:nb_is_tc_rule_configured" -ds

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function removes port with provided name from the native bridge.
#   Raises an exception if port cannot be deleted.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   0 on success.
#   1 on failure
# USAGE EXAMPLE(S):
#   nb_remove_port_from_bridge br-wan br-wan.tdns
###############################################################################
nb_remove_port_from_bridge()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:nb_remove_port_from_bridge requires ${NARGS} input argument(s)" -arg

    bridge=$1
    port_name=$2

    res=$(check_if_port_in_bridge "$bridge" "$port_name")
    if [ "$?" != 0 ]; then
        log -deb "unit_lib:nb_remove_port_from_bridge - Port '$port_name' does not exist in bridge $bridge"
        return 0
    fi

    log -deb "unit_lib:nb_remove_port_from_bridge - Port $port_name exists in bridge $bridge - Removing"
    port_uuid=$(${OVSH} s Port -w name=="${port_name}" -c -r _uuid)
    log -deb "unit_lib:nb_remove_port_from_bridge - Port_uuid $port_uuid"

    ${OVSH} u Bridge -w name=="${bridge}" ports:del:'["set", ['"${port_uuid}"']]' &&
        log -deb "unit_lib:nb_remove_port_from_bridge - ovsdb-client delete $port_name from $bridge - Success" ||
        log -deb "unit_lib:nb_remove_port_from_bridge - ovsdb-client delete $port_name from $bridge - Failed"
}

###############################################################################
# DESCRIPTION:
#   Functions sets interface option when device is in Native Bridge Configuration
#   Raises an exception on failure.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
#   $2  Option (string, required)
#   $3  Value (string, required)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   nb_set_interface_option br-home.tdns type internal
#   nb_set_interface_option br-home.tdns ofport_request 3001
###############################################################################
nb_set_interface_option()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:nb_set_interface_option requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1
    option=$2
    value=$3

    log "unit_lib:nb_set_interface_option: updating Interface ${if_name} table with $option = ${value}"

    update_ovsdb_entry Interface -w name "$if_name" -u "$option" "$value" &&
        log "unit_lib:nb_set_interface_option: updating Interface ${if_name} table with $option = ${value} - Success" ||
        raise "nb_set_interface_option - Failed to update Interface table with ${option} = ${value}" -l "unit_lib:nb_set_interface_option" -fc

}

###############################################################################
# DESCRIPTION:
#   Function adds port with provided name to ovs bridge.
#   Procedure:
#       - check if ovs bridge exists
#       - check if port with provided name already exists on bridge
#       - if port does not exist add port
#   Raises an exception if
#       - bridge does not exist,
#       - port cannot be added.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   ovs_add_port_to_bridge br-home patch-h2w
###############################################################################
ovs_add_port_to_bridge()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:ovs_add_port_to_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1
    port_name=$2

    log "unit_lib:ovs_add_port_to_bridge - Adding port '${port_name}' to bridge '${bridge}'"
    ovs-vsctl br-exists "${bridge}"
    if [ $? = 2 ]; then
        raise "Bridge '${bridge}' does not exist" -l "unit_lib:ovs_add_port_to_bridge" -ds
    fi
    ovs-vsctl list-ports "${bridge}" || true
    ovs-vsctl list-ports "${bridge}" | grep -wF "${port_name}"
    if [ $? = 0 ]; then
        log -deb "unit_lib:ovs_add_port_to_bridge - Port '${port_name}' already in bridge '${bridge}'"
        return 0
    else
        ovs-vsctl add-port "${bridge}" "${port_name}" &&
            log -deb "unit_lib:ovs_add_port_to_bridge - ovs-vsctl add-port ${bridge} ${port_name} - Success" ||
            raise "Could not add port '${port_name}' to bridge '${bridge}'" -l unit_lib:ovs_add_port_to_bridge -ds
    fi
}

###############################################################################
# DESCRIPTION:
#   Function sets interface option.
#   Function uses ovs-vsctl command, different from native Linux bridge.
#   Raises an exception on failure.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
#   $2  Option (string, required)
#   $3  Value (string, required)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   ovs_set_interface_optionme.tdns type internal
#   ovs_set_interface_option br-home.tdns ofport_request 3001
###############################################################################
ovs_set_interface_option()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:ovs_set_interface_option requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1
    option=$2
    value=$3

    ovs-vsctl set interface "${if_name}" "${option}"="${value}" &&
        log -deb "unit_lib:ovs_set_interface_option - ovs-vsctl set interface ${if_name} ${option}=${value} - Success" ||
        raise "Could not set interface option: set interface ${if_name} ${option}=${value}" -l "unit_lib:ovs_set_interface_option" -ds
}

###############################################################################
# DESCRIPTION:
#   Function creates a network bridge by creating an entry in Open_vSwitch and
#   Bridge tables
# INPUT PARAMETER(S):
#   $1  bridge name (string, required)
# RETURNS:
#   0
# USAGE EXAMPLE(S):
#   ovsdb_create_bridge br-home
###############################################################################
ovsdb_create_bridge()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib.sh:ovsdb_create_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1

    ovsdb_client_command=$(ovsdb_gen_bridge_config "$bridge")
    ovsdb-client transact "$ovsdb_client_command"
}

###############################################################################
# DESCRIPTION:
#   Function deletes the given bridge from Open_vSwitch and Bridge table.
# INPUT PARAMETER(S):
#   $1  bridge name (string, required)
# RETURNS:
#   0
# USAGE EXAMPLE(S):
#   ovsdb_delete_bridge br-home
###############################################################################
ovsdb_delete_bridge()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib.sh:ovsdb_delete_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1

    bridge_uuid=$(${OVSH} -rU s Bridge _uuid -w name=="${bridge}")
    log "unit_lib:ovsdb_delete_bridge Removing Bridge ${bridge} from Open_vSwitch table"
    ${OVSH} u Open_vSwitch bridges:del:'["set", ['"${bridge_uuid}"']]'

    log "unit_lib:ovsdb_delete_bridge Removing ${bridge} from Bridge table"
    ${OVSH} d Bridge -w name=="${bridge}"
}

###############################################################################
# DESCRIPTION:
#   Function creates the configuration required for adding bridge into ovsdb
#   This function is used as a helper function to add the bridge.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
# RETURNS:
#   NONE
# USAGE EXAMPLE(S):
#   ovsdb_gen_bridge_config br-home
###############################################################################
ovsdb_gen_bridge_config()
{
    bridge=$1
    cat <<EOF
[
    "Open_vSwitch",
    {
        "op" : "insert",
        "table" : "Bridge",
        "uuid-name": "newBridge",
        "row": {
            "datapath_id": "00026df9edfc63",
            "name": "${bridge}"
        }
    },
    {
        "op" : "mutate",
        "table" : "Open_vSwitch",
        "where" : [["cur_cfg", "==", 0]],
        "mutations": [["bridges", "insert", ["set", [["named-uuid", "newBridge"]]]]]
    }
]
EOF
}

###############################################################################
# DESCRIPTION:
#   Function removes port with provided name from ovs bridge.
#   Procedure:
#       - check if ovs bridge exists
#       - check if port with provided name already exists on bridge
#       - if port exists, remove port
#   Raises an exception if
#       - bridge does not exist,
#       - port cannot be removed.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   ovs_remove_port_from_bridge br-home patch-h2w
###############################################################################
ovs_remove_port_from_bridge()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:ovs_remove_port_from_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1
    port_name=$2

    log "unit_lib:ovs_remove_port_from_bridge - Removing port '${port_name}' from bridge '${bridge}'"
    ovs-vsctl br-exists "${bridge}"
    if [ $? = 2 ]; then
        raise "Bridge '${bridge}' does not exist" -l "unit_lib:ovs_remove_port_from_bridge" -ds
    fi
    ovs-vsctl list-ports "${bridge}" || true
    ovs-vsctl list-ports "${bridge}" | grep -wF "${port_name}"
    if [ $? = 0 ]; then
        log -deb "unit_lib:ovs_remove_port_from_bridge - Port '${port_name}' exists in bridge '${bridge}', removing."
        ovs-vsctl del-port "${bridge}" "${port_name}" &&
            log -deb "unit_lib:ovs_remove_port_from_bridge - ovs-vsctl del-port ${bridge} ${port_name} - Success" ||
            raise "Could not remove port '${port_name}' from bridge '${bridge}'" -l unit_lib:ovs_remove_port_from_bridge -ds
    else
        log -deb "unit_lib:ovs_remove_port_from_bridge - Port '${port_name}' does not exist in bridge '${bridge}', nothing to do."
    fi
}

###############################################################################
# DESCRIPTION:
#   Function prints all tables provided as parameter.
#   Useful for debugging and logging to stdout.
# INPUT PARAMETER(S):
#   $@  ovsdb table name(s) (required)
# RETURNS:
#   0   Always.
# USAGE EXAMPLE(S):
#   print_tables Manager
#   print_tables Wifi_Route_State
#   print_tables Connection_Manager_Uplink
###############################################################################
print_tables()
{
    NARGS_MIN=1
    [ $# -ge ${NARGS_MIN} ] ||
        raise "unit_lib:print_tables requires at least ${NARGS_MIN} input argument(s), $# given" -arg

    for table in "$@"
    do
        log -deb "unit_lib:print_tables - OVSDB table - $table:"
        ${OVSH} s "$table"
    done

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function removes port with provided name from the network bridge.
#   Procedure:
#       - check if bridge exists
#       - check if port with provided name already exists on bridge
#       - if port exists, remove port
#   Raises an exception if
#       - bridge does not exist,
#       - port cannot be removed.
# INPUT PARAMETER(S):
#   $1  Bridge name (string, required)
#   $2  Port name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   remove_port_from_bridge br-home patch-h2w
###############################################################################
remove_port_from_bridge()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:remove_port_from_bridge requires ${NARGS} input argument(s), $# given" -arg
    bridge=$1
    port_name=$2

    if linux_native_bridge_enabled; then
        nb_remove_port_from_bridge "${bridge}" "${port_name}"
    else
        ovs_remove_port_from_bridge "${bridge}" "${port_name}"
    fi
}

###############################################################################
# DESCRIPTION:
#   Function deletes selected row from ovsdb table. Raises an exception if
#   selected row cannot be deleted.
#   It can be used with supported option(s):
#
#   -w (where)  field value used as a condition to select ovsdb table column
#
#   If -w option is used then two additional parameters must follow to
#   define condition string. Several -w options are possible, but for any
#   additional -w option used, there must always be 2 additional parameters.
#   In short, optional parameters come in groups of 3.
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  option, supported options: -w (optional, see DESCRIPTION)
#   $3  ovsdb field in ovsdb table (optional, see DESCRIPTION)
#   $4  ovsdb field value (optional, see DESCRIPTION)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   remove_ovsdb_entry Wifi_Inet_Config -w if_name eth0
#   remove_ovsdb_entry Wifi_VIF_Config -w vif_radio_idx 2 -w ssid custom_ssid
###############################################################################
remove_ovsdb_entry()
{
    ovsdb_table=$1
    shift
    conditions_string=""

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -w)
                conditions_string="$conditions_string -w $1==$2"
                shift 2
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:remove_ovsdb_entry" -arg
                ;;
        esac
    done

    remove_command="${OVSH} d $ovsdb_table $conditions_string"
    log -deb "unit_lib:remove_ovsdb_entry - $remove_command"
    ${remove_command}
    if [ "$?" -eq 0 ]; then
        log -deb "unit_lib:remove_ovsdb_entry - Entry removed"
    else
        print_tables "$ovsdb_table" ||
            log -deb "unit_lib:remove_ovsdb_entry - Failed to print table $ovsdb_table"
        raise  "Could not remove entry from $ovsdb_table" -l "unit_lib:remove_ovsdb_entry" -fc
    fi

    return 0
}

###############################################################################
# DESCRIPTION:
# INPUT PARAMETER(S):
# RETURNS:
# USAGE EXAMPLE(S):
###############################################################################
remove_sta_connections()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:remove_sta_connections requires ${NARGS} input argument(s), $# given" -arg
    sta_if_name=$1

    log -deb "[DEPRECATED] - Function unit_lib:remove_sta_connections is deprecated in favor of remove_sta_interfaces_exclude"
    log -deb "unit_lib:remove_sta_connections - Removing STA connections except $sta_if_name"
    ${OVSH} d Wifi_VIF_Config -w if_name!="$sta_if_name" -w mode==sta &&
        log -deb "unit_lib:remove_sta_connections - STA connections except '$sta_if_name' removed - Success" ||
        raise "Could not remove STA connections" -l "unit_lib:remove_sta_connections" -fc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function deletes VIF interface and removes interface entry for selected
#   VIF interface from Wifi_VIF_Config, and waits for entry to be removed from
#   Wifi_VIF_State.
# INPUT PARAMETER(S):
#   Parameters are fed into function as key-value pairs.
#   Function supports the following keys for parameter values:
#       -if_name, -vif_if_name
#   Where mandatory key-value pairs are:
#       -if_name <if_name> (string, required)
#       -vif_if_name <vif_if_name> (string, required)
#   Other parameters are optional. Order of key-value pairs can be random.
#   Refer to USAGE EXAMPLE(S) for details.
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   remove_vif_interface -if_name wifi2 \
#       -vif_if_name home-ap-u50 \
###############################################################################
remove_vif_interface()
{
    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -if_name)
                if_name=$1
                shift
                ;;
            -vif_if_name)
                vif_if_name=$1
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:remove_vif_interface" -arg
                ;;
        esac
    done

    [ -z "${if_name}" ] &&
        raise "'if_name' argument empty" -l "unit_lib:remove_vif_interface" -arg
    [ -z "${vif_if_name}" ] &&
        raise "'vif_if_name' argument empty" -l "unit_lib:remove_vif_interface" -arg

    log -deb "unit_lib:remove_vif_interface - Removing VIF interface"

    # shellcheck disable=SC2086
    remove_ovsdb_entry Wifi_VIF_Config -w if_name "$vif_if_name" &&
        log -deb "unit_lib:remove_vif_interface - Entry '$vif_if_name' removed from table Wifi_VIF_Config - Success" ||
        raise "Could not remove entry '$vif_if_name' from table Wifi_VIF_Config" -l "unit_lib:remove_vif_interface" -fc
    # shellcheck disable=SC2086
    wait_ovsdb_entry_remove Wifi_VIF_State -w if_name "$vif_if_name" &&
        log -deb "unit_lib:remove_vif_interface - Wifi_VIF_Config reflected to Wifi_VIF_State for '$vif_if_name' - Success" ||
        raise "Could not reflect Wifi_VIF_Config to Wifi_VIF_State for '$vif_if_name'" -l "unit_lib:remove_vif_interface" -fc

    log -deb "unit_lib:remove_vif_interface - Wireless interface deleted from Wifi_VIF_State"

    return 0
}

###############################################################################
# DESCRIPTION:
#     This function removes entries from the Wifi_VIF_Config and
#     Wifi_Inet_Config OVSDB tables that match the specified AP
#     virtual interface. Raises exception on fail.
# INPUT PARAMETER(S):
#     - if_name: Wifi_VIF_Config::if_name
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   remove_ap_interface b-ap-24
###############################################################################
remove_ap_interface()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:remove_ap_interface requires ${NARGS} input argument(s), $# given" -arg
    # shellcheck disable=SC2034
    if_name=${1}

    log -deb "unit_lib:remove_ap_interface - Resetting ${if_name} AP interface"
    remove_ovsdb_entry Wifi_VIF_Config -w if_name $if_name ||
        raise "remove_ovsdb_entry - Could not remove interface '$if_name' from Wifi_VIF_Config table" -l "unit_lib:remove_ap_interface" -fc
    wait_ovsdb_entry_remove Wifi_VIF_State -w if_name $if_name ||
        raise "wait_ovsdb_entry_remove - Could not reflect Wifi_VIF_Config to Wifi_VIF_State for '$if_name'" -l "unit_lib:remove_ap_interface" -fc
    remove_ovsdb_entry Wifi_Inet_Config -w if_name $if_name ||
        raise "remove_ovsdb_entry - Could not remove Wifi_Inet_Config entry for '$if_name' AP interface" -l "unit_lib:remove_ap_interface" -fc
    wait_ovsdb_entry_remove Wifi_Inet_Config -w if_name $if_name ||
        raise "wait_ovsdb_entry_remove - Could not reflect Wifi_Inet_Config to Wifi_Inet_State for '$if_name' AP interface" -l "unit_lib:remove_ap_interface" -fc
    remove_ovsdb_entry Wifi_Inet_Config -w gre_ifname $if_name ||
        raise "remove_ovsdb_entry - Could not remove Wifi_Inet_Config entry for '$if_name' GRE interface" -l "unit_lib:remove_ap_interface" -fc
    wait_ovsdb_entry_remove Wifi_Inet_Config -w gre_ifname $if_name ||
        raise "wait_ovsdb_entry_remove - Could not reflect Wifi_Inet_Config to Wifi_Inet_State for '$if_name' GRE interface" -l "unit_lib:remove_ap_interface" -fc
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function sets entry values for interface in Wifi_Inet_Config
#   table to default.
#   Raises exception on fail.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   reset_inet_entry eth0
#   reset_inet_entry wifi0
###############################################################################
reset_inet_entry()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:reset_inet_entry requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    log -deb "unit_lib:reset_inet_entry - Setting Wifi_Inet_Config for $if_name to default values"
    update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" \
        -u NAT "false" \
        -u broadcast "[\"set\",[]]" \
        -u dhcpd "[\"map\",[]]" \
        -u dns "[\"map\",[]]" \
        -u enabled "true" \
        -u gateway "[\"set\",[]]" \
        -u gre_ifname "[\"set\",[]]" \
        -u gre_local_inet_addr "[\"set\",[]]" \
        -u gre_remote_inet_addr "[\"set\",[]]" \
        -u inet_addr "[\"set\",[]]" \
        -u ip_assign_scheme "none" \
        -u mtu "[\"set\",[]]" \
        -u netmask "[\"set\",[]]" \
        -u network "true" \
        -u parent_ifname "[\"set\",[]]" \
        -u softwds_mac_addr "[\"set\",[]]" \
        -u softwds_wrap "[\"set\",[]]" \
        -u upnp_mode "[\"set\",[]]" \
        -u vlan_id "[\"set\",[]]" &&
            log -deb "unit_lib:reset_inet_entry - Wifi_Inet_Config updated - Success" ||
            raise "Could not update Wifi_Inet_Config" -l "unit_lib:reset_inet_entry" -fc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function resets VIF STA interface.
#     This function reset Wifi_VIF_Config table entry for specific STA interface to default values
#
#   Raises exception on fail.
# INPUT PARAMETER(S):
#     - if_name: Wifi_VIF_Config::if_name
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   reset_sta_interface bhaul-sta-l50
###############################################################################
reset_sta_interface()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:reset_sta_interface requires ${NARGS} input argument(s), $# given" -arg
    # shellcheck disable=SC2034
    if_name=${1}

    log -deb "unit_lib:reset_sta_interface - Resetting STA ${if_name} interface"
    update_ovsdb_entry Wifi_VIF_Config -w if_name "${if_name}" -w mode "sta" \
        -u credential_configs "[\"set\",[]]" \
        -u mac_list "[\"set\",[]]" \
        -u mac_list_type "[\"set\",[]]" \
        -u parent "[\"set\",[]]" \
        -u security "[\"map\",[]]" \
        -u ssid "" \
        -u ssid_broadcast "[\"set\",[]]" &&
            log -deb "unit_lib:reset_sta_interface - STA VIF-s reset"
    check_ovsdb_table_field_exists Wifi_VIF_Config "wpa"
    if [ "${?}" == "0" ]; then
        log -deb "unit_lib:reset_sta_interface - Checking and resetting wpa, wpa_key_mgmt, wpa_oftags, wpa_psks for STA VIF-s"
        update_ovsdb_entry Wifi_VIF_Config -w if_name "${if_name}" -w mode "sta" \
            -u wpa "[\"set\",[]]" \
            -u wpa_key_mgmt "[\"set\",[]]" \
            -u wpa_oftags "[\"map\",[]]" \
            -u wpa_psks "[\"map\",[]]" &&
                log -deb "unit_lib:reset_sta_interface - wpa, wpa_key_mgmt, wpa_oftags, wpa_psks are reset for STA VIF-s"
    else
        log -err "unit_lib:reset_sta_interface - WPA not implemented for this OS implementation"
        print_tables Wifi_VIF_Config
    fi
    return 0
}
###############################################################################
# DESCRIPTION:
#   Function erases the firmware image and resets all triggers that would
#   start the upgrade process.
#   Raises exception on fail.
# INPUT PARAMETER(S):
#   $1  path to FW image (required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   reset_um_triggers <fw_path>
###############################################################################
reset_um_triggers()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:reset_um_triggers requires ${NARGS} input argument(s), $# given" -arg
    fw_path=$1

    log -deb "unit_lib:reset_um_triggers - Erasing $fw_path"
    rm -rf "$fw_path" || true

    log -deb "unit_lib:reset_um_triggers - Resetting AWLAN_Node UM related fields"
    update_ovsdb_entry AWLAN_Node \
      -u firmware_pass '' \
      -u firmware_url '' \
      -u upgrade_dl_timer '0' \
      -u upgrade_status '0' \
      -u upgrade_timer '0' &&
          log -deb "unit_lib:reset_um_triggers - AWLAN_Node UM related fields reset - Success" ||
          raise "update_ovsdb_entry - Could not reset AWLAN_Node UM related fields" -l "unit_lib:reset_um_triggers" -fc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function re-starts all OpenSync managers.
#   Executes managers script with restart option.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   restart_managers
###############################################################################
restart_managers()
{
    log -deb "unit_lib:restart_managers - Restarting OpenSync managers"
    MANAGER_SCRIPT=$(get_managers_script)
    # shellcheck disable=2034
    ret=$($MANAGER_SCRIPT restart)
    ec=$?
    log -deb "unit_lib:restart_managers - manager restart exit code ${ec}"
    return $ec
}

###############################################################################
# DESCRIPTION:
#   Function kills the WPD (Watchdog Proxy Daemon) binary.
#   The function depends on the tool pkill.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   wpd_process_kill
###############################################################################
wpd_process_kill()
{
    log "unit_lib:wpd_process_kill - Killing WPD process."
    pkill -9 ${OPENSYNC_ROOTDIR}/bin/wpd
    wpd_pid=$(get_pid ${OPENSYNC_ROOTDIR}/bin/wpd)
    test -z ${wpd_pid} &&
        log "unit_lib:wpd_process_kill - WPD was killed - Success" ||
        raise "WPD was not killed, PID: ${wpd_pid}" -l "unit_lib:wpd_process_kill" -ds
    wpd_pid_filepath=$(get_kconfig_option_value "CONFIG_WPD_PID_PATH")
    # Clean string of quotes:
    wpd_pid_filepath=$(echo ${wpd_pid_filepath} | tr -d '"')
    log "unit_lib:wpd_process_kill - Ensure PID file is removed: ${wpd_pid_filepath}."
    test -e ${wpd_pid_filepath} && rm -f ${wpd_pid_filepath}
}

###############################################################################
# DESCRIPTION:
#   Function starts the WPD (Watchdog Proxy Daemon) via the init.d script.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   wpd_service_start
###############################################################################
wpd_service_start()
{
    log "unit_lib:wpd_service_start - Starting WPD service."
    /etc/init.d/wpd start
    wpd_pid=$(get_pid ${OPENSYNC_ROOTDIR}/bin/wpd)
    test -n ${wpd_pid} &&
        log "unit_lib:wpd_service_start - WPD was started: ${wpd_pid} - Success" ||
        log -err "unit_lib:wpd_service_start - WPD was not started"
}

###############################################################################
# DESCRIPTION:
#   Function ensures that "dir_path" is writable.
#   Common usage is to ensure TARGET_PATH_LOG_STATE can be updated.
#   Requires the path "/tmp" to be writable, executable, tmpfs
# INPUT PARAMETER(S):
#   $1  dir_path: absolute path to dir (string, required)
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   set_dir_to_writable "/etc"
###############################################################################
set_dir_to_writable()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:set_dir_to_writable: requires ${NARGS} input argument(s), $# given" -arg
    [ -n "${1}" ] || raise "Input argument empty" -l "unit_lib:set_dir_to_writable"  -arg
    [ -d "${1}" ] || raise "Input argument '${1}' is not a directory" -l "unit_lib:set_dir_to_writable"  -arg
    dir_path="${1}"
    subst_dir=${dir_path//\//_}

    if touch ${dir_path}/.test_write 2>/dev/null; then
        rm -f ${dir_path}/.test_write
    else
        mkdir -p /tmp/${subst_dir}-ro
        mkdir -p /tmp/${subst_dir}-rw
        mount --bind ${dir_path} /tmp/${subst_dir}-ro
        ln -sf /tmp/${subst_dir}-ro/* /tmp/${subst_dir}-rw/
        mount --bind /tmp/${subst_dir}-rw ${dir_path}
    fi
}

###############################################################################
# DESCRIPTION:
#   Function drops interface.
#   Uses and requires ifconfig tool to be installed on device.
#   Provide adequate function in overrides otherwise.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   If interface was dropped, non zero otherwise.
# USAGE EXAMPLE(S):
#   set_interface_down eth0
###############################################################################
set_interface_down()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:set_interface_down requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    ifconfig "$if_name" down
    return $?
}

###############################################################################
# DESCRIPTION:
#   Function sets interface option.
#   Raises an exception on failure.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
#   $2  Option (string, required)
#   $3  Value (string, required)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   set_interface_option br-home.tdns type internal
#   set_interface_option br-home.tdns ofport_request 3001
###############################################################################
set_interface_option()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:set_interface_option requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1
    option=$2
    value=$3

    if linux_native_bridge_enabled; then
        nb_set_interface_option "$if_name" "$option" "$value"
    else
        ovs_set_interface_option "$if_name" "$option" "$value"
    fi

}

###############################################################################
# DESCRIPTION:
#   Function sets interface to patch port.
#   Function uses ovs-vsctl command, different from native Linux bridge.
#   Raises an exception if patch cannot be set.
# INPUT PARAMETER(S):
#   $1  interface name (string, required, not used)
#   $2  patch name (string, required)
#   $3  peer name (string, required)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   set_interface_patch patch-h2w patch-w2h patch-h2w
#   set_interface_patch patch-w2h patch-h2w patch-w2h
###############################################################################
set_interface_patch()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:set_interface_patch requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1
    patch=$2
    peer=$3

    ovs-vsctl set interface "$patch" type=patch &&
        log -deb "unit_lib:set_interface_patch - ovs-vsctl set interface '$patch' type=patch - Success" ||
        raise "Could not set interface patch: ovs-vsctl set interface '$patch' type=patch" -l "unit_lib:set_interface_patch" -ds

    ovs-vsctl set interface "$patch" options:peer="$peer" &&
        log -deb "unit_lib:set_interface_patch - ovs-vsctl set interface '$patch' options:peer=$peer - Success" ||
        raise "Could not set interface patch peer: ovs-vsctl set interface '$patch' options:peer=$peer" -l "unit_lib:set_interface_patch" -ds
}

###############################################################################
# DESCRIPTION:
#   Function brings up interface
#   Uses and requires ifconfig tool to be installed on device.
#   Provide adequate function in overrides otherwise.
# INPUT PARAMETER(S):
#   $1  Interface name (string, required)
# RETURNS:
#   0   If interface was brought up, non zero otherwise.
# USAGE EXAMPLE(S):
#   set_interface_up eth0
###############################################################################
set_interface_up()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:set_interface_up requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    ifconfig "$if_name" up
    return $?
}

###############################################################################
# DESCRIPTION:
#   Function sets port forwarding for given interface.
#   Raises exception if port forwarding is not set.
# INPUT PARAMETER(S):
#   $1  Source interface name (string, required)
#   $2  Source port (string, required)
#   $3  Destination IP address (string, required)
#   $4  Destination port (string, required)
#   $5  Protocol (string, required)
#   $5  OVSDB table (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION
# USAGE EXAMPLE(S):
#   set_ip_port_forwarding bhaul-sta-24 8080 10.10.10.123 80 tcp Netfilter
###############################################################################
set_ip_port_forwarding()
{
    local NARGS=6
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:set_ip_port_forwarding requires ${NARGS} input argument(s), $# given" -arg
    src_ifname=$1
    src_port=$2
    dst_ipaddr=$3
    dst_port=$4
    protocol=$5
    pf_table=$6

    log -deb "unit_lib:set_ip_port_forwarding - Creating port forward on interface '$src_ifname'"

    if [ "$pf_table" = "Netfilter" ]; then
        insert_ovsdb_entry Netfilter \
            -i chain "PF_PREROUTING" \
            -i enable true \
            -i name "pf.dnat_tcp_$src_ifname" \
            -i priority 0 \
            -i protocol "ipv4" \
            -i rule "-p $protocol -i $src_ifname --dport $src_port --to-destination $dst_ipaddr:$dst_port" \
            -i status "enabled" \
            -i table "nat" \
            -i target "DNAT" ||
                raise "Could not insert entry to Netfilter table" -l "unit_lib:set_ip_port_forwarding" -fc
    else
        insert_ovsdb_entry IP_Port_Forward \
            -i dst_ipaddr "$dst_ipaddr" \
            -i dst_port "$dst_port" \
            -i src_port "$src_port" \
            -i protocol "$protocol" \
            -i src_ifname "$src_ifname" ||
                raise "Could not insert entry to IP_Port_Forward table" -l "unit_lib:set_ip_port_forwarding" -fc
    fi

    log -deb "unit_lib:set_ip_port_forwarding - Port forward created on interface '$src_ifname' - Success"

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function sets log severity for manager by managing AW_Debug table.
#   Possible log severity levels are INFO, TRACE, DEBUG..
#   Raises an exception if log severity is not successfully set.
# INPUT PARAMETER(S):
#   $1 manager name (string, required)
#   $2 log severity (string, required)
# RETURNS:
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   set_manager_log NM TRACE
#   set_manager_log WM TRACE
###############################################################################
set_manager_log()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:set_manager_log requires ${NARGS} input argument(s), $# given" -arg
    name=$1
    log_severity=$2

    log -deb "unit_lib:set_manager_log - Checking if AW_Debug contains ${name}"
    check_ovsdb_entry AW_Debug -w name "${name}"
    if [ "$?" == 0 ];then
        log -deb "unit_lib:set_manager_log - AW_Debug contains ${name}, will update"
        update_ovsdb_entry AW_Debug -w name "${name}" -u log_severity "${log_severity}" &&
            log -deb "unit_lib:set_manager_log - AW_Debug ${name} updated to ${log_severity}" ||
            raise "Could not update AW_Debug ${name} to ${log_severity}" -l "unit_lib:set_manager_log" -fc
    else
        log -deb "unit_lib:set_manager_log - Adding ${name} to AW_Debug with severity ${log_severity}"
        insert_ovsdb_entry AW_Debug -i name "${name}" -i log_severity "${log_severity}" ||
            raise "Could not insert to table AW_Debug::log_severity" -l "unit_lib:set_manager_log" -fc
    fi
    log -deb "unit_lib:set_manager_log - Dumping table AW_Debug"
    print_tables AW_Debug || true
}

###############################################################################
# DESCRIPTION:
#   Function will shows the  bridge information and its attached ports.
# INPUT PARAMETER(S):
#   None
# RETURNS:
#   See DESCRIPTION.
# USAGE EXAMPLES(S):
#   show_bridge_details
###############################################################################
show_bridge_details()
{
    linux_native_bridge_enabled && brctl show || ovs-vsctl show
}

###############################################################################
# DESCRIPTION:
#   Function echoes single quoted input argument. Used for ovsh tool.
#   It is imperative that this function does not log or echo anything, as its main
#   functionality is to echo and the value being used upstream.
# INPUT PARAMETER(S):
#   arg: string containing double quotes, command or other special characters (string, required)
# PRINTS:
#   Single quoted input argument.
# RETURNS:
#   returns exit code of printf operation: 0 for success, >0 for failure
# USAGE EXAMPLE(S):
#   single_quote_arg "[map,[[encryption,WPA-PSK],[key,FutTestPSK],[mode,2]]]"
###############################################################################
single_quote_arg()
{
    printf %s\\n "$1" | sed "s/'/'\\\\''/g;1s/^/'/;\$s/\$/'/" ;
}

###############################################################################
# DESCRIPTION:
#   Function starts all OpenSync managers.
#   Executes managers script with start option.
#   Raises an exception if managers script is not successfully executed or if
#   DM (Diagnostic Manager) slave or master is not started.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   start_managers
###############################################################################
start_managers()
{
    log -deb "unit_lib:start_managers Starting OpenSync managers"

    MANAGER_SCRIPT=$(get_managers_script)
    ${MANAGER_SCRIPT} start &&
        log -deb "unit_lib:start_managers - OpenSync managers started - Success" ||
        raise "Issue during OpenSync manager start" -l "unit_lib:start_managers" -ds

    # Check dm slave PID
    # shellcheck disable=2091
    PID=$($(get_process_cmd) | grep -e "${OPENSYNC_ROOTDIR}/bin/dm" | grep -v 'grep' | grep -v slave | awk '{ print $1 }')
    if [ -z "$PID" ]; then
        raise "Issue during manager start, dm slave not running" -l "unit_lib:start_managers" -ds
    else
        log -deb "unit_lib:start_managers - dm slave PID = $PID"
    fi

    # Check dm master PID
    # shellcheck disable=2091
    PID=$($(get_process_cmd) | grep -e "${OPENSYNC_ROOTDIR}/bin/dm" | grep -v 'grep' | grep -v master | awk '{ print $1 }')
    if [ -z "$PID" ]; then
        raise "Issue during manager start, dm master not running" -l "unit_lib:start_managers" -ds
    else
        log -deb "unit_lib:start_managers - dm master PID = $PID"
    fi

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function starts a single specific OpenSync manager.
#   Raises an exception if managers script is not executable or if
#   it does not exist.
# INPUT PARAMETER(S):
#   $1  manager name (string, required)
#   $2  option used with start manager (string, optional)
# RETURNS:
#   0   On success.
#   1   Manager is not executable.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   start_specific_manager cm -v
#   start_specific_manager cm -d
###############################################################################
start_specific_manager()
{
    NARGS_MIN=1
    NARGS_MAX=2
    [ $# -ge ${NARGS_MIN} ] && [ $# -le ${NARGS_MAX} ] ||
        raise "unit_lib:start_specific_manager requires ${NARGS_MIN}-${NARGS_MAX} input arguments, $# given" -arg
    manager="${OPENSYNC_ROOTDIR}/bin/$1"
    option=$2

    # Check if executable
    if [ ! -x "$manager" ]; then
        log -deb "unit_lib:start_specific_manager - Manager $manager does not exist or is not executable"
        return 1
    fi

    # Start manager
    # shellcheck disable=SC2018,SC2019
    log -deb "unit_lib:start_specific_manager - Starting $manager $option" | tr a-z A-Z

    if [ "$1" == "wm" ]; then
        ps_out=$(pgrep $manager)
        if [ $? -eq 0 ]; then
            kill -9 $ps_out && log -deb "unit_lib:start_specific_manager - Old pid killed for $manager"
        fi
        sleep 10
    fi

    $manager "$option" >/dev/null 2>&1 &
    sleep 1
}

###############################################################################
# DESCRIPTION:
#   Function stops all OpenSync managers. Executes managers script with
#   stop option. Raises an exception if managers cannot be stopped.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   stop_managers
###############################################################################
stop_managers()
{
    log -deb "unit_lib:stop_managers - Stopping OpenSync managers"
    MANAGER_SCRIPT=$(get_managers_script)
    $MANAGER_SCRIPT stop &&
        log -deb "unit_lib:stop_managers - OpenSync manager stopped - Success" ||
        raise "Issue during OpenSync manager stop" -l "unit_lib:stop_managers" -ds

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function triggers cloud reboot by creating Wifi_Test_Config table
#   and inserting reboot command to table.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   Always
# USAGE EXAMPLE(S):
#   trigger_cloud_reboot
###############################################################################
trigger_cloud_reboot()
{
    opensync_path="${1}"
    params="[\"map\",[[\"arg\",\"5\"],[\"path\",\"${opensync_path}/bin/delayed-reboot\"]]]"
    insert_ovsdb_entry Wifi_Test_Config -i params "$params" -i test_id reboot

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function updates selected field value in ovsdb table.
#   If selected field is not updated after wait time, it raises an exception.
#
#   It can be used with supported option(s):
#   -m (update method)
#
#   -w (where)  field value used as a condition to select ovsdb table column
#
#   If -w option is used then two additional parameters must follow to
#   define condition string. Several -w options are possible, but for any
#   additional -w option used, there must always be 2 additional parameters.
#   In short, optional parameters come in groups of 3.
#
#   -u (update)
#
#   -force (force)  forces update to selected field
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  option, supported options: -m, -w, -u, -force
#   $3  ovsdb field in ovsdb table (-w option); update method (-m option)
#   $4  ovsdb field value (-w option)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   update_ovsdb_entry Wifi_Inet_Config -w if_name br-home -u ip_assign_scheme static
###############################################################################
update_ovsdb_entry()
{
    ovsdb_table=$1
    shift
    conditions_string=""
    update_string=""
    update_method=":="
    force_insert=1

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -m)
                update_method="$1"
                shift
                ;;
            -w)
                conditions_string="$conditions_string -w $1==$2"
                shift 2
                ;;
            -u)
                echo ${2} | grep -e "[ \"]" -e '\\' &&
                    update_string="${update_string} ${1}${update_method}$(single_quote_arg "${2}")" ||
                    update_string="${update_string} ${1}${update_method}${2}"
                shift 2
                update_method=":="
                ;;
            -force)
                force_insert=0
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:update_ovsdb_entry" -arg
                ;;
        esac
    done

    entry_command="${OVSH} u $ovsdb_table $conditions_string $update_string"
    log -deb "unit_lib:update_ovsdb_entry - Executing update command:\n\t$entry_command"

    eval ${entry_command}
    # shellcheck disable=SC2181
    if [ "$?" -eq 0 ]; then
        log -deb "unit_lib:update_ovsdb_entry - Entry updated"
        log -deb "${OVSH} s $ovsdb_table $conditions_string"
        # shellcheck disable=SC2086
        ${OVSH} s "$ovsdb_table" $conditions_string ||
            log -deb "unit_lib:update_ovsdb_entry - Failed to print entry"
    else
        ${OVSH} s "$ovsdb_table" || log -deb "unit_lib:update_ovsdb_entry - Failed to print table $ovsdb_table"

        if [ $force_insert -eq 0 ]; then
            log -deb "unit_lib:update_ovsdb_entry - Force insert, not failing!"
        else
            raise "Could not update entry in $ovsdb_table" -l "unit_lib:update_ovsdb_entry" -fc
        fi
    fi

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function validates that CAC was completed in set CAC time for specific channel which is set in Wifi_Radio_State
#     Function is also aware of channel width and it checks CAC for all required channels in given range.
#     For example, if we set channel 52 with HT40, then CAC will be checked for channel 52 and channel 56 as well
# INPUT PARAMETER(S):
#   $1  Physical Radio interface name for which to validate CAC if needed
# RETURNS:
#   0 - In following cases:
#       - shell/config/regulatory.txt file was not found
#       - No associated, enabled and AP VIF found for specified Phy Radio interface
#       - Channel, ht_mode or freq_band is not set in Wifi_Radio_State for specified Phy Radio interface
#       - Channel which is set in Wifi_Radio_State is not DFS nor DFS-WEATHER channel
#       - CAC was at cac_completed state in Wifi_Radio_State for specific channel which is set in Wifi_Radio_State
#   1 - In following cases:
#       - Invalid number of arguments specified
#       - Failure to acquire vif_states uuid-s from Wifi_Radio_State for specified Phy Radio name
#       - CAC was not completed in given CAC time for specific channel which is set in Wifi_Radio_State
# NOTE:
# - CAC times are hardcoded inside this function and their values are following:
#   - NON-DFS : 0s (CAC is not required for NON-DFS channels)
#   - DFS     : 60s
#   - WEATHER : 600s
# - WM reconfiguration time is hardcoded to 30s
# - CAC is validated for all channels in given channel width HT40, HT80 or HT160
# DEPENDENCY:
# - Function is dependent on FUT generated regulatory.txt file config
# USAGE EXAMPLE(S):
#   validate_cac wifi0
###############################################################################
validate_cac()
{
    # First validate presence of regulatory.txt file
    regulatory_file_path="${FUT_TOPDIR}/shell/config/regulatory.txt"
    if [ ! -f "${regulatory_file_path}" ]; then
        log -deb "unit_lib:validate_cac - Regulatory file ${regulatory_file_path} does not exist, nothing to do."
        return 0
    fi

    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:validate_cac requires ${NARGS} input argument(s), $# given" -arg
    # shellcheck disable=SC2034
    if_name="${1}"

    # WM reconfiguration time - used to wait from nop_finished to cac_started channel status
    wm_reconfiguration_time=30
    # Check if Radio interface is associated to VIF ap
    vif_states=$(get_ovsdb_entry_value Wifi_Radio_State vif_states -w if_name "${if_name}")
    if [ "${vif_states}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:validate_cac - Radio interfaces is not associated to any VIF, nothing to do."
        return 0
    fi
    # Check if channel is set in Wifi_Radio_State
    state_channel=$(get_ovsdb_entry_value Wifi_Radio_State channel -w if_name "${if_name}")
    if [ "${state_channel}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:validate_cac - Channel is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi
    state_ht_mode=$(get_ovsdb_entry_value Wifi_Radio_State ht_mode -w if_name "${if_name}")
    if [ "${state_ht_mode}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:validate_cac - ht_mode is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi
    state_freq_band=$(get_ovsdb_entry_value Wifi_Radio_State freq_band -w if_name "${if_name}" | tr '[A-Z]' '[a-z]' | tr -d '.')
    if [ "${state_freq_band}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:validate_cac - freq_band is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi
    # Disable CAC check for 2.4g
    if [ "${state_freq_band}" == "24g" ]; then
        log -deb "unit_lib:validate_cac - freq_band is 24g, nothing to do."
        return 0
    fi
    # Retrieve device regulatory domain
    state_country=$(get_iface_regulatory_domain "${if_name}")
    echo "${state_country}"
    state_country=$(echo "${state_country}" | tail -1)

    # Check channel type if it requires CAC
    log -deb "unit_lib:validate_cac - Country: ${state_country} | Channel: ${state_channel} | Freq band: ${state_freq_band} | HT mode: ${state_ht_mode}"
    reg_dfs_standard_match=$(cat "${regulatory_file_path}" | grep -i "${state_country}_dfs_standard_${state_freq_band}_${state_ht_mode}")
    check_standard=$(contains_element "${state_channel}" ${reg_dfs_standard_match})

    reg_dfs_weather_match=$(cat "${regulatory_file_path}" | grep -i "${state_country}_dfs_weather_${state_freq_band}_${state_ht_mode}")
    check_weather=$(contains_element "${state_channel}" ${reg_dfs_weather_match})

    # If HT mode is HT20 and channel is not dfs nor weather, skip next steps to preserve time.
    if [ "${check_standard}" != "0" ] && [ "${check_weather}" != "0" ] && [ "${state_ht_mode}" == "HT20" ]; then
        log -deb "unit_lib:validate_cac - Channel ${state_channel} (HT20) is not DFS nor WEATHER channel so CAC wait is not required."
        return 0
    fi

    # Check if Radio is associated to any AP VIF (ignore STA vif-s)
    vif_states_uuids="$(get_ovsdb_entry_value Wifi_Radio_State vif_states -w if_name "${if_name}" -json_value uuid)"
    if [ "$?" != 0 ]; then
        raise "unit_lib:validate_cac - Failed to acquire vif_states uuid-s for ${if_name}" -ds
    fi
    # Check if there is AP VIF and is enabled for specific Radio
    vif_found=1
    for i in ${vif_states_uuids}; do
        if ! check_ovsdb_entry Wifi_VIF_State -w _uuid '["uuid",'$i']' -w mode ap; then
            continue
        fi
        if wait_ovsdb_entry Wifi_VIF_State -w _uuid '["uuid",'$i']' -w mode ap -is enabled true -t 180; then
            log -deb "unit_lib:validate_cac - Enabled and associated AP VIF found for Radio ${if_name} - Success"
            vif_found=0
            break
        fi
    done
    if [ "${vif_found}" == 1 ]; then
        raise "Radio interfaces is not associated to any AP enabled VIF" -l "unit_lib:validate_cac" -ds
    fi

    channels_to_check=$(get_channels_to_check_for_cac "${if_name}" | tail -1)

    log -deb "unit_lib:validate_cac - Acquiring channels to validate CAC for ${state_channel} in range of ${state_ht_mode} are ${channels_to_check}"
    # shellcheck disable=SC1073
    for check_channel in ${channels_to_check}; do
        check_standard=$(contains_element "${check_channel}" ${reg_dfs_standard_match})
        check_weather=$(contains_element "${check_channel}" ${reg_dfs_weather_match})
        if [ "${check_standard}" == "0" ]; then
            cac_time=60
            cac_state="cac_completed"
            log -deb "unit_lib:validate_cac - Channel ${check_channel} is standard DFS channel - CAC time ${cac_time}s"
        elif [ "${check_weather}" == "0" ]; then
            cac_time=600
            cac_state="cac_completed"
            log -deb "unit_lib:validate_cac - Channel ${check_channel} is weather DFS channel - CAC time ${cac_time}s"
        else
            cac_time=1
            cac_state="allowed"
            log -deb "unit_lib:validate_cac - Channel ${check_channel} is standard channel - CAC time 1s"
        fi
        wait_for_function_output -of "${cac_state} nop_finished nop_started" "get_radio_channel_state ${check_channel} ${if_name}" ${cac_time} &&
            log -deb "unit_lib:validate_cac - Channel state went to ${cac_state}. Channel available" ||
            log -err "unit_lib:validate_cac - Channel state did not went to ${cac_state}. Channel unavailable"

        log -deb "unit_lib:validate_cac - Checking interface ${if_name} channel ${check_channel} status"
        channel_status="$(get_radio_channel_state "${check_channel}" "${if_name}")"
        log -deb "unit_lib:validate_cac - Channel status is: ${channel_status}"
        if [ "${channel_status}" == "${cac_state}" ]; then
            log -deb "unit_lib:validate_cac - Channel ${check_channel} available - Success"
        elif [ "${channel_status}" == "nop_finished" ]; then
            log -deb "unit_lib:validate_cac - Channel ${check_channel} started recalculation, channel status is nop_finished - Success"
            log -deb "unit_lib:validate_cac - Waiting channel ${check_channel} status cac_started - Success"
            # WM recalculation time is 30s
            wait_for_function_output "cac_started" "get_radio_channel_state ${check_channel} ${if_name}" "${wm_reconfiguration_time}" &&
                log -deb "unit_lib:validate_cac - Channel state went to cac_started. Channel CAC started" ||
                log -err "unit_lib:validate_cac - Channel state did not went to cac_started. Channel CAC did not start, checking if nop_finished" -l "unit_lib:validate_cac" -ds
            channel_status="$(get_radio_channel_state "${check_channel}" "${if_name}")"
            log -deb "unit_lib:validate_cac - Channel state is ${channel_status}. Waiting for cac_completed"
            wait_for_function_output "${cac_state}" "get_radio_channel_state ${check_channel} ${if_name}" ${cac_time} &&
                log -deb "unit_lib:validate_cac - Channel state went to ${cac_state}. Channel available" ||
                log -err "unit_lib:validate_cac - Channel state did not went to ${cac_state}. Channel unavailable"
            channel_status="$(get_radio_channel_state "${check_channel}" "${if_name}")"
            if [ "${channel_status}" == "cac_completed" ]; then
                log -deb "unit_lib:validate_cac - Channel state is ${cac_state}. Channel available"
            elif [ "${channel_status}" == "nop_finished" ]; then
                raise "Channel state is nop_finished. Channel is not cac_completed" -l "unit_lib:validate_cac" -ds
            else
                raise "Channel is unavailable. Channel state is ${channel_status}" -l "unit_lib:validate_cac" -ds
            fi
        elif [ "${channel_status}" == "nop_started" ]; then
            raise "SKIP: Channel ${check_channel} NOP time started, channel  unavailable" -l "unit_lib:validate_cac" -s
        else
            print_tables Wifi_Radio_State || true
            raise "Channel ${check_channel} is not available or ready for use" -l "unit_lib:validate_cac" -ds
        fi
    done
}

###############################################################################
# DESCRIPTION:
#   Function validate the format of MAC address and
#   returns 0 (true) it MAC is valid or 1 (false) if not.
# INPUT PARAMETER(S):
#   $1 MAC address
# RETURNS:
#   O (true) or 1 (false)
# USAGE EXAMPLES(S):
#   validate_mac "e8:9f:80:ad:68:73"
###############################################################################
validate_mac()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:validate_mac requires ${NARGS} input argument(s), $# given" -arg
    mac_address=$1

    # No logging, this function echoes the requested value to caller!
    echo "$mac_address" | grep -Eq '^([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}$' && return 0 || return 1
}

validate_pre_cac_behaviour()
{
    # First validate presence of regulatory.txt file
    regulatory_file_path="${FUT_TOPDIR}/shell/config/regulatory.txt"
    if [ ! -f "${regulatory_file_path}" ]; then
        log -deb "unit_lib:validate_pre_cac_behaviour - Regulatory file ${regulatory_file_path} does not exist, nothing to do."
        return 0
    fi

    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:validate_pre_cac_behaviour requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1
    reg_domain=$2

    state_ht_mode=$(get_ovsdb_entry_value Wifi_Radio_State ht_mode -w if_name "${if_name}")
    if [ "${state_ht_mode}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:validate_pre_cac_behaviour - ht_mode is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi
    state_freq_band=$(get_ovsdb_entry_value Wifi_Radio_State freq_band -w if_name "${if_name}" | tr '[A-Z]' '[a-z]' | tr -d '.')
    if [ "${state_freq_band}" == "[\"set\",[]]" ]; then
        log -deb "unit_lib:validate_pre_cac_behaviour - freq_band is not set in Wifi_Radio_State, nothing to do."
        return 0
    fi

    reg_dfs_standard_match=$(cat "${regulatory_file_path}" | grep -i "${reg_domain}_dfs_standard_${state_freq_band}_${state_ht_mode}")
    reg_dfs_weather_match=$(cat "${regulatory_file_path}" | grep -i "${reg_domain}_dfs_weather_${state_freq_band}_${state_ht_mode}")
    cac_channels=$(get_channels_to_check_for_cac "${if_name}" | tail -1)

    if [ -z "${cac_channels}" ]; then
        log -deb "unit_lib:validate_pre_cac_behaviour - No channels to do CAC on. Nothing to do."
        return 0
    fi

    for check_channel in ${cac_channels}; do
        check_standard=$(contains_element "${check_channel}" ${reg_dfs_standard_match})
        check_weather=$(contains_element "${check_channel}" ${reg_dfs_weather_match})
        check_cac_state="cac_completed"
        if [ "${check_weather}" != "0" ] && [ "${check_standard}" != "0" ]; then
            check_cac_state="allowed"
        fi
        wait_for_function_output "${check_cac_state}" "get_radio_channel_state ${check_channel} ${if_name}" 60 &&
            log -deb "unit_lib:validate_pre_cac_behaviour - Channel state is cac_completed. Channel available" ||
            raise "Channel state did is not cac_completed" -l "unit_lib:validate_pre_cac_behaviour" -tc
    done

    # Acquire all allowed channels for interface and validate pre-CAC
    allowed_channels=$(get_allowed_channels_for_interface "${if_name}")
    for allowed_channel in ${allowed_channels}; do
        contains_element "${allowed_channel}" ${cac_channels} && continue
        # pre-CAC is disabled for US reg domain, any channels outside ch range should not be in cac_completed
        if [ "${reg_domain}" == 'US' ]; then
            wait_for_function_output -of "nop_finished nop_started allowed" "get_radio_channel_state ${allowed_channel} ${if_name}" 60
            al_ch_check=$?
            ch_state=$(get_radio_channel_state ${allowed_channel} ${if_name})
            if [ "${al_ch_check}" == "0" ]; then
                log -deb "unit_lib:validate_pre_cac_behaviour - Channel ${allowed_channel} state is ${ch_state}"
            else
                raise "Channel ${allowed_channel} state is ${ch_state}. It should not be since pre-CAC is disabled." -l "unit_lib:validate_pre_cac_behaviour" -tc
            fi
        else
            wait_for_function_output -of "cac_completed cac_started nop_finished nop_started allowed" "get_radio_channel_state ${allowed_channel} ${if_name}" 60
            al_ch_check=$?
            ch_state=$(get_radio_channel_state ${allowed_channel} ${if_name})
            ch_in_cac=$(contains_element "${ch_state}" "cac_completed cac_started")
            if [ "${ch_in_cac}" == "0" ]; then
                log -deb "unit_lib:validate_pre_cac_behaviour - Channel ${allowed_channel} state is ${ch_state}. PRE-CAC is working."
            else
                log -deb "unit_lib:validate_pre_cac_behaviour - Channel ${allowed_channel} state is ${ch_state}."
            fi
        fi
    done
}

###############################################################################
# DESCRIPTION:
#   Function takes interface as input, to see if channel is even supported
#   Takes desired channel as input, to check if its in NOP_FINISHED state.
#   If it is, echo this channel, as the desired one fits the criteria.
#   If not, take the excluded channel as input, to filter out of the available channels.
#   Find the first alternative, that is in NOP_FINISHED state and echoes the same.
#   Raises exception:
#       1. If channel is not allowed on the selected radio.
#       2. If no alternate channels in NOP_FINISHED state are found.
#
# INPUT PARAMETER(S):
#   $1  Radio interface (string, required)
#   $2  Channel (int, required)
#   $3  Alternative channel if first is unusable (int, required)
# RETURNS:
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   verify_channel_is_in_nop_finished wifi2 120 124
###############################################################################
verify_channel_is_in_nop_finished()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:verify_channel_is_in_nop_finished requires ${NARGS} input argument(s), $# given" -arg
    if_name=${1}
    channel_1=${2}
    channel_2=${3}

    # Sanity check - are channels even allowed on the radio
    check_is_channel_allowed "$channel_1" "$if_name" >/dev/null 2>&1 ||
        raise "Channel $channel_1 is not allowed on radio $if_name" -l "unit_lib:verify_channel_is_in_nop_finished" -ds

    # Echo channel_1 if it is in nop_finished state for the test.
    check_is_nop_finished "$channel_1" "$if_name" >/dev/null 2>&1
    [ $? = 0 ] && echo "${channel_1}" && return

    # If channel_1 is not in nop_finished state, iterate for new channel. If not found raise the exception
    get_chan_list=$(get_ovsdb_entry_value Wifi_Radio_State allowed_channels -w if_name "$if_name" -r)
    list_of_chans=$(echo "${get_chan_list}" | cut -d '[' -f3 | cut -d ']' -f1 | sed "s/,/ /g")
    [ -z "$list_of_chans" ] &&
        raise "Wifi_Radio_State::allowed_channels not populated" -l "unit_lib:verify_channel_is_in_nop_finished" -ds

    # Get the first channel in list that has state NOP_FINISHED and
    # is not the one provided in the argument.
    for channel in ${list_of_chans}; do
        [ "$channel" -eq "$channel_2" ] && continue
        check_is_nop_finished "$channel" "$if_name" >/dev/null 2>&1
        [ $? = 0 ] && echo "$channel" && return
    done

    raise "Could not find alternative channel in NOP_FINISHED state" -l "unit_lib:verify_channel_is_in_nop_finished" -s
}

###############################################################################
# DESCRIPTION:
#   Function verifies the validity of the client certificate by checking on
#   the signature and other parameters.
#   Raises exception if one of the following fails:
#       i. Client certificate format is invalid(Not PEM format)
#       ii. If CA certificate is not approved by Plume CA
#       iii. If certificate is not signed by the CA and/or
#            validity expired.
# INPUT PARAMETER(S):
#   $1  client certificate (string, required)
#   $2  CA certificate used to validate client certificate (string, required)
#   $3  Plume CA (string, required)
# RETURNS:
#   See DESCRIPTION
# USAGE EXAMPLE(S):
#   verify_client_certificate_file client.pem ca.pem ca_chain.pem
###############################################################################
verify_client_certificate_file()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:verify_client_certificate_file requires ${NARGS} input argument(s), $# given" -arg
    client_cert=${1}
    ca_cert=${2}
    plume_ca=${3}

    cert_file="${FUT_TOPDIR}/${client_cert}"
    ca_file="${FUT_TOPDIR}/${ca_cert}"
    plume_ca_file="${FUT_TOPDIR}/shell/tools/server/files/${plume_ca}"

    openssl x509 -in $cert_file -noout > /dev/null
    [ $? -eq 0 ] &&
        log "unit_lib:verify_client_certificate_file - Certificate ${client_cert} is in valid PEM format" ||
        raise "Certificate ${client_cert} format is not valid. Expected format of the certificate is PEM!" -l "unit_lib:verify_client_certificate_file" -tc

    openssl verify -verbose -CAfile $plume_ca_file $ca_file > /dev/null
    [ $? -eq 0 ] &&
        log "unit_lib:verify_client_certificate_file - CA certificate: ${ca_cert} approved by Plume CA: $plume_ca_file" ||
        raise "CA Certificate: ${ca_cert} not approved by Plume CA: $plume_ca_file" -l "unit_lib:verify_client_certificate_file" -tc

    end_date=$(openssl x509 -enddate -noout -in $cert_file | cut -d'=' -f2-)
    openssl x509 -checkend 0 -noout -in $cert_file > /dev/null
    [ $? -eq 0 ] &&
        log "unit_lib:verify_client_certificate_file - Certificate ${client_cert} is not expired, valid until $end_date" ||
        raise "Certificate ${client_cert} has expired on $end_date" -l "unit_lib:verify_client_certificate_file" -tc
}

###############################################################################
# DESCRIPTION:
#   Function resets VIF STA interfaces and removes all VIF AP interfaces from
#   the Wifi_VIF_Config table and waits for Wifi_VIF_State table to reflect.
#   Specific interface names, which should be reset, can be passed to this script
#   as optional arguments. Raises exception on failure.
# INPUT PARAMETER(S):
#   [interface1] [interface2] ... (str, optional)
# RETURNS:
#   0 On Success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   vif_reset
#   vif_reset b-ap-24
###############################################################################
vif_reset()
{
    # Reset specific VIFs
    if [ $# -ne 0 ]; then
        log -deb "unit_lib:vif_reset - Resetting VIFs: $*"
        for iface in "$@"; do
            iface_mode=$(get_ovsdb_entry_value Wifi_VIF_Config mode -w if_name "$iface")
            if [ "$iface_mode" = "ap" ]; then
                remove_ap_interface "$iface" ||
                    raise "remove_ap_interface - Could not remove AP interface in Wifi_VIF_Config table" -l "unit_lib:vif_reset" -fc
            else
                reset_sta_interface "$iface" ||
                    raise "reset_sta_interface - Could not reset STA interface in Wifi_VIF_Config table" -l "unit_lib:vif_reset" -fc
            fi
        done
    else
        log -deb "unit_lib:vif_reset - Resetting VIFs"

        # Reset all STA VIFs
        sta_iface_list=$(get_ovsdb_entry_value Wifi_VIF_Config if_name -w mode sta)
        for sta_iface in $sta_iface_list; do
            reset_sta_interface $sta_iface ||
                raise "reset_sta_interface - Could not reset STA interface in Wifi_VIF_Config table" -l "unit_lib:vif_reset" -fc
        done

        # Remove all AP VIFs
        ap_iface_list=$(get_ovsdb_entry_value Wifi_VIF_Config if_name -w mode ap)
        for ap_iface in $ap_iface_list; do
            remove_ap_interface "$ap_iface" ||
                raise "remove_ap_interface - Could not remove AP interface in the Wifi_VIF_Config table" -l "unit_lib:vif_reset" -fc
        done

        log -deb "unit_lib:vif_reset- VIF interfaces reset - Success"
        return 0
    fi
}

###############################################################################
# DESCRIPTION:
#   Function waits for Cloud status in Manager table to become
#   as provided in parameter.
#   Cloud status can be one of:
#       ACTIVE          device is connected to the Cloud.
#       BACKOFF         device could not connect to the Cloud, will retry.
#       CONNECTING      connecting to the Cloud in progress.
#       DISCONNECTED    device is disconnected from the Cloud.
#   Raises an exception on fail.
# INPUT PARAMETER(S):
#   $1  Desired Cloud state (string, required)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   wait_cloud_state ACTIVE
###############################################################################
wait_cloud_state()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "unit_lib:wait_cloud_state requires ${NARGS} input argument(s), $# given" -arg
    wait_for_cloud_status=$1

    log "unit_lib:wait_cloud_state - Waiting for the FUT cloud status $wait_for_cloud_status"
    wait_for_function_response 0 "${OVSH} s Manager status -r | grep \"$wait_for_cloud_status\"" &&
        log -deb "unit_lib:wait_cloud_state - FUT cloud status is $wait_for_cloud_status" ||
        raise "FUT cloud status is not $wait_for_cloud_status" -l "unit_lib:wait_cloud_state" -fc
}

###############################################################################
# DESCRIPTION:
#   Function waits for Cloud status in Manager table not to become
#   as provided in parameter.
#   Cloud status can be one of:
#       ACTIVE          device is connected to Cloud.
#       BACKOFF         device could not connect to Cloud, will retry.
#       CONNECTING      connecting to Cloud in progress.
#       DISCONNECTED    device is disconnected from Cloud.
#   Raises an exception on fail.
# INPUT PARAMETER(S):
#   $1  un-desired cloud state (string, required)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   wait_cloud_state_not ACTIVE
###############################################################################
wait_cloud_state_not()
{
    local NARGS=1
    [ $# -lt ${NARGS} ] &&
        raise "unit_lib:wait_cloud_state_not requires ${NARGS} input argument(s), $# given" -arg
    wait_for_cloud_state_not=${1}
    wait_for_cloud_state_not_timeout=${2:-60}

    log "unit_lib:wait_cloud_state_not - Waiting for cloud state not to be $wait_for_cloud_state_not"
    wait_for_function_response 0 "${OVSH} s Manager status -r | grep \"$wait_for_cloud_state_not\"" "${wait_for_cloud_state_not_timeout}" &&
        raise "Manager::status is $wait_for_cloud_state_not" -l "unit_lib:wait_cloud_state_not" -fc ||
        log -deb "unit_lib:wait_cloud_state_not - Cloud state is not $wait_for_cloud_state_not"
}

###############################################################################
# DESCRIPTION:
#   Function waits for expected exit code, not stdout/stderr output.
#   Raises an exception if timeouts.
# INPUT PARAMETER(S):
#   $1  expected exit code (int, required)
#   $2  function call, function returning value (string, required)
#   $3  retry count, number of iterations to stop checks
#                    (int, optional, default=DEFAULT_WAIT_TIME)
#   $4  retry sleep, time in seconds between checks (int, optional, default=1)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   wait_for_function_exit_code 0 <function_to_wait_for> 30 1
###############################################################################
wait_for_function_exit_code()
{
    NARGS_MIN=2
    NARGS_MAX=4
    [ $# -ge ${NARGS_MIN} ] && [ $# -le ${NARGS_MAX} ] ||
        raise "unit_lib:wait_for_function_exit_code requires ${NARGS_MIN}-${NARGS_MAX} input arguments, $# given" -arg
    local exp_ec=$1
    local function_to_wait_for=$2
    local retry_count=${3:-$DEFAULT_WAIT_TIME}
    local retry_sleep=${4:-1}
    local fn_exec_cnt=1

    log -deb "unit_lib:wait_for_function_exit_code - Executing $function_to_wait_for, waiting for exit code ${exp_ec}"
    $function_to_wait_for
    local act_ec=$?
    while [ ${act_ec} -ne "${exp_ec}" ]; do
        log -deb "unit_lib:wait_for_function_exit_code - Retry ${fn_exec_cnt}, exit code: ${act_ec}, expecting: ${exp_ec}"
        if [ ${fn_exec_cnt} -ge "${retry_count}" ]; then
            log -err "unit_lib:wait_for_function_exit_code: Function ${function_to_wait_for} timed out"
            return $?
        fi
        sleep "${retry_sleep}"
        $function_to_wait_for
        act_ec=$?
        fn_exec_cnt=$(( $fn_exec_cnt + 1 ))
    done

    log -deb "unit_lib:wait_for_function_exit_code - Exit code: ${act_ec} equal to expected: ${exp_ec}"

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function waits for expected output from provided function call,
#   but not its exit code.
#   Raises an exception if times out.
#   Supported expected values are "empty", "notempty" or custom.
# INPUT PARAMETER(S):
#   (optional) $1 = -of : If first arguments is equal to -of (one-of)
#     Script will wait for one of values given in the wait for output value
#       Example:
#         wait_for_function_output "value1 value2 value3" "echo value3" 30 1
#         Script will wait for one of values (split with space!) value1, value2 or value3
#   $1  wait for output value (int, required)
#   $2  function call, function returning value (string, required)
#   $3  retry count, number of iterations to stop checks
#                    (int, optional, default=DEFAULT_WAIT_TIME)
#   $4  retry_sleep, time in seconds between checks (int, optional, default=1)
# RETURNS:
#   0   On success.
#   1   On fail.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   wait_for_function_output "notempty" <function_to_wait_for> 30 1
###############################################################################
wait_for_function_output()
{
    NARGS_MIN=2
    NARGS_MAX=5
    [ $# -ge ${NARGS_MIN} ] && [ $# -le ${NARGS_MAX} ] ||
        raise "unit_lib:wait_for_function_output requires ${NARGS_MIN}-${NARGS_MAX} input arguments, $# given" -arg
    local one_of_values="false"
    if [ "${1}" == "-of" ]; then
        one_of_values="true"
        shift
    fi
    local wait_for_value=${1}
    local function_to_wait_for=${2}
    local retry_count=${3:-$DEFAULT_WAIT_TIME}
    local retry_sleep=${4:-1}
    local fn_exec_cnt=0
    local is_get_ovsdb_entry_value=0

    [ $(echo "$function_to_wait_for" | grep -wF "get_ovsdb_entry_value") ] &&
        is_get_ovsdb_entry_value=1

    log -deb "unit_lib:wait_for_function_output - Executing $function_to_wait_for, waiting for $wait_for_value response"
    while [ $fn_exec_cnt -le $retry_count ]; do
        fn_exec_cnt=$(( $fn_exec_cnt + 1 ))

        res=$($function_to_wait_for)
        if [ "$wait_for_value" = 'notempty' ]; then
            if [ $is_get_ovsdb_entry_value ]; then
                [ -n "$res" ] && [ "$res" != '["set",[]]' ] && [ "$res" != '["map",[]]' ] && return 0
            else
                [ -n "$res" ] &&
                    break
            fi
        elif [ "$wait_for_value" = 'empty' ]; then
            if [ $is_get_ovsdb_entry_value ]; then
                [ -z "$res" ] || [ "$res" = '["set",[]]' ] || [ "$res" = '["map",[]]' ] && return 0
            else
                [ -z "$res" ] &&
                    break
            fi
        else
            if [ "${one_of_values}" == "true" ]; then
                for wait_value in ${wait_for_value}; do
                    [ "$res" == "$wait_value" ] && return 0
                done
            else
                [ "$res" == "$wait_for_value" ] && return 0
            fi
        fi
        log -deb "unit_lib:wait_for_function_output - Function retry ${fn_exec_cnt} output: ${res}"
        sleep "${retry_sleep}"
    done

    if [ $fn_exec_cnt -gt "$retry_count" ]; then
        raise "Function $function_to_wait_for timed out" -l "unit_lib:wait_for_function_output"
        return 1
    else
        return 0
    fi
}

###############################################################################
# DESCRIPTION:
#   Function waits for expected return value from provided function call.
#   Responses can be: return values, empty, notempty.
#
#   return value (exit code): waits for the provided command to return the
#               expected exit code. Useful for commands that fail for some
#               time and succeed after some time, like "ping" or "grep"
#
#   "empty": has several meanings, it succeeds if the result of a command
#            (usually "ovsh") is blank (no echo), or the field value is
#            "unset", so it matches '["set",[]]' or '["map",[]]'
#
#   "notempty": the inverse of the above: if the command is an "ovsh" command,
#               any non-empty value means success (not blank or
#               not '["set",[]]' or not '["map",[]]').
#
# INPUT PARAMETER(S):
#   $1  value to wait for (int, required)
#   $2  function call (string, required)
#   $3  wait timeout in seconds (int, optional)
# RETURNS:
#   0   On success.
#   1   Function did not return expected value within timeout.
# USAGE EXAMPLE(S):
#   wait_for_function_response 0 "check_number_of_radios 3"
#   wait_for_function_response 1 "check_dhcp_from_dnsmasq_conf wifi0 10.10.10.16 10.10.10.32"
###############################################################################
wait_for_function_response()
{
    NARGS_MIN=2
    NARGS_MAX=3
    [ $# -ge ${NARGS_MIN} ] && [ $# -le ${NARGS_MAX} ] ||
        raise "unit_lib:wait_for_function_response requires ${NARGS_MIN}-${NARGS_MAX} input arguments, $# given" -arg
    wait_for_value="$1"
    function_to_wait_for="$2"
    wait_time=${3:-$DEFAULT_WAIT_TIME}
    func_exec_time=0
    is_get_ovsdb_entry_value=1
    local retval=1

    if [ "$wait_for_value" = 'empty' ]; then
        log -deb "unit_lib:wait_for_function_response - Waiting for function $function_to_wait_for empty response"
    elif [ "$wait_for_value" = 'notempty' ]; then
        log -deb "unit_lib:wait_for_function_response - Waiting for function $function_to_wait_for not empty response"
        echo "$function_to_wait_for" | grep -q "get_ovsdb_entry_value" && is_get_ovsdb_entry_value=0
    else
        log -deb "unit_lib:wait_for_function_response - Waiting for function $function_to_wait_for exit code $wait_for_value"
    fi

    while [ $func_exec_time -le $wait_time ]; do
        log -deb "unit_lib:wait_for_function_response - Executing: $function_to_wait_for"
        func_exec_time=$((func_exec_time+1))

        if [ "$wait_for_value" = 'empty' ] || [ "$wait_for_value" = 'notempty' ]; then
            res=$(eval "$function_to_wait_for" || echo 1)
            if [ -n "$res" ]; then
                if [ "$is_get_ovsdb_entry_value" -eq 0 ]; then
                    if [ "$res" = '["set",[]]' ] || [ "$res" = '["map",[]]' ]; then
                        function_res='empty'
                    else
                        function_res='notempty'
                    fi
                else
                    function_res='notempty'
                fi
            else
                function_res='empty'
            fi
        else
            eval "$function_to_wait_for" && function_res=0 || function_res=1
        fi

        log -deb "unit_lib:wait_for_function_response - Function response/code is $function_res"

        if [ "$function_res" = "$wait_for_value" ]; then
            retval=0
            break
        fi

        sleep 1
    done

    if [ $retval = 1 ]; then
        log -deb "unit_lib:wait_for_function_response - Function $function_to_wait_for timed out"
    fi
    return $retval
}

###############################################################################
# DESCRIPTION:
#   Function waits for entry in ovsdb table to become
#   expected value or satisfy condition. Waits for default wait time
#   It can be used with supported option(s):
#
#   -w (where)  field value used as a condition to select ovsdb column
#   -wn (where not) field value used as a condition to ignore ovsdb column
#
#   If -w or -wn option is used then two additional parameters must follow to
#   define condition string. Several -w options are possible, but for any
#   additional -w option used, there must always be 2 additional parameters.
#   In short, optional parameters come in groups of 3.
#
#   -is             value is as provided in parameter.
#   -is_not         value is not as provided in parameter.
#
#   If -is or -is_not option is used then two additional parameters must
#   follow to define condition string. Several options are possible, but for
#   any additional option used, there must always be 2 additional parameters.
#   In short, optional parameters come in groups of 3
#
#   -ec             exit code is used as a condition
#   -ec option requires 1 additional parameter specifying exit code.
#
#   -t              timeout in seconds
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  option, supported options: -w, -wn, -is, -is_not, -ec
#   $3  ovsdb field in ovsdb table, exit code
#   $4  ovsdb field value
# RETURNS:
#   0   On success.
#   1   Value is not as required within timeout.
# USAGE EXAMPLE(S):
#   wait_ovsdb_entry Manager -is is_connected true
#   wait_ovsdb_entry Wifi_Inet_State -w if_name eth0 -is NAT true
#   wait_ovsdb_entry Wifi_Radio_State -w if_name wifi0 \
#   -is channel 1 -is ht_mode HT20 -t 60
###############################################################################
wait_ovsdb_entry()
{
    ovsdb_table=$1
    shift
    conditions_string=""
    where_is_string=""
    where_is_not_string=""
    expected_ec=0
    ovsh_cmd=${OVSH}
    wait_entry_not_equal_command=""
    wait_entry_not_equal_command_ec="0"
    wait_entry_equal_command_ec="0"

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -w)
                echo ${2} | grep -e "[ \"]" -e '\\' &&
                    conditions_string="$conditions_string -w $1==$(single_quote_arg "${2}")" ||
                    conditions_string="$conditions_string -w $1==$2"
                shift 2
                ;;
            -wn)
                echo ${2} | grep -e "[ \"]" -e '\\' &&
                    conditions_string="$conditions_string -w $1!=$(single_quote_arg "${2}")" ||
                    conditions_string="$conditions_string -w $1!=$2"
                shift 2
                ;;
            -is)
                echo ${2} | grep -e "[ \"]" -e '\\' &&
                    where_is_string="$where_is_string $1:=$(single_quote_arg "${2}")" ||
                    where_is_string="$where_is_string $1:=$2"
                shift 2
                ;;
            -is_not)
                # Due to ovsh limitation, in -n option, we need to seperatly wait for NOT equal part
                echo ${2} | grep -e "[ \"]" -e '\\' &&
                    where_is_not_string="$where_is_not_string -n $1:=$(single_quote_arg "${2}")" ||
                    where_is_not_string="$where_is_not_string -n $1:=$2"
                shift 2
                ;;
            -ec)
                expected_ec=1
                ;;
            -t)
                # Timeout is given in seconds, ovsh takes milliseconds
                ovsh_cmd="${ovsh_cmd} --timeout ${1}000"
                shift
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:wait_ovsdb_entry" -arg
                ;;
        esac
    done

    if [ -n "${where_is_string}" ]; then
        wait_entry_equal_command="$ovsh_cmd wait $ovsdb_table $conditions_string $where_is_string"
    fi

    if [ -n "${where_is_not_string}" ]; then
        wait_entry_not_equal_command="$ovsh_cmd wait $ovsdb_table $conditions_string $where_is_not_string"
    fi

    if [ -n "${wait_entry_equal_command}" ]; then
        log "unit_lib:wait_ovsdb_entry - Waiting for entry:\n\t$wait_entry_equal_command"
        eval ${wait_entry_equal_command}
        wait_entry_equal_command_ec="$?"
    fi

    if [ -n "${wait_entry_not_equal_command}" ]; then
        log -deb "unit_lib:wait_ovsdb_entry - Waiting for entry:\n\t$wait_entry_not_equal_command"
        eval ${wait_entry_not_equal_command}
        wait_entry_not_equal_command_ec="$?"
    fi

    if [ "${wait_entry_equal_command_ec}" -eq "0" ] && [ "${wait_entry_not_equal_command_ec}" -eq "0" ]; then
        wait_entry_final_ec="0"
    else
        wait_entry_final_ec="1"
    fi

    if [ "$wait_entry_final_ec" -eq "$expected_ec" ]; then
        log -deb "unit_lib:wait_ovsdb_entry - $wait_entry_equal_command - Success"
        # shellcheck disable=SC2086
        eval "${OVSH} s ${ovsdb_table} ${conditions_string}" || log -err "unit_lib:wait_ovsdb_entry: Failed to select entry: ${OVSH} s $ovsdb_table $conditions_string"
        return 0
    else
        log -deb "unit_lib:wait_ovsdb_entry - FAIL: Table $ovsdb_table"
        ${OVSH} s "$ovsdb_table" || log -err "unit_lib:wait_ovsdb_entry: Failed to print table: ${OVSH} s $ovsdb_table"
        log -deb "unit_lib:wait_ovsdb_entry - FAIL: $wait_entry_equal_command"
        return 1
    fi
}

###############################################################################
# DESCRIPTION:
#   Function waits removal of selected entry from ovsdb table. Always
#   waits for default wait time (DEFAULT_WAIT_TIME). If selected entry is not
#   removed after wait time, it raises an exception.
#
#   It can be used with supported option(s):
#   -w (where)  field value used as a condition to select ovsdb table column
#
#   If -w option is used then two additional parameters must follow to
#   define condition string. Several -w options are possible, but for any
#   additional -w option used, there must always be 2 additional parameters.
#   In short, optional parameters come in groups of 3.
#
# INPUT PARAMETER(S):
#   $1  ovsdb table (string, required)
#   $2  option, supported options: -w (string, optional, see DESCRIPTION)
#   $3  ovsdb field in ovsdb table (string, optional, see DESCRIPTION)
#   $4  ovsdb field value (string, optional, see DESCRIPTION)
# RETURNS:
#   0   On success.
#   1   On fail.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   wait_ovsdb_entry_remove Wifi_VIF_Config -w vif_radio_idx 2 -w ssid custom_ssid
###############################################################################
wait_ovsdb_entry_remove()
{
    ovsdb_table=$1
    shift
    conditions_string=""
    info_string="unit_lib:wait_ovsdb_entry_remove - Waiting for entry removal:\n"

    while [ -n "$1" ]; do
        option=$1
        shift
        case "$option" in
            -w)
                conditions_string="$conditions_string -w $1==$2"
                info_string="$info_string where $1 is $2\n"
                shift 2
                ;;
            *)
                raise "Wrong option provided: $option" -l "unit_lib:wait_ovsdb_entry_remove" -arg
                ;;
        esac
    done

    log "$info_string"
    select_entry_command="$ovsdb_table $conditions_string"
    wait_time=0
    while [ $wait_time -le $DEFAULT_WAIT_TIME ]; do
        wait_time=$((wait_time+1))

        # shellcheck disable=SC2086
        entry_select=$(${OVSH} s $select_entry_command) || true
        if [ -z "$entry_select" ]; then
            break
        fi

        sleep 1
    done

    if [ $wait_time -gt "$DEFAULT_WAIT_TIME" ]; then
        raise "Could not remove entry from $ovsdb_table" -l "unit_lib:wait_ovsdb_entry_remove" -fc
        return 1
    else
        log -deb "unit_lib:wait_ovsdb_entry_remove - Entry deleted - Success"
        return 0
    fi
}
