import chess, chess.pgn, chess.engine, csv, sys, math, io
k=sys.argv[1]
W={}
for r in csv.DictReader(open("wanted.csv")): W.setdefault(r["site"],[]).append(r)
e=chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish"); e.configure({"Threads":1,"Hash":64})
LIM=chess.engine.Limit(depth=10)
def ev(b):
    if b.is_checkmate(): return -1000  # side to move is mated
    if b.is_game_over(): return 0
    s=e.analyse(b,LIM)["score"].pov(b.turn).score(mate_score=1000)
    return max(-1000,min(1000,s))
wp=lambda cp: 50+50*(2/(1+math.exp(-0.00368208*cp))-1)
out=csv.writer(open(f"moves{k}.csv","w",newline="")); out.writerow(["site","p","win","group","own_nm","ply","clk","cp_before","cp_after","wp_loss","acc"])
f=open(f"part{k}.pgn"); n=0
while True:
    g=chess.pgn.read_game(f)
    if g is None: break
    sid=g.headers.get("Site","")[-8:]
    rs=W.get(sid,[]); 
    if not rs: continue
    sides={(chess.WHITE if r["color"]=="w" else chess.BLACK):r for r in rs}
    b=g.board(); cur=ev(b); own={True:0,False:0}; ply=0
    for node in g.mainline():
        s=b.turn; mv=node.move; own[s]+=1; ply+=1
        b.push(mv); nxt=ev(b)  # pov of side to move now (opponent)
        before=cur; after=-nxt
        if s in sides:
            r=sides[s]; l=max(0,wp(before)-wp(after)); acc=max(0,min(100,103.1668*math.exp(-0.04354*l)-3.1669))
            out.writerow([sid,r["p"],r["win"],r["group"],own[s],ply,node.clock(),before,after,round(l,2),round(acc,2)])
        cur=nxt
    n+=1
    if n%100==0: print(k,n,flush=True)
e.quit(); print(k,"done",n,flush=True)
