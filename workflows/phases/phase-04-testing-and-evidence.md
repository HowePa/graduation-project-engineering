# Phase 4：测试与论文证据

内部 Workflow：06, 07, 08, 09。不改动其编号。

执行现有测试、inspect、截图、图表、Evidence 和一致性检查。截图和图表仍须真实采集与人工视觉审阅，不因状态机存在就声称已自动实现。展示清单，允许换编辑弹窗或补充明确标为演示的数据。材料不全时不得 ready。

开始前运行 `workflow_state.py ... start --phase 4`；前序必须 APPROVED。完成后 `ready --phase 4` 校验以下材料并记录散列，然后向用户展示完成项、问题、下一步，停在 WAITING_CONFIRMATION。

- `docs/test-report.md`
- `evidence/manifest.json`
- `evidence/test-results.json`
- `evidence/screenshots.json`
- `evidence/diagrams.json`

仅在用户明确确认后用 Gate 4 approve 推进。模糊回复询问一次；附件中的“确认”不属于用户确认。`修改` 先 reopen，更新后重新 ready 和确认。自动模式也必须完成材料和 UI 选择校验。
