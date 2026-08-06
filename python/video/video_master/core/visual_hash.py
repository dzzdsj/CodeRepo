from PIL import Image

def calculate_dhash(img: Image.Image) -> str:
    """Calculate the 64-bit Difference Hash (dHash) of a PIL Image.
    
    dHash tracks gradients of intensity. It is extremely fast and robust
    against scaling, aspect ratio changes, and minor compression artifacts.
    
    Args:
        img: A PIL Image object.
        
    Returns:
        A 16-character hex string representing the 64-bit hash, or empty string if failed.
    """
    if img is None:
        return ""
    
    try:
        # Convert to grayscale and resize to 9x8 (9 columns, 8 rows)
        # Note: We use 9 columns because we compare adjacent pixels horizontally (9 pixels = 8 comparisons)
        gray = img.convert('L')
        resized = gray.resize((9, 8), Image.Resampling.LANCZOS)
        
        pixels = list(resized.getdata())
        
        difference = []
        for row in range(8):
            for col in range(8):
                pixel_left = pixels[row * 9 + col]
                pixel_right = pixels[row * 9 + col + 1]
                difference.append(pixel_left > pixel_right)
        
        # Convert the 64 boolean values to a 64-bit integer, then to a 16-character hex string
        decimal_value = 0
        for index, value in enumerate(difference):
            if value:
                decimal_value += 1 << index
                
        return f"{decimal_value:016x}"
    except Exception:
        return ""

def hamming_distance(hash1: str, hash2: str) -> int:
    """Compute the Hamming distance between two 64-bit hex hash strings.
    
    Hamming distance is the number of bits that are different between two hashes.
    A distance of 0 means identical images, <= 4 means highly similar,
    and > 10 means different images.
    
    Args:
        hash1: 16-character hex hash.
        hash2: 16-character hex hash.
        
    Returns:
        The number of differing bits, or 64 if either hash is invalid/empty.
    """
    if not hash1 or not hash2 or len(hash1) != 16 or len(hash2) != 16:
        return 64
        
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        return bin(val1 ^ val2).count('1')
    except ValueError:
        return 64
