# If you changed some code which you expect to change the output files, then run
# this script to regenerate the test output.
#
# NOTE: Do not run this script unless you are expecting the output files to
# change. Examine the git diff carefully to make sure the new test output files
# are as you expect them to be

cd $(dirname $0)/.. && PVI_REGENERATE_OUTPUT=1 pytest .
