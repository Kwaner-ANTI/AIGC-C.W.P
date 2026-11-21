---
title: AIWorkbench × Galleon MV · 图像/H3/超分跨项目共享经验
updated: 2026-11-21
status: active_decisions_and_execution_guide
record_type: ordinary_project_data_not_new_skill
owners: [AIWorkbench, Galleon_MV]
archive: AIWORKBENCH_GALLEON_IMAGEGEN_EXPERIENCE_2026-11-21_HISTORY_FULL.md
---

# AIWorkbench × Galleon MV · 当前共享经验（在线精简版）

> **替换说明**：这是原 `...PHASE2_FULL.md` 的现行执行版；不是新建并行 Skill 或新数据库。原 2026-11-21 Phase 2 完整稿（§0–§18）和较早 `...WORKFLOW_TEST_NOTES_FULL.md` 的逐字原件均已汇入单独离线历史档。Prompt、Seed、旧 ANN/ANIMA/FLUX/Krea 测试、H3 和工作流 Note **没有被无备份丢弃**；需要对照时临时上传历史档。本版只保留当前用于操作的事实、关键配置和指向历史的索引。
>
> **优先级**：2026-11-21 用户最新决定及本次实物 JSON > 本轮媒体文件/用户评价 > 旧共享文档 > 公开上游建议 > 推断。`JSON 写入` ≠ `实例加载` ≠ `GPU 出片`，不能互相代替；本次离线生成不等于已更新任何 ChatGPT Project、GitHub、Workbench 代码或云实例。

## 1. 当前工作次序与已确认取舍

1. **SeedVR2 首轮及倍率复测已执行；当前转至 Vast.ai 的 VOSR2 测试，FlashVSR 保留后备**。SeedVR2 3B INT8 的四段 P1 视频已分别完成 2×、1.5×、1.33× 超分；正式评价与运行条件见 §3 的 2026-11-21 实测追加。用户已提供 Vast Template 配置并在 ComfyUI 截图中展示 VOSR2 节点及后置缩放，但本次上传的 JSON 仍是原三组示例文件，尚无新的视频拆帧线路或 VOSR2 实际 GPU 出片证据。
2. **下一阶段 Illustrious XL 在云端部署，不在本地新增其常驻图片模型**。本地已有 Qwen 9B 与 8B 文字模型，未来还计划 ANIMA 图片模型；避免本地同时叠加 Qwen、ANIMA、Illustrious 形成显存和模型环境争用。Illustrious 的两组参考配置仍保留，**当前暂缓部署**。
3. H3 视频下一项创作优先 **S02 电车坐姿起身 → 扶杆 → 列车晃动后恢复站稳**。T01 折返跑保留为已有高动态观察，**T02 Line Dance 暂停**；不继续机械测试舞蹈。
4. 8-step Turbo、Long Video 双段、Motion Dials、BUNNY、FlowHMR/Blender、SLA、视频再生成/潜空间超分均有历史研究基础，但不能被列成“已 GPU 通过”。按具体镜头需要选择，不机械全排列。
5. **当用户请求方案、研究、复盘或 Skill 更新时不自动创作新 Prompt**；明确要求具体执行输入或提示词时才编写。

## 2. 这次唯一确认的工作流增量：7TE 右下角 SeedVR2 block

