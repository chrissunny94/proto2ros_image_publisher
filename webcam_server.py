import cv2
import grpc
import time
from concurrent import futures

import camera_stream_pb2 as pb
import camera_stream_pb2_grpc as pb_grpc

class CameraStreamServicer(pb_grpc.CameraStreamServicer):
    def StreamWebcam(self, request, context):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            height, width, _ = frame.shape
            _, jpeg_bytes = cv2.imencode('.jpg', frame)  # compress image
            yield pb.WebcamImage(
                width=width,
                height=height,
                encoding='jpeg',
                data=jpeg_bytes.tobytes()
            )
            time.sleep(1/30)  # simulate 30fps
        cap.release()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    pb_grpc.add_CameraStreamServicer_to_server(CameraStreamServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
