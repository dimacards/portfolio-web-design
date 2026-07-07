import zlib, struct, sys

def load(path):
    with open(path,'rb') as f: data=f.read()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    pos=8; W=H=bitd=ct=None; idat=b''
    while pos<len(data):
        ln=struct.unpack('>I',data[pos:pos+4])[0]; typ=data[pos+4:pos+8]
        chunk=data[pos+8:pos+8+ln]
        if typ==b'IHDR':
            W,H,bitd,ct=struct.unpack('>IIBB',chunk[:10])
        elif typ==b'IDAT': idat+=chunk
        elif typ==b'IEND': break
        pos+=12+ln
    raw=zlib.decompress(idat)
    ch={0:1,2:3,3:1,4:2,6:4}[ct]
    bpp=ch  # 8-bit
    stride=W*bpp
    out=bytearray()
    prev=bytearray(stride)
    p=0
    def pae(a,b,c):
        pp=a+b-c; pa=abs(pp-a); pb=abs(pp-b); pc=abs(pp-c)
        return a if(pa<=pb and pa<=pc) else (b if pb<=pc else c)
    for y in range(H):
        ft=raw[p]; p+=1
        line=bytearray(raw[p:p+stride]); p+=stride
        if ft==1:
            for i in range(bpp,stride): line[i]=(line[i]+line[i-bpp])&255
        elif ft==2:
            for i in range(stride): line[i]=(line[i]+prev[i])&255
        elif ft==3:
            for i in range(stride):
                a=line[i-bpp] if i>=bpp else 0
                line[i]=(line[i]+((a+prev[i])>>1))&255
        elif ft==4:
            for i in range(stride):
                a=line[i-bpp] if i>=bpp else 0
                c=prev[i-bpp] if i>=bpp else 0
                line[i]=(line[i]+pae(a,prev[i],c))&255
        out+=line; prev=line
    return W,H,ch,bytes(out)

def bbox(path, pred, y0=0, y1=None, x0=0, x1=None):
    W,H,ch,px=load(path)
    if y1 is None: y1=H
    if x1 is None: x1=W
    minx,miny,maxx,maxy,cnt=1e9,1e9,-1,-1,0
    for y in range(y0,y1):
        row=y*W*ch
        for x in range(x0,x1):
            i=row+x*ch
            r,g,b=px[i],px[i+1],px[i+2]
            if pred(r,g,b):
                cnt+=1
                if x<minx:minx=x
                if x>maxx:maxx=x
                if y<miny:miny=y
                if y>maxy:maxy=y
    if cnt==0: return None
    return dict(x0=minx,x1=maxx,y0=miny,y1=maxy,w=maxx-minx,h=maxy-miny,
               cx=(minx+maxx)/2,cy=(miny+maxy)/2,cnt=cnt)
