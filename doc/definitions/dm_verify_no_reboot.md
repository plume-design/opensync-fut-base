# Testcase dm_verify_no_reboot

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this test case is to verify the functionality of the deferred reboot when `module_name` is performing a
critical task.

The command `./dm --no-reboot --set module_name` creates a new file `/tmp/.no_reboot/module_name` and the
table `Node_State` entry is created with `module:=no_reboot` and `value:=true`.

The command `./dm --no-reboot --set another_module_name` creates a new file `/tmp/.no_reboot/another_module_name` and
the table `Node_State` entry with `module==no_reboot` keeps the `value==true`.

The command `./dm --no-reboot --clear module_name` removes the file `/tmp/.no_reboot/module_name`. The table
`Node_State` entry where `module==no_reboot` is only updated to `value:=false`, when all the modules have been cleared
and there are no more files in the directory `/tmp/.no_reboot`.

``` bash
root@caesar:~# ovsh s Node_State
-----------------------
_uuid    | c27d~5d4a  |
_version | 1018~98a6  |
key      | no_reboot  |
module   | no_reboot  |
persist  | ["set",[]] |
value    | true       |
-----------------------
```

With the last file `module_name` deleted from the directory `/tmp/.no_reboot`, the table `Node_State` entry where
`module==no_reboot` gets updated to `value:=false`.

Therefore the value of the `value`key in the table `Node_State` where `module==no_reboot` reflects whether the
`/tmp/.no_reboot` directory is empty or not. If the directory is empty, the table `Node_State` entry, where
`module==no_reboot` has the value `value==false` or there is no such entry. If the directory is not empty, the table
`Node_State` entry, where `module==no_reboot` has the value `value==true`, regardless of the number of files in it.

## Expected outcome and pass criteria

The directory `/tmp/.no_reboot` does not exist. The table `Node_State` entry where `module==no_reboot` does not exist.

Call `./dm --no-reboot --set voip`. A new file `/tmp/.no_reboot/voip` is created. The table `Node_State` entry is
created where `module:=no_reboot` and `value:=true`.

Call `./dm --no-reboot --set another_critical_app`. A new file `/tmp/.no_reboot/another_critical_app` is created. The
table `Node_State` entry where `module==no_reboot` stays the same with `value==true`.

Call `./dm --no-reboot --clear another_critical_app`. The file `/tmp/.no_reboot/another_critical_app` is removed. The
table `Node_State` entry where `module==no_reboot` stays the same with `value==true`.

Call `./dm --no-reboot --clear voip`. The file `/tmp/.no_reboot/voip` is removed. The directory `/tmp/.no_reboot` is
empty. The table `Node_State` entry where `module==no_reboot` is updated with `value:=true`.

## Implementation status

Implemented.
