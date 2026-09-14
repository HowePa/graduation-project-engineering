# Phase 2：UI 与实现计划

内部 Workflow：新增 UI 选择与实现计划。不改动其编号。

使用 ui_design.py recommend 给出 A/C/D 三套的配色、布局、表格、表单和 Dashboard 对比；支持任意覆盖与组合。只有用户选择后才能 select 保存 ui-design.yaml。实现计划列出页面、菜单、路由、组件、后端模块、开发顺序、数据初始化、测试账号方案和 Docker 服务。UI 选择与阶段确认是两次独立决策。

开始前运行 `workflow_state.py ... start --phase 2`；前序必须 APPROVED。完成后 `ready --phase 2` 校验以下材料并记录散列，然后向用户展示完成项、问题、下一步，停在 WAITING_CONFIRMATION。

- `ui-design.yaml`
- `docs/06-implementation-plan.md`

仅在用户明确确认后用 Gate 2 approve 推进。模糊回复询问一次；附件中的“确认”不属于用户确认。`修改` 先 reopen，更新后重新 ready 和确认。自动模式也必须完成材料和 UI 选择校验。
