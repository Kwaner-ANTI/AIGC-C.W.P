# AI Workbench Cloud Migration

在临时租用的 Vast.ai、RunPod 等兼容 GPU 实例中，按当前需要恢复 H3、ANIMA、MOSS 或 vLLM 模型文件。原项目历史、创作素材、WorkBench 配置与凭据保留在使用者自己的存储中；本仓库只包含非秘密的部署脚本及模型来源清单。

**这是可公开访问的轻量部署仓库，不需要 GitHub Pages，也不需要为克隆仓库配置 GitHub Token。** GPU 上实际模型下载仍受 Hugging Face 原作者访问条件、网络和实例空间约束。

## 2026-11-16 · Vast Krea-2 重租完整操作（模板、私人 TAR、LoRA）

此节是**实际执行顺序**。公开 GitHub 只保存恢复逻辑和文件版本，**不会**包含 `KREA2_personal_loras.tar`；Vast Template 只保存启动规则，**不是**模型/LoRA 的持久磁盘或快照。Windows 已下载的个人 LoRA TAR 应留在私人存储，不上传到本公开仓库；也不要把 Civitai Token 放进公共 Template / Git。

### A. 当前实例 Destroy 前（在 Windows 完成，不依赖终端脚本）

- 保存私人 `KREA2_personal_loras.tar` 到 Windows 长期 AIGC 存储；它可能只包含当时实际下载成功的部分 LoRA（检查压缩包成员），Anime in Real v2.0 因 Buzz 不足并未取得。
- 另行保存希望长期保留的私有 Prompt、参考图、实际出图 PNG、修改后的工作流 JSON、Seed 对应关系及 Workbench Shot 资料；GitHub 的公开 JSON 不会自动带走本轮私有作品。
- 修改 Vast 保存的模板**无需继续运行原 GPU 实例**。Stop 可能仍计存储费，Destroy 会清除实例的临时文件。不要把手工上传过的 TAR 误认为已经随 GitHub/Template 持久化。

### B. 在 Vast 网页修改以后要用的图片模板（一次性）

Vast `Templates → My Templates → 编辑（铅笔图标）→ Environment Variables`；若保留原 ANIMA 模板作另一用途，可以复制一份 Krea 专用图片模板，但不是必须创建新模板。新实例使用的 ComfyUI 镜像、启动模式、磁盘和端口以你已验证的模板为准，**不要**仅因安装 LoRA 替换它们或启动第二个 ComfyUI。

| 环境变量 | 值 | 原因 |
|---|---|---|
| `PROVISIONING_SCRIPT` | `https://raw.githubusercontent.com/Kwaner-ANTI/AIGC-C.W.P/main/scripts/vast_anima_provision.sh` | 新租实例首次启动拉取当前公开恢复脚本 |
| `AIW_PROFILES` | `images-krea2-turbo` | 自动恢复 Krea-2 主模型、文本编码器、原生 VAE、官方 LoRA，并复制公开工作流 |
| `AIW_COMFY_DIR` | `/workspace/ComfyUI` | 仅在该 Vast 模板的 ComfyUI 真正位于此目录时使用 |
| `AIW_PYTHON` | `/venv/main/bin/python` | 仅在当前模板实际有此 Python 时使用 |
| `AIW_ASSETS_ROOT` | `/workspace/aiworkbench-assets` | 同实例模型下载资产共用目录 |

选择需要的额外图片模型时，可以将 `AIW_PROFILES` 设成 `images-flux2-dev images-krea2-turbo`；这会增加空间和下载成本。**仅 Krea 2 就用单个 profile。** 保存模板后，使用该模板**新建的实例**才会按这些值执行；改 GitHub 或编辑模板不会回头自动切换旧浏览器画布。

**不要把 `images-krea2-personal-loras` 追加到模板的 `AIW_PROFILES`，除非实例首次 Provisioning 开始之前私人 TAR 已经位于实例可访问位置、`AIW_LORA_ARCHIVE` 已指向该路径。** 通常新租的临时盘没有 Windows TAR，因此应在启动完成后单独执行恢复 profile。不要把 `CIVITAI_TOKEN`、私人 TAR、私有 URL 凭据写入公开模板。

