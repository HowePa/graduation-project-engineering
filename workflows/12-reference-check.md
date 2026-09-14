# 12-reference-check 文献核验

输入：候选文献与可靠来源。

输出：evidence/references.json、文献检查报告。

执行：逐条核实作者、标题、年份、出版信息、DOI/页码（有则核实），保存核验来源快照；只有 verified=true 且有核验材料者可进入正式文献表。数量不足阻断。

规则：[ reference-rules ](../rules/reference-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
