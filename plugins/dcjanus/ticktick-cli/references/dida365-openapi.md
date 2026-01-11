# [Dida365 Open API](#/openapi?id=dida365-open-api)

## [Introduction](#/openapi?id=introduction)

Welcome to the Dida365 Open API documentation. Dida365 is a powerful task management application that allows users to easily manage and organize their daily tasks, deadlines, and projects. With Dida365 Open API, developers can integrate Dida365's powerful task management features into their own applications and create a seamless user experience.

## [Getting Started](#/openapi?id=getting-started)

To get started using the Dida365 Open API, you will need to register your application and obtain a client ID and client secret. You can register your application by visiting the [Dida365 Developer Center](https://developer.dida365.com/manage) . Once registered, you will receive a client ID and client secret which you will use to authenticate your requests.

## [Authorization](#/openapi?id=authorization)

### [Get Access Token](#/openapi?id=get-access-token)

In order to call Dida365's Open API, it is necessary to obtain an access token for the corresponding user. Dida365 uses the OAuth2 protocol to obtain the access token.

#### [First Step](#/openapi?id=first-step)

Redirect the user to the Dida365 authorization page, [https://dida365.com/oauth/authorize](https://dida365.com/oauth/authorize) . The required parameters are as follows:

| Name | Description |
| --- | --- |
| client_id | Application unique id |
| scope | Spaces-separated permission scope. The currently available scopes are tasks:write tasks:read |
| state | Passed to redirect url as is |
| redirect_uri | User-configured redirect url |
| response_type | Fixed as code |

Example: [https://dida365.com/oauth/authorize?scope=scope&client_id=client_id&state=state&redirect_uri=redirect_uri&response_type=code](https://dida365.com/oauth/authorize?scope=scope&client_id=client_id&state=state&redirect_uri=redirect_uri&response_type=code)

#### [Second Step](#/openapi?id=second-step)

After the user grants access, Dida365 will redirect the user back to your application's redirect_uri with an authorization code as a query parameter.

| Name | Description |
| --- | --- |
| code | Authorization code for subsequent access tokens |
| state | state parameter passed in the first step |

#### [Third Step](#/openapi?id=third-step)

To exchange the authorization code for an access token, make a POST request to https://dida365.com/oauth/token with the following parameters(Content-Type: application/x-www-form-urlencoded):

| Name | Description |
| --- | --- |
| client_id | The username is located in the HEADER using the Basic Auth authentication method |
| client_secret | The password is located in the HEADER using the Basic Auth authentication method |
| code | The code obtained in the second step |
| grant_type | grant type, now only authorization_code |
| scope | spaces-separated permission scope. The currently available scopes are tasks: write, tasks: read |
| redirect_uri | user-configured redirect url |

Access_token for openapi request authentication in the request response

```
 {
...
"access_token": "access token value"
...
}
```

#### [Request OpenAPI](#/openapi?id=request-openapi)

Set Authorization in the header, the value is Bearer access token value

```
Authorization: Bearer e*****b
```

## [API Reference](#/openapi?id=api-reference)

The Dida365 Open API provides a RESTful interface for accessing and managing user tasks, lists, and other related resources. The API is based on the standard HTTP protocol and supports JSON data formats.

### [Task](#/openapi?id=task)

#### [Get Task By Project ID And Task ID](#/openapi?id=get-task-by-project-id-and-task-id)

```
GET /open/v1/project/{projectId}/task/{taskId}
```

##### [Parameters](#/openapi?id=parameters)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Path | projectId required | Project identifier | string |
| Path | taskId required | Task identifier | string |

##### [Responses](#/openapi?id=responses)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | Task |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example)

###### [Request](#/openapi?id=request)

```
GET /open/v1/project/{{projectId}}/task/{{taskId}} HTTP/1.1
Host: api.dida365.com
Authorization: Bearer {{token}}
```

###### [Response](#/openapi?id=response)

```
{
"id" : "63b7bebb91c0a5474805fcd4",
"isAllDay" : true,
"projectId" : "6226ff9877acee87727f6bca",
"title" : "Task Title",
"content" : "Task Content",
"desc" : "Task Description",
"timeZone" : "America/Los_Angeles",
"repeatFlag" : "RRULE:FREQ=DAILY;INTERVAL=1",
"startDate" : "2019-11-13T03:00:00+0000",
"dueDate" : "2019-11-14T03:00:00+0000",
"reminders" : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ],
"priority" : 1,
"status" : 0,
"completedTime" : "2019-11-13T03:00:00+0000",
"sortOrder" : 12345,
"items" : [ {
    "id" : "6435074647fd2e6387145f20",
    "status" : 0,
    "title" : "Item Title",
    "sortOrder" : 12345,
    "startDate" : "2019-11-13T03:00:00+0000",
    "isAllDay" : false,
    "timeZone" : "America/Los_Angeles",
    "completedTime" : "2019-11-13T03:00:00+0000"
    } ]
}
```

#### [Create Task](#/openapi?id=create-task)

```
POST /open/v1/task
```

##### [Parameters](#/openapi?id=parameters-1)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Body | title required | Task title | string |
| Body | projectId required | Project id | string |
| Body | content | Task content | string |
| Body | desc | Description of checklist | string |
| Body | isAllDay | All day | boolean |
| Body | startDate | Start date and time in "yyyy-MM-dd'T'HH:mm:ssZ" format Example : "2019-11-13T03:00:00+0000" | date |
| Body | dueDate | Due date and time in "yyyy-MM-dd'T'HH:mm:ssZ" format Example : "2019-11-13T03:00:00+0000" | date |
| Body | timeZone | The time zone in which the time is specified | String |
| Body | reminders | Lists of reminders specific to the task | list |
| Body | repeatFlag | Recurring rules of task | string |
| Body | priority | The priority of task, default is "0" | integer |
| Body | sortOrder | The order of task | integer |
| Body | items | The list of subtasks | list |
| Body | items.title | Subtask title | string |
| Body | items.startDate | Start date and time in "yyyy-MM-dd'T'HH:mm:ssZ" format | date |
| Body | items.isAllDay | All day | boolean |
| Body | items.sortOrder | The order of subtask | integer |
| Body | items.timeZone | The time zone in which the Start time is specified | string |
| Body | items.status | The completion status of subtask | integer |
| Body | items.completedTime | Completed time in "yyyy-MM-dd'T'HH:mm:ssZ" format Example : "2019-11-13T03:00:00+0000" | date |

##### [Responses](#/openapi?id=responses-1)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | Task |
| 201 | Created | No Content |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-1)

###### [Request](#/openapi?id=request-1)

```
POST /open/v1/task HTTP/1.1
Host: api.dida365.com
Content-Type: application/json
Authorization: Bearer {{token}}
{
    ...
    "title":"Task Title",
    "projectId":"6226ff9877acee87727f6bca"
    ...
}
```

###### [Response](#/openapi?id=response-1)

```
{
"id" : "63b7bebb91c0a5474805fcd4",
"projectId" : "6226ff9877acee87727f6bca",
"title" : "Task Title",
"content" : "Task Content",
"desc" : "Task Description",
"isAllDay" : true,
"startDate" : "2019-11-13T03:00:00+0000",
"dueDate" : "2019-11-14T03:00:00+0000",
"timeZone" : "America/Los_Angeles",
"reminders" : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ],
"repeatFlag" : "RRULE:FREQ=DAILY;INTERVAL=1",
"priority" : 1,
"status" : 0,
"completedTime" : "2019-11-13T03:00:00+0000",
"sortOrder" : 12345,
"items" : [ {
    "id" : "6435074647fd2e6387145f20",
    "status" : 1,
    "title" : "Subtask Title",
    "sortOrder" : 12345,
    "startDate" : "2019-11-13T03:00:00+0000",
    "isAllDay" : false,
    "timeZone" : "America/Los_Angeles",
    "completedTime" : "2019-11-13T03:00:00+0000"
    } ]
}
```


#### [Update Task](#/openapi?id=update-task)

```
POST /open/v1/task/{taskId}
```

##### [Parameters](#/openapi?id=parameters-2)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Path | taskId required | Task identifier | string |
| Body | id required | Task id. | string |
| Body | projectId required | Project id. | string |
| Body | title | Task title | string |
| Body | content | Task content | string |
| Body | desc | Description of checklist | string |
| Body | isAllDay | All day | boolean |
| Body | startDate | Start date and time in "yyyy-MM-dd'T'HH:mm:ssZ" format Example : "2019-11-13T03:00:00+0000" | date |
| Body | dueDate | Due date and time in "yyyy-MM-dd'T'HH:mm:ssZ" format Example : "2019-11-13T03:00:00+0000" | date |
| Body | timeZone | The time zone in which the time is specified | String |
| Body | reminders | Lists of reminders specific to the task | list |
| Body | repeatFlag | Recurring rules of task | string |
| Body | priority | The priority of task, default is "normal" | integer |
| Body | sortOrder | The order of task | integer |
| Body | items | The list of subtasks | list |
| Body | items.title | Subtask title | string |
| Body | items.startDate | Start date and time in "yyyy-MM-dd'T'HH:mm:ssZ" format | date |
| Body | items.isAllDay | All day | boolean |
| Body | items.sortOrder | The order of subtask | integer |
| Body | items.timeZone | The time zone in which the Start time is specified | string |
| Body | items.status | The completion status of subtask | integer |
| Body | items.completedTime | Completed time in "yyyy-MM-dd'T'HH:mm:ssZ" format Example : "2019-11-13T03:00:00+0000" | date |

##### [Responses](#/openapi?id=responses-2)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | Task |
| 201 | Created | No Content |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-2)

###### [Request](#/openapi?id=request-2)

```
POST /open/v1/task/{{taskId}} HTTP/1.1
Host: api.dida365.com
Content-Type: application/json
Authorization: Bearer {{token}}
{
    "id": "{{taskId}}",
    "projectId": "{{projectId}}",
    "title": "Task Title",
    "priority": 1,
    ...
}
```

###### [Response](#/openapi?id=response-2)

```
{
"id" : "63b7bebb91c0a5474805fcd4",
"projectId" : "6226ff9877acee87727f6bca",
"title" : "Task Title",
"content" : "Task Content",
"desc" : "Task Description",
"isAllDay" : true,
"startDate" : "2019-11-13T03:00:00+0000",
"dueDate" : "2019-11-14T03:00:00+0000",
"timeZone" : "America/Los_Angeles",
"reminders" : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ],
"repeatFlag" : "RRULE:FREQ=DAILY;INTERVAL=1",
"priority" : 1,
"status" : 0,
"completedTime" : "2019-11-13T03:00:00+0000",
"sortOrder" : 12345,
"items" : [ {
    "id" : "6435074647fd2e6387145f20",
    "status" : 1,
    "title" : "Item Title",
    "sortOrder" : 12345,
    "startDate" : "2019-11-13T03:00:00+0000",
    "isAllDay" : false,
    "timeZone" : "America/Los_Angeles",
    "completedTime" : "2019-11-13T03:00:00+0000"
    } ],
"kind": "CHECKLIST"
}
```


#### [Complete Task](#/openapi?id=complete-task)

```
POST /open/v1/project/{projectId}/task/{taskId}/complete
```

##### [Parameters](#/openapi?id=parameters-3)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Path | projectId required | Project identifier | string |
| Path | taskId required | Task identifier | string |

##### [Responses](#/openapi?id=responses-3)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | No Content |
| 201 | Created | No Content |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-3)

