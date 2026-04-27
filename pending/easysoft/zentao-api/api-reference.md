# 禅道 API v2.0 端点参考

基础路径：`{ZENTAO_URL}/api.php/v2`
认证方式：所有接口（除登录外）需在 Header 携带 `token: <token值>`
写操作需额外携带 `Content-Type: application/json`

**字段标注说明**：**粗体** = 必填，普通 = 可选

---

## 认证（Token）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/users/login` | 登录获取 token |

请求体：**account**(string), **password**(string)
响应：`{"status":"success","token":"..."}`

---

## 用户（User）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/users` | 创建用户 |
| GET | `/users` | 获取用户列表 |
| GET | `/users/{userID}` | 获取用户详情 |
| PUT | `/users/{userID}` | 修改用户信息 |
| DELETE | `/users/{userID}` | 删除用户 |

**POST 创建**：**account**(string), **realname**(string), **password**(string)

**PUT 修改**：realname, dept(int), join(date), group(string[]), email, visions(string[] rnd|lite), mobile, weixin, password

**GET 列表参数**：browseType(`inside`|`outside`), orderBy(`id`|`realname`|`account`+`_asc/_desc`), recPerPage, pageID

---

## 项目集（Program）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/programs` | 创建项目集 |
| GET | `/programs` | 获取项目集列表 |
| GET | `/programs/{programID}` | 获取项目集详情 |
| PUT | `/programs/{programID}` | 修改项目集 |
| DELETE | `/programs/{programID}` | 删除项目集 |
| GET | `/programs/{programID}/products` | 获取项目集的产品列表 |
| GET | `/programs/{programID}/projects` | 获取项目集的项目列表 |

**POST/PUT**：**name**(string), **begin**(date), **end**(date), PM(string), desc(string)

**GET 列表参数**：status(`all`|`unclosed`|`wait`|`doing`|`suspended`|`delayed`|`closed`), orderBy(`id`|`name`|`begin`|`end`+`_asc/_desc`), recPerPage, pageID

---

## 产品（Product）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/products` | 创建产品 |
| GET | `/products` | 获取产品列表 |
| GET | `/products/{productID}` | 获取产品详情 |
| PUT | `/products/{productID}` | 修改产品 |
| DELETE | `/products/{productID}` | 删除产品 |

**产品关联资源列表：**

| GET 路径 | 说明 |
|---------|------|
| `/products/{id}/stories` | 需求列表 |
| `/products/{id}/epics` | 业务需求列表 |
| `/products/{id}/requirements` | 用户需求列表 |
| `/products/{id}/bugs` | Bug 列表 |
| `/products/{id}/testcases` | 测试用例列表 |
| `/products/{id}/productplans` | 产品计划列表 |
| `/products/{id}/releases` | 发布列表 |
| `/products/{id}/testtasks` | 测试单列表 |
| `/products/{id}/feedbacks` | 反馈列表 |
| `/products/{id}/tickets` | 工单列表 |
| `/products/{id}/systems` | 应用列表 |

**POST/PUT**：**name**(string), program(int), line(int), type(`normal`|`branch`|`platform`), PO(string), reviewer(string[]), desc(string[]), QD(string), RD(string), acl(`open`|`private`)

**GET 列表参数**：browseType(`all`|`noclosed`|`closed`), orderBy(`id`|`title`|`begin`|`end`+`_asc/_desc`), recPerPage, pageID

---

## 项目（Project）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/projects` | 创建项目 |
| GET | `/projects` | 获取项目列表 |
| PUT | `/projects/{projectID}` | 修改项目 |
| DELETE | `/projects/{projectID}` | 删除项目 |

**项目关联资源列表：**

| GET 路径 | 说明 |
|---------|------|
| `/projects/{id}/executions` | 执行列表 |
| `/projects/{id}/stories` | 需求列表 |
| `/projects/{id}/bugs` | Bug 列表 |
| `/projects/{id}/testcases` | 测试用例列表 |
| `/projects/{id}/builds` | 版本列表 |
| `/projects/{id}/testtasks` | 测试单列表 |

