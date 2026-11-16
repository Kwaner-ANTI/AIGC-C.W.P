# Featurize · ANIMA Add Micro Details v2 + PVC 2.9B (2026-11-16)

本分支只增加两个 Civitai 指定版本的恢复和独立 ComfyUI UI 画布：`3443066` = Add Micro Details v2 Anima（28-block LoRA）；`3402701` = PVC Style Model Anima 2.9B（40-block 完整 diffusion checkpoint）。**没有**加入 Masterpiece/Highres。

## 已启动的 Featurize 图片实例：执行一次

在 Featurize **图片实例** Terminal 粘贴：

```bash
set -e
ROOT=/home/featurize/work/AIWorkbench/AIGC-C.W.P-anima-micro-pvc
mkdir -p "$(dirname "$ROOT")"
if [ -d "$ROOT/.git" ]; then
  git -C "$ROOT" pull --ff-only
else
  git clone --depth 1 --branch deploy-anima-micro-pvc-20261116 https://github.com/Kwaner-ANTI/AIGC-C.W.P.git "$ROOT"
fi
export AIW_COMFY_DIR=/home/featurize/ComfyUI-images
export AIW_PYTHON=/home/featurize/venvs/comfy-images/bin/python
export AIW_LORA_DIR=/home/featurize/work/AIWorkbench/models/loras
bash "$ROOT/scripts/install_featurize_anima_micro_pvc.sh"
```

如 Civitai 返回 401/403，先核对该版本是否必须在本人账号登录/取得下载权限；若仅需要 API Token，可在当次 **Terminal** 使用 `read -rsp 'Civitai read-only key: ' CIVITAI_TOKEN; export CIVITAI_TOKEN; echo` 输入后重试最后一条 `bash` 命令，结束后 `unset CIVITAI_TOKEN`。不要把 Token 发到聊天、上传工作流、公开 GitHub 或下载 URL。下载器按已存在文件复用，不会重下已完成权重。若版本需要付费/解锁，本脚本不会绕过。

## 模型保存位置

- Micro LoRA 实体：`/home/featurize/work/AIWorkbench/models/loras/AddMicroDetails_Anima_v2.safetensors`；链接到 `ComfyUI-images/models/loras/`。
- PVC 实体：`/home/featurize/aiworkbench-assets/civitai/pvc-anima29b/PVCStyleModelMovable_anima29B10.safetensors`；链接到 `ComfyUI-images/models/diffusion_models/`。PVC 约 5.44GB，不默认占用历史约 30GB 的 `work` 同步盘；实例被销毁后其保存是否仍有效取决于实际镜像/存储策略，重新运行安装器可重取。
- 工作流实体：`/home/featurize/work/AIWorkbench/workflows/anima-micro-pvc/`；可从 ComfyUI 的 Workflows 区域或 Jupyter 文件浏览器打开。

## 五份画布

| 文件 | 用途 | 采样起点 |
|---|---|---|
| `ANIMA_MICRO_BACKGROUND.json` | Aesthetic + Micro、幻想都市背景 | 原生 60 steps/CFG4.5/Euler Simple；1536×864；Turbo OFF |
| `ANIMA_MICRO_CHARACTER.json` | Aesthetic + Micro、人物正立全身 | 原生 60 steps/CFG4.5/Euler Simple；1056×1408；Turbo OFF |
| `ANIMA_BASE_REF_MICRO_CHARACTER.json` | Base + Micro + Ref Adapter、人物 Atlas | 保留既有 Ref 配置和原始人物参考链，加载**真实 Atlas 图**后可 Queue |
| `PVC_ANIMA29B_BACKGROUND.json` | 独立 PVC 2.9B、背景/城市模型 | 30 steps/CFG4/Euler SGM Uniform；1536×920 |
| `PVC_ANIMA29B_CHARACTER.json` | 独立 PVC 2.9B、人物手办 | 30 steps/CFG4/Euler SGM Uniform；920×1536 |

所有画布均为现有 ANIMA 文本或 Reference 模板的**副本**。原始 Aesthetic / Ref Adapter / Turbo 分支未修改。PVC 没有额外叠加 Micro；原 28-block LoRA 直接叠加到 40-block 2.9B 可能错误映射层，必须使用明确支持 remapping 的 Loader 才能作为后续独立实验。

## 实际测试

同一题材采用固定 Prompt/Seed，比对 Aesthetic 原生（Micro strength=0）与 Micro=0.5 的背景/人物结果；PVC 则是独立风格与结构对照，不把跨底模同 Seed 当同随机变量。人物 Ref 画布需先指定上传的原 Atlas 图，再检查服装、身份与视角。保留 ComfyUI 原始 PNG/History 并在既有 Workbench Shot/Generation 中关联。

若 PVC 呈现异常，先注意 **2.9B 是 40-block，而早期 ComfyUI 可能错误加载为 28-block**；较新 ComfyUI 已有原生修复，不要在未知版本上无条件安装第三方 patch 或覆盖 H3 Python。参考：<https://github.com/sparklingcoffee777/ComfyUI-Anima-2.9B-blocksPatch>。

**状态**：GitHub 分支安装器、清单、五份 JSON 已保存并核查节点图链接。**未直接访问用户正在运行的 Featurize 实例**，所以未执行实际 GPU 下载/Queue；只有运行命令及产生 PNG/History 后才是本次真实部署完成。