- **输入原件**：`H3_B25-49_13Step-L.D.B-7TE.json`（实际已解析，78 节点、66 条连线、无原有 group）。
- **交付**：`H3_B25-49_13Step-L.D.B-7TE_SeedVR2_ONE_BLOCK.json`（仅一份，用于 4 条视频依次切换文件，不再产生一堆相似 JSON）。
- **不可改变项**：原 78 个节点所有 ID/坐标/尺寸/完整中英文标题、人工注释、widgets、Prompt、模型、开关、原连线和画布 viewport **逐项原样保留**；原工作流没有任何原始连线被移除或更改。
- **新增项**：独立 **SeedVR2 3B INT8 · 独立超分测试区块** group，放在主画布右下方（bounding `[10950,2560,6520,1350]`），20 个新增节点、30 条内部连线。节点位置和旧区块不重叠；含源 MP4 Load Video、拆帧/FPS/音频、模型/独立 VAE、2×、原生 SeedVR2 conditioning/KSampler/分块、裁切 1080p、Create/Save Video、中文说明 Note。
- **执行语义**：新增 block 由自己的 `LoadVideo` 读取**已经存在的 MP4**，并有完整输出链；**故意不连接 H3 采样和 `H3LongVideoAppend`**，原采样主线不受影响；但普通 `Queue Prompt` 可能同时执行工作流中的其他输出节点。仅测试超分时，应在当前 ComfyUI 使用 **Queue Selected Output Nodes** 只选 SeedVR2 `SaveVideo`，或临时 Mute 原 H3 输出节点；不能仅凭内部不连接就保证不会重新跑 H3。用户需要测试新的 H3 生成物时，仅更换超分输入文件；不默认为每个输入复制工作流。
- **初始超分参数**：SeedVR2 `seedvr2_3b_int8_convrot.safetensors` + `seedvr2_ema_vae_fp16.safetensors`；960×544 → 2× 1920×1088 → `ImageCrop(1920,1080,x=0,y=4)`；透传原视频 FPS/Audio/Bit depth，不额外插帧；KSampler 采用官方原生示例的 1 step、CFG 1、Euler/simple、denoise 1。先尝试 temporal split 开启，chunk auto；它是**显存可行性候选**，需要真实 5090 Queue 验证。
- **来源与边界**：参考 Comfy-Org 官方原生模板 `utility_seedvr2_3b_int8_upscale_video.json`（https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_seedvr2_3b_int8_upscale_video.json）。本次新增节点在静态 JSON 中形成了类型匹配的内部线路，**未**在用户 Featurize 的真实 ComfyUI 版本上导入、Queue 或检查视觉效果；原生 SeedVR2 节点是否已存在由本次实例实际版本决定。

### 对今后所有工作流修改的默认规则

- **先确认交付数量、目标配置和要更改的节点范围**，再生成文件；一份可切换输入/强度的工作流优于很多复制件。未收到生成授权时只给方案，不落 JSON。
- **不改任何原节点标题旁的中文**，不擅自翻译、删短或重编号；主工作流布局、组、色彩、已有 Note、Seed、Prompt、开关、连接及节点 ID 不得因“整理”改变。
- 只在用户指定的位置新增有明确用途的节点；新节点使用新 ID、新 group，确保不与旧区块重叠。若发现已有中文标题的语义有误，在说明中指出，不偷偷覆盖原注释。
- 首选可视 UI JSON，不能把 API prompt JSON 误作为原画布。只动指定范围，执行时以云端真实节点 API 和 Queue 为准。原 Workbench Project/Shot/Generation 与当前 Runtime 不增设第二套管理系统。

## 3. SeedVR2 四条视频：真实输入与观察目标

原 P1 媒体元数据已在之前批次核实：**960×544、24 fps、124 帧（约 5.167 秒）**。目标输出 **1920×1080、24 fps、保持原 124 帧**；输出文件是否真的符合需要在实际 MP4 中验证。

| 顺序 | 在云端 Load Video 选择的实际文件名 | 主要观察 |
|---|---|---|
| 1 | `P1_REF03_SUNSET_STATION_13S_full.mp4` | 梁架/轨道、夕光、角耳、服装、线条闪烁 |
| 2 | `P1_REF05_ROOFTOP_13S_full.mp4` | 天台栏杆、楼体、笔触、人物轮廓 |
| 3 | `P1_REF01_SKY_CLOUD_13S_full (1).mp4` | 原画云层僵硬运动、边缘与纹理漂移 |
| 4 | `P1_TEXT_SKY_OPTIONAL_13S_full.mp4` | 纯文字云层动态、渐变、细节恢复 |

**不能预支的结论**：SeedVR2 可以改变画面纹理/空间细节和闪烁，但不能保证修复云层时间演化、人物脚底接地或复杂动作因果。首轮只使用这四条，不转向另一堆超分器试错。输出采用一个统一的 Save Video 前缀即可，不改变已有四个源影片。

### Featurize 执行边界

