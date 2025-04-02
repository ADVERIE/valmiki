set -e  # Exit immediately if a command exits with a non-zero status

# Create proto directory if it doesn't exist
mkdir -p proto

cp -v ../gyandoot-svc/proto/valmiki/valmiki.proto proto/

pip install grpcio-tools

python -m grpc_tools.protoc \
    -I proto \
    --python_out=app \
    --grpc_python_out=app \
    proto/valmiki.proto

sed -i.bak -E 's/^import valmiki_pb2/from . import valmiki_pb2/' app/valmiki_pb2_grpc.py
rm -f app/valmiki_pb2_grpc.py.bak

echo "Proto files generated successfully" 