###### [Request](#/openapi?id=request-3)

```
POST /open/v1/project/{{projectId}}/task/{{taskId}}/complete HTTP/1.1
Host: api.dida365.com
Authorization: Bearer {{token}}
```

#### [Delete Task](#/openapi?id=delete-task)

```
DELETE /open/v1/project/{projectId}/task/{taskId}
```

##### [Parameters](#/openapi?id=parameters-4)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Path | projectId required | Project identifier | string |
| Path | taskId required | Task identifier | string |

##### [Responses](#/openapi?id=responses-4)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | No Content |
| 201 | Created | No Content |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-4)

###### [Request](#/openapi?id=request-4)

```
DELETE /open/v1/project/{{projectId}}/task/{{taskId}} HTTP/1.1
Host: api.dida365.com
Authorization: Bearer {{token}}
```

### [Project](#/openapi?id=project)

#### [Get User Project](#/openapi?id=get-user-project)

```
GET /open/v1/project
```

##### [Responses](#/openapi?id=responses-5)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | < Project > array |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-5)

###### [Request](#/openapi?id=request-5)

```
GET /open/v1/project HTTP/1.1
Host: api.dida365.com
Authorization: Bearer {{token}}
```

###### [Response](#/openapi?id=response-3)

```
[{
"id": "6226ff9877acee87727f6bca",
"name": "project name",
"color": "#F18181",
"closed": false,
"groupId": "6436176a47fd2e05f26ef56e",
"viewMode": "list",
"permission": "write",
"kind": "TASK"
}]
```