- H3 旧成功实例是 `/home/featurize/ComfyUI`，ComfyUI 0.46.0、Python 3.12.16、PyTorch 2.15.0+cu132；**新实例不能默认永久继承这些版本/安装包**。云 GPU 使用现有 AIWorkbench Prepare / Start/Reuse 和单一 ComfyUI 服务。
- SeedVR2 的两个权重分别属于当前 ComfyUI 的 `models/diffusion_models/` 与 `models/vae/`。这些不是 H3 的权重/VAE。优先复用当前环境已有可用文件，不为离线 JSON 布局执行 CUDA 重装。
- **只运行 SeedVR2 输出**（支持时使用 Queue Selected Output Nodes，或暂时 Mute H3 其它输出节点），实际读取四个 MP4 并出超分文件；若缺原生节点，按真实 ComfyUI 版本兼容情况补齐，**不因此推倒已有 H3 已跑通环境**。无法 GPU 运行时不可宣称成功。
- 离开实例前取回实际生成的 MP4、最终可导入 UI JSON 与真实运行参数、FPS/帧数/耗时；不需要新 hash、冻结配置、仪式化 gate 或额外审核服务。

### 2026-11-21 · SeedVR2 已执行实测、原生 JSON 核验及下一次模型选择（新进展；覆盖本 § 先前“待 GPU 验证”状态）

- **已发生**：用户在 Featurize RTX 5090 上实际完成四段 P1 视频的 SeedVR2 3B INT8 超分，并追加 **2× / 1.5× / 1.33×** 三档比较。四个原片均为约 960×544、124 帧、24 fps；实测输出分别为 **1920×1088（约 2.09MP）**、**1440×816（约 1.175MP）**、**1276×724（约 0.924MP）**，上传视频核验帧数均为 124。这里的 1.33 / 1.5 / 2.0 是**宽高线性倍率**，不能写成 1.33MP / 1.5MP / 2.0MP。最终实测视频没有执行预期的 1080p 裁切；保留真正输出规格，勿改写为 1920×1080 已完成。
- **用户画面反馈**：原片结构较好的夕照车站，2× 整体锐利且只有轻微轨道闪烁；1.5×、1.33× 反而出现更明显的轨道闪烁；人物主体在三档均相对稳定。都市天台原片背景偏模糊，超分后不足被放大；原画晴空和纯文字天空整体尚可，但中远景 Galleon 面部有细节丢失或不自然补绘，原视频已有瑕疵不会因降低倍率自动消失。闪烁的精确归因未完成，不可推出 2× 在所有动画视频均更稳定。
- **运行速度证据**：截图显示第一次 2× 四条约 184–209 秒/条；复测 2× 约 73–75 秒/条、1.5× 约 74–75 秒/条、1.33× 约 60–61 秒/条。可能混入实例缓存、运行状态、不同输入链及编码时间；不能据此直接得出纯采样速度随倍率的普遍关系。
- **本轮用户提供的实际官方风格 JSON**：`seedvr2_3b_int8_upscale_.json`，本地已解析，22 节点、32 连接。实际保存配置：`ResizeImageMaskNode #111` 倍率 **1.33**，`lanczos`；`KSampler #109` **1 step / CFG 1 / euler / simple / denoise 1**，`control_after_generate=randomize`；`SeedVR2TemporalChunk #119` **chunking_mode=auto / temporal_overlap=0**，`PrimitiveBoolean #123` 为 `true`（启用分块）；编码与解码 `VAE*Tiled` 的 tile/overlap/time/temporal-overlap 均为 **512/128/64/8**；`SeedVR2PostProcessing #113` 色彩校正 `none`；`CreateVideo` 的 FPS 实际由上游连接输入覆盖。当前工作流没有末端裁切节点。JSON 保存的 Seed 只证明 UI 缓存，不能代替具体执行历史；`randomize` 意味着不同倍率的对照**可能同时变化随机 Seed**。
- **下一次实验，用户指定顺序**：**先 VOSR2，再视实际观感决定是否试 FlashVSR**；这是模型试验的优先次序，**不是“VOSR2 已经比 FlashVSR/SeedVR2 更好”的结论**。VOSR2 属于偏单帧图像恢复的候选，应用到 MP4 时要明确其逐帧处理及潜在时序不稳定，不要声称原生视频一致性已验证。FlashVSR 是后备的视频恢复候选，具体采用哪个版本、ComfyUI 插件及运行依赖须在下一次部署时以真实上游版本/环境核对，不能默认为已安装。
- **评价维度**：先看原片内容遵守（闭眼人脸、角耳、服装、天空笔触）、轨道和建筑细线的跨帧闪烁/蠕动、人物身份稳定度，再看锐度和性能；使用原始 H3 MP4，不拿 SeedVR2 重建视频作为另一模型的默认输入。需要公平横比时记录实际尺寸、输入文件、版本、Seed、处理链、帧数、耗时；不额外设新 hash、冻结合约或前置门禁。视觉观察不理想即可依据用户判断切换 FlashVSR，不必让准备工作取代 GPU 实测。
- **与后续 H3 的关系**：中远景角色尤其是原画晴空/纯文字天空可优先考虑让 H3 在源头尝试更高于 960×544（约 0.52MP）的实际生成规格，例如 **1280×720（约 0.92MP）为候选**，但在当前 Hybrid 13-step 组合中尚未验证，不冒称已经 GPU 通过。后期超分不能可靠补足源视频完全缺失的角色信息。