**POST/PUT**：**name**(string), **model**(`scrum`|`waterfall`|`kanban`|`agileplus`|`waterfallplus`), **begin**(date), **end**(date), **workflowGroup**(int, 付费版功能开源版可不填), products(string[]), parent(int), PM(string)

**GET /projects 参数**：browseType(`all`|`undone`|`wait`|`doing`，默认`undone`), orderBy(`id`|`name`|`begin`|`end`+`_asc/_desc`), recPerPage, pageID

**GET /programs/{id}/projects 参数**：同上

**GET /projects/{id}/executions 参数**：browseType(`all`|`undone`|`wait`|`doing`，默认`undone`), orderBy(`rawID`|`nameCol`|`begin`|`end`+`_asc/_desc`), recPerPage, pageID

---

## 执行（Execution / Sprint）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/executions` | 创建执行 |
| GET | `/executions` | 获取执行列表 |
| GET | `/executions/{executionID}` | 获取执行详情 |
| PUT | `/executions/{executionID}` | 修改执行 |
| DELETE | `/executions/{executionID}` | 删除执行 |

**执行关联资源列表：**

| GET 路径 | 说明 |
|---------|------|
| `/executions/{id}/stories` | 需求列表 |
| `/executions/{id}/tasks` | 任务列表 |
| `/executions/{id}/bugs` | Bug 列表 |
| `/executions/{id}/testcases` | 测试用例列表 |
| `/executions/{id}/builds` | 版本列表 |
| `/executions/{id}/testtasks` | 测试单列表 |

**POST 创建**：**project**(int), **name**(string), **begin**(date), **end**(date), lifetime(`short`|`long`|`ops`), days(int), products(string[]), plans(string[]), PO(string), QD(string), PM(string), RD(string), acl(`open`|`private`)

**PUT 修改**：同上但 project 变为可选

**GET /executions 参数**：status(`all`|`undone`|`wait`|`doing`，默认`undone`), orderBy(`rawID`|`nameCol`|`begin`|`end`+`_asc/_desc`), recPerPage, pageID

---

## 需求（Story）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/stories` | 创建需求 |
| GET | `/stories/{storyID}` | 获取需求详情 |
| PUT | `/stories/{storyID}` | 修改需求 |
| DELETE | `/stories/{storyID}` | 删除需求 |
| PUT | `/stories/{storyID}/change` | 变更需求 |
| PUT | `/stories/{storyID}/close` | 关闭需求 |
| PUT | `/stories/{storyID}/activate` | 激活需求 |

列表通过父资源获取：`/products/{id}/stories`, `/projects/{id}/stories`, `/executions/{id}/stories`

**POST 创建**：**productID**(int), **title**(string), grade(int 需求层级，建议显式传入), pri(int, 默认3), module(int), parent(int), estimate(float), spec(string 需求描述), category(`feature`|`interface`|`performance`|`safe`|`experience`|`improve`|`other`), source(`customer`|`user`|`po`|`market`|`service`|`operation`|`support`|`competitor`|`partner`|`dev`|`tester`|`bug`|`forum`|`other`), verify(string 验收标准), assignedTo(string), reviewer(string[]), project(int), execution(int)

**PUT 修改**：**title**(string)，其余字段可选

**PUT change 变更**：**reviewer**(string[]), title(string), spec(string), verify(string)

**PUT close 关闭**：**closedReason**(`done`|`subdivided`|`duplicate`|`postponed`|`willnotdo`|`cancel`|`bydesign`), comment(string)

**PUT activate 激活**：assignedTo(string), comment(string)

