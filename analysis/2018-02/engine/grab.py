import gzip, csv, glob
want=set(r["site"] for r in csv.DictReader(open("wanted.csv")))
got={}
files=sorted(glob.glob("/mnt/user-data/uploads/Exp_Adap_AI/outputs/analysis_2018-0[12]/sel*.pgn.gz"))
for fn in files:
    buf=[];sid=None
    for line in gzip.open(fn,"rt",encoding="utf-8"):
        if line.startswith("[Event "):
            if sid in want and sid not in got: got[sid]="".join(buf)
            buf=[line]; sid=None
        else:
            buf.append(line)
            if line.startswith("[Site "): sid=line.strip()[-10:-2]
    if sid in want and sid not in got: got[sid]="".join(buf)
    print(fn,len(got),flush=True)
ids=sorted(got)
for k in range(4):
    with open(f"part{k}.pgn","w") as o:
        for s in ids[k::4]: o.write(got[s]+"\n")
print("missing",len(want-set(got)))
