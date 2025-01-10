import os
import heapq
from collections import defaultdict
import pickle
import base64
import zlib

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCompressor:
    @staticmethod
    def build_frequency_dict(data):
        """
        Build frequency dictionary using a defaultdict
        Time Complexity: O(n), where n is the length of data
        Space Complexity: O(k), where k is the number of unique characters
        """
        freq_dict = defaultdict(int)
        for char in data:
            freq_dict[char] += 1
        return freq_dict

    @staticmethod
    def build_huffman_tree(freq_dict):
        """
        Build Huffman tree using a min-heap
        Time Complexity: O(k log k), where k is the number of unique characters
        Space Complexity: O(k)
        """
        heap = [HuffmanNode(char, freq) for char, freq in freq_dict.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            merged = HuffmanNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            
            heapq.heappush(heap, merged)
        
        return heap[0] if heap else None

    @staticmethod
    def build_huffman_codes(root):
        """
        Generate Huffman codes for each character
        Time Complexity: O(k), where k is the number of unique characters
        Space Complexity: O(k)
        """
        def traverse(node, current_code):
            if not node:
                return {}
            
            if not node.left and not node.right:
                return {node.char: current_code}
            
            codes = {}
            codes.update(traverse(node.left, current_code + "0"))
            codes.update(traverse(node.right, current_code + "1"))
            return codes

        return traverse(root, "")

    @staticmethod
    def compress(data, compression_percentage=50):
        """
        Main compression method with compression percentage support
        Time Complexity: O(n log k), where n is data length, k is unique characters
        Space Complexity: O(n)
        """
        if not data:
            return "", {}

        # Build frequency dictionary
        freq_dict = HuffmanCompressor.build_frequency_dict(data)
        
        # Adjust frequency based on compression percentage
        total_chars = sum(freq_dict.values())
        
        # Calculate threshold to remove less frequent characters
        # Lower compression percentage means more aggressive removal
        threshold = total_chars * (1 - (compression_percentage / 100))
        
        # Sort characters by frequency in ascending order
        sorted_chars = sorted(freq_dict.items(), key=lambda x: x[1])
        
        # Remove least frequent characters
        chars_to_remove = set()
        current_removed_count = 0
        for char, freq in sorted_chars:
            if current_removed_count >= threshold:
                break
            chars_to_remove.add(char)
            current_removed_count += freq
        
        # Rebuild frequency dictionary without removed characters
        filtered_freq_dict = {
            char: freq for char, freq in freq_dict.items() 
            if char not in chars_to_remove
        }
        
        # If no characters left, return original data
        if not filtered_freq_dict:
            return data, {}
        
        # Build Huffman tree
        huffman_tree = HuffmanCompressor.build_huffman_tree(filtered_freq_dict)
        
        # Generate Huffman codes
        huffman_codes = HuffmanCompressor.build_huffman_codes(huffman_tree)
        
        # Compress the data
        compressed_data = ''.join(huffman_codes.get(char, '') for char in data)
        
        # Additional compression using zlib
        compressed_data_bytes = compressed_data.encode('utf-8')
        zlib_compressed = zlib.compress(compressed_data_bytes, level=9)
        
        # Base64 encode for safe storage
        base64_compressed = base64.b64encode(zlib_compressed).decode('utf-8')
        
        return base64_compressed, huffman_codes

    @staticmethod
    def decompress(compressed_data, huffman_codes):
        """
        Decompress method
        Time Complexity: O(n), where n is compressed data length
        Space Complexity: O(n)
        """
        # Reverse the Huffman codes dictionary
        reverse_codes = {code: char for char, code in huffman_codes.items()}
        
        # Decode base64 and decompress zlib
        zlib_compressed = base64.b64decode(compressed_data)
        decompressed_data_bytes = zlib.decompress(zlib_compressed)
        compressed_data = decompressed_data_bytes.decode('utf-8')
        
        current_code = ""
        decompressed_data = ""
        
        for bit in compressed_data:
            current_code += bit
            if current_code in reverse_codes:
                decompressed_data += reverse_codes[current_code]
                current_code = ""
        
        return decompressed_data

    @staticmethod
    def compress_file(input_path, output_path=None, compression_percentage=50):
        """
        Compress a file using Huffman coding
        
        Args:
            input_path (str): Path to the input file
            output_path (str, optional): Path to save the compressed file
            compression_percentage (int, optional): Compression percentage
        
        Returns:
            dict: Compression result details
        """
        try:
            # Read file contents
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Convert bytes to string for Huffman compression
            data_str = data.decode('latin-1')
            
            # Compress data with compression percentage
            compressed_data, huffman_codes = HuffmanCompressor.compress(
                data_str, 
                compression_percentage=compression_percentage
            )
            
            # Prepare output path
            if output_path is None:
                output_path = input_path + '.huffman'
            
            # Save compressed data and Huffman codes
            with open(output_path, 'wb') as f:
                # Save Huffman codes and compressed data
                pickle.dump({
                    'codes': huffman_codes, 
                    'compressed_data': compressed_data,
                    'original_length': len(data_str)
                }, f)
            
            # Calculate compression metrics
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            return {
                'original_path': input_path,
                'compressed_path': output_path,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_percentage': round(compression_ratio, 2)
            }
        
        except Exception as e:
            raise ValueError(f"File compression failed: {str(e)}")

    @staticmethod
    def decompress_file(input_path, output_path=None):
        """
        Decompress a Huffman-compressed file
        
        Args:
            input_path (str): Path to the compressed file
            output_path (str, optional): Path to save the decompressed file
        
        Returns:
            str: Path to the decompressed file
        """
        try:
            # Read compressed data and Huffman codes
            with open(input_path, 'rb') as f:
                compressed_data_dict = pickle.load(f)
            
            # Extract compressed data and codes
            compressed_data = compressed_data_dict['compressed_data']
            huffman_codes = compressed_data_dict['codes']
            original_length = compressed_data_dict.get('original_length', None)
            
            # Decompress data
            decompressed_data = HuffmanCompressor.decompress(compressed_data, huffman_codes)
            
            # Prepare output path
            if output_path is None:
                output_path = input_path.replace('.huffman', '')
            
            # Truncate to original length if available
            if original_length is not None:
                decompressed_data = decompressed_data[:original_length]
            
            # Save decompressed data
            with open(output_path, 'wb') as f:
                f.write(decompressed_data.encode('latin-1'))
            
            return output_path
        
        except Exception as e:
            raise ValueError(f"File decompression failed: {str(e)}")