#### [Get Project By ID](#/openapi?id=get-project-by-id)

```
GET /open/v1/project/{projectId}
```

##### [Parameters](#/openapi?id=parameters-5)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Path | project required | Project identifier | string |

##### [Responses](#/openapi?id=responses-6)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | Project |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-6)

###### [Request path](#/openapi?id=request-path)

```
GET /open/v1/project/{{projectId}} HTTP/1.1
Host: api.dida365.com
Authorization: Bearer {{token}}
```

###### [Response](#/openapi?id=response-4)

```
{
    "id": "6226ff9877acee87727f6bca",
    "name": "project name",
    "color": "#F18181",
    "closed": false,
    "groupId": "6436176a47fd2e05f26ef56e",
    "viewMode": "list",
    "kind": "TASK"
}
```

#### [Get Project With Data](#/openapi?id=get-project-with-data)

```
GET /open/v1/project/{projectId}/data
```

##### [Parameters](#/openapi?id=parameters-6)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Path | projectId required | Project identifier | string |

##### [Responses](#/openapi?id=responses-7)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | ProjectData |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-7)

###### [Request](#/openapi?id=request-6)

```
GET /open/v1/project/{{projectId}}/data HTTP/1.1
Host: api.dida365.com
Authorization: Bearer {{token}}
```