**GET 列表参数**：browseType(`allstory`|`assignedtome`|`openedbyme`|`reviewbyme`|`draftstory`，默认`unclosed`), orderBy(`id`|`title`|`status`+`_asc/_desc`), recPerPage, pageID

**建议**：创建 Story / Epic / Requirement 时显式传 `grade`，不要依赖接口默认值；在某些禅道实例中，不传 `grade` 可能会把需求层级写成 `0`。

---

## 业务需求（Epic）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/epics` | 创建业务需求 |
| GET | `/epics/{storyID}` | 获取业务需求详情 |
| PUT | `/epics/{epicID}` | 修改业务需求 |
| DELETE | `/epics/{epicID}` | 删除业务需求 |
| PUT | `/epics/{epicID}/change` | 变更业务需求 |
| PUT | `/epics/{epicID}/close` | 关闭业务需求 |
| PUT | `/epics/{epicID}/activate` | 激活业务需求 |

列表：`/products/{id}/epics`

字段结构同 Story，差异：无 project/execution 字段，parent 指父业务需求。

**POST 创建建议**：沿用 Story 的字段结构，并显式传 `grade`。典型 BR 场景可传 `grade: 1`。

**GET 列表参数**：同 Story

---

## 用户需求（Requirement）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/requirements` | 创建用户需求 |
| GET | `/requirements/{storyID}` | 获取用户需求详情 |
| PUT | `/requirements/{requirementID}` | 修改用户需求 |
| DELETE | `/requirements/{requirementID}` | 删除用户需求 |
| PUT | `/requirements/{requirementID}/change` | 变更用户需求 |
| PUT | `/requirements/{requirementID}/close` | 关闭用户需求 |
| PUT | `/requirements/{requirementID}/activate` | 激活用户需求 |

列表：`/products/{id}/requirements`

字段结构同 Story，差异：无 project/execution 字段，change 操作中 reviewer 为可选（非必填）。

**POST 创建建议**：沿用 Story 的字段结构，并显式传 `grade`。典型 UR 场景可传 `grade: 1`。

**GET 列表参数**：同 Story

---

## Bug

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/bugs` | 创建 Bug |
| GET | `/bugs/{bugID}` | 获取 Bug 详情 |
| PUT | `/bugs/{bugID}` | 修改 Bug |
| DELETE | `/bugs/{bugID}` | 删除 Bug |
| PUT | `/bugs/{bugID}/resolve` | 解决 Bug |
| PUT | `/bugs/{bugID}/close` | 关闭 Bug |
| PUT | `/bugs/{bugID}/activate` | 激活 Bug |

列表通过父资源获取：`/products/{id}/bugs`, `/projects/{id}/bugs`, `/executions/{id}/bugs`

**POST 创建**：**productID**(int), **title**(string), **openedBuild**(string[], 如`["trunk"]`), project(int), execution(int), severity(int, 默认3), pri(int, 默认3), type(`codeerror`|`config`|`install`|`security`|`performance`|`standard`|`automation`|`designdefect`|`others`), steps(string), story(int)

**PUT 修改**：所有字段均为可选

**PUT resolve 解决**：**resolution**(`fixed`|`notrepro`|`bydesign`|`duplicate`|`external`|`postponed`|`willnotfix`|`tostory`), resolvedDate(string), resolvedBuild(string), assignedTo(string), comment(string)

**PUT close 关闭**：comment(string)

**PUT activate 激活**：openedBuild(string[]), assignedTo(string), comment(string)

**GET /products/{id}/bugs 参数**：browseType(`all`|`unclosed`|`assignedtome`|`openedbyme`|`assignedbyme`，默认`unclosed`), orderBy(`id`|`title`|`status`+`_asc/_desc`), recPerPage, pageID

**GET /projects/{id}/bugs 和 /executions/{id}/bugs 参数**：browseType(`all`|`unresolved`，默认`all`), orderBy 同上

---

## 任务（Task）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/tasks` | 创建任务 |
| GET | `/tasks/{taskID}` | 获取任务详情 |
| PUT | `/tasks/{taskID}` | 修改任务 |
| DELETE | `/tasks/{taskID}` | 删除任务 |
| PUT | `/tasks/{taskID}/start` | 启动任务 |
| PUT | `/tasks/{taskID}/finish` | 完成任务 |
| PUT | `/tasks/{taskID}/close` | 关闭任务 |
| PUT | `/tasks/{taskID}/activate` | 激活任务 |

