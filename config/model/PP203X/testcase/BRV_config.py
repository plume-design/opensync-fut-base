test_cfg = {
    "brv_busybox_builtins": [
        {
            "busybox_builtin": "[",
        },
        {
            "busybox_builtin": "[[",
        },
        {
            "busybox_builtin": "arping",
        },
        {
            "busybox_builtin": "ash",
        },
        {
            "busybox_builtin": "awk",
        },
        {
            "busybox_builtin": "base64",
        },
        {
            "busybox_builtin": "basename",
        },
        {
            "busybox_builtin": "cat",
        },
        {
            "busybox_builtin": "chmod",
        },
        {
            "busybox_builtin": "cmp",
        },
        {
            "busybox_builtin": "cp",
        },
        {
            "busybox_builtin": "cut",
        },
        {
            "busybox_builtin": "date",
        },
        {
            "busybox_builtin": "dd",
        },
        {
            "busybox_builtin": "devmem",
        },
        {
            "busybox_builtin": "df",
        },
        {
            "busybox_builtin": "dirname",
        },
        {
            "busybox_builtin": "dmesg",
        },
        {
            "busybox_builtin": "du",
        },
        {
            "busybox_builtin": "echo",
        },
        {
            "busybox_builtin": "egrep",
        },
        {
            "busybox_builtin": "env",
        },
        {
            "busybox_builtin": "expr",
        },
        {
            "busybox_builtin": "false",
        },
        {
            "busybox_builtin": "find",
        },
        {
            "busybox_builtin": "free",
        },
        {
            "busybox_builtin": "grep",
        },
        {
            "busybox_builtin": "gzip",
        },
        {
            "busybox_builtin": "halt",
        },
        {
            "busybox_builtin": "head",
        },
        {
            "busybox_builtin": "hexdump",
        },
        {
            "busybox_builtin": "kill",
        },
        {
            "busybox_builtin": "killall",
        },
        {
            "busybox_builtin": "ln",
        },
        {
            "busybox_builtin": "logger",
        },
        {
            "busybox_builtin": "ls",
        },
        {
            "busybox_builtin": "lspci",
        },
        {
            "busybox_builtin": "md5sum",
        },
        {
            "busybox_builtin": "mkdir",
        },
        {
            "busybox_builtin": "mkfifo",
        },
        {
            "busybox_builtin": "mktemp",
        },
        {
            "busybox_builtin": "mount",
        },
        {
            "busybox_builtin": "mv",
        },
        {
            "busybox_builtin": "nc",
        },
        {
            "busybox_builtin": "netstat",
        },
        {
            "busybox_builtin": "nslookup",
        },
        {
            "busybox_builtin": "passwd",
        },
        {
            "busybox_builtin": "pgrep",
        },
        {
            "busybox_builtin": "pidof",
        },
        {
            "busybox_builtin": "pivot_root",
        },
        {
            "busybox_builtin": "printf",
        },
        {
            "busybox_builtin": "ps",
        },
        {
            "busybox_builtin": "pwd",
        },
        {
            "busybox_builtin": "readlink",
        },
        {
            "busybox_builtin": "reboot",
        },
        {
            "busybox_builtin": "rm",
        },
        {
            "busybox_builtin": "rmdir",
        },
        {
            "busybox_builtin": "route",
        },
        {
            "busybox_builtin": "sed",
        },
        {
            "busybox_builtin": "seq",
        },
        {
            "busybox_builtin": "sh",
        },
        {
            "busybox_builtin": "sleep",
        },
        {
            "busybox_builtin": "sort",
        },
        {
            "busybox_builtin": "start-stop-daemon",
        },
        {
            "busybox_builtin": "sync",
        },
        {
            "busybox_builtin": "tail",
        },
        {
            "busybox_builtin": "tar",
        },
        {
            "busybox_builtin": "tee",
        },
        {
            "busybox_builtin": "test",
        },
        {
            "busybox_builtin": "timeout",
        },
        {
            "busybox_builtin": "touch",
        },
        {
            "busybox_builtin": "tr",
        },
        {
            "busybox_builtin": "true",
        },
        {
            "busybox_builtin": "udhcpc",
        },
        {
            "busybox_builtin": "umount",
        },
        {
            "busybox_builtin": "uname",
        },
        {
            "busybox_builtin": "uptime",
        },
        {
            "busybox_builtin": "vconfig",
        },
        {
            "busybox_builtin": "vi",
        },
        {
            "busybox_builtin": "wc",
        },
        {
            "busybox_builtin": "wget",
        },
        {
            "busybox_builtin": "which",
        },
        {
            "busybox_builtin": "xargs",
        },
        {
            "busybox_builtin": "yes",
        },
    ],
    "brv_is_script_on_system_fut": [
        {
            "system_script": "/etc/init.d/healthcheck",
        },
        {
            # $MANAGER_SCRIPT
            "system_script": "/etc/init.d/manager",
        },
        {
            # $OPENVSWITCH_SCRIPT
            "system_script": "/etc/init.d/openvswitch",
        },
        {
            "system_script": "/etc/init.d/qca-hostapd",
        },
        {
            "system_script": "/etc/init.d/qca-wpa-supplicant",
        },
        {
            "system_script": "/proc/net/vlan/config",
        },
        {
            "system_script": "/sbin/udhcpc",
        },
        {
            "ignore_collect": True,
            "ignore_collect_msg": "NOT_APPLICABLE: Testcase not applicable",
            "system_script": "/sys/class/leds/white/brightness",
        },
        {
            "system_script": "/sys/class/leds/pp203x:red:system/brightness",
        },
        {
            "system_script": "/sys/class/leds/pp203x:green:system/brightness",
        },
        {
            "system_script": "/sys/class/leds/pp203x:blue:system/brightness",
        },
        {
            "system_script": "/tmp/resolv.conf",
        },
        {
            # $OPENSYNC_ROOTDIR/etc/kconfig
            "system_script": "/usr/opensync/etc/kconfig",
        },
        {
            "system_script": "/var/etc/dnsmasq.conf",
        },
    ],
    "brv_is_tool_on_system_fut": [
        {
            "system_tool": "[",
        },
        {
            "system_tool": "[[",
        },
        {
            "system_tool": "awk",
        },
        {
            "system_tool": "basename",
        },
        {
            "system_tool": "break",
        },
        {
            "system_tool": "case",
        },
        {
            "system_tool": "cat",
        },
        {
            "system_tool": "cd",
        },
        {
            "system_tool": "chmod",
        },
        {
            "system_tool": "command",
        },
        {
            "system_tool": "curl",
        },
        {
            "system_tool": "cut",
        },
        {
            "system_tool": "date",
        },
        {
            "system_tool": "do",
        },
        {
            "system_tool": "echo",
        },
        {
            "system_tool": "eval",
        },
        {
            "system_tool": "exit",
        },
        {
            "system_tool": "export",
        },
        {
            "system_tool": "exttool",
        },
        {
            "system_tool": "false",
        },
        {
            "system_tool": "find",
        },
        {
            "system_tool": "for",
        },
        {
            "system_tool": "getopts",
        },
        {
            "system_tool": "grep",
        },
        {
            "system_tool": "head",
        },
        {
            "system_tool": "hostapd",
        },
        {
            "system_tool": "hostapd_cli",
        },
        {
            "system_tool": "if",
        },
        {
            "system_tool": "ifconfig",
        },
        {
            "system_tool": "ip",
        },
        {
            "system_tool": "iptables",
        },
        {
            "system_tool": "iwconfig",
        },
        {
            "system_tool": "iwlist",
        },
        {
            "system_tool": "iwpriv",
        },
        {
            "system_tool": "kill",
        },
        {
            "system_tool": "killall",
        },
        {
            "system_tool": "ls",
        },
        {
            "system_tool": "miniupnpd",
        },
        {
            "system_tool": "mkdir",
        },
        {
            "system_tool": "ovsh",
        },
        {
            "system_tool": "pgrep",
        },
        {
            "system_tool": "pidof",
        },
        {
            "system_tool": "ping",
        },
        {
            "system_tool": "ping6",
        },
        {
            "system_tool": "printf",
        },
        {
            "system_tool": "ps",
        },
        {
            "system_tool": "radartool",
        },
        {
            "system_tool": "return",
        },
        {
            "system_tool": "rm",
        },
        {
            "system_tool": "route",
        },
        {
            "system_tool": "scp",
        },
        {
            "system_tool": "sed",
        },
        {
            "system_tool": "seq",
        },
        {
            "system_tool": "set",
        },
        {
            "system_tool": "sh",
        },
        {
            "system_tool": "shift",
        },
        {
            "system_tool": "sleep",
        },
        {
            "system_tool": "source",
        },
        {
            "system_tool": "ssh",
        },
        {
            "system_tool": "tail",
        },
        {
            "system_tool": "tar",
        },
        {
            "system_tool": "test",
        },
        {
            "system_tool": "touch",
        },
        {
            "system_tool": "tr",
        },
        {
            "system_tool": "trap",
        },
        {
            "system_tool": "true",
        },
        {
            "system_tool": "type",
        },
        {
            "system_tool": "udhcpc",
        },
        {
            "system_tool": "wc",
        },
        {
            "system_tool": "which",
        },
        {
            "system_tool": "while",
        },
        {
            "system_tool": "wpa_cli",
        },
        {
            "system_tool": "wpa_supplicant",
        },
        {
            "system_tool": "/usr/opensync/bin/wpd",
        },
    ],
    "brv_is_tool_on_system_native_bridge": [
        {
            "system_tool": "brctl",
        },
        {
            "system_tool": "ebtables",
        },
        {
            "system_tool": "ebtables-restore",
        },
        {
            "system_tool": "ebtables-save",
        },
        {
            "system_tool": "tc",
        },
    ],
    "brv_is_tool_on_system_ovs_bridge": [
        {
            "system_tool": "ovs-appctl",
        },
        {
            "system_tool": "ovs-dpctl",
        },
        {
            "system_tool": "ovs-ofctl",
        },
        {
            "system_tool": "ovs-vsctl",
        },
        {
            "system_tool": "ovs-vswitchd",
        },
        {
            "system_tool": "ovsdb-server",
        },
    ],
    "brv_is_tool_on_system_opensync": [
        {
            "system_tool": "arping",
        },
        {
            "system_tool": "ash",
        },
        {
            "system_tool": "base64",
        },
        {
            "system_tool": "cp",
        },
        {
            "system_tool": "dd",
        },
        {
            "system_tool": "devmem",
        },
        {
            "system_tool": "df",
        },
        {
            "system_tool": "dirname",
        },
        {
            "system_tool": "dnsmasq",
        },
        {
            "system_tool": "du",
        },
        {
            "system_tool": "egrep",
        },
        {
            "system_tool": "env",
        },
        {
            "system_tool": "expr",
        },
        {
            "system_tool": "free",
        },
        {
            "system_tool": "hexdump",
        },
        {
            "system_tool": "hostapd_cli",
        },
        {
            "system_tool": "iptables-restore",
        },
        {
            "system_tool": "logger",
        },
        {
            "system_tool": "lspci",
        },
        {
            "system_tool": "md5sum",
        },
        {
            "system_tool": "mkfifo",
        },
        {
            "system_tool": "mktemp",
        },
        {
            "system_tool": "odhcp6c",
        },
        {
            "system_tool": "passwd",
        },
        {
            "system_tool": "pivot_root",
        },
        {
            "system_tool": "pppd",
        },
        {
            "system_tool": "pwd",
        },
        {
            "system_tool": "read",
        },
        {
            "system_tool": "reboot",
        },
        {
            "system_tool": "rmdir",
        },
        {
            "system_tool": "scp",
        },
        {
            "system_tool": "sort",
        },
        {
            "system_tool": "start-stop-daemon",
        },
        {
            "system_tool": "tcpdump",
        },
        {
            "system_tool": "tee",
        },
        {
            "system_tool": "timeout",
        },
        {
            "system_tool": "umount",
        },
        {
            "system_tool": "uname",
        },
        {
            "system_tool": "uptime",
        },
        {
            "system_tool": "vconfig",
        },
        {
            "system_tool": "vi",
        },
        {
            "system_tool": "wpa_cli",
        },
        {
            "system_tool": "wpa_supplicant",
        },
        {
            "system_tool": "xargs",
        },
        {
            "system_tool": "yes",
        },
    ],
    "brv_ovs_check_version": [
        {},
    ],
}
