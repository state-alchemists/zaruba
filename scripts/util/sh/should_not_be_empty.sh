# USAGE
# sh should_not_be_empty.sh <value> <error-message>

. "${ZARUBA_HOME}/scripts/util/sh/_include.sh"

if [ -z "${1}" ]
then
    echo "${2}" 1>&2
    exit 1
fi