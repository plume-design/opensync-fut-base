#!/usr/bin/env bash

NAME="$(basename "$0")"
help()
{
cat << EOF
${NAME}: Functional Unit Testing Framework Helper Script

${NAME} [-h|--help] [-p] [-o] [-d] [-path P] [-l] [-c] [-li] [-lic] [-lip] [-m [mark]] [-r TEST] [-allure D] [-tr]

Make sure to execute ${NAME} from within the parent directory!
Commands:
    -h|--help : Print this help message
    -p        : Enable live logging of log/stdout/stderr to terminal
    -o        : Disable pytest capture of log/stdout/stderr and print to terminal
    -d        : Debug - increase pytest verbosity level to debug
    -dfb      : Rebuild docker image required for fut, otherwise, use existing one if present (if not, image will be built)
    -lp       : --log-pass - enable logread output for PASS-ed testcases
    -log-pull : --log-pull - enable logpull Allure attachment for failed test cases. Use with caution with minimal number of testcases
    -path P   : Filepath to pytest testcase definition file(s) or folder. Default folder: "test/"
            ${NAME} -path test/NM_test.py                   -> single pytest file
            ${NAME} -path test/UT_test.py,test/CM_test.py   -> comma separated list of pytest files
    -ut       : Run FUT unit tests located in self_test/
    -l        : Run pytest --listtest to print all collected testcases for selected configuration
    -c        : Run pytest --listconfigs to list all available configurations for selected model
    -cd       : Run pytest --listconfigsdetails to list all available configurations with parameters for selected model
    -li       : Run pytest --listignored to print all ignored testcases for selected configuration
    -lic      : Run pytest --listignoredconfig to print all ignored testcase configurations
    -lip      : Run pytest --listignoredparams to print all ignored testcase configurations with parameters
    -j P      : Run pytest --json and save the testcase list and testcase configuration into json file P
    -config-from-json P : Run FUT using test configuration loaded from JSON file at P path
    -m [mark] : Run pytest --markers|-m [mark] to list available markers, or use one or more markers with boolean expression
            ${NAME} --markers                                   -> List possible markers
            ${NAME} -m "require_dut"                            -> Use a single custom marker
            ${NAME} -m "require_dut and not dfs or require_rc"  -> Boolean expression using several custom markers (use quotes)

    -r TEST   : Run single test case, or comma-separated list
            ${NAME} -r foo
            ${NAME} -r foo,bar,baz
            ${NAME} -r foo[2,4],bar[:4],baz[4:]  ->
               - Run test foo configs 2 and 4
               - Run test bar from config 0 to config 4
               - Run test baz from config 4 to last config

    -allure D : Run pytest --alluredir X to generate Allure results into directory D
            ${NAME} -allure allure-results       -> Allure results will be in allure-results
            ${NAME} -allure /tmp/allure-results  -> Allure results will be in /tmp/allure-results

    -tr       : Run pytest --transferonly=True to only transfer shell folder onto devices without test execution
    -nodocker : Disable docker execution (not recommended, debug only)
    -dry      : Execute FUT in DRY RUN mode:
                  - Nothing is executed on device
                  - Allure report contains RECIPE section
                  - Use (-d) flag to output RECIPE to std-out

    -pdb      : Enable Python debugger:
                  - Set breakpoints in code, use 'pdb.set_trace()' which will trigger debugger

    -noshunpack  : Disable unpacking of shell tarball from resource/shell/*.tar.bz2
    -ignore-osrt-versions  : Ignore OSRT (server, clients) version check in COMPAT test suite
    -skip-l2     : Skip LEVEL2 testcase steps
    -log-path P  : Enable writing a copy of log of ${NAME} to P.
            ${NAME} -log-path /tmp/fut_run.log -> log of ${NAME} run will be saved in /tmp/fut_run.log.
    -use-generator : Enable generic FUT test generator feature - suitable for new models
    -gen-type GT   : Specify test generation type - Default for 'default' type
            - 'optimized' GT will generate optimized FUT test configuration with less test scenarios

    -tc-select-from-file    : Include test-cases from file (see pytest-select docs for more).
    -tc-deselect-from-file  : Exclude test-cases from file (see pytest-select docs for more).

Notes:
    - for options -r, -m, -path list arguments should be comma-separated, without spaces:
      ${NAME} -r test_foo,test_bar  -> OK
      ${NAME} -r test_foo test_bar  -> NOT OK

UT (Unit Tests) execution:
    UT_test collection is disabled by default. Only with explicit -path setting, UT_test will be collected and executed
    Steps:
        1. Place <UT_TAR_NAME>.tar into resource/ut/ folder
            - optional - set config/<DEVICE-NAME>/UT_config.py -> test_cfg['ut']['ut_name'] to match <UT_TAR_NAME>
              useful if resource/ut/ contains multiple .tar files
        2. Run ${NAME} -path test/UT_test.py - add other arg as needed (-d, -p, etc.)

Using the pdb debugger:
    pdb debugger is enabled by default. To use it, set breakpoints is the code:
        - use: "import pdb; pdb.set_trace()"
        - use pdb built-in breakpoints: "breakpoint()"

Examples:
  Run all collected tests in pytest folder, enable live terminal logging:
    ${NAME} -p
  Run all collected tests in pytest folder, disable capture:
    ${NAME} -o
  Collect tests pytest folder, run only configurations for test_foo, enable live terminal logging:
    ${NAME} -p -r test_foo
  Collect tests pytest folder, run specified tests test_foo and test_bar with test_config_3, enable live terminal logging:
    ${NAME} -p -r test_foo,test_bar[3]
  Run all collected tests in pytest folder, create Allure results in allure-results/ folder:
    ${NAME} -allure allure-results
  Dry run test_foo test, output RECIPE to std-out:
    ${NAME} -r test_foo -dry -d
  Use pdb debugger for test_foo test (set breakpoints in the code):
    ${NAME} -r test_foo -pdb
EOF
}

if [[ -n $SUDO_USER ]]; then
    help
    echo "err: Execute script without 'sudo' privilege"
    exit 1
fi

# Workaround for Docker volume being owned by root instead wanted active user
sudo chown -R plume:plume /tmp/automation || true

# Globals:
FUT_COMPAT_PATH="test/COMPAT_test.py"
FUT_PYTEST_PATH="test/"
PYTEST_CMD="python3 -u -m pytest --color=yes"

# Options (defaults):
DOCKER_FORCE_REBUILD=${DOCKER_FORCE_REBUILD:-"false"}
CAPTURE="-rsx"
DBG_FLAG=""
LOGCLI=""
MARKERS=""
PSEUDO_TTY="--tty"
RESULTS=""
SH_UNPACK="true"
TC_LIST=""
TC_DE_SELECT_FROM_FILE=""
USE_DOCKER="true"
VERBOSE="-v"
FUT_DRY_RUN=""
# Switches:
TC_COLLECT=""
TRANSFER_ONLY=""
DEBUGGER=""
IGNORE_OSRT_VER=""
JSON=""
FUT_CONFIG_FROM_JSON="false"
FUT_GEN_TYPE="optimized"
FUT_USE_GENERATOR="false"
FUT_SKIP_L2="false"

while [[ "${1}" == -* ]]; do
    option="${1}"
    shift
    case "${option}" in
        -h|--help)
            help
            exit 0
            ;;
        -p)
            LOGCLI="-o log_cli=true"
            ;;
        -o)
            CAPTURE="-rsx --capture=no"
            ;;
        -path)
            FUT_PYTEST_PATH="${1//,/ }"
            FUT_PYTEST_PATH="${FUT_COMPAT_PATH} ${FUT_PYTEST_PATH}"
            shift
            ;;
        -ut)
            FUT_PYTEST_PATH="self_test/ --cov=config/model/generic/ --cov-report term-missing"
            shift
            ;;
        -d)
            DBG_FLAG="--dbg"
            ;;
        -dfb)
            DOCKER_FORCE_REBUILD="true"
            ;;
        -lp)
            LOG_PASS="--log-pass"
            ;;
        -log-pull)
            LOG_PULL="--log-pull"
            ;;
        -r)
            # "comma" separated list
            TC_LIST="--runtest ${1}"
            shift
            ;;
        -tc-select-from-file)
            # filename containing test-cases, separated by new-line
            TC_DE_SELECT_FROM_FILE="${TC_DE_SELECT_FROM_FILE} --select-from-file ${1}"
            shift
            ;;
        -tc-deselect-from-file)
            # filename containing test-cases, separated by new-line
            TC_DE_SELECT_FROM_FILE="${TC_DE_SELECT_FROM_FILE} --deselect-from-file ${1}"
            shift
            ;;
        -allure)
            RESULTS="--alluredir=${1}"
            CAPTURE="${CAPTURE} --allure-no-capture"
            shift
            ;;
        -tr)
            TRANSFER_ONLY="--transferonly"
            ;;
        -l)
            TC_COLLECT="--listtests"
            ;;
        -li)
            TC_COLLECT="--listignored"
            ;;
        -lic)
            TC_COLLECT="--listignoredconfig"
            ;;
        -lip)
            TC_COLLECT="--listignoredparams"
            ;;
        -c)
            TC_COLLECT="--listconfigs"
            ;;
        -cd)
            TC_COLLECT="--listconfigsdetails"
            ;;
        -C)
            TC_COLLECT="--collect-only"
            ;;
        -j)
            JSON="--json ${1}"
            shift
            ;;
        -config-from-json)
            FUT_CONFIG_FROM_JSON="${1}"
            shift
            ;;
        -m)
            MARKERS="--markers"
            if [[ "${1}" == [^-]* ]]; then
                MARKERS="-m \"${1}\""
                shift
            fi
            ;;
        -nodocker)
            USE_DOCKER="false"
            ;;
        -dry)
            FUT_DRY_RUN="true"
            IGNORE_OSRT_VER="--ignoreosrtversion"
            ;;
        -notty)
            PSEUDO_TTY=""
            ;;
        -noshunpack)
            SH_UNPACK="false"
            ;;
        -pdb)
            DBG_FLAG="--dbg"
            CAPTURE="-rsx --capture=no"
            DEBUGGER="--pdb"
            PSEUDO_TTY="--interactive --tty"
            ;;
        -ignore-osrt-versions)
            IGNORE_OSRT_VER="--ignoreosrtversion"
            ;;
        -gen-type)
            FUT_GEN_TYPE="${1}"
            shift
            ;;
        -use-generator)
            FUT_USE_GENERATOR="true"
            ;;
        -log-path)
            LOG_FILE_PATH=${1}
            shift
            LOG_FILE_BASENAME=$(basename -- "$LOG_FILE_PATH")
            LOG_FILE_NAME="${LOG_FILE_BASENAME%.*}"
            LOG_FILE_EXT=${LOG_FILE_BASENAME##*\.}
            if [[ ${LOG_FILE_BASENAME%.*} == $LOG_FILE_EXT ]]; then
                LOG_FILE_COUNT=$( find $( dirname $LOG_FILE_PATH ) -name $LOG_FILE_NAME* 2>/dev/null | wc -l )
                if [[ $LOG_FILE_COUNT -gt 0 ]]; then
                    LOG_FILE_NAME="${LOG_FILE_NAME}_${LOG_FILE_COUNT}"
                fi
                LOG_FILE_PATH="$( dirname $LOG_FILE_PATH )/$LOG_FILE_NAME"
            elif [[ $LOG_FILE_BASENAME == .* ]]; then
                if [[ $LOG_FILE_NAME == "" ]]; then
                    LOG_FILE_NAME=${LOG_FILE_BASENAME:1}
                    LOG_FILE_COUNT=$( find $( dirname $LOG_FILE_PATH ) -name $LOG_FILE_NAME* 2>/dev/null | wc -l )
                    if [[ $LOG_FILE_COUNT -gt 0 ]]; then
                        LOG_FILE_NAME="${LOG_FILE_NAME}_${LOG_FILE_COUNT}"
                    fi
                    LOG_FILE_PATH="$( dirname $LOG_FILE_PATH )/$LOG_FILE_NAME"
                else
                    LOG_FILE_NAME=${LOG_FILE_NAME:1}
                    LOG_FILE_COUNT=$( find $( dirname $LOG_FILE_PATH ) -name $LOG_FILE_NAME* 2>/dev/null | wc -l )
                    if [[ $LOG_FILE_COUNT -gt 0 ]]; then
                        LOG_FILE_NAME="${LOG_FILE_NAME}_${LOG_FILE_COUNT}"
                    fi
                    LOG_FILE_PATH="$( dirname $LOG_FILE_PATH )/$LOG_FILE_NAME.$LOG_FILE_EXT"
                fi
            else
                LOG_FILE_COUNT=$( find $( dirname $LOG_FILE_PATH ) -name $LOG_FILE_NAME* 2>/dev/null | wc -l )
                if [[ $LOG_FILE_COUNT -gt 0 ]]; then
                    LOG_FILE_NAME="${LOG_FILE_NAME}_${LOG_FILE_COUNT}"
                fi
                LOG_FILE_PATH="$( dirname $LOG_FILE_PATH )/$LOG_FILE_NAME.$LOG_FILE_EXT"
            fi
            ;;
        -skip-l2)
            SKIP_L2="--skipl2"
            FUT_SKIP_L2="true"
            ;;

        -*)
            echo "Unknown argument: ${option}"
            help
            exit 1
            ;;
    esac
done

# Make sure that path to log file is printed to console in case that run of init.sh is interrupted.
function trap_function() {
    if [[ $LOG_FILE_PATH != "" ]]; then
        echo "Full log of this run is saved to $LOG_FILE_PATH."
    fi
}
trap trap_function SIGINT SIGTERM SIGHUP SIGABRT

# Checking env var in framework
export FUT_PYTEST_PATH
export USE_DOCKER
export FUT_DRY_RUN
export PSEUDO_TTY
export FUT_CONFIG_FROM_JSON
export FUT_GEN_TYPE
export FUT_USE_GENERATOR

FUT_OPTS="${TC_LIST} ${RESULTS} ${CAPTURE} ${VERBOSE} ${DBG_FLAG} ${LOG_PASS} ${LOG_PULL} ${LOGCLI} ${MARKERS} ${DRY_RUN} ${DEBUGGER} ${IGNORE_OSRT_VER} ${SKIP_L2} ${TC_DE_SELECT_FROM_FILE}"
FUT_CMD=""

export FUT_SKIP_L2

# Special commands that prevent testcase execution:
if [[ "${TC_COLLECT}" != "" ]] || [[ "${JSON}" != "" ]]; then
    FUT_CMD="${PYTEST_CMD} ${FUT_PYTEST_PATH} ${TC_COLLECT} ${LOGCLI} ${VERBOSE} ${DBG_FLAG} ${DEBUGGER} ${JSON} ${TC_LIST} ${TC_DE_SELECT_FROM_FILE}"
elif [[ "${TRANSFER_ONLY}" != "" ]]; then
    FUT_CMD="${PYTEST_CMD} ${FUT_COMPAT_PATH} ${TRANSFER_ONLY} ${LOGCLI} ${VERBOSE} ${DBG_FLAG} ${DEBUGGER}"
else
    FUT_CMD="${PYTEST_CMD} ${FUT_PYTEST_PATH} ${FUT_OPTS}"
fi

# Enable exit on non 0
set -e

{
# Unpack shell tar file on request. Ensure single file in target dir
SH_TAR_NAME='resource/shell/*.tar.bz2'
# shellcheck disable=SC2012
if [ "${SH_UNPACK}" == "true" ]; then
    echo "Shell tar file unpack requested"
    # shellcheck disable=SC2086
    if [ "$(ls ${SH_TAR_NAME} 2>/dev/null | wc -l)" == "1" ]; then
        tar -xvjf ${SH_TAR_NAME} -C ./ --transform 's/fut\/shell/shell/'
    else
        echo "More than one tar file exists, or none, SKIPPING UNPACK"
    fi
fi

export DOCKER_FORCE_REBUILD
# FUT_IN_DOCKER is set to true in case the user uses the FutWebApp (docker-compose up)
FUT_IN_DOCKER="${FUT_IN_DOCKER:-false}"
# Check whatever there is installed docker on system, if not, alert user and run FUT without docker
command -v docker &> /dev/null && DOCKER_EXISTS="true" || DOCKER_EXISTS="false"

if [ $DOCKER_EXISTS == "false" ]; then
    echo "ALERT: docker is not installed on system, will run FUT outside docker container ! May result in unexpected behaviour"
fi
if [ "$USE_DOCKER" == "true" ] && [ "$FUT_IN_DOCKER" == false ] && [ $DOCKER_EXISTS == "true" ]; then
    cd docker/
    DOCKER_CMD="./dock-run ${FUT_CMD}"
    echo "Using Docker to execute: ${FUT_CMD}"
    echo "${DOCKER_CMD}"
    ${DOCKER_CMD}
else
    echo "${FUT_CMD}"
    eval "${FUT_CMD}"
fi
} 2>&1 | if [[ $LOG_FILE_PATH == "" ]]; then cat; else tee -a >(sed -r 's/\x1b\[[0-9;]*m//g' > $LOG_FILE_PATH) && echo "Full log of this run is saved to $LOG_FILE_PATH."; fi
