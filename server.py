from concurrent import futures

import grpc

from predictor.predictor import PaddyPredictor
import predictor_pb2
import predictor_pb2_grpc
import boto3
import os


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    predictor_pb2_grpc.add_PredictorServicer_to_server(PredictorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051.")
    server.wait_for_termination()


class PredictorServicer(predictor_pb2_grpc.PredictorServicer):
    def __init__(self):
        self.predictor = PaddyPredictor()
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )


    def Hello(self, request, context):
        return predictor_pb2.HelloResponse(greeting=f"Hello, {request.greeting.name}!")

    def PredictImage(self, request, context):
        print("PredictImage called with request:", request)
        local_path = f'/tmp/{request.key}'
        try:
            self.s3.download_file(request.bucket, request.key, local_path)
            print("Download successful:", local_path)
        except Exception as e:
            print("Error downloading from S3:", e)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return predictor_pb2.PredictImageResponse(className="Error")

        try:
            predicted_label = self.predictor.predict_image(local_path)
            print("Prediction successful:", predicted_label)
            return predictor_pb2.PredictImageResponse(className=f'The disease is {predicted_label}')
        except Exception as e:
            print("Error during prediction:", e)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return predictor_pb2.PredictImageResponse(className="Error")