###### [Response](#/openapi?id=response-5)

```
{
"project": {
    "id": "6226ff9877acee87727f6bca",
    "name": "project name",
    "color": "#F18181",
    "closed": false,
    "groupId": "6436176a47fd2e05f26ef56e",
    "viewMode": "list",
    "kind": "TASK"
},
"tasks": [{
    "id": "6247ee29630c800f064fd145",
    "isAllDay": true,
    "projectId": "6226ff9877acee87727f6bca",
    "title": "Task Title",
    "content": "Task Content",
    "desc": "Task Description",
    "timeZone": "America/Los_Angeles",
    "repeatFlag": "RRULE:FREQ=DAILY;INTERVAL=1",
    "startDate": "2019-11-13T03:00:00+0000",
    "dueDate": "2019-11-14T03:00:00+0000",
    "reminders": [
        "TRIGGER:P0DT9H0M0S",
        "TRIGGER:PT0S"
    ],
    "priority": 1,
    "status": 0,
    "completedTime": "2019-11-13T03:00:00+0000",
    "sortOrder": 12345,
    "items": [{
        "id": "6435074647fd2e6387145f20",
        "status": 0,
        "title": "Subtask Title",
        "sortOrder": 12345,
        "startDate": "2019-11-13T03:00:00+0000",
        "isAllDay": false,
        "timeZone": "America/Los_Angeles",
        "completedTime": "2019-11-13T03:00:00+0000"
    }]
}],
"columns": [{
    "id": "6226ff9e76e5fc39f2862d1b",
    "projectId": "6226ff9877acee87727f6bca",
    "name": "Column Name",
    "sortOrder": 0
}]
}
```

#### [Create Project](#/openapi?id=create-project)

```
POST /open/v1/project
```

##### [Parameters](#/openapi?id=parameters-7)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Body | name required | name of the project | string |
| Body | color | color of project, eg. "#F18181" | string |
| Body | sortOrder | sort order value of the project | integer (int64) |
| Body | viewMode | view mode, "list", "kanban", "timeline" | string |
| Body | kind | project kind, "TASK", "NOTE" | string |

##### [Responses](#/openapi?id=responses-8)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | Project |
| 201 | Created | No Content |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-8)

###### [Request](#/openapi?id=request-7)

```
POST /open/v1/project HTTP/1.1
Host: api.dida365.com
Content-Type: application/json
Authorization: Bearer {{token}}
{
    "name": "project name",
    "color": "#F18181",
    "viewMode": "list",
    "kind": "task"
}
```

###### [Response](#/openapi?id=response-6)

```
{
"id": "6226ff9877acee87727f6bca",
"name": "project name",
"color": "#F18181",
"sortOrder": 0,
"viewMode": "list",
"kind": "TASK"
}
```

#### [Update Project](#/openapi?id=update-project)

```
POST /open/v1/project/{projectId}
```

##### [Parameters](#/openapi?id=parameters-8)

| Type | Parameter | Description | Schema |
| --- | --- | --- | --- |
| Path | projectId required | project identifier | string |
| Body | name | name of the project | string |
| Body | color | color of the project | string |
| Body | sortOrder | sort order value, default 0 | integer (int64) |
| Body | viewMode | view mode, "list", "kanban", "timeline" | string |
| Body | kind | project kind, "TASK", "NOTE" | string |

