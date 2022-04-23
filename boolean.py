def f(i,j):
    op=[]
    st=[]
    no=False 
    while i<=j:
        
        if q[i]=='(':
            z=f(i+1,p[i]-1)
            i=p[i]+1
            if no:
                #z=set(iii for iii in range(50000) if iii not in z)
                z=not z
            st.append(z)

            
        elif q[i] in ('AND','OR'):
            
            if q[i]=='OR':
                while op:
                    
                    operator=op.pop()
                    
                    a=st.pop(-1)
                    b=st.pop(-1)

                    if operator=='AND':
                        #st.append(a.intersection(b))
                        st.append(a and b)
                    else:
                        #st.append(a.union(b))
                        st.append(a or b)
            else:
                while op and op[-1]=='AND':
                    operator=op.pop()
                    a=st.pop(-1)
                    b=st.pop(-1)
                    #st.append(a.intersection(b))
                    st.append(a and b)
                    
            op.append(q[i])
            i+=1
            
            
        elif q[i]=='NOT':
            no=True 
            i+=1 
        else:
            z=ids[q[i]]
            if no:
                #z=set(iii for iii in range(50000) if iii not in z)
                z=not z 
            st.append(z)
            i+=1
    while op:
        operator=op.pop()
        a=st.pop(-1)
        b=st.pop(-1)
        if operator=='AND':
            #st.append(a.intersection(b))
            st.append(a and b)
        else:
            #st.append(a.union(b))
            st.append(a or b)
    return st[-1]
        
ids={'a':False,'b':True,'c':False}
x=[]
se=set()


q='a AND b OR c'
q=q.split()
l=len(q)
st=[]
p={}
for i in range(l):
    if q[i]=='(':
        st.append(i)
    elif q[i]==')':
        p[st.pop(-1)]=i 


print(f(0,l-1))    
        