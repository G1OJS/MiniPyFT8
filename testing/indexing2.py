import numpy as np

def pp0(arr):
    print([f"{v:+05.2f}" for v in arr])

def pp(arr):
    print()
    for i in range(arr.shape[0]):
        print([f"{v:+05.2f}" for v in arr[i]])



p = np.random.rand(58,8)

#p[:,:] = 0
#p[27,6] = 1

llra = np.max(p[:, [4,5,6,7]], axis=1) - np.max(p[:, [0,1,2,3]], axis=1)
llrb = np.max(p[:, [2,3,4,7]], axis=1) - np.max(p[:, [0,1,5,6]], axis=1)
llrc = np.max(p[:, [1,2,6,7]], axis=1) - np.max(p[:, [0,3,4,5]], axis=1)
llr = np.column_stack((llra, llrb, llrc))
llr = llr.ravel()

bits91_int = 0
for bit in (llr[:91] > 0).astype(int).tolist():
    bits91_int = (bits91_int << 1) | bit
print(bits91_int)

syms = np.argmax(p[:31, :], axis = 1)
gray_seq = [0,1,3,2,6,4,5,7]
syms = [gray_seq[s] for s in syms]
bits91_int = 0
syms[-1] &= 1
for s in syms:
    bits91_int = (bits91_int << 3) | (s & 7)
bits91_int >>= 2
print(bits91_int)