##### [Responses](#/openapi?id=responses-9)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | Project |
| 201 | Created | No Content |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-9)

###### [Request](#/openapi?id=request-8)

```
POST /open/v1/project/{{projectId}} HTTP/1.1
Host: api.dida365.com
Content-Type: application/json
Authorization: Bearer {{token}}

{
    "name": "Project Name",
    "color": "#F18181",
    "viewMode": "list",
    "kind": "TASK"
}
```

###### [Response](#/openapi?id=response-7)

```
{
"id": "6226ff9877acee87727f6bca",
"name": "Project Name",
"color": "#F18181",
"sortOrder": 0,
"viewMode": "list",
"kind": "TASK"
}
```

#### [Delete Project](#/openapi?id=delete-project)

```
DELETE /open/v1/project/{projectId}
```

##### [Parameters](#/openapi?id=parameters-9)

| Type | Name | Description | Schema |
| --- | --- | --- | --- |
| Path | projectId required | Project identifier | string |

##### [Responses](#/openapi?id=responses-10)

| HTTP Code | Description | Schema |
| --- | --- | --- |
| 200 | OK | No Content |
| 401 | Unauthorized | No Content |
| 403 | Forbidden | No Content |
| 404 | Not Found | No Content |

##### [Example](#/openapi?id=example-10)

###### [Request](#/openapi?id=request-9)

```
DELETE /open/v1/project/{{projectId}} HTTP/1.1
Host: api.dida365.com
Authorization: Bearer {{token}}
```

## [Definitions](#/openapi?id=definitions)

### [ChecklistItem](#/openapi?id=checklistitem)

| Name | Description | Schema |
| --- | --- | --- |
| id | Subtask identifier | string |
| title | Subtask title | string |
| status | The completion status of subtask Value : Normal: 0 , Completed: 1 | integer (int32) |
| completedTime | Subtask completed time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000" | string (date-time) |
| isAllDay | All day | boolean |
| sortOrder | Subtask sort order Example : 234444 | integer (int64) |
| startDate | Subtask start date time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000" | string (date-time) |
| timeZone | Subtask timezone Example : "America/Los_Angeles" | string |

### [Task](#/openapi?id=task-1)

| Name | Description | Schema |
| --- | --- | --- |
| id | Task identifier | string |
| projectId | Task project id | string |
| title | Task title | string |
| isAllDay | All day | boolean |
| completedTime | Task completed time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000" | string (date-time) |
| content | Task content | string |
| desc | Task description of checklist | string |
| dueDate | Task due date time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000" | string (date-time) |
| items | Subtasks of Task | < ChecklistItem > array |
| priority | Task priority Value : None: 0 , Low: 1 , Medium: 3 , High 5 | integer (int32) |
| reminders | List of reminder triggers Example : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ] | < string > array |
| repeatFlag | Recurring rules of task Example : "RRULE:FREQ=DAILY;INTERVAL=1" | string |
| sortOrder | Task sort order Example : 12345 | integer (int64) |
| startDate | Start date time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000" | string (date-time) |
| status | Task completion status Value : Normal: 0 , Completed: 2 | integer (int32) |
| timeZone | Task timezone Example : "America/Los_Angeles" | string |
| kind | "TEXT", "NOTE", "CHECKLIST" | string |

### [Project](#/openapi?id=project-1)

| Name | Description | Schema |
| --- | --- | --- |
| id | Project identifier | string |
| name | Project name | string |
| color | Project color | string |
| sortOrder | Order value | integer (int64) |
| closed | Projcet closed | boolean |
| groupId | Project group identifier | string |
| viewMode | view mode, "list", "kanban", "timeline" | string |
| permission | "read", "write" or "comment" | string |
| kind | "TASK" or "NOTE" | string |

### [Column](#/openapi?id=column)

| Name | Description | Schema |
| --- | --- | --- |
| id | Column identifier | string |
| projectId | Project identifier | string |
| name | Column name | string |
| sortOrder | Order value | integer (int64) |

### [ProjectData](#/openapi?id=projectdata)

| Name | Description | Schema |
| --- | --- | --- |
| project | Project info | Project |
| tasks | Undone tasks under project | < Task > array |
| columns | Columns under project | < Column > array |

## [Feedback and Support](#/openapi?id=feedback-and-support)

If you have any questions or feedback regarding the Dida365 Open API documentation, please contact us at [support@dida365.com](mailto:support@dida365.com) . We appreciate your input and will work to address any concerns or issues as quickly as possible. Thank you for choosing Dida!
