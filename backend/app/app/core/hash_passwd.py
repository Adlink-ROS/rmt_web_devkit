#!/usr/bin/env python

import sys
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext

def get_password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def main(argv):

    if len(sys.argv) != 2:
        print("Usage: {} <password>".format(sys.argv[0]))
        sys.exit(2)

    passwd = sys.argv[1]
    hashed_pw = get_password_hash(passwd)

    print("The hashed password({}) is: {}".format(passwd, hashed_pw))

if __name__ == "__main__":
    main(sys.argv[1:])