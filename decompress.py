import pickle

def decompress_file(input_path, output_path):
    with open(input_path, "rb") as f:
        try:
            codes = pickle.load(f)
        except Exception as e:
            raise ValueError("❌ Failed to load Huffman codes. File may be corrupted or not a valid .huff file.") from e

        
        reverse_codes = {}

        for k, v in codes.items():
            
            if isinstance(k, int):
               
                reverse_codes[v] = k
            elif isinstance(k, bytes):
                
                if len(k) == 1:
                    reverse_codes[v] = k[0]
                else:
                    raise ValueError(f"Invalid key length in codes dict: {k}")
            elif isinstance(k, str):
                
                if len(k) == 1:
                    reverse_codes[v] = ord(k)
                else:
                    raise ValueError(f"Invalid key length in codes dict: {k}")
            else:
                raise ValueError(f"Unexpected key type in codes dict: {type(k)}")

        padding_byte = f.read(1)
        if not padding_byte:
            raise ValueError("❌ Padding information missing.")
        padding = padding_byte[0]

        byte_data = f.read()
        if not byte_data:
            raise ValueError("❌ Encoded data is missing.")

        bit_string = ''.join(f'{byte:08b}' for byte in byte_data)

        if padding > 0:
            bit_string = bit_string[:-padding]

        decoded_bytes = bytearray()
        current_bits = ""
        for bit in bit_string:
            current_bits += bit
            if current_bits in reverse_codes:
                decoded_bytes.append(reverse_codes[current_bits])
                current_bits = ""

        with open(output_path, "wb") as out_file:
            out_file.write(decoded_bytes)

        print(f"✅ Decompression complete: {output_path}")
