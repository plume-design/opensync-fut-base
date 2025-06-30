# Testcase cpm_delete_while_restarting

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot. Ensure the OpenSync version is 5.6.0 or greater.

## Testcase description

The goal of this testcase is to check that removal of `tinyproxy` instances and their configuration files from the
system works the same even while `CPM` attempts to restart the service, which had previously failed to start.

One example, when `CPM` would attempt to restart `tinyproxy` instances, would be due to an existing instance listening
on the same ip and port, but this is not the only case.

Insert an entry into the `Captive_Portal` table to spawn a `tinyproxy` instance listening on a selected IP and port.

Insert a second identical entry into the `Captive_Portal` table, listening on the same IP and port. This is a
misconfiguration. This will result in 10 repeated attempts to start a `tinyproxy` instance and would then stop. Each
retry takes about 1 second.

After five failed attempts to start the second instance, manually remove the second entry from the `Captive_Portal`
table. This should remove the second `tinyproxy` instance, regardless if it is running or if `CPM` is attempting to
restart it.

About two seconds after removing the second entry from the `Captive_Portal` table, check that there is no `tinyproxy`
instance running or configuration file present on the system, that would match the second entry.

## Expected outcome and pass criteria

One `tinyproxy` instance is running with correct configuration file content, matching the first `Captive_Portal` entry.

After inserting the second `Captive_Portal` table entry, a second `tinyproxy` instance is not running and there is no
corresponding configuration file content on the system.

After removing the second `Captive_Portal` table entry, exactly one `tinyproxy` instance remains running and exactly one
corresponding configuration file is present on the system.

## Implementation status

Implemented
