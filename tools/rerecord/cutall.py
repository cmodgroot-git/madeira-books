"""Cut every take in WORK/urls.tsv that has no WORK/chk/<take>.json yet, in one process."""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import cuttake
W=cuttake.WORK
for line in open(f'{W}/urls.tsv'):
    t,u=line.split()
    if not os.path.exists(f'{W}/chk/{t}.json'): cuttake.run(t,u)