### 2026-11-21 · Vast.ai VOSR2 本轮工作流、分辨率讨论与实际上传版本

- **本次平台已明确为 VA（Vast.ai），不是 FEA**。用户提供的第二个 Vast Template 标识 `b5771d53a8d95d86922dc9f4f61e0192`，编辑页名称 `NEW.H3_SEEDVR`，镜像 `vastai/comfy:v0.44.0-cuda-13.2-py312`；模板声明 `AIW_COMFY_DIR=/workspace/ComfyUI`、`AIW_PYTHON=/venv/main/bin/python`、`AIW_ASSETS_ROOT=/workspace/aiworkbench-assets`、`COMFYUI_ARGS="--disable-auto-launch --disable-xformers --port 18188 --enable-cors-header"`，Portal 将外部 8188 指向内部 18188。以上是**用户提供的模板配置**，不等于已核实当前实例的实装版本或一次成功 Queue；后续部署必须沿用当前服务，不另起第二个 ComfyUI。
- **本轮上传文件的真实身份**：`vosr_workflow(1).json` 与早先 `vosr_workflow.json` **字节完全相同**（本轮在容器直接比对）；其原始 UI JSON 为 **19 个顶层节点、17 条顶层链接、3 个分组、2 个嵌入子图**。分组分别是 `Input Image + VOSR workflow`、`FLUX + VOSR2 Workflow`、`MiniMax H3 + VOSR2`，属于保留的示例全画布，**不是**已经完成现有 MP4 输入/输出超分的专用图。未经用户新的导出证据，不得将截图里的改动写成已保存在此 JSON。
- **保留的 JSON 参数（已直接读取）**：图片分组 `VOSR2ModelLoader #26 → VOSR2Upscale #27`，#27 当前是 **5×**，Seed 42/fixed、wavelet、tile 512/64、VAE tile 512/64；FLUX 分组 #21→#22 默认 **4×**，VAE tile 1024/128；H3 分组 #135→#134 默认 **4×**、Seed 42/fixed、wavelet、tile 512/64、VAE tile 512/64，#134 的 IMAGE 来自内置 `Image to Video (MiniMax H3)` 子图 #129，而非视频文件。#137 `CreateVideo` 在这份 JSON 中仍是 **30 fps**，并接 #132 `SaveVideo`。模型 Loader 在本 JSON 的 dtype 全部为 `default`，**不是** screenshot 显示的 `fp16`。
- **此上传 JSON 里不存在** `LoadVideo`、`GetVideoComponents` 或 `ImageScale`。用户之后的 ComfyUI 截图中可见 VOSR2 `upscale=2`、`fp16`、wavelet、512/64、1024/128、后置「缩放图像」1440×816、最近邻、以及「创建视频」30fps；截图只证明画布界面曾显示这些控件，不能证明已正确接入视频、保存到上传文件或 GPU 出片。单独做已有 MP4 的超分，目标线路应为 `LoadVideo → GetVideoComponents.images → VOSR2Upscale(IMAGE) → [可选后置 ImageScale] → CreateVideo(源 fps/音频) → SaveVideo`，不触发 MiniMax H3 采样；具体实际节点和运行应以更新后的实例导出 JSON/Queue 为证。
- **分辨率讨论属于测试候选，不属于实测**：源视频历史约 960×544、24fps、124帧；VOSR2 的 `upscale` 为整数倍率，2× 时真实 AI 超分为 **1920×1088**，可选后置缩至 **1440×816** 或 1280×720；3× 为 **2880×1632**，可再后置缩至约 2560×1450。后置缩小只改变输出分辨率，不节省 VOSR2 先做 2×/3× 的主要推理成本。图中 `CreateVideo=30fps` 若处理历史 24fps P1 视频，会改变时长，应连源 fps 或改 24fps；后置 `nearest-exact` 降采样与 `lanczos` 比较须以画面实测为准。没有超分 MP4、耗时或质量证据之前，不记录“VOSR2优于SeedVR2”。
- **仓库存档约束**：如将此 JSON 上传至 `Kwaner-ANTI/AIGC-C.W.P`，务必将它标识为**用户本轮原样上传的三组示例 UI 工作流**，不能作为“视频输入已完成”版本宣传。可在未来取得新的真实 ComfyUI 导出后原位更新同一文件，不另外制造多个重复版本；公有仓库不放私有参考图、MP4、Token、SSH 凭据。

