# FUT repository structure and directory names

```plaintext
fut-base [repository: https://github.com/plume-design/opensync-fut-base]
    ├── lib_testbed -> ../lib_testbed
    └── config
        └── locations -> ../../config/locations
        └── model_properties -> ../../config/model_properties
config
    └── locations
    └── model_properties
        └── reference [repository: https://github.com/plume-design/opensync-qa-dut-config]
lib_testbed
    └── generic [repository: https://github.com/plume-design/opensync-qa-lib-testbed]
```

## Creating the directory structure and cloning the repositories

```bash
OPENSYNC_ROOT=$(pwd)
mkdir -p ${OPENSYNC_ROOT:?}/qa
cd ${OPENSYNC_ROOT:?}/qa
```

```bash
mkdir -p fut-base
git clone https://github.com/plume-design/opensync-fut-base.git fut-base
```

```bash
mkdir -p lib_testbed/generic
git clone https://github.com/plume-design/opensync-qa-lib-testbed.git lib_testbed/generic
```

```bash
mkdir -p config/model_properties/reference
git clone https://github.com/plume-design/opensync-qa-dut-config.git config/model_properties/reference
```

```bash
mkdir -p config/locations
cp fut-base/config/fut_location_example.yaml config/locations/example.yaml
```