列表：`/executions/{id}/tasks`

**POST 创建**：**name**(string), **executionID**(int), type(string), assignedTo(string), estStarted(date), deadline(date), pri(int), estimate(float), module(int), story(int), desc(string)

**PUT 修改**：所有字段可选

**PUT start 启动**：**realStarted**(date), assignedTo(string), consumed(float), left(float), comment(string)

**PUT finish 完成**：**currentConsumed**(float), **realStarted**(date), **finishedDate**(date), assignedTo(string), consumed(float), comment(string)

**PUT close 关闭**：comment(string)

**PUT activate 激活**：left(float), assignedTo(string), comment(string)

**GET 列表参数**：status(`all`|`unclosed`|`assignedtome`|`myinvolved`|`assignedbyme`，默认`unclosed`), orderBy(`id`|`name`|`status`+`_asc/_desc`), recPerPage, pageID

---

## 测试用例（Testcase）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/testcases` | 创建测试用例 |
| GET | `/testcases/{caseID}` | 获取测试用例详情 |
| PUT | `/testcases/{testcasID}` | 修改测试用例 |
| DELETE | `/testcases/{testcasID}` | 删除测试用例 |

列表通过父资源获取：`/products/{id}/testcases`, `/projects/{id}/testcases`, `/executions/{id}/testcases`

**POST 创建**：**productID**(int), **title**(string), module(int), story(int), pri(int), type(`unit`|`interface`|`feature`|`install`|`config`|`performance`|`security`|`other`), precondition(string), steps(string[]), expects(string[]), stepType(string[] `step`|`group`), project(int), execution(int)

**PUT 修改**：**title**(string)，其余可选（注意：模块字段名为 `moudule`）

**GET 列表参数**：browseType(`all`|`wait`|`needconfirm`，默认`all`), orderBy(`id`|`title`|`status`或`pri`+`_asc/_desc`), recPerPage, pageID

---

## 产品计划（Productplan）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/productplans` | 创建产品计划 |
| GET | `/productplans/{planID}` | 获取产品计划详情 |
| PUT | `/productplans/{productplanID}` | 修改产品计划 |
| DELETE | `/productplans/{productplanID}` | 删除产品计划 |

列表：`/products/{id}/productplans`

**POST 创建**：**productID**(int), **title**(string), parent(int), begin(date), end(date), branchID(int), desc(string)

**PUT 修改**：**title**(string)，productID 不再必填，其余可选

**GET 列表参数**：browseType(`all`|`undone`|`wait`|`doing`，默认`undone`), orderBy(`id`|`title`|`begin`|`end`|`status`+`_asc/_desc`), recPerPage, pageID

---

## 版本（Build）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/builds` | 创建版本 |
| PUT | `/builds/{buildID}` | 修改版本 |
| DELETE | `/builds/{buildID}` | 删除版本 |

列表：`/projects/{id}/builds`, `/executions/{id}/builds`（无查询参数）

**POST 创建**：**executionID**(int), **product**(int), **name**(string), **system**(int), **builder**(string), **date**(date), scmPath(string), filePath(string), desc(string)

**PUT 修改**：同上但字段名为 **execution**(int)（非 executionID）

---

## 发布（Release）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/releases` | 创建发布 |
| PUT | `/releases/{releasID}` | 修改发布 |
| DELETE | `/releases/{releasID}` | 删除发布 |

列表：`/products/{id}/releases`（无查询参数）

