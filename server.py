from concurrent import futures

import grpc
import predictor_pb2
import predictor_pb2_grpc


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    predictor_pb2_grpc.add_PredictorServicer_to_server(PredictorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051.")
    server.wait_for_termination()


class PredictorServicer(predictor_pb2_grpc.PredictorServicer):
    def Hello(self, request, context):
        return predictor_pb2.HelloResponse(greeting=f"Hello, {request.greeting.name}!")

