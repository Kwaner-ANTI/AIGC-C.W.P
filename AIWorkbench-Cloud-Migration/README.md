# AI Workbench Cloud Migration

在临时租用的 Vast.ai、RunPod 等兼容 GPU 实例中，按当前需要恢复 H3、ANIMA、MOSS 或 vLLM 模型文件。原项目历史、创作素材、WorkBench 配置与凭据保留在使用者自己的存储中；本仓库只包含非秘密的部署脚本及模型来源清单。

**这是可公开访问的轻量部署仓库，不需要 GitHub Pages，也不需要为克隆仓库配置 GitHub Token。** GPU 上实际模型下载仍受 Hugging Face 原作者访问条件、网络和实例空间约束。

## 每次新租实例：获取脚本并恢复指定工作负载

实例应已带有对应工作负载可运行的 ComfyUI/Python/Torch 或 vLLM 环境。下面是以 `/workspace` 为工作区的**路径示例**；请改为所租 GPU 模板上的真实路径。

```bash
cd /workspace
git clone --depth 1 https://github.com/YOUR_ACCOUNT/AIWorkbench-Cloud-Migration.git
cd AIWorkbench-Cloud-Migration

export AIW_COMFY_DIR=/workspace/ComfyUI
export AIW_PYTHON=/venv/main/bin/python
export AIW_ASSETS_ROOT=/workspace/aiworkbench-assets
export HF_XET_HIGH_PERFORMANCE=1

bash bootstrap.sh images-anima
```

将 `YOUR_ACCOUNT` 换成你的 GitHub 用户名。`AIW_PYTHON` 必须指向实际镜像的 Python；不要照抄不适配的路径。`.env.example` 只是示例，脚本**不会自动读取** `.env`，请在 shell 中设置所需环境变量。重复使用同一实例时，可以在仓库目录执行 `git pull --ff-only` 更新代码；已有模型文件会按现有逻辑复用。

## 按需恢复的配置

| Profile | 用途 |
|---|---|
| `images-anima` | ANIMA Aesthetic v1.1 文生图：主模型、文本编码器、VAE |
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
- `workflows/`、`prompts/` 只保留说明及原文存放位置：原项目实际成功运行的用户工作流 JSON 和 Prompt **尚未导入本仓库**。模板链接不能代替用户已调整的工作流；执行真实 Ref2VA 时可能还需要单独恢复所用的 ControlNet、LoRA、其他节点或自有参考素材。
- 原有项目的三份汇编 MD 和完整工程任务书**未放入公开仓库**，而是保留在原始离线资料中。它们不是云端启动脚本的运行依赖。
- 当前工程通过了本地离线逻辑测试；尚无 Vast.ai/RunPod GPU 真实生图或 H3 成片的执行证据。

## 退租与公开安全

GPU 实例销毁前，先把重要的参考素材、满意的 PNG/MP4、实际工作流 JSON 和其他新产生且需要保存的文件取回；本地 AI Workbench 的 Project/Shot/Prompt/Review/History 数据不由此仓库自动同步。

公共 GitHub 仓库**绝对不要提交** Hugging Face Token、GitHub Token、SSH 私钥、账户认证文件、Workbench 数据库、私有参考素材和创作输出。`.gitignore` 只减少误加文件的机会，不会阻止把机密粘进被跟踪的 JSON、脚本、Markdown 或 Git 提交历史中。需要访问 HF 受限模型时，必须由使用者按原仓库条款授权，并把只读凭据仅提供给运行实例，不写进本仓库。

## 首次发布到自己的公共 GitHub 仓库

先在 GitHub 创建一个**Public** 空仓库，名称建议为 `AIWorkbench-Cloud-Migration`；**不要**启用 GitHub Pages。解压此项目文件夹后，在本地电脑的该文件夹里执行：

```bash
git init
git add .
git commit -m "Add public cross-cloud bootstrap"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/AIWorkbench-Cloud-Migration.git
git push -u origin main
```

替换 `YOUR_ACCOUNT`，推送时在**自己的电脑**上使用已有 GitHub 凭据进行登录。公共仓库只意味着以后 GPU 实例能够**匿名读取**，并不表示你在自己的电脑上推送代码不需要身份认证。若创建仓库时已勾选添加 README，初始提交会不同，建议直接创建空仓库以使用以上命令。
