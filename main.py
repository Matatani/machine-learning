import grpc
import predictor_pb2_grpc
import predictor_pb2

def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = predictor_pb2_grpc.PredictorStub(channel)

    greeting = predictor_pb2.Greeting(greeting='Hello, world!', name='World')
    request = predictor_pb2.HelloRequest(greeting=greeting)
    setattr(request, "from", "Python Server")

    response = stub.Hello(request)
    print("Go server responded:", response.greeting)

if __name__ == "__main__":
    main()