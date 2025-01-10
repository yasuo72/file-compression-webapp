# File Compression Web Application

## Overview
A powerful web application for file compression using advanced data structures and algorithms, demonstrating key computer science principles.

## Data Structures and Algorithms Explored

### 1. Huffman Coding Algorithm
#### Key DSA Concepts
- **Greedy Algorithm**: Huffman coding uses a greedy approach to build an optimal prefix code
- **Priority Queue (Min-Heap)**: Efficiently manages character frequencies during tree construction
- **Binary Tree**: Represents the Huffman encoding tree
- **Hash Map (Dictionary)**: Stores character frequencies and encoding mappings

#### Implementation Details
- Time Complexity: O(n log k), where n is data length and k is unique characters
- Space Complexity: O(k), where k is the number of unique characters
- Uses heapq for priority queue operations
- Builds an optimal prefix code for data compression

### 2. Frequency-Based Compression Techniques
#### DSA Concepts
- **Sorting Algorithms**: Used to sort characters by frequency
- **Set Data Structure**: Efficiently remove less frequent characters
- **Statistical Analysis**: Calculate character frequency thresholds

### 3. Compression Strategies
#### Algorithmic Approaches
- Character frequency filtering
- Prefix coding
- Lossy and lossless compression techniques
- Multi-stage compression algorithm

### 4. Advanced Data Processing
- **Stream Processing**: Handle data in chunks
- **Encoding Techniques**: 
  - Base64 encoding
  - zlib compression
- **Error Handling**: Robust decompression mechanisms

## Algorithmic Complexity Analysis

### Compression Process
1. Frequency Dictionary Creation: O(n)
2. Huffman Tree Construction: O(k log k)
3. Encoding Generation: O(k)
4. Data Compression: O(n)

### Decompression Process
1. Code Reversal: O(k)
2. Bit Stream Decoding: O(n)

## Technologies
- Python
- Flask
- Huffman Coding Algorithm
- zlib Compression
- Base64 Encoding

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/file-compression-webapp.git
cd file-compression-webapp
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python app.py
```

## Usage
- Upload files for compression
- Adjust compression percentage
- Download compressed or decompressed files

## Compression Techniques
- Character frequency filtering
- Huffman coding
- zlib compression
- Base64 encoding

## Learning Outcomes
- Advanced compression algorithms
- Efficient data representation
- Algorithmic optimization techniques
- Practical application of theoretical computer science concepts

## License
MIT License

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
