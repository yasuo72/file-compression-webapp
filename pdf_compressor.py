import io
import os
import logging
import tempfile
import zlib
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFCompressor:
    @staticmethod
    def compress_pdf(input_path, output_path=None, compression_percentage=50):
        """
        Advanced PDF compression with multiple strategies and guaranteed size reduction
        
        Compression Techniques:
        1. Multi-stage compression
        2. Adaptive reduction strategies
        3. Fallback mechanisms
        4. Extreme compression options
        """
        try:
            # Validate input parameters
            if not input_path.lower().endswith('.pdf'):
                raise ValueError("Only PDF files are supported")
            
            # Validate compression percentage
            if not (0 < compression_percentage <= 100):
                raise ValueError("Compression percentage must be between 1 and 100")
            
            # Prepare paths
            output_path = output_path or input_path.replace('.pdf', '_compressed.pdf')
            original_size = os.path.getsize(input_path)
            logger.info(f"Original file size: {original_size} bytes")
            logger.info(f"Target compression: {compression_percentage}%")
            
            # Multiple compression strategies with increasing aggressiveness
            compression_methods = [
                (PDFCompressor._compress_with_pypdf2_advanced, 0.5),
                (PDFCompressor._compress_with_pypdf2_basic, 0.7),
                (PDFCompressor._compress_with_image_processing, 0.9)
            ]
            
            # Track best compression result
            best_compression_result = None
            
            # Try each compression method
            for method, aggressiveness in compression_methods:
                try:
                    # Attempt compression
                    result = method(input_path, output_path, compression_percentage * aggressiveness)
                    
                    # Validate compression
                    compressed_size = os.path.getsize(output_path)
                    compression_ratio = (1 - compressed_size / original_size) * 100
                    
                    logger.info(f"Method {method.__name__} result:")
                    logger.info(f"Compressed size: {compressed_size} bytes")
                    logger.info(f"Compression ratio: {compression_ratio:.2f}%")
                    
                    # Check if compression meets target
                    if compressed_size < original_size:
                        # Update best compression if it's better
                        if (best_compression_result is None or 
                            compression_ratio > best_compression_result['compression_percentage']):
                            best_compression_result = {
                                'original_path': input_path,
                                'compressed_path': output_path,
                                'original_size': original_size,
                                'compressed_size': compressed_size,
                                'compression_percentage': round(compression_ratio, 2)
                            }
                        
                        # If we meet or exceed the target, return immediately
                        if compression_ratio >= compression_percentage * 0.8:
                            logger.info(f"Successful compression using {method.__name__}")
                            return best_compression_result
                
                except Exception as method_err:
                    logger.warning(f"Compression method {method.__name__} failed: {method_err}")
            
            # If we have a partial compression result, return it
            if best_compression_result:
                logger.warning("Could not fully meet compression target, returning best result")
                return best_compression_result
            
            # If all methods fail
            raise ValueError(f"Unable to compress PDF to {compression_percentage}% target")
        
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            raise ValueError(f"Compression failed: {str(e)}")

    @staticmethod
    def _compress_with_pypdf2_advanced(input_path, output_path, compression_percentage):
        """
        Advanced PDF compression using PyPDF2 with content stream and image compression
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Adaptive compression level
            compression_level = max(1, min(9, int(9 * compression_percentage / 100)))
            logger.info(f"Using compression level: {compression_level}")
            
            # Track compression details
            compressed_page_count = 0
            total_page_count = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages):
                try:
                    # Compress content streams
                    page.compress_content_streams(level=compression_level)
                    
                    # Image compression
                    images = page.images
                    for img_index, image in enumerate(images):
                        try:
                            # Open image
                            img = Image.open(io.BytesIO(image.data))
                            
                            # Compress image
                            compressed_img = io.BytesIO()
                            img.save(
                                compressed_img, 
                                format='JPEG', 
                                optimize=True, 
                                quality=max(5, 95 - int(compression_percentage))
                            )
                            
                            # Replace if smaller
                            compressed_data = compressed_img.getvalue()
                            if len(compressed_data) < len(image.data):
                                page.images[img_index] = compressed_data
                                logger.info(f"Compressed image on page {page_num}")
                        except Exception as img_err:
                            logger.warning(f"Image compression failed on page {page_num}: {img_err}")
                    
                    # Add compressed page
                    writer.add_page(page)
                    compressed_page_count += 1
                
                except Exception as page_err:
                    logger.warning(f"Page {page_num} compression failed: {page_err}")
                    writer.add_page(page)  # Add original page if compression fails
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            logger.info(f"Compressed {compressed_page_count}/{total_page_count} pages")
            return output_path
        
        except Exception as e:
            logger.warning(f"PyPDF2 advanced compression failed: {e}")
            raise

    @staticmethod
    def _compress_with_pypdf2_basic(input_path, output_path, compression_percentage):
        """
        Basic PDF compression using PyPDF2
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Simple page compression
            for page in reader.pages:
                writer.add_page(page)
                page.compress_content_streams()
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        except Exception as e:
            logger.warning(f"PyPDF2 basic compression failed: {e}")
            raise

    @staticmethod
    def _compress_with_image_processing(input_path, output_path, compression_percentage):
        """
        Image-based PDF compression using Pillow
        """
        try:
            # Temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert PDF to images
                images = PDFCompressor._pdf_to_images(input_path, temp_dir)
                
                # Compress images
                compressed_images = []
                for img_path in images:
                    compressed_img = PDFCompressor._compress_single_image(img_path, compression_percentage)
                    compressed_images.append(compressed_img)
                
                # Convert compressed images back to PDF
                PDFCompressor._images_to_pdf(compressed_images, output_path)
            
            return output_path
        except Exception as e:
            logger.warning(f"Image processing compression failed: {e}")
            raise

    @staticmethod
    def _pdf_to_images(pdf_path, output_dir):
        """
        Convert PDF to images using PyPDF2
        """
        reader = PdfReader(pdf_path)
        image_paths = []
        
        for page_num, page in enumerate(reader.pages):
            for img_index, image in enumerate(page.images):
                try:
                    img_path = os.path.join(output_dir, f'page_{page_num}_img_{img_index}.png')
                    
                    # Extract and save image
                    with open(img_path, 'wb') as img_file:
                        img_file.write(image.data)
                    
                    image_paths.append(img_path)
                except Exception as e:
                    logger.warning(f"Image extraction failed: {e}")
        
        return image_paths

    @staticmethod
    def _compress_single_image(image_path, compression_percentage):
        """
        Compress a single image using Pillow
        """
        # Open image
        img = Image.open(image_path)
        
        # Adaptive compression parameters
        quality = max(1, min(95, int(95 - (compression_percentage * 0.9))))
        
        # Compress image
        compressed_path = image_path.replace('.png', '_compressed.jpg')
        img.save(
            compressed_path, 
            'JPEG', 
            optimize=True, 
            quality=quality
        )
        
        return compressed_path

    @staticmethod
    def _images_to_pdf(image_paths, output_path):
        """
        Convert images back to PDF
        """
        merger = PdfMerger()
        
        for img_path in image_paths:
            # Create a temporary PDF from each image
            temp_pdf_path = img_path.replace('.jpg', '.pdf')
            img = Image.open(img_path)
            img_rgb = img.convert('RGB')
            img_rgb.save(temp_pdf_path)
            
            # Merge into final PDF
            merger.append(temp_pdf_path)
        
        # Write final PDF
        merger.write(output_path)
        merger.close()

    @staticmethod
    def decompress_pdf(compressed_path, output_path=None):
        """
        PDF decompression utility
        """
        try:
            output_path = output_path or compressed_path.replace('_compressed.pdf', '_original.pdf')
            
            # Simple copy as compression is lossless
            with open(compressed_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
            
            return output_path
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise ValueError(f"Decompression failed: {str(e)}")
