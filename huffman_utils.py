import pickle
from collections import Counter
import heapq

class Node:
    def __init__(self, byte=None, freq=None):
        self.byte = byte
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(data_bytes):
    freq = Counter(data_bytes)  # count frequency of each byte
    heap = [Node(byte=b, freq=f) for b, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]

def build_codes(root, current_code="", codes={}):
    if root is None:
        return
    if root.byte is not None:
        codes[root.byte] = current_code
    build_codes(root.left, current_code + "0", codes)
    build_codes(root.right, current_code + "1", codes)
    return codes

def compress_file(input_path, output_path):
    with open(input_path, "rb") as f:  # read binary
        data = f.read()
    if not data:
        raise ValueError("Input file is empty. Please provide a file with content.")
    
    root = build_huffman_tree(data)
    codes = build_codes(root)
    
    encoded_text = ''.join([codes[b] for b in data])
    padding = 8 - len(encoded_text) % 8
    if padding == 8:
        padding = 0
    encoded_text += '0' * padding
    
    b_array = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i+8]
        b_array.append(int(byte, 2))
    
    with open(output_path, "wb") as out:
        out.write(pickle.dumps(codes))
        out.write(bytes([padding]))
        out.write(b_array)
    return output_path
