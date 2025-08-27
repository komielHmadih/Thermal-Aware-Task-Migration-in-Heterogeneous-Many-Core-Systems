from models.core_info import PER_CORE

def same_type(i,j):
    return PER_CORE[i]["type_key"]==PER_CORE[j]["type_key"]

def enumerate_migration_pairs(A):
    actives = [i for i,a in enumerate(A) if a==1]
    idles   = [i for i,a in enumerate(A) if a==0]
    for s in actives:
        for d in idles:
            if same_type(s,d):
                yield (s,d)

def apply_migration(A,s,d):
    A2 = A[:]
    A2[s]=0
    A2[d]=1
    return A2
