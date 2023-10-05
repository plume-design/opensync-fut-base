# Testcase onbrd_verify_dhcp_dry_run_success

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goals of this testcase are to verify that in case DUT has wired uplink, "dry-run" is executed correctly, and that
the Ethernet interface is added to WAN bridge, since there is a DHCP server present upstream.

**Note:**\
Testcase is not applicable to the WANO-enabled devices.

**Important:**\
Bringing the interface down will break the SSH connection between the FUT framework and DUT. Therefore,
the test script must be autonomous, meaning all the steps must execute in a single script.

## Expected outcome and pass criteria

After interface is brought down, the field `has_L2` is `false` in the `Connection_Manager_Uplink` table.

After the interface is brought up:

- Field `has_L2` is `true` in the `Connection_Manager_Uplink` table.
- Field `has_L3` is `true` in the `Connection_Manager_Uplink` table.

## Implementation status

Implemented