## 4. Illustrious XL：云端待办，当前不抢超分测试

- **执行位置**：用户已撤回“本地优先部署 Illustrious XL”的旧建议。改为 **Featurize 等云端图片 ComfyUI 工作负载**；本地现有文字模型和未来 ANIMA 规划不因此改变。模型任务选择与图片 Runtime 独立于 H3 视频 Runtime。
- **配置 A**：`Hassaku XL (Illustrious) v1.3 Style A`；来自用户截图的 LoRA：`mon (monmon2133) style` v1.0 **0.5**；Civitai 模型 1065247 / version 1195582 **0.6**（原图标题不可靠）；`Pony: People's Works v1-v6` v6 noobEv1.1 **0.3**；`Stabilizer II /NAI/CK` illus01 v1.23 **0.3**；`ma1ma1helmes | Shiiro's Styles | Niji` Style A **0.4**。这些只是对应截图的使用值，不是社区普遍最优。
- **配置 B**：`JANKU Trained + Chenkin & Noobai Rouwei Illustrious XL v5.0`；含 `People's Works: SDXL` v8_Illusv2.0Stable、`Cryosibilum Style | Illustrious` Experimental、`Anime in real` V1.0 Illustrious、`Aesthetic Quality Modifiers – Masterpiece` v3.0 [illustrious]、`GENESIS` v1.0 LyCORIS。**第二组截图未给可靠 strength**，不得伪造。
- 两组不混合 checkpoint；先 A 后 B，是否共用画布和各需多少 JSON 依用户下一次明确确认。当前未在 GPU 部署或出图。原创背景/文字背景可互补，不能假定直接挪用其他作品原画拥有发行授权。

## 5. H3 实测事实与后续动作用途（留在当前版）

