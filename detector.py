from ultralytics import YOLO
import torch


# GPU 있으면 GPU, 없으면 CPU
DEVICE = 0 if torch.cuda.is_available() else "cpu"

print("DEVICE :", DEVICE)
print("CUDA :", torch.cuda.is_available())

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))


# 모델 로드
model = YOLO("bestv2.pt")

if torch.cuda.is_available():
    model.to("cuda")


# 객체 탐지 함수
def detect(frame):

    results = model.track(

        source=frame,

        persist=True,

        tracker="bytetrack.yaml",

        device=DEVICE,

        conf=0.30,

        iou=0.50,

        imgsz=416,

        verbose=False

    )

    return results