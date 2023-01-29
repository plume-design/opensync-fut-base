# Testcase wm2_dfs_cac_aborted

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to check that CAC (_Channel Availability Check_)
for the initial DFS (_Dynamic Frequency Shift_) channel-1 is aborted, if the
channel is switched to a new DFS channel, and that CAC is started for the newly
set channel-2.

Make sure channel-1 is of a valid type to perform the test. The type must be DFS.\
Make sure channel-2 is of a valid type to perform the test. The type must be DFS.

## Expected outcome and pass criteria

Make sure all radio interfaces on DUT are up and have a valid configuration.

After the change of `channel` to channel-1:

- CAC for channel-1 has started.

Before CAC for channel-1 is finished, and the `channel` is changed to
channel-2:

- NOP (_No Occupancy Period_) is finished for channel-1
- CAC has started for channel-2

## Implementation status

Implemented