**POST 创建**：**productID**(int), **system**(int), **name**(string), **build**(string[]), **date**(date), status(`wait`|`normal`|`fail`|`terminate`), desc(string)

**PUT 修改**：productID 不再必填，其余同上

> 路径参数名为 `releasID`（非 releaseID）

---

## 测试单（Testtask）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/testtasks` | 创建测试单 |
| PUT | `/testtasks/{testtaskID}` | 修改测试单 |
| DELETE | `/testtasks/{testtaskID}` | 删除测试单 |

列表：`/products/{id}/testtasks`, `/projects/{id}/testtasks`, `/executions/{id}/testtasks`（无查询参数）

**POST 创建**：**productID**(int), **name**(string), **build**(int), **begin**(date), **end**(date), execution(int), type(string[] `integrate`|`system`|`acceptance`|`performance`|`safety`), owner(string), status(`wait`|`doing`|`done`|`blocked`), desc(string)

**PUT 修改**：productID 不再必填，其余同上

---

## 反馈（Feedback）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/feedbacks` | 创建反馈 |
| GET | `/feedbacks/{feedbackID}` | 获取反馈详情 |
| PUT | `/feedbacks/{feedbackID}` | 修改反馈 |
| DELETE | `/feedbacks/{feedbackID}` | 删除反馈 |
| PUT | `/feedbacks/{feedbackID}/close` | 关闭反馈 |
| PUT | `/feedbacks/{feedbackID}/activate` | 激活反馈 |

列表：`/products/{id}/feedbacks`

**POST/PUT**：**product**(int), **title**(string), module(int), type(`story`|`task`|`bug`|`todo`|`advice`|`issue`|`risk`|`opportunity`), desc(string), feedbackBy(string), source(string)

**PUT close 关闭**：**closedReason**(`commented`|`repeat`|`refuse`), comment(string)

**PUT activate 激活**：assignedTo(string), comment(string)

**GET 列表参数**：browseType(`all`|`wait`|`doing`|`toclosed`|`review`|`assigntome`|`openedbyme`，默认`wait`), orderBy(`id`|`title`|`status`+`_asc/_desc`), recPerPage, pageID

---

## 工单（Ticket）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/tickets` | 创建工单 |
| GET | `/tickets/{ticketID}` | 获取工单详情 |
| PUT | `/tickets/{ticketID}` | 修改工单 |
| DELETE | `/tickets/{ticketID}` | 删除工单 |
| PUT | `/tickets/{ticketID}/close` | 关闭工单 |
| PUT | `/tickets/{ticketID}/activate` | 激活工单 |

列表：`/products/{id}/tickets`

**POST 创建**：**product**(int), **title**(string), module(int), type(`code`|`data`|`stuck`|`security`|`affair`), desc(string), assignedTo(string), deadline(date), openedBuild(string[])

**PUT 修改**：所有字段可选

**PUT close 关闭**：**closedReason**(`commented`|`repeat`|`refuse`), **comment**(string)

**PUT activate 激活**：assignedTo(string), comment(string)

**GET 列表参数**：browseType(`all`|`unclosed`|`wait`|`doing`|`done`|`finishedbyme`|`assigntome`|`openedbyme`，默认`wait`), orderBy(`id`|`title`|`status`+`_asc/_desc`), recPerPage, pageID

---

## 应用（System）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/systems` | 创建应用 |
| PUT | `/systems/{systemID}` | 修改应用 |

列表：`/products/{id}/systems`（无查询参数）

**POST 创建**：**productID**(int), **integrated**(int, 0=否 1=是), **children**(string[], 非集成传[]), **name**(string), desc(string)

**PUT 修改**：**name**(string), **children**(string[]), desc(string)

---

## 文件（File）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/files` | 编辑附件名称 |
| DELETE | `/files/{fileID}` | 删除附件 |

**POST**：**fileName**(string)
