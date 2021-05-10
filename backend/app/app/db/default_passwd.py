#!/usr/bin/env python

import os
import sys, getopt
import pandas as pd
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext

def get_password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def main(argv):
    account = ''
    passwd = ''
    acct_file = 'user.csv'

    if len(sys.argv)-1 == 0:
        print("%s -a <admin_account> -p <password>" % sys.argv[0])
        sys.exit(2)

    try:
       opts, args = getopt.getopt(argv,"a:p:")
    except getopt.GetoptError:
        print("%s -a <admin_account> -p <password>" % sys.argv[0])
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("%s -a <admin_account> -p <password>" % sys.argv[0])
            sys.exit()
        elif opt in ("-a"):
            account = arg
        elif opt in ("-p"):
            passwd = arg

    hashed_pw = get_password_hash(passwd)
    init_data_path = os.path.join(os.path.dirname(__file__), "init_data")
    file_path = os.path.join(init_data_path, acct_file)
    df = pd.read_csv(file_path, sep=",")
    df['username'] = account
    df['hashed_password'] = hashed_pw    
    df.to_csv(file_path, sep=",", index=False)
    print("Successfully set default password(%s) to account(%s)\n" % (passwd, account))

if __name__ == "__main__":
    main(sys.argv[1:])