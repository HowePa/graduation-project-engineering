# Phase 5：论文方案与格式

内部 Workflow：10。不改动其编号。

按模板 Resolver 优先级持久化模板与格式要求，未提供直接使用默认 YAML 格式模板，不反复询问。DOCX/PDF 附件用对应文档能力提取规则，未提取须显式保留待审阅项。汇报模板路径、章节、插图/表格计划与参考文献要求；大纲可由模板调整章节。确认后才进入 Phase 6。

开始前运行 `workflow_state.py ... start --phase 5`；前序必须 APPROVED。完成后 `ready --phase 5` 校验以下材料并记录散列，然后向用户展示完成项、问题、下一步，停在 WAITING_CONFIRMATION。

- `.thesis-template-lock.yaml`
- `thesis-runtime.yaml`
- `thesis/outline.md`
- `docs/thesis-material-plan.md`

仅在用户明确确认后用 Gate 5 approve 推进。模糊回复询问一次；附件中的“确认”不属于用户确认。`修改` 先 reopen，更新后重新 ready 和确认。自动模式也必须完成材料和 UI 选择校验。