- **已发生**：2026-11-20 Featurize RTX5090 成功载入 B25-49 Hybrid `minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors` + Qwen3-VL 32B INT8 `qwen3vl_32b_minimax_h3_int8_convrot.safetensors`，13/13 steps 采样、修复 `H3LongVideoAppend` 的 `ffmpeg` 找不到故障之后用户报告生成首片。早期失败日志约 74–75s 是采样阶段，不是端到端成片耗时。
- **随后 P1 生成批次**：用户报告 13-step、无 LoRA，常规约 **84s**、首条 **181s**（未完整分离加载与编码）；P1 原画人物/背景融合获用户认可，REF03 效果接近其历史双 INT8 视频感受；原画云层被保持得僵硬，纯文字天空动态较自然。数据不足以证明模型精度相等。
- **T01 折返跑**：有可见跑停转身，动幅高于预期；**T02 Line Dance 暂停**，问题集中在人物像贴景、脚底和地面接触失败、漂移与动作错乱。不能凭此得出所有舞蹈或 H3 高动态必然失败。
- **下一项 S02**：车厢坐姿起身、扶杆、重心与列车惯性；优先观察支撑接触、扶杆相对位置、衣着/角耳身份、画面几何及跨段连续。历史交接材料为 `GALLEON_H3_SHOT_ASSET_HANDOFF_2026-11-20_UPDATED.md` 的原 S02/BG-07。未见所提 `...2026-11-21_UPDATED.md` 完整交接文件，**不能擅自把旧的 S02 参考槽位写成已核实的新版输入**。
- **其它技术**：FL2VA Turbo v1.0 8-step != LightX2V Ref2VA v1.1；Hook Motion Dial (`h3_motion.safetensors`) != 普通 Motion LoRA；BUNNY Impact Slider != BUNNY Conditioning Bridge；fuzzballb Long Video != ooizj Long Video。旧 7TE 的 #70/#92/#96/#77 控制不同分支；Hook/BUNNY/8step/真正两段续接与 FlowHMR/Blender 尚无足以认定本轮 GPU 完成的证据。

## 6. 历史经验中仍会复用的参数、Seed 与研究注意事项

- ANIMA Aesthetic 历史有效局部配置：`er_sde + simple`，约 60 steps、CFG 4；背景样本曾使用 1792×1008。第三方创作 LoRA `anima-base-1-masterpiece-v51.safetensors` 曾先 1.0 后约 **0.7**，Turbo loader OFF；这些不应套给 H3 或 Illustrious。历史候选 Seed：`1037900080820553`、`1029420174235775`、`957452313466548`、`1070301962178338`、`624953497604917`，**尚未完整绑定原 PNG/History**，非万能稳定 Seed。
- 5090 历史 LightX2V Ref2VA v1.1 已有六条实际 MP4；人物替换时用户曾评价接近原生20步，而普通视频场景画质不如旧 Full INT8。两类任务不应合并为一条绝对结论。
- Vast PRO6000 Full INT8 + INT8 Text 原生 20-step MP4 是旧 GPU 事实，**不恢复为本轮 5090 默认**。Full INT8、Pruned、NVFP4-AWQ/ BF16 Text 量化互换须有真实文件/采样条件，不能用旧 Full INT8 bootstrap 冒充 Hybrid 恢复。
- Seed 的有效记录须与真实执行图、模型量化、任务模式、LoRA/Hook、sampler/scheduler/sigmas、尺寸/帧数、参考顺序、Prompt revision、MP4 对应；`RandomNoise.widgets_values` 只是 UI 缓存，不能当已成功生成的 executed Seed。
- 旧 P1 “单张原画 vs 纯文字”、旧 T01/T02 双动作计划、GE-1.2、所有历史英文 Prompt、ANIMA/Krea/FLUX 原图提示词、详细实验数据表、原作者考证与旧 Note 都在**离线历史档原文**，不在现行在线版重复占用体积。

## 7. 原系统与跨项目回流方式

- **工作分工**：Galleon 管 Shot/美术/人物/原始媒体和主观视觉评价；AIWorkbench 管 ComfyUI 节点/量化/模型安装、租机/运行时、生成参数与 Workbench Project → Shot → Prompt Revision → Generation → Review。不要为视频输出另做一套管理/History。
- Workbench 原有 SSH-owned tunnel、known_hosts、凭证保护、Start/Reuse、keepalive、远端真实健康检查和私有资产的长期保存不改变；本次无用户授权不改 GitHub/云机器/Project 来源。
- **整理方式**：只有最新执行事实写回本在线版；要追溯旧 Prompt/Seed/实验或发现历史矛盾时，临时上传 `AIWORKBENCH_GALLEON_IMAGEGEN_EXPERIENCE_2026-11-21_HISTORY_FULL.md`，按原始证据逐条对比，再把确实可复用的新结论归并到相应现有章节，不创建第二个“常驻历史数据库”。
- **事实等级**：已发布或可导入的 JSON ≠ 插件已安装；模型可选 ≠ MODEL 线路实际采用；节点接好 ≠ Queue 通过；样片视频存在 ≠ 画质达标；工作流集成进 Workbench ≠ 已跨项目同步。