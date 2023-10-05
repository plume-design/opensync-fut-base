#!/bin/sh

# This script is used for a manual shellcheck of fut-base scripts.
# To run shellcheck on all fut-base directories that contain shell
# scripts execute:
# ./all_shellcheck.sh
# (from fut-base directory, where the script is located)

# Excluded:
# SC2015: Note that A && B || C is not if-then-else. C may run when A is true.
# SC2039: In POSIX sh, *something* is undefined.
# SC1091: Not following: .sourcefile was not specified as input.

shellcheck --exclude=SC2015,SC2039,SC1091 ./docker/*.sh
shellcheck --exclude=SC2015,SC2039,SC1091 ./helpers/*.sh
shellcheck --exclude=SC2015,SC2039,SC1091 ./plume/tools/switch/*.sh
shellcheck --exclude=SC2015,SC2039,SC1091 ./shell/lib/override/*.sh
