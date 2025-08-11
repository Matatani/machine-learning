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

        base_filename = os.path.basename(request.key)
        temp_original_path = f'./original_{base_filename}.png'
        temp_predicted_path = f'./predicted_{base_filename}.png'

        output_key = f'predicted/{base_filename}'

        self.__download_file__(request.bucket, request.key, temp_original_path)

        try:
            self.predictor.predict_image(image_path=temp_original_path, output_path=temp_predicted_path)
            self.__upload_file__(request.bucket, output_key, temp_predicted_path)
            print("Prediction successful:")
            return predictor_pb2.PredictImageResponse(className=output_key)

        except Exception as e:
            print("Error during prediction:", e)
            return predictor_pb2.PredictImageResponse(className="Error")

        finally:
            os.remove(temp_original_path)
            os.remove(temp_predicted_path)

    def __download_file__(self, bucket, key, path):
        try:
            print(f"Downloading s3://{bucket}/{key} to {path}")
            self.s3.download_file(bucket, key, path)
            print("Download successful.")
        except Exception as e:
            print(f"Error downloading from S3: {e}")
    def __upload_file__(self, bucket, key, path):
        try:
            self.s3.upload_file(
                path,
                bucket,
                key,
                ExtraArgs={'ContentType': 'image/png'}
            )
        except Exception as e:
            print(f"Error uploading to S3: {e}")
