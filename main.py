import grpc
import predictor_pb2_grpc
import predictor_pb2
import server


def main():
    server.serve()

if __name__ == "__main__":
    main()