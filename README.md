# Flux Krea for RunPod Serverless
[한국어 README 보기](README_kr.md)

This project is a template designed to easily deploy and use [Flux Krea](https://bfl.ai/blog/flux-1-krea-dev) in the RunPod Serverless environment.

[![Runpod](https://api.runpod.io/badge/wlsdml1114/Flux-krea_Runpod_hub)](https://console.runpod.io/hub/wlsdml1114/Flux-krea_Runpod_hub)

Flux Krea is an advanced AI model that generates high-quality images with creative text-to-image capabilities using the Flux architecture, with support for multiple LoRA (Low-Rank Adaptation) models.


## 🎨 Engui Studio Integration

[![EnguiStudio](https://raw.githubusercontent.com/wlsdml1114/Engui_Studio/main/assets/banner.png)](https://github.com/wlsdml1114/Engui_Studio)

This InfiniteTalk template is primarily designed for **Engui Studio**, a comprehensive AI model management platform. While it can be used via API, Engui Studio provides enhanced features and broader model support.

**Engui Studio Benefits:**
- **Expanded Model Support**: Access to a wider variety of AI models beyond what's available through API
- **Enhanced User Interface**: Intuitive workflow management and model selection
- **Advanced Features**: Additional tools and capabilities for AI model deployment
- **Seamless Integration**: Optimized for Engui Studio's ecosystem

> **Note**: While this template works perfectly with API calls, Engui Studio users will have access to additional models and features that are planned for future releases.

## ✨ Key Features

*   **Text-to-Image Generation**: Creates high-quality images from text descriptions with advanced Flux architecture.
*   **Multi-LoRA Support**: Supports up to 3 LoRA models simultaneously for enhanced customization.
*   **Dynamic Model Loading**: Automatically selects appropriate workflow based on LoRA count (0-3 LoRAs).
*   **Customizable Parameters**: Control image generation with various parameters including seed, guidance, width, height, and prompts.
*   **ComfyUI Integration**: Built on top of ComfyUI for flexible workflow management.
*   **Dual CLIP Support**: Enhanced text understanding with dual CLIP model integration.

## 🚀 RunPod Serverless Template

This template includes all the necessary components to run Flux Krea as a RunPod Serverless Worker.

*   **Dockerfile**: Configures the environment and installs all dependencies required for model execution.
*   **handler.py**: Implements the handler function that processes requests for RunPod Serverless.
*   **entrypoint.sh**: Performs initialization tasks when the worker starts.
*   **Workflow JSONs**: Multiple workflow configurations for different LoRA combinations.

### Input

The `input` object must contain the following fields. All parameters except `model` and `lora` are required.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `prompt` | `string` | **Yes** | `N/A` | Description text for the image to be generated. |
| `seed` | `integer` | **Yes** | `N/A` | Random seed for image generation (affects output randomness). |
| `guidance` | `float` | **Yes** | `N/A` | Guidance scale for controlling generation adherence to prompt. |
| `width` | `integer` | **Yes** | `N/A` | Width of the output image in pixels. |
| `height` | `integer` | **Yes** | `N/A` | Height of the output image in pixels. |
| `model` | `string` | **No** | `flux1-krea-dev_fp8_scaled.safetensors` | Custom model path (requires Network Volume). |
| `lora` | `array` | **No** | `[]` | Array of LoRA configurations as `[model_path, weight]` tuples (requires Network Volume). |

**LoRA Configuration:**
- Each LoRA entry should be an array with two elements: `[model_name, weight]`
- `model_name`: Full path to the LoRA model file (e.g., `"/my_volume/loras/lora.safetensors"`)
- `weight`: Strength/weight of the LoRA (typically between 0.0 and 2.0)
- Maximum 3 LoRAs supported
- If more than 3 LoRAs are provided, only the first 3 will be used
- **Note**: Custom models and LoRAs require Network Volumes to be configured

**Request Examples:**

**Basic Request (No LoRA):**
```json
{
  "input": {
    "prompt": "a beautiful landscape with mountains and a lake",
    "seed": 12345,
    "guidance": 7.5,
    "width": 1024,
    "height": 1024
  }
}
```

**Request with Custom Model (Network Volume):**
```json
{
  "input": {
    "prompt": "a beautiful landscape with mountains and a lake",
    "seed": 12345,
    "guidance": 7.5,
    "width": 1024,
    "height": 1024,
    "model": "/my_volume/models/custom_model.safetensors"
  }
}
```

**Request with Single LoRA (Network Volume):**
```json
{
  "input": {
    "prompt": "a beautiful landscape with mountains and a lake",
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

**Request with Multiple LoRAs (Network Volume):**
```json
{
  "input": {
    "prompt": "a beautiful landscape with mountains and a lake",
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

### Output

#### Success

If the job is successful, it returns a JSON object with the generated image Base64 encoded.

| Parameter | Type | Description |
| --- | --- | --- |
| `image` | `string` | Base64 encoded image file data. |

**Success Response Example:**

```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
}
```

#### Error

If the job fails, it returns a JSON object containing an error message.

| Parameter | Type | Description |
| --- | --- | --- |
| `error` | `string` | Description of the error that occurred. |

**Error Response Example:**

```json
{
  "error": "이미지를 생성할 수 없습니다."
}
```

## 🛠️ Usage and API Reference

1.  Create a Serverless Endpoint on RunPod based on this repository.
2.  Once the build is complete and the endpoint is active, submit jobs via HTTP POST requests according to the API Reference below.

### 📁 Using Network Volumes

**Important**: Custom models and LoRAs are only applied when using Network Volumes. The default models are used when Network Volumes are not configured.

Instead of directly transmitting Base64 encoded files, you can use RunPod's Network Volumes to handle large files. This is especially useful when dealing with large model files.

1.  **Create and Connect Network Volume**: Create a Network Volume (e.g., S3-based volume) from the RunPod dashboard and connect it to your Serverless Endpoint settings.
2.  **Upload Files**: Upload the model files and LoRA files you want to use to the created Network Volume.
3.  **File Organization**: Organize your files in the following structure within the Network Volume:
    - **Models**: Place custom model files in the `models/` folder
    - **LoRAs**: Place LoRA files in the `loras/` folder
4.  **Specify Paths**: When making an API request, specify the file paths within the Network Volume for `model` and LoRA names. For example:
    - If the volume is mounted at `/my_volume` and you use `custom_model.safetensors`, the path would be `"/my_volume/models/custom_model.safetensors"`
    - For LoRA files, use paths like `"/my_volume/loras/style_lora.safetensors"`

**Example Network Volume Structure:**
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

## 🔧 Workflow Configuration

This template includes the following workflow configurations:

*   **flux1_krea_dev_api_nolora.json**: Basic text-to-image generation without LoRA
*   **flux1_krea_dev_api_1lora.json**: Text-to-image generation with 1 LoRA
*   **flux1_krea_dev_api_2lora.json**: Text-to-image generation with 2 LoRAs
*   **flux1_krea_dev_api_3lora.json**: Text-to-image generation with 3 LoRAs

The workflows are based on ComfyUI and include all necessary nodes for Flux Krea processing:
- CLIP Text Encoding for prompts
- Dual CLIP Loader for enhanced text understanding
- VAE Loading and processing
- UNET Loader with Flux Krea model
- KSampler for image generation
- LoRA Loader nodes (1-3 depending on configuration)
- Image saving and output processing

## 🎯 LoRA Usage Tips

1. **Weight Values**: Start with weights between 0.5-1.0 for most LoRAs. Higher values (1.0-2.0) create stronger effects, while lower values (0.1-0.5) create subtle effects.

2. **LoRA Combinations**: When using multiple LoRAs, consider their compatibility. Some LoRAs work better together than others.

3. **Model Compatibility**: Ensure your LoRA models are compatible with the Flux Krea architecture.

4. **Performance**: More LoRAs may increase generation time and memory usage.

## 🙏 Original Project

This project is based on the following original repository. All rights to the model and core logic belong to the original authors.

*   **Flux Krea:** [https://bfl.ai/blog/flux-1-krea-dev](https://bfl.ai/blog/flux-1-krea-dev)
*   **ComfyUI:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

## 📄 License

The original Flux Krea project follows its respective license. This template also adheres to that license.
