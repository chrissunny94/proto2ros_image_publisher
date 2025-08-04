import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import grpc
import numpy as np
import cv2

import camera_stream_pb2 as pb
import camera_stream_pb2_grpc as pb_grpc

class GrpcImagePublisher(Node):
    def __init__(self):
        super().__init__('grpc_image_publisher')
        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()

        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = pb_grpc.CameraStreamStub(self.channel)
        self.stream = self.stub.StreamWebcam(pb.Empty())

        self.timer = self.create_timer(0.03, self.publish_image)  # 30 Hz

    def publish_image(self):
        try:
            msg = next(self.stream)
            img_bytes = np.frombuffer(msg.data, dtype=np.uint8)
            cv_img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
            ros_img = self.bridge.cv2_to_imgmsg(cv_img, encoding='bgr8')
            self.publisher.publish(ros_img)
        except StopIteration:
            self.get_logger().info('gRPC stream ended')
        except Exception as e:
            self.get_logger().error(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = GrpcImagePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
