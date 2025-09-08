import runpod
from runpod.serverless.utils import rp_upload
import os
import websocket
import base64
import json
import uuid
import logging
import urllib.request
import urllib.parse
import binascii # Base64 에러 처리를 위해 import
# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


server_address = os.getenv('SERVER_ADDRESS', '127.0.0.1')
client_id = str(uuid.uuid4())
def save_data_if_base64(data_input, temp_dir, output_filename):
    """
    입력 데이터가 Base64 문자열인지 확인하고, 맞다면 파일로 저장 후 경로를 반환합니다.
    만약 일반 경로 문자열이라면 그대로 반환합니다.
    """
    # 입력값이 문자열이 아니면 그대로 반환
    if not isinstance(data_input, str):
        return data_input

    try:
        # Base64 문자열은 디코딩을 시도하면 성공합니다.
        decoded_data = base64.b64decode(data_input)
        
        # 디렉토리가 존재하지 않으면 생성
        os.makedirs(temp_dir, exist_ok=True)
        
        # 디코딩에 성공하면, 임시 파일로 저장합니다.
        file_path = os.path.abspath(os.path.join(temp_dir, output_filename))
        with open(file_path, 'wb') as f: # 바이너리 쓰기 모드('wb')로 저장
            f.write(decoded_data)
        
        # 저장된 파일의 경로를 반환합니다.
        print(f"✅ Base64 입력을 '{file_path}' 파일로 저장했습니다.")
        return file_path

    except (binascii.Error, ValueError):
        # 디코딩에 실패하면, 일반 경로로 간주하고 원래 값을 그대로 반환합니다.
        print(f"➡️ '{data_input}'은(는) 파일 경로로 처리합니다.")
        return data_input
    
def queue_prompt(prompt):
    url = f"http://{server_address}:8188/prompt"
    logger.info(f"Queueing prompt to: {url}")
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    url = f"http://{server_address}:8188/view"
    logger.info(f"Getting image from: {url}")
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{url}?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    url = f"http://{server_address}:8188/history/{prompt_id}"
    logger.info(f"Getting history from: {url}")
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break
        else:
            continue

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                # bytes 객체를 base64로 인코딩하여 JSON 직렬화 가능하게 변환
                if isinstance(image_data, bytes):
                    import base64
                    image_data = base64.b64encode(image_data).decode('utf-8')
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images

def load_workflow(workflow_path):
    with open(workflow_path, 'r') as file:
        return json.load(file)

def handler(job):
    job_input = job.get("input", {})

    logger.info(f"Received job input: {job_input}")

    # LoRA 개수에 따라 적절한 워크플로우 파일 선택
    lora_list = job_input.get("lora", [])
    lora_count = len(lora_list)
    
    if lora_count == 0:
        workflow_file = "/flux_krea_dev_api_nolora.json"
    elif lora_count == 1:
        workflow_file = "/flux_krea_dev_api_1lora.json"
    elif lora_count == 2:
        workflow_file = "/flux_krea_dev_api_2lora.json"
    elif lora_count == 3:
        workflow_file = "/flux_krea_dev_api_3lora.json"
    else:
        logger.warning(f"LoRA 개수가 {lora_count}개입니다. 최대 3개까지만 지원됩니다. 3개로 제한합니다.")
        lora_count = 3
        workflow_file = "/flux_krea_dev_api_3lora.json"
        lora_list = lora_list[:3]  # 처음 3개만 사용

    logger.info(f"Loading workflow: {workflow_file} with {lora_count} LoRAs")
    prompt = load_workflow(workflow_file)

    # 기본 설정
    prompt["45"]["inputs"]["text"] = job_input["prompt"]
    prompt["31"]["inputs"]["seed"] = job_input["seed"]
    prompt["31"]["inputs"]["cfg"] = job_input["guidance"]
    prompt["27"]["inputs"]["width"] = job_input["width"]
    prompt["27"]["inputs"]["height"] = job_input["height"]
    
    # 모델명이 입력으로 들어온 경우 38번 노드의 모델명 변경
    if "model" in job_input:
        prompt["38"]["inputs"]["unet_name"] = job_input["model"]
        logger.info(f"Model changed to: {job_input['model']}")
    
    # LoRA 설정 적용
    if lora_count > 0:
        # LoRA 노드 ID 매핑 (각 워크플로우에서 LoRA 노드 ID가 다름)
        lora_node_ids = {
            1: ["52"],
            2: ["52", "55"], 
            3: ["52", "55", "56"]
        }
        
        current_lora_nodes = lora_node_ids[lora_count]
        
        for i, (lora_name, weight) in enumerate(lora_list):
            if i < len(current_lora_nodes):
                node_id = current_lora_nodes[i]
                prompt[node_id]["inputs"]["lora_name"] = lora_name
                prompt[node_id]["inputs"]["strength_model"] = weight
                prompt[node_id]["inputs"]["strength_clip"] = weight
                logger.info(f"LoRA {i+1} applied: {lora_name} with weight {weight}")
    

    ws_url = f"ws://{server_address}:8188/ws?clientId={client_id}"
    logger.info(f"Connecting to WebSocket: {ws_url}")
    
    # 먼저 HTTP 연결이 가능한지 확인
    http_url = f"http://{server_address}:8188/"
    logger.info(f"Checking HTTP connection to: {http_url}")
    
    # HTTP 연결 확인 (최대 1분)
    max_http_attempts = 180
    for http_attempt in range(max_http_attempts):
        try:
            import urllib.request
            response = urllib.request.urlopen(http_url, timeout=5)
            logger.info(f"HTTP 연결 성공 (시도 {http_attempt+1})")
            break
        except Exception as e:
            logger.warning(f"HTTP 연결 실패 (시도 {http_attempt+1}/{max_http_attempts}): {e}")
            if http_attempt == max_http_attempts - 1:
                raise Exception("ComfyUI 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            time.sleep(1)
    
    ws = websocket.WebSocket()
    # 웹소켓 연결 시도 (최대 3분)
    max_attempts = int(180/5)  # 3분 (1초에 한 번씩 시도)
    for attempt in range(max_attempts):
        import time
        try:
            ws.connect(ws_url)
            logger.info(f"웹소켓 연결 성공 (시도 {attempt+1})")
            break
        except Exception as e:
            logger.warning(f"웹소켓 연결 실패 (시도 {attempt+1}/{max_attempts}): {e}")
            if attempt == max_attempts - 1:
                raise Exception("웹소켓 연결 시간 초과 (3분)")
            time.sleep(5)
    images = get_images(ws, prompt)
    ws.close()

    # 이미지가 없는 경우 처리
    if not images:
        return {"error": "이미지를 생성할 수 없습니다."}
    
    # 첫 번째 이미지 반환
    for node_id in images:
        if images[node_id]:
            return {"image": images[node_id][0]}
    
    return {"error": "이미지를 찾을 수 없습니다."}

runpod.serverless.start({"handler": handler})