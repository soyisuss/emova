import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from emova.core.model.emotion_predictor import EmotionPredictor

@patch('emova.core.model.emotion_predictor.ort.InferenceSession')
@patch('os.path.exists', return_value=True)
def test_emotion_predictor_single_image(mock_exists, mock_ort_session):
    """Test that the EmotionPredictor processes a single image tensor and returns the dominant emotion."""
    # Setup mock session
    mock_session_instance = MagicMock()
    mock_ort_session.return_value = mock_session_instance
    
    mock_input = MagicMock()
    mock_input.name = "input"
    mock_session_instance.get_inputs.return_value = [mock_input]
    
    # Mock return values for probabilities
    # Logits: [0.1, 0.2, 5.0] -> "Contento" dominates (idx 2)
    mock_session_instance.run.return_value = [np.array([[0.1, 0.2, 5.0]], dtype=np.float32)]
    
    predictor = EmotionPredictor("dummy_path.onnx")
    
    # Create dummy tensor (3, 224, 224)
    tensor = np.zeros((3, 224, 224), dtype=np.float32)
    
    emotion, confidence = predictor.predict(tensor)
    
    assert emotion == "Contento"
    assert confidence > 0.9

@patch('emova.core.model.emotion_predictor.ort.InferenceSession')
@patch('os.path.exists', return_value=True)
def test_emotion_predictor_batch_images(mock_exists, mock_ort_session):
    """Test that the EmotionPredictor handles a batch of images and averages predictions."""
    mock_session_instance = MagicMock()
    mock_ort_session.return_value = mock_session_instance
    
    mock_input = MagicMock()
    mock_input.name = "input"
    mock_session_instance.get_inputs.return_value = [mock_input]
    
    # We will pass a batch of 2 images.
    # MagicMock run side_effect allows us to return different results per call.
    # Call 1: predicts "Contento" strongly
    # Call 2: predicts "Neutral" strongly
    mock_session_instance.run.side_effect = [
        [np.array([[-5.0, -5.0, 5.0]], dtype=np.float32)],  # "Contento" ~100%
        [np.array([[-5.0, 5.0, -5.0]], dtype=np.float32)]   # "Neutral" ~100%
    ]
    
    predictor = EmotionPredictor("dummy_path.onnx")
    
    # Create dummy batch tensor (2, 3, 224, 224)
    batch_tensor = np.zeros((2, 3, 224, 224), dtype=np.float32)
    
    emotion, confidence = predictor.predict(batch_tensor)
    
    # The average should be roughly 50% Contento and 50% Neutral.
    # With floating point max arg, the first one that matches might win, or the one slightly higher.
    # Here they should both be ~0.5 probability.
    assert confidence >= 0.49
    assert emotion in ["Contento", "Neutral"]
