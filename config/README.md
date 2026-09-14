# 配置契约

`*.schema.yaml` 是 JSON Schema Draft 2020-12，以 JSON（YAML 子集）存储，支持任意标准 YAML 配置。拒绝未知字段；项目配置必须完整。`thesis.yaml` 可省略，使用 defaults.yaml；提供时须完整并显式覆盖。论文参考文献最低数同时配置时取两者较大值，避免偷偷降低要求。

所有项目路径相对 project.yaml，禁止绝对路径、路径穿越与指向项目外的符号链接。目标技术栈目前限定 Golden Example；角色和业务字段可配置但不代表其他系统已适配。配置中的测试命令使用参数数组，无 shell；这是执行本地代码，使用前检查项目配置的可信度。

Evidence 结构见 [evidence.md](evidence.md)。Schema 是结构验证，脚本还校验文件散列、来源存在、重复标识及状态语义。

## v0.2 增量

thesis.yaml 可增添 template（相对项目路径）和 chapters（非空章节标题数组）。Resolver 持久化最终 thesis-runtime.yaml；common.config 在锁有效时读取 runtime，原 inspect/Evidence 格式不变。既有 project.yaml 的五章目标保持兼容，最终论文结构以 runtime.chapters 为准。

新增 ui.schema.yaml、workflow-state.schema.json、phases.yaml。旧 .project-state.json 与新 .workflow-state.json 职责分开；原六个 Gate 记录不自动迁移。模板和对话控制文件按路径精准排除系统 snapshot，由 Phase/模板锁单独校验，业务源码失效规则不变。
