##########################################################################################
## File     : Example_ENV_Read_Write.py
##
## Purpose  : Example program to READ and WRITE Environment key values
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-07-11 Initial Version
##          : 2026-09-07 Updates for hkr and ChatGPT code revisions
##########################################################################################

from env_read_write import *

#------------------------------------------------------------------------------------------
# Read Env Key
#------------------------------------------------------------------------------------------
TEST_ENV_VAR_READ = env_read_key("TEST_ENV_VAR_READ")
print(TEST_ENV_VAR_READ)

#------------------------------------------------------------------------------------------
# Write Env Key
#------------------------------------------------------------------------------------------
success = env_write_key("TEST_ENV_VAR_WRITE", "WRITE")
if success:
    print("Key=TEST_ENV_VAR_WRITE written saved successfully!")
