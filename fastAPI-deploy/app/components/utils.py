import sys
from typing import Any

import tritonclient.grpc as grpcclient


def create_client(url) -> Any:
	triton_client = grpcclient.InferenceServerClient(url)

	# Health check
	if not triton_client.is_server_live():
		print("FAILED : is_server_live")
		sys.exit(1)

	if not triton_client.is_server_ready():
		print("FAILED : is_server_ready")
		sys.exit(1)

	if not triton_client.is_model_ready('yolov4'):
		print("FAILED : is_model_ready")
		sys.exit(1)

	return triton_client