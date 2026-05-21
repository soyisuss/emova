import numpy as np
from emova.core.vision.preprocess import preprocess

def test_preprocess_shape_and_type(dummy_image_rgb):
    """Test that preprocessing outputs the correct shape (3, 224, 224) and dtype."""
    tensor = preprocess(dummy_image_rgb)
    
    # 1. Output shape should be (3, 224, 224)
    assert tensor.shape == (3, 224, 224)
    
    # 2. Output dtype should be float32
    assert tensor.dtype == np.float32

def test_preprocess_normalization():
    """Test that ImageNet normalization is applied correctly."""
    # We create an image with zero values (black)
    black_image = np.zeros((300, 300, 3), dtype=np.uint8)
    tensor = preprocess(black_image)
    
    # For a black image (all zeros), after /255.0, it's 0.0
    # Then normalized: (0 - mean) / std
    # mean = [0.485, 0.456, 0.406]
    # std = [0.229, 0.224, 0.225]
    # Expected channel 0 (R) -> (0 - 0.485) / 0.229 ≈ -2.1179
    expected_R = -0.485 / 0.229
    expected_G = -0.456 / 0.224
    expected_B = -0.406 / 0.225
    
    # Assert close for the first pixel of channels
    assert np.isclose(tensor[0, 0, 0], expected_R, atol=1e-3)
    assert np.isclose(tensor[1, 0, 0], expected_G, atol=1e-3)
    assert np.isclose(tensor[2, 0, 0], expected_B, atol=1e-3)
