# graduation-project-engineering

以真实系统为核心、Evidence 为桥梁的毕业设计工程 Skill。当前版本 **v0.2 — Interactive Staged Workflow**，仅以科研成果管理系统为 Golden Example。

v0.2 增量提供六个交互 Phase、真正约束推进的 Gate、UI 选择、对话模板 Resolver 与有范围的回退失效。保留 v0.1 的 12 类 Evidence、inspect、真实测试、SHA256 与一致性工具链，不重新实现它们。完整业务系统、截图/设计图和 Word 生成器仍是后续工作；状态机不会把这些缺项变成完成。

## 安装与启动

Python 3.10+；Golden Example 还需 JDK 11+，`java`、`javac` 在 PATH 中。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system status
```

Windows 将 `.venv/bin/python` 换为 `.venv\Scripts\python.exe`。脚本使用 pathlib 与参数数组，不依赖 shell。当前已在 macOS 验证，Windows/Linux 尚未实际验证。已验证依赖版本记录在 requirements.lock.txt；虚拟环境不属于交付源码。

作为 Codex Skill 使用时，将整个目录复制到个人 skills 目录并保留名称 `graduation-project-engineering`，或在任务中显式引用当前目录的 SKILL.md。不要把 `.venv` 和示例生成的 evidence/artifacts 复制为 Skill 素材。当前任务只在工作目录实现，未安装到全局。

## 配置

[项目示例](examples/research-achievement-system/project.yaml) 是可直接运行的配置，格式受 [project.schema.yaml](config/project.schema.yaml) 校验。所有路径相对目标项目，不能越出项目；未知字段、重复功能 ID、未声明角色会失败。技术栈配置表示开发目标，不能当成使用事实。

`thesis.yaml` 受 [thesis.schema.yaml](config/thesis.schema.yaml) 校验，省略时读取 [defaults.yaml](config/defaults.yaml)。默认五章及文献数量、字体、字号、页边距等已有配置契约；当前 Word 生成器尚未实现；模板可由 v0.2 Resolver 动态选择并形成最终规则。

`workflow.test_command` 为实际执行的 argv；必须用 `{report_dir}` 传入本次唯一报告目录。`test_report_glob` 用 `{run_id}` 匹配本次 JUnit。命令受项目配置控制，运行前审阅它；退出码为 0 且报告含非空、全部通过的真实用例才通过。

Golden Example 的测试命令编译并运行独立 Java 成果状态机，用例涵盖正常审核、驳回、空标题、长度边界、越权修改/提交、错误角色审核、非法状态与重复提交；它不证明 Spring HTTP、MySQL 或页面通过验收。

## 执行与续作

```sh
# 单阶段；也可直接运行 inspect_database.py 等独立脚本
.venv/bin/python scripts/pipeline.py --project examples/research-achievement-system inspect
.venv/bin/python scripts/pipeline.py --project examples/research-achievement-system test
.venv/bin/python scripts/pipeline.py --project examples/research-achievement-system evidence
.venv/bin/python scripts/pipeline.py --project examples/research-achievement-system check

# 当前输入与 evidence 均有效才复用成功阶段
.venv/bin/python scripts/pipeline.py --project examples/research-achievement-system all --resume

# Skill 自身回归测试，含隔离目录中的 Golden Example 端到端测试
.venv/bin/python -m unittest discover -s tests -v
```

`all` 仅表示以上四步。第一次运行失败即停止；缺依赖、编译失败、无用例、跳过/失败用例、过期来源、篡改记录都会非零退出。中断后重跑 `all --resume`；缺少最终有效清单时保守重跑。源码变化后重跑 `all`，不能只重建 manifest 为旧测试证据盖新时间。

`.project-state.json` 记录当前阶段、完成项、待办、检查清单和 Gate。Evidence 各记录保存当前全输入 snapshot 与直接来源 SHA256，manifest 再记录每份 evidence 的 SHA256。新增、修改、删除输入均使旧记录失效。此机制检测意外变化，不是针对恶意重写全部散列的数字签名。

`check` 的退出码仅代表 **Evidence 完整性检查**。报告中的 `delivery_status` 当前始终 `blocked`，因为 v0.1 不执行完整论文验收；不得把完整性 PASS 转述为正式交付通过。

## 交互式使用方式

推荐在 Codex 中说：“使用当前 Skill，从现有阶段继续；每阶段给我审阅后再继续。”默认顺序：

| Phase / Gate | 审阅内容 | 内部 Workflow |
|---|---|---|
| 1 | 需求、角色权限、总体设计、用例/功能/流程/ER图、数据库和 API 草案 | 00～04 |
| 2 | UI 选择、菜单页面、实现计划 | 新增交互步骤 |
| 3 | 可运行 Demo、角色功能、前后端/数据库、UI 对照 | 05 |
| 4 | 测试、真实截图、设计图、Evidence | 06～09 |
| 5 | 模板、格式、章节、图表计划、文献要求 | 10 |
| 6 | 逐章论文、Word、格式与最终校验 | 11～14 |

状态保存到 `.workflow-state.json`，重要决策在 `decisions/`。旧 `.project-state.json` 仍记录局部工具链；旧 Gate 1/2 含义不同，不自动迁移为新批准。

```sh
.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system status
.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system start --phase 1
# Agent 完成阶段材料后请求审阅；必需清单在 config/phases.yaml
.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system ready --phase 1
# 仅用户明确确认后执行；不是本仓库已获确认的声明
.venv/bin/python scripts/gates.py --project examples/research-achievement-system --gate 1 --confirmed-by reviewer --note "确认本次需求与设计"
.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system start --phase 2
```

`ready` 检查材料并保存散列，然后停在 WAITING_CONFIRMATION；`approve` 再验材料，前序未批准禁止推进。额外材料用 `ready --artifact <相对路径>`。Gate 4 拒绝缺失的真实测试/截图/图表，Gate 5 拒绝未审阅格式的二进制模板，Gate 6 拒绝 blocked 交付报告。文件检查不能替代用户实质审阅。

用户可回复“确认，下一阶段”或“修改：……”。Agent 只在已展示具体阶段材料、等待对应确认的上下文中解释“可以/继续”；含修改条件的回复先修改，不视为无条件批准。模糊时澄清一次。

```sh
# 回退不删除旧成果，只撤销批准、标记相关返工项
.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system reopen --change ui --note "主色调整，卡片取消阴影"
# 也支持 reopen --phase 1；数据库修改用 --change database
```

需求/数据库→Phase 1；UI→Phase 2；系统功能→Phase 3；素材→Phase 4；模板→Phase 5。UI 修改不将全部后端列为返工项，但修改后的 Demo 必须再确认。模板修改保留系统与 Evidence，仅令 Word、格式、目录、分页、图表布局失效。已审阅文件变化自动撤销对应确认；Phase 3 还检查运行源码的新增/删除。

默认不连续自动执行。用户明确说“自动执行后续阶段”后，可记录授权：

```sh
.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system authorize-auto --confirmed-by reviewer --note "用户明确授权自动执行后续阶段"
# 每个阶段仍 start、ready、approve；自动批准需显式 --automatic
# disable-auto 使用同样的 --confirmed-by 与 --note 撤销自动授权
```

也兼容项目 `auto_approve_gates: true`。自动模式不替用户猜 UI，不绕过材料验证。`pipeline.py all` 保持用于 CI、回归和 Evidence 刷新，**不是毕业设计一键完成，也不是默认用户 Phase 入口**。

## UI 选择与定制

内置 A 蓝白科研管理、B 青绿轻商务、C 深蓝灰专业、D 现代紫色数据四套风格，科研案例推荐稳定编号 A/C/D 三套，逐项展示主色、背景、布局、表格、表单和 Dashboard。

```sh
.venv/bin/python scripts/ui_design.py recommend
# Phase 1 已确认且 Phase 2 start 后，才可记录用户选择
.venv/bin/python scripts/ui_design.py select --project examples/research-achievement-system --preset A --dashboard D --overrides /path/to/ui-overrides.yaml --confirmed-by reviewer --note "选 A 配色，加 D 的 Dashboard"
```

`ui-overrides.yaml` 示例：

```yaml
theme:
  primary: "#1677FF"
components:
  shadow: none
