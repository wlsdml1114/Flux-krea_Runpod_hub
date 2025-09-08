# Flux Krea for RunPod Serverless

이 프로젝트는 RunPod Serverless 환경에서 [Flux Krea](https://bfl.ai/blog/flux-1-krea-dev)를 쉽게 배포하고 사용할 수 있도록 설계된 템플릿입니다.

[![Runpod](https://api.runpod.io/badge/wlsdml1114/Flux-krea_Runpod_hub)](https://console.runpod.io/hub/wlsdml1114/Flux-krea_Runpod_hub)

Flux Krea는 Flux 아키텍처를 사용하여 고품질 이미지를 생성하는 고급 AI 모델로, 여러 LoRA(Low-Rank Adaptation) 모델을 지원합니다.

## ✨ 주요 기능

*   **텍스트-이미지 생성**: 고급 Flux 아키텍처를 사용하여 텍스트 설명으로부터 고품질 이미지를 생성합니다.
*   **다중 LoRA 지원**: 최대 3개의 LoRA 모델을 동시에 지원하여 향상된 커스터마이제이션을 제공합니다.
*   **동적 모델 로딩**: LoRA 개수에 따라 적절한 워크플로우를 자동으로 선택합니다 (0-3개 LoRA).
*   **커스터마이징 가능한 파라미터**: 시드, 가이던스, 너비, 높이, 프롬프트 등 다양한 파라미터로 이미지 생성을 제어할 수 있습니다.
*   **ComfyUI 통합**: 유연한 워크플로우 관리를 위해 ComfyUI를 기반으로 구축되었습니다.
*   **듀얼 CLIP 지원**: 듀얼 CLIP 모델 통합으로 향상된 텍스트 이해를 제공합니다.

## 🚀 RunPod Serverless 템플릿

이 템플릿은 Flux Krea를 RunPod Serverless Worker로 실행하는 데 필요한 모든 구성 요소를 포함합니다.

*   **Dockerfile**: 모델 실행에 필요한 모든 의존성을 설치하고 환경을 구성합니다.
*   **handler.py**: RunPod Serverless를 위한 요청을 처리하는 핸들러 함수를 구현합니다.
*   **entrypoint.sh**: 워커가 시작될 때 초기화 작업을 수행합니다.
*   **워크플로우 JSON**: 다양한 LoRA 조합을 위한 여러 워크플로우 구성을 포함합니다.

### 입력

`input` 객체는 다음 필드들을 포함해야 합니다. `model`과 `lora`를 제외한 모든 파라미터는 필수입니다.

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `prompt` | `string` | **예** | `N/A` | 생성할 이미지에 대한 설명 텍스트입니다. |
| `seed` | `integer` | **예** | `N/A` | 이미지 생성용 랜덤 시드입니다 (출력의 무작위성에 영향을 줍니다). |
| `guidance` | `float` | **예** | `N/A` | 프롬프트에 대한 생성 준수도를 제어하는 가이던스 스케일입니다. |
| `width` | `integer` | **예** | `N/A` | 출력 이미지의 픽셀 단위 너비입니다. |
| `height` | `integer` | **예** | `N/A` | 출력 이미지의 픽셀 단위 높이입니다. |
| `model` | `string` | **아니오** | `flux1-krea-dev_fp8_scaled.safetensors` | 기본값 대신 사용할 커스텀 모델 경로입니다 (네트워크 볼륨 필요). |
| `lora` | `array` | **아니오** | `[]` | `[모델_경로, 가중치]` 튜플의 LoRA 구성 배열입니다 (네트워크 볼륨 필요). |

**LoRA 구성:**
- 각 LoRA 항목은 두 개의 요소를 가진 배열이어야 합니다: `[모델_이름, 가중치]`
- `모델_이름`: LoRA 모델 파일의 전체 경로 (예: `"/my_volume/loras/lora.safetensors"`)
- `가중치`: LoRA의 강도/가중치 (일반적으로 0.0과 2.0 사이)
- 최대 3개의 LoRA 지원
- 3개 이상의 LoRA가 제공되면 처음 3개만 사용됩니다
- **참고**: 커스텀 모델과 LoRA는 네트워크 볼륨이 구성되어야 합니다

**요청 예시:**

**기본 요청 (LoRA 없음):**
```json
{
  "input": {
    "prompt": "산과 호수가 있는 아름다운 풍경",
    "seed": 12345,
    "guidance": 7.5,
    "width": 1024,
    "height": 1024
  }
}
```

**커스텀 모델 요청 (네트워크 볼륨):**
```json
{
  "input": {
    "prompt": "산과 호수가 있는 아름다운 풍경",
    "seed": 12345,
    "guidance": 7.5,
    "width": 1024,
    "height": 1024,
    "model": "/my_volume/models/custom_model.safetensors"
  }
}
```

**단일 LoRA 요청 (네트워크 볼륨):**
```json
{
  "input": {
    "prompt": "산과 호수가 있는 아름다운 풍경",
    "seed": 12345,
    "guidance": 7.5,
    "width": 1024,
    "height": 1024,
    "lora": [
      ["/my_volume/loras/style_lora.safetensors", 0.8]
    ]
  }
}
```

**다중 LoRA 요청 (네트워크 볼륨):**
```json
{
  "input": {
    "prompt": "산과 호수가 있는 아름다운 풍경",
    "seed": 12345,
    "guidance": 7.5,
    "width": 1024,
    "height": 1024,
    "model": "/my_volume/models/custom_model.safetensors",
    "lora": [
      ["/my_volume/loras/style_lora.safetensors", 0.8],
      ["/my_volume/loras/character_lora.safetensors", 1.0],
      ["/my_volume/loras/background_lora.safetensors", 0.5]
    ]
  }
}
```

### 출력

#### 성공

작업이 성공하면 생성된 이미지가 Base64로 인코딩된 JSON 객체를 반환합니다.

| 파라미터 | 타입 | 설명 |
| --- | --- | --- |
| `image` | `string` | Base64로 인코딩된 이미지 파일 데이터입니다. |

**성공 응답 예시:**

```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
}
```

#### 오류

작업이 실패하면 오류 메시지가 포함된 JSON 객체를 반환합니다.

| 파라미터 | 타입 | 설명 |
| --- | --- | --- |
| `error` | `string` | 발생한 오류에 대한 설명입니다. |

**오류 응답 예시:**

```json
{
  "error": "이미지를 생성할 수 없습니다."
}
```

## 🛠️ 사용법 및 API 참조

1.  이 저장소를 기반으로 RunPod에서 Serverless Endpoint를 생성합니다.
2.  빌드가 완료되고 엔드포인트가 활성화되면 아래 API 참조에 따라 HTTP POST 요청을 통해 작업을 제출합니다.

### 📁 네트워크 볼륨 사용

**중요**: 커스텀 모델과 LoRA는 네트워크 볼륨을 사용할 때만 적용됩니다. 네트워크 볼륨이 구성되지 않으면 기본 모델이 사용됩니다.

Base64로 인코딩된 파일을 직접 전송하는 대신 RunPod의 네트워크 볼륨을 사용하여 대용량 파일을 처리할 수 있습니다. 이는 특히 대용량 모델 파일을 다룰 때 유용합니다.

1.  **네트워크 볼륨 생성 및 연결**: RunPod 대시보드에서 네트워크 볼륨(예: S3 기반 볼륨)을 생성하고 Serverless Endpoint 설정에 연결합니다.
2.  **파일 업로드**: 사용하려는 모델 파일과 LoRA 파일을 생성된 네트워크 볼륨에 업로드합니다.
3.  **파일 구성**: 네트워크 볼륨 내에서 다음 구조로 파일을 구성합니다:
    - **모델**: 커스텀 모델 파일을 `models/` 폴더에 배치
    - **LoRA**: LoRA 파일을 `loras/` 폴더에 배치
4.  **경로 지정**: API 요청 시 `model`과 LoRA 이름에 대해 네트워크 볼륨 내의 파일 경로를 지정합니다. 예를 들어:
    - 볼륨이 `/my_volume`에 마운트되고 `custom_model.safetensors`를 사용하는 경우, 경로는 `"/my_volume/models/custom_model.safetensors"`가 됩니다
    - LoRA 파일의 경우 `"/my_volume/loras/style_lora.safetensors"`와 같은 경로를 사용합니다

**네트워크 볼륨 구조 예시:**
```
/my_volume/
├── models/
│   ├── custom_model.safetensors
│   └── another_model.safetensors
└── loras/
    ├── style_lora.safetensors
    ├── character_lora.safetensors
    └── background_lora.safetensors
```

## 🔧 워크플로우 구성

이 템플릿은 다음 워크플로우 구성을 포함합니다:

*   **flux1_krea_dev_api_nolora.json**: LoRA 없이 기본 텍스트-이미지 생성
*   **flux1_krea_dev_api_1lora.json**: 1개 LoRA로 텍스트-이미지 생성
*   **flux1_krea_dev_api_2lora.json**: 2개 LoRA로 텍스트-이미지 생성
*   **flux1_krea_dev_api_3lora.json**: 3개 LoRA로 텍스트-이미지 생성

워크플로우는 ComfyUI를 기반으로 하며 Flux Krea 처리에 필요한 모든 노드를 포함합니다:
- 프롬프트용 CLIP 텍스트 인코딩
- 향상된 텍스트 이해를 위한 듀얼 CLIP 로더
- VAE 로딩 및 처리
- Flux Krea 모델이 있는 UNET 로더
- 이미지 생성용 KSampler
- LoRA 로더 노드 (구성에 따라 1-3개)
- 이미지 저장 및 출력 처리

## 🎯 LoRA 사용 팁

1. **가중치 값**: 대부분의 LoRA에 대해 0.5-1.0 사이의 가중치로 시작하세요. 높은 값(1.0-2.0)은 강한 효과를 만들고, 낮은 값(0.1-0.5)은 미묘한 효과를 만듭니다.

2. **LoRA 조합**: 여러 LoRA를 사용할 때는 호환성을 고려하세요. 일부 LoRA는 다른 LoRA와 함께 사용할 때 더 잘 작동합니다.

3. **모델 호환성**: LoRA 모델이 Flux Krea 아키텍처와 호환되는지 확인하세요.

4. **성능**: 더 많은 LoRA는 생성 시간과 메모리 사용량을 증가시킬 수 있습니다.

## 🙏 원본 프로젝트

이 프로젝트는 다음 원본 저장소를 기반으로 합니다. 모델과 핵심 로직에 대한 모든 권리는 원본 작성자에게 있습니다.

*   **Flux Krea:** [https://bfl.ai/blog/flux-1-krea-dev](https://bfl.ai/blog/flux-1-krea-dev)
*   **ComfyUI:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

## 📄 라이선스

원본 Flux Krea 프로젝트는 해당 라이선스를 따릅니다. 이 템플릿도 해당 라이선스를 준수합니다.