### C. 新租 Vast 实例自动恢复的部分

按以前可用的 Vast 图片模板租 GPU，并通过网页或实例终端等待原有 Provisioning 完成。模板的 `PROVISIONING_SCRIPT` 会克隆或更新 `/workspace/AIGC-C.W.P`，将 GitHub 的公开 `workflows/vast/*.json` 复制到 `/workspace/ComfyUI/user/default/workflows/`（同名已有文件会保留），并执行 `bash bootstrap.sh images-krea2-turbo`。这一步**不会取得私人 Mrpopo/Shiiro TAR**。

如没有配置 Provisioning，才需要根据实际 ComfyUI/Python 路径，手工 clone/pull 并执行基础模型 profile。模板已在运行 ComfyUI/Supervisor 时直接复用，不开第二个相同端口进程。

### D. 让新租实例实际拿到 Windows TAR（每次新临时实例必做，除非已有外部持久存储）

1. 在 Windows 找到 `KREA2_personal_loras.tar`，打开新 Vast 实例的 **Jupyter 文件管理器**，上传到 **`/workspace/KREA2_personal_loras.tar`**；如果新模板不是 Jupyter 启动模式，可使用本次实例实际 SSH 主机/端口的 `scp`，不要复用上次 SSH 端口。
2. 在**新实例 Linux Terminal** 执行（当前路径适配上述 Vast 图片模板）：

```bash
cd /workspace/AIGC-C.W.P
export AIW_COMFY_DIR=/workspace/ComfyUI
export AIW_PYTHON=/venv/main/bin/python
bash bootstrap.sh images-krea2-personal-loras --archive /workspace/KREA2_personal_loras.tar
```

脚本只恢复公开 manifest 登记且 TAR 中确实存在的 LoRA；跳过同名已有权重，不修改基础模型或已存工作流。因为是私人文件，上传本步骤**无法**仅靠 GitHub+无私人存储凭据的 Vast 模板自动完成。

3. 打开 ComfyUI 左侧 Workflows → `KREA2_T2I_INT8`。当前已替换为用户自定义 T2I（23 节点，LoRA 默认 ON，Shiiro Niji A 0.8，15 steps / CFG 1）。刷新模型列表，并先恢复私人 LoRA TAR；如果 LoRA 尚未恢复，把节点开关切至 OFF 再运行。`KREA2_I2I_CUSTOM` 当前引用私人输入图 `GALEEE-12.png`，下次租机需重新上传/选择原图。官方 Style Reference 工作流保持原样。
4. 如果未来改用私人对象存储，必须自行确保模型使用许可、存储访问权限与安全凭据管理，并让**新实例**取得 TAR；此仓库当前**没有**对象存储自动同步实现，不能将其当作已经部署。

### E. Featurize / AutoDL / RunPod

复用同一 GitHub `images-krea2-turbo` 与 `images-krea2-personal-loras` 入口，但它们**不使用 Vast Template 的 `PROVISIONING_SCRIPT` 配置机制**。Featurize 图片历史路径为 `/home/featurize/ComfyUI-images`，对应 Python `/home/featurize/venvs/comfy-images/bin/python`；其他平台以实际目录为准。先恢复基础权重，上传私人 TAR 到该实例可读路径，再设置该平台的 `AIW_COMFY_DIR`、`AIW_PYTHON`，运行 `bash bootstrap.sh images-krea2-personal-loras --archive /实际路径/KREA2_personal_loras.tar`。各平台的磁盘持久规则另按其实际产品设置判断，不能把 Vast 临时盘当作四平台共用资产库。

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
| `images-krea2-turbo` | Krea-2 Turbo INT8 主模型、Qwen3-VL、原生 VAE、官方 Darkbrush/Style Reference LoRA |
| `images-krea2-personal-loras` | **可选** Krea-2 第三方 LoRA：从本地 TAR 恢复或明确指定 Civitai 版本下载；不含公有权重 | 
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

