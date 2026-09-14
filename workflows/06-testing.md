# 06-testing 真实测试

输入：可构建源码与测试命令。

输出：evidence/test-results.json、真实测试日志。

执行：run_tests.py 执行参数数组并读取本次 JUnit；覆盖正常、异常、边界、角色越权、审核状态流转。性能未测记 not_run。本步骤归属 Phase 4；进入前须已有 Phase 3 系统验收批准。

规则：[ project-rules ](../rules/project-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
