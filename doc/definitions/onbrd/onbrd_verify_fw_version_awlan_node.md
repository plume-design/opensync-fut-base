# Testcase onbrd_verify_fw_version_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the version string matches the
required pattern.

**Note:**\
Determine the pattern of a version string in test configuration.\
Alternatively, if pattern string is not known in advance, test configuration
should specify only to assert "non-empty" string.

## Expected outcome and pass criteria

Version string matches the required pattern, or is not-empty if the version
string pattern is not known.

## Implementation status

Implemented
