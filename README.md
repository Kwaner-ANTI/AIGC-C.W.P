# AI Workbench Cloud Migration

在临时租用的 Vast.ai、RunPod 等兼容 GPU 实例中，按当前需要恢复 H3、ANIMA、MOSS 或 vLLM 模型文件。原项目历史、创作素材、WorkBench 配置与凭据保留在使用者自己的存储中；本仓库只包含非秘密的部署脚本及模型来源清单。

**这是可公开访问的轻量部署仓库，不需要 GitHub Pages，也不需要为克隆仓库配置 GitHub Token。** GPU 上实际模型下载仍受 Hugging Face 原作者访问条件、网络和实例空间约束。

## 已成功运行的 ANIMA 环境与验收边界

用户已在 Vast.ai RTX 4090 24GB、ComfyUI 模板镜像 `vastai/comfy:v0.43.0-cuda-12.9-py312` 上完成 ANIMA Aesthetic v1.1 首次真实出图，并提供实际工作流 `C.A-VT1.json`。成功记录来自用户原实例；本次仓库修改没有重新执行 GPU 推理。

| 项目 | 状态 |
|---|---|
| 原 Vast.ai 实例 ANIMA 首次出图 | 用户已确认成功 |
| 本地真实工作流收录 | 原始 JSON 原样保存，仅本地保留，含原 Prompt、节点与连接 |
| 模型恢复清单 | Aesthetic v1.1、Qwen 编码器、VAE、Turbo LoRA v0.2 |
| 新实例从本仓库恢复后再次出图 | 尚未验收 |
| Windows 本地 GPU 推理 | 本次未执行，不能由云端出图推断 |
| 原始 PNG 的本地备份 | 由用户自行保存，本仓库不收录或自动取回 |

## 每次新租 Vast.ai 实例：恢复 ANIMA

复用上述已成功出图的 RTX 4090 + ComfyUI 模板环境。原实例的 ComfyUI 目录为 `/workspace/ComfyUI`，Python 为 `/venv/main/bin/python`；新模板路径发生变化时按实际值调整。复用模板自带的 ComfyUI/Python/Torch，无需重新安装整套环境。

在新实例的 SSH 终端执行：

```bash
cd /workspace
git clone --depth 1 https://github.com/Kwaner-ANTI/AIGC-C.W.P.git
cd AIGC-C.W.P

export AIW_COMFY_DIR=/workspace/ComfyUI
export AIW_PYTHON=/venv/main/bin/python
export AIW_ASSETS_ROOT=/workspace/aiworkbench-assets
export HF_XET_HIGH_PERFORMANCE=1

bash bootstrap.sh images-anima
```

同一实例已有仓库时，在仓库内执行 `git pull --ff-only` 后运行相同恢复命令。已有同名普通模型文件和有效恢复链接会复用；缺少的文件从 manifest 指定的 HF 仓库下载，由现有 `restore.py` 链接到 ComfyUI `models/`。`.env` 不会自动读取，环境变量需在 shell 中设置。克隆公开仓库无需 GitHub Token；模型下载仍遵循原作者的访问条件。

下载完成后：

1. 通过 Vast.ai 模板入口或现有 Workbench Runtime 打开并复用 ComfyUI。模板 Supervisor 已运行服务时直接复用。
2. 从本地电脑将私有 `C.A-VT1.json` 拖入 ComfyUI，导入完整 UI 画布 JSON。本次按用户要求将它保存在本地 `workflows/local/`（Git 忽略）；公开 clone 不包含这份 JSON 或其中的 Prompt，需要单独从自己的存储取得。
3. 保持原模型、Prompt、节点、连接和 Turbo 分支。实际采样 Steps/CFG 由连入 KSampler 的开关节点决定，不能用 KSampler 内残留的未连接控件值替代实际连线。无需改回历史教程的首图建议参数。
4. 确认模型列表包含 `anima-turbo-lora-v0.2.safetensors`。原工作流保留了 LoRA Loader，关闭 Turbo 后仍曾因缺少 `lora_name` 报错；因此恢复清单同时下载 LoRA，是否启用仍由原 JSON 决定。
5. 执行一次实际生成，保存输出 PNG 和当前 JSON；新实例生成成功后，才能记录该次跨实例恢复通过。离线测试或下载成功不能替代这一步。

Workbench 继续使用已有 SSH、隧道、Start/Reuse 和 `/system_stats` readiness。工作目录和 Python 使用上面的真实路径；ComfyUI 远端端口使用模板实际运行的端口，SSH 主机及映射端口使用当次租机信息。恢复脚本不启动额外服务。

## 按需恢复的配置

