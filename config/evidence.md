# Evidence v1

每个 evidence JSON 使用统一 envelope：schema_version、kind、status、generated_at（UTC）、producer、input_snapshot（全部输入的 SHA256）、sources[{path,sha256}]、limitations、data。12 类 data 的字段见 evidence.schema.json；observed 必须有非空来源并通过类别模型校验。

状态：planned=意图；observed=观察到（不等于业务验收）；missing=未取得；failed=采集或执行失败；not_run=明确未执行。缺失项使用空 data 并写明原因；performance 未执行用 not_run，禁止填默认成绩。API 的未提取权限、请求与响应必须标明局限，不能根据需求补全。

manifest.json 保存各记录散列和全项目输入 snapshot。输入集合含配置、源码、数据库、测试及 docs；排除 evidence、artifacts、thesis、构建缓存。每份 evidence 另存直接来源散列。新增/删除源码也改变 snapshot。变化使旧清单、Gate 和下游状态失效，检查器必须非零退出。

运行日志保存至 artifacts/test-runs/<run-id>/，JUnit 来自本次执行，旧报告须拒绝。测试用例未提供细节时标为“JUnit 未记录”，不得将断言预期复制为实际 API 返回。

v0.1 Gate approval={snapshot, confirmed_by, confirmed_at, note} 保留为历史记录。v0.2 的阶段批准改用 .workflow-state.json，绑定审阅材料散列并记录确认来源，见 phase-rules.md；旧 Gate 不自动迁移。状态不是证据。

后续论文 claims.json 推荐保存 {chapter, text, evidence_path, json_pointer, evidence_sha256}，每条事实可追溯；不能仅靠关键词扫描声称语义一致。正式最终验收仍需逐条审阅正文事实。

## v0.2 控制文件

原 12 类 envelope、manifest 和采集器不变。新增 .workflow-state.json、.thesis-template-lock.yaml、thesis-runtime.yaml、ui-design.yaml、decisions/、inputs/thesis-template/ 不计入系统输入 snapshot，分别由 Phase 的材料散列与模板锁核验；实际业务代码变更仍使原 Evidence 失效。evidence/ui-design.json 是 planned 的辅助选择记录，不混入既有 manifest 或冒充实际前端实现。
