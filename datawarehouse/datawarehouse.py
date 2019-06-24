# myscript.py
from __future__ import print_function
import cx_Oracle
from configparser import ConfigParser

config = ConfigParser()
config.read('../config/config.ini')

print(config.sections())
info = config.items('datawarehouse')
# Connect as user "hr" with password "welcome" to the "oraclepdb" service running on this computer.



def userlookup(pennid):
    connection = cx_Oracle.connect(info['user'], info['password'], info['service'])
    cursor = connection.cursor()


    cursor.execute("""
        SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENNKEY
        FROM EMPLOYEE_GENERAL
        WHERE PENN_ID= :pennid """,
        pennid = '89450759')
    for fname, lname, email, pennkey in cursor:
        print("Values:", [fname, lname, email, pennkey])

    #return([fname, lname, email, pennkey])