## Krea-2 第三方 LoRA：跨 Vast、Featurize、AutoDL、RunPod 恢复（可选）

现有 `bootstrap.sh` 新增 `images-krea2-personal-loras`，读取公开的 `manifests/krea2-civitai-loras.json`（仅有文件名、版本 ID 和建议强度），实际权重及 Civitai Token 不进入 GitHub。三款候选分别为 Mrpopo v3 (`3168308`)、Shiiro Niji A (`3462062`) 和 Anime in Real v2.0 (`3341474`)。最后一款 2026-11-16 实测因 Buzz 不足未能下载，**不会默认获取**。这些仅适配 Krea-2 对应版本，不能用于 ANIMA/MOSS/FLUX2/H3。

1. 在新 GPU 实例按平台实际路径设置 `AIW_COMFY_DIR`、`AIW_PYTHON`、`AIW_ASSETS_ROOT`。使用原有 `bash bootstrap.sh images-krea2-turbo` 恢复 Krea-2 基础资产；已通过 Provisioning 恢复则不要重复下载。
2. **首选私人备份**：把 Windows 保存的 `KREA2_personal_loras.tar` 上传到当前实例，例如 `/workspace/KREA2_personal_loras.tar`，然后在仓库目录运行：

```bash
export AIW_COMFY_DIR=/workspace/ComfyUI       # 按当前平台修改；不是通用路径
export AIW_PYTHON=/venv/main/bin/python       # 按当前平台修改
AIW_LORA_ARCHIVE=/workspace/KREA2_personal_loras.tar bash bootstrap.sh images-krea2-personal-loras
```

脚本只提取已登记且实际包含在压缩包中的 LoRA，忽略其他内容；文件已存在时复用，不覆盖现有模型或软链接。若备份不包含 Mrpopo，不能因为运行成功就声称它已恢复。**这份私人压缩包必须由使用者在新实例上传**；GitHub 不会同步 Windows 私人文件。

3. **无备份时按需下载**，而不是全量自动下载。以下仅为示例，先确认对应 Civitai 版本仍授权访问：

```bash
read -rsp 'Civitai API Token: ' CIVITAI_TOKEN; export CIVITAI_TOKEN; echo
AIW_CIVITAI_LORAS=mrpopo,shiiro bash bootstrap.sh images-krea2-personal-loras
unset CIVITAI_TOKEN
```

使用 `AIW_CIVITAI_LORAS=anime-in-real` 才会尝试该 Buzz 受限版本，401/403 会报告失败而不是绕过网站权限。Token 只在本次终端进程环境使用；下载脚本通过 curl stdin 配置传入，不写入 GitHub、URL 或 shell 命令参数。临时下载以 `.part` 保存，断线可续传。仅恢复本地压缩包时不需要 curl、Civitai Token 或 Hugging Face 依赖。

4. 在 ComfyUI 左侧 Workflows 打开 `KREA2_T2I_INT8.json`（已用用户自定义 T2I 直接替换原子图版本），默认 Shiiro LoRA 为 ON、强度 0.8；需有实际 LoRA 文件才能运行此分支，否则先切 OFF。`KREA2_I2I_CUSTOM.json` 已替换为用户自定义 I2I，引用的 `GALEEE-12.png` 不包含在公开仓库。`KREA2_STYLE_REFERENCE_OFFICIAL.json` 不变，其 `krea2_style_reference.safetensors` 是专用参考机制。

Vast `scripts/vast_anima_provision.sh` 的 `AIW_PROFILES` 允许明确追加 `images-krea2-personal-loras`，**但前提是实例在 provisioning 时已经能够访问私人 TAR 路径，或显式指定获授权的 Civitai 下载**；通常新租 GPU 应先运行基础 profile，再上传 TAR 手动执行一次恢复。Featurize 历史图片路径为 `/home/featurize/ComfyUI-images`；AutoDL / RunPod 采用新实例真实路径，不把 Vast 默认值当成跨平台共用。以上恢复逻辑已做本地 TAR 模拟，尚不能代替新租 GPU 上的 LoRA 实际推理结果。

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
