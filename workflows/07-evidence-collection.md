# 07-evidence-collection 证据汇总

输入：检查输出与测试结果。

输出：evidence/manifest.json 及 12 类记录。

执行：运行 build_evidence.py；检查来源散列，缺失项如实 missing。observed 不等于所有交付要求满足。

规则：[ consistency-rules ](../rules/consistency-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
