def f(i,j):
    def ff(z):
        if ans=='':return z 
        nonlocal no 
        if no:
            z=not z
            no=False
        if prev=='AND':return ans and z
        if prev=='OR':return ans or z 
        
    ans=''
    prev=''
    no=False 
    while i<=j:
        if q[i]=='(':
            z=f(i+1,p[i]-1)
            i=p[i]+1
            ans=ff(z)
        elif q[i] in ('AND','OR'):
            prev=q[i]
            i+=1
        elif q[i]=='NOT':
            no=True 
            i+=1 
        else:
            ans=ff(q[i] in se)
            i+=1
    return ans 
        

x=[]
se=set()
y=[{'a','c'},{'b','d','f'},{'a','b','c','d','e'},{'a','c','f'},{'c','d'}]

q='a AND NOT ( b AND c )'
q=q.split()
l=len(q)
st=[]
p={}
for i in range(l):
    if q[i]=='(':
        st.append(i)
    elif q[i]==')':
        p[st.pop(-1)]=i 

for se in y:
    print(f(0,l-1))    
        