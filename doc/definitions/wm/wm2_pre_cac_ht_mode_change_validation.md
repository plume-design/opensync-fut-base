# Testcase wm2_pre_cac_ht_mode_change_validation

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

This test case is only applicable for `DFS` (_Dynamic Frequency Shift_) channels in the `5GHz` band.

The word `segment` is used to describe a valid `20MHz` wide operational channel, where a higher bandwidth (`ht_mode`)
will mean that the selected `channel` spans several segments, e.g., 40MHz spans two segments, 80MHz spans four segments,
etc.

The `US` regulatory domain does not allow leaving any segments as `cac_completed` when moving the radio from a segment.

The `EU` regulatory domain allows leaving all prior segments as `cac_completed` when moving the radio from a segment.

Only the `EU` regulatory domain can keep the `cac_completed` status even after leaving DFS segments. The `US` regulatory
domain can keep the `cac_completed` status on segments only if it operates on them at the time. If the radio moves away
and stops observing 20MHz DFS segments, they must be moved back to `"cac_required"` (e.g. `nop_finished`). This forces a
fresh CAC of 60s or 600s when trying to use these segments again.

## Testcase description

The goal of this testcase is to check the `pre-CAC` (_Channel Availability Check_) behaviour of the device in different
regulatory domains (jurisdictions) for `DFS` channels.

The `home_ap` is created on the gateway device and the first selected channel bandwidth is applied on a DFS channel. The
test case waits for CAC to complete (if required). All affected 20MHz channel segments, determined by the combination of
`channel` and `ht_mode`, are checked for the CAC status `cac_completed`. All other segments are checked for the allowed
`pre-CAC` status, based on the regulatory domain.

The channel bandwidth (`ht_mode`) is changed to the second selected bandwidth.

The test case waits for CAC to complete (if required). All affected 20MHz channel segments, determined by the
combination of `channel` and `ht_mode`, are checked for the CAC status `cac_completed`. All other segments are checked
for the allowed `pre-CAC` status, based on the regulatory domain.

## Expected outcome and pass criteria

The `home_ap` interface is created on the gateway device and has the first bandwidth applied. The `CAC` is completed
correctly on all 20MHz segments, determined by the combination of `channel` and `ht_mode`. Each segment has the CAC
status `cac_completed`. The allowed CAC status of other segments is valid for the regulatory domain of the device:

- Any prior CAC status for the `EU` regulatory domain.
- A CAC status of `nop_finished`, `nop_started` or `allowed` for the `US` regulatory domain. These segments are not
  immediately usable and require `CAC` again.

The device changes to the second bandwidth successfully. The `CAC` is completed correctly on all 20MHz segments,
determined by the combination of `channel` and `ht_mode`. Each segment has the CAC status `cac_completed`. The allowed
CAC status of other segments is valid for the regulatory domain of the device:

- Any prior CAC status for the `EU` regulatory domain.
- A CAC status of `nop_finished`, `nop_started` or `allowed` for the `US` regulatory domain. These segments are not
  immediately usable and require `CAC` again.

## Example

The `home_ap` interface starts with `channel 60 @ HT80`. All 4 20MHz segments require CAC: `52+56+60+64`. Then, change
to `channel 60 @ HT40`. There are now 2 20MHz segments that require CAC: `60+64`.

The expectation in the `EU` regulatory domain after the channel change is that the CAC state can remain:
`channel 60 @ HT80`: segments `52+56+60+64`: `cac_completed`. `channel 60 @ HT40`: segments `52+56`: `cac_completed`.
`channel 60 @ HT40`: segments `60+64`: `cac_completed`.

The expectation in the `US` regulatory domain after the channel change is that the CAC state must reset:
`channel 60 @ HT80`: segments `52+56+60+64`: `cac_completed`. `channel 60 @ HT40`: segments `52+56`: CAC is required
(e.g. `nop_finished`). `channel 60 @ HT40`: segments `60+64`: `cac_completed`.

## Implementation status

Implemented
