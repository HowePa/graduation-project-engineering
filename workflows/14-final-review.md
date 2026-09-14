# 14-final-review 最终审查

输入：全部成果。

输出：artifacts/consistency-report.json、交付清单。

执行：检查 snapshot、来源、全文事实映射、图表引用编号、章节小结、文献、DOCX 结构及渲染；任何缺项写 blocked，返回非零。Phase 6 / Gate 6 批准后才可正式交付。

规则：[ consistency-rules ](../rules/consistency-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
