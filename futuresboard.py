#!/home/vadim/anaconda3/envs/tst_env/bin/python
# -*- coding: utf-8 -*-
import re
import sys
from CredentialManager import CredentialManager
from futuresboard.cli import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