| Profile | 用途 |
|---|---|
| `images-anima` | ANIMA Aesthetic v1.1 文生图：主模型、文本编码器、VAE、Turbo LoRA v0.2 |
| `images-anima-ref` | ANIMA Base v1.0 与参考适配节点 |
| `images-moss` | MOSS SFT BF16 文生图 |
| `images-moss-edit` | MOSS SFT BF16、编辑 patch 及多参考节点 |
| `h3-int8-int8` | MiniMax H3 **完整非 Pruned** INT8 Ref2VA + INT8 文本编码器 + Video VAE |
| `h3-int8-bf16` | MiniMax H3 **完整非 Pruned** INT8 Ref2VA + BF16 文本编码器 + Video VAE |
| `h3-audio` | 仅工作流需要时补充 H3 Audio VAE |
| `h3-controlnet-int8` / `h3-controlnet-bf16` | 仅原工作流确实引用相应 Fun ControlNet Patch 时使用 |
| `vlm` | 单独 vLLM 环境中恢复 Workbench 已选定模型的**完整 HF 仓库** |

例如执行其他图片任务：

```bash
bash bootstrap.sh images-moss-edit
```

vLLM 是独立 workload，使用真实模型仓库名与专用 Python，不复用 ComfyUI 环境：

```bash
export AIW_PYTHON=/path/to/vllm/bin/python
export AIW_VLM_REPO='OWNER/EXACT_MODEL'
bash bootstrap.sh vlm
```

## 功能边界与重要限制

- 本仓库**不是** ComfyUI/PyTorch/vLLM 安装器、第二启动器或 ComfyUI API 工作流编排工具。ComfyUI 由现有 Workbench Runtime 或 GPU 模板 Supervisor 启动／复用；脚本只下载、复用并链接必要模型。
- 不下载所有 H3 精度／分支；当前 H3 主生产组合是完整 `minimax_h3_ref2va_int8_convrot.safetensors`，文本编码器使用 BF16 或 INT8，原视频工作流的 20-step、`res_multistep`、`beta` 配置应由**实际工作流 JSON** 承担。
- H3 完整模型需要单独兼容的显存／磁盘和 PyTorch CUDA 环境；不能将 ANIMA/MOSS 的 24GB 图片镜像直接视为满足 H3 生产要求。所需目录及 Python 由具体云 GPU 模板决定。
- 若目标位置已经存在同名模型普通文件，脚本沿用该文件以节省下载；若符号链接失效或指向冲突位置，脚本报错，不覆盖其他模型。`huggingface_hub` 管理下载续传。
- ANIMA 真实工作流与 Prompt **仅本地保存**，不进入公共 Git 历史；`workflows/README.md` 说明导入方式。H3、MOSS 的真实用户工作流尚未收录；官方模板不能代替用户已调整的 JSON。执行真实 Ref2VA 时可能还需恢复所用 ControlNet、LoRA、节点和私有参考素材。
- 原有项目的三份汇编 MD 和完整工程任务书**未放入公开仓库**，而是保留在原始离线资料中。它们不是云端启动脚本的运行依赖。
- 用户原 Vast.ai ANIMA 实例已成功出图；本次离线测试只验证恢复逻辑。新实例恢复出图、MOSS、H3 和 vLLM 不因本次修改视为已验收。

## 退租与公开安全

GPU 实例销毁前，先把重要的参考素材、满意的 PNG/MP4、实际工作流 JSON 和其他新产生且需要保存的文件取回；本地 AI Workbench 的 Project/Shot/Prompt/Review/History 数据不由此仓库自动同步。

公共 GitHub 仓库**绝对不要提交** Hugging Face Token、GitHub Token、SSH 私钥、账户认证文件、Workbench 数据库、私有参考素材和创作输出。`.gitignore` 只减少误加文件的机会，不会阻止把机密粘进被跟踪的 JSON、脚本、Markdown 或 Git 提交历史中。需要访问 HF 受限模型时，必须由使用者按原仓库条款授权，并把只读凭据仅提供给运行实例，不写进本仓库。

## 离线测试

使用已安装 `huggingface_hub` 的 Python，在仓库目录运行已有测试：

```bash
python -m unittest discover -s tests -v
```

测试模拟下载，不访问 HF、不下载真实权重、不启动 GPU 推理。`bootstrap.sh` 和 `scripts/restore.py` 继续作为统一恢复入口。

## 现有公开仓库

继续使用 [Kwaner-ANTI/AIGC-C.W.P](https://github.com/Kwaner-ANTI/AIGC-C.W.P)，保持公开 HTTPS 匿名克隆，无需 GitHub Pages。仅提交明确可公开的修改；`workflows/local/` 内的原始工作流和 Prompt 留在用户自己的本地备份中。
