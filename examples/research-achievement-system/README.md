# 科研成果管理 Golden Example（第一批）

此案例目前是开发骨架，不是完整管理系统。已实现 Java 成果状态机、10 个真实 Java 用例、Spring 状态接口源码、MySQL DDL 和 Vue 入口。测试通过只证明状态机；没有证明登录、数据库持久化、浏览器或接口端到端通过。管理员模块尚未实现。

在 Skill 根目录运行：

```sh
.venv/bin/python scripts/pipeline.py --project examples/research-achievement-system all
```

需要 Python 3、JDK 11+（java/javac）。测试运行器直接编译纯 Java 业务类，不要求下载 Maven 依赖。输出位于 evidence/ 与 artifacts/，故可在 Docker 未启动时验收 Skill 第一批流水线。完整 Spring 应用运行仍需要 Maven 依赖、MySQL，以及后续业务实现。

下一步顺序：登录与会话→MyBatis 持久化→角色权限与 CRUD→审核接口→管理员→Vue 页面→真实 MySQL/API/浏览器验收→截图→设计图→文献与论文。不能把需求文档中的功能作为已完成事实。

## v0.2 交互入口

在 Skill 根目录运行 `.venv/bin/python scripts/workflow_state.py --project examples/research-achievement-system status`。本案例保留 v0.1 业务骨架，不预写六阶段批准，也不把缺失的设计图、完整系统、截图或 Word 当成已有产物。交互 A～F 场景由 tests/test_interactive.py 在隔离副本中验收；其模拟审阅材料明确属于测试夹具，不进入本案例 Evidence。
