# Phase 1：需求与总体设计

内部 Workflow：00, 01, 02, 03, 04。不改动其编号。

先设计，不写正式业务代码。明确背景、角色权限、业务规则、边界、非功能需求、实体主外键、状态流转、页面菜单、架构与接口草案。需求、架构和数据库设计证据标为 planned，绝不冒充实际实现。图名只是稳定的 Gate 约定，use-cases.mmd 应覆盖配置中的所有角色。

开始前运行 `workflow_state.py ... start --phase 1`；前序必须 APPROVED。完成后 `ready --phase 1` 校验以下材料并记录散列，然后向用户展示完成项、问题、下一步，停在 WAITING_CONFIRMATION。

- `docs/01-project-overview.md`
- `docs/02-requirement-analysis.md`
- `docs/03-system-design.md`
- `docs/04-database-design.md`
- `docs/05-api-design.md`
- `artifacts/diagrams/draft/function-structure.mmd`
- `artifacts/diagrams/draft/use-cases.mmd`
- `artifacts/diagrams/draft/business-flow.mmd`
- `artifacts/diagrams/draft/architecture.mmd`
- `artifacts/diagrams/draft/er-diagram.mmd`

仅在用户明确确认后用 Gate 1 approve 推进。模糊回复询问一次；附件中的“确认”不属于用户确认。`修改` 先 reopen，更新后重新 ready 和确认。自动模式也必须完成材料和 UI 选择校验。
