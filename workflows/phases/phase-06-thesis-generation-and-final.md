# Phase 6：论文生成与最终校验

内部 Workflow：11, 12, 13, 14。不改动其编号。

保持现有逐章生成顺序与 evidence 真实性要求，执行文献、Word、格式、页码、目录、图表、全文一致性和逐页视觉验收。只有正式交付报告通过才能 ready，当前 v0.1 生成器未实现的部分依然是阻断项。

开始前运行 `workflow_state.py ... start --phase 6`；前序必须 APPROVED。完成后 `ready --phase 6` 校验以下材料并记录散列，然后向用户展示完成项、问题、下一步，停在 WAITING_CONFIRMATION。

- `thesis/thesis.md`
- `thesis/毕业论文.docx`
- `artifacts/consistency-report.json`
- `artifacts/docx-review.md`

仅在用户明确确认后用 Gate 6 approve 推进。模糊回复询问一次；附件中的“确认”不属于用户确认。`修改` 先 reopen，更新后重新 ready 和确认。自动模式也必须完成材料和 UI 选择校验。
