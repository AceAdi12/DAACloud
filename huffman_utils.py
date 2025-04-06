from collections import Counter
import heapq #priority Queue
#Build the block of tree
class Node:
    def __init__(self,char=None,freq=None):
        self.char=char
        self.freq=freq
        self.left=None
        self.right=None
    
    def __lt__(self,other):
        return self.freq<other.freq

def build_huffman_tree(text):
    freq=Counter(text) #counts how many times charcter appears
    heap=[Node(char,fr) for char,fr in freq.items()] #min heap
    heapq.heapify(heap)

    while len(heap)>1:
        left=heapq.heappop(heap)
        right=heapq.heappop(heap)
        merged=Node(None,left.freq+right.freq)
        merged.left=left
        merged.right=right
        heapq.heappush(heap,merged)
    return heap[0]
#code table
def build_codes(root,current_code="",codes={}):
    if root is None:
        return
    if root.char is not None:
        codes[root.char]=current_code
    build_codes(root.left,current_code+"0",codes)
    build_codes(root.right,current_code+"1",codes)
    return codes
#Compressing file:->
def compress_file(input_path,output_path):
    with open(input_path,"r",encoding="utf-8") as f:
        text=f.read()
    if not text.strip():
        raise ValueError("Input file is empty .Please provide a file with content.")

    root=build_huffman_tree(text)
    codes=build_codes(root)
    encoded_text=''.join([codes[char] for char in text])
    padding=8-len(encoded_text)%8
    encoded_text+='0'*padding
    b_array=bytearray()
    for i in range(0,len(encoded_text),8):
        byte=encoded_text[i:i+8]
        b_array.append(int(byte,2))
    with open(output_path,"wb") as out:
        out.write(bytes([padding]))
        out.write(b_array)
    return output_path