```

用户：“选 A，但主色换成 #1677FF，卡片不要阴影。”Agent 将选择转为上述覆盖，保存 `ui-design.yaml`、`decisions/ui-design.yaml`、辅助 `evidence/ui-design.json`，然后完善实现计划供第二次确认。UI 辅助记录不加入既有 12 类 manifest；前端开发必须读取 `ui-design.yaml`。没有选择时不生成默认已选设计。

## 对话论文模板

优先级：**对话明确格式要求 > 对话附件 > thesis.yaml 指定模板 > Skill 默认**。兼容旧 project.yaml 指向实际存在的模板。未提供自定义模板直接使用默认，不反复询问。

```sh
# 无模板：自动解析项目配置或内置默认
.venv/bin/python scripts/resolve_thesis_template.py --project examples/research-achievement-system
# 用户提供可访问附件，不需要手改 thesis.yaml
.venv/bin/python scripts/resolve_thesis_template.py --project examples/research-achievement-system --template /path/to/thesis.docx --overrides /path/to/thesis-overrides.yaml
```

覆盖例：`references: {minimum: 20}`。`chapters` 可指定任意非空章节标题数组。Resolver 将附件复制到 `inputs/thesis-template/`，生成 `.thesis-template-lock.yaml`、`thesis-runtime.yaml` 与决策文件。后续 config 读取锁校验过的 runtime，参考文献数量仍保留原校验器取项目下限较大值的规则。重复运行保留对话选择；`--reset` 清除对话选择和覆盖。

内置默认是 **templates/default-thesis.yaml 格式模板**，不是学校 Word 模板。DOCX/PDF 支持登记和持久化；其复杂格式需 Agent 阅读并提取规则，用 `--template-rules <YAML> --reviewed-by <审阅者>` 登记。未经审阅设置 needs_format_review，阻断 Gate 5；不冒充已自动解析学校全部版式。附件不可访问明确报错，不能静默降级默认。

对话模板副本、锁、runtime、UI 决策和 Phase 状态不进入系统 snapshot，分别由模板锁/Phase 材料散列追踪，所以更换模板不会重建系统 Evidence。原 v0.1 配置与其他目录文件保留原输入语义：直接改 thesis.yaml/project.yaml 会保守使旧 Evidence 失效；对话换模板应使用 Resolver，不改旧配置。

## 目录与实现状态

| 目录/文件 | 当前内容 |
|---|---|
| SKILL.md | 入口、路由、授权边界、证据优先级与交付标准 |
| config/ | 保留原 Schema，新增 UI、Phase 状态 Schema 与 Gate 材料清单 |
| workflows/ | 保留 00～14，新增 phases/ 六个用户阶段 |
| rules/ | 项目、论文内容/格式、截图、图、数据库表、文献、一致性规则 |
| templates/ | 原 Markdown/manifest、四套 UI 预设、默认论文 YAML 格式模板 |
| scripts/ | 原工具链，加 workflow_state、ui_design、resolve_thesis_template；gates 适配 Phase |
| examples/research-achievement-system/ | Java 业务状态机与真实测试、Spring 状态接口、DDL、Vue 入口及设计意图 |
| tests/ | 保留原回归，增加 Golden Example 隔离目录中的交互 A～F 与绕过/篡改测试 |

Evidence 12 类结构见 [数据契约](config/evidence.md)。采集器尚未实现的类别生成 `missing`，性能未测试生成 `not_run`，需求为 `planned`。这些状态不是完成证据。

DDL 提取仅支持示例所用 CREATE TABLE 子集（BIGINT/INT/VARCHAR/TEXT/DATETIME/TIMESTAMP/DECIMAL/BOOLEAN，主键、外键、普通/唯一索引、默认值、注释）。不支持 ALTER、SQL 注释、生成列或复杂索引，遇到会拒绝整次提取。API 提取只支持直接 `@RestController`、单个字面量类 `@RequestMapping` 和方法映射；不支持数组、常量表达式、组合注解。权限、DTO 和运行响应不推测。

`validate_references.py` 检查核验记录、来源材料散列和配置数量；不自动联网证明文献真实存在。无文献时非零退出。

## 后续实现顺序

1. 在当前科研成果案例补齐登录、MyBatis 持久化、角色权限、CRUD、审核、管理员及 Vue 业务页面；用真实 MySQL 和 HTTP/浏览器验收。
2. 实现 `collect_screenshots.py`、`generate_diagrams.py`，按现有契约保存真实图片、图源及溯源，完成 Gate 3、4。
3. 实现 `build_thesis.py` 的逐章生成及 claims 映射，完成大纲 Gate 与文献核验。
4. 接入真实学校模板，实施 Word 生成、`validate_docx.py`、thesis-lint 和全文一致性检查，渲染逐页验收后完成 Gate 6。

未实现的脚本没有放置“返回成功”的占位文件。新增模板优先交给 Resolver 持久化，在后续 Word 阶段验证字体、分节、目录和图表排版。暂不新增其他技术栈或业务案例；如需修改当前案例，先更新需求与配置、实现源码、重跑 evidence，再推进论文。

## 本机验证边界

当前 Docker 守护进程未运行；未启动或验收 Spring/MySQL/Vue 完整系统。学校模板和经核验文献未提供。上述因素不会阻止第一批 Skill 工具链运行，但会阻止正式论文交付。运行结果见示例 `evidence/test-results.json`、`artifacts/consistency-report.json`，具体测试日志由证据记录给出相对路径。
