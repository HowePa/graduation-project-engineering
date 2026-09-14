# Phase 3：系统实现

内部 Workflow：05。不改动其编号。

读取 ui-design.yaml，按计划实现登录、权限、持久化、核心业务和页面。真实启动与联调后展示 Demo，由用户体验、修改再确认。runtime-acceptance.md 记录前端/后端地址、数据库、核心功能演示及 UI 对照结果；文件本身不能代替真实验收。首页卡片调整走 implementation 回退；不要直接开始写论文。

开始前运行 `workflow_state.py ... start --phase 3`；前序必须 APPROVED。完成后 `ready --phase 3` 校验以下材料并记录散列，然后向用户展示完成项、问题、下一步，停在 WAITING_CONFIRMATION。

- `docs/runtime-acceptance.md`

仅在用户明确确认后用 Gate 3 approve 推进。模糊回复询问一次；附件中的“确认”不属于用户确认。`修改` 先 reopen，更新后重新 ready 和确认。自动模式也必须完成材料和 UI 选择校验。
