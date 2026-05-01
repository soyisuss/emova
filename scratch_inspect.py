import onnxruntime as ort
import os

model_path = os.path.join("models", "resnet50_emotion.onnx")
sess = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])

meta = sess.get_modelmeta()
print("Metadata:")
print("Custom Metadata Map:", meta.custom_metadata_map)
print("Description:", meta.description)
print("Domain:", meta.domain)
print("Graph Name:", meta.graph_name)
print("Producer Name:", meta.producer_name)
print("Version:", meta.version)

for item in sess.get_outputs():
    print("Output Name:", item.name)
    print("Output Shape:", item.shape)
    print("Output Type:", item.type)
