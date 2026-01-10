# MCP Server Tools

*22 tools available*

## `browser_close`

Close the page

*Flags: destructive*

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_resize`

Resize the browser window

*Flags: destructive*

### Parameters

- **`width`** (`number`) *(required)*: Width of the browser window
- **`height`** (`number`) *(required)*: Height of the browser window

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "width": {
      "type": "number",
      "description": "Width of the browser window"
    },
    "height": {
      "type": "number",
      "description": "Height of the browser window"
    }
  },
  "required": [
    "width",
    "height"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_console_messages`

Returns all console messages

*Flags: read-only*

### Parameters

- **`level`** (`string`): Level of the console messages to return. Each level includes the messages of more severe levels. Defaults to "info".

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "level": {
      "type": "string",
      "enum": [
        "error",
        "warning",
        "info",
        "debug"
      ],
      "default": "info",
      "description": "Level of the console messages to return. Each level includes the messages of more severe levels. Defaults to \"info\"."
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_handle_dialog`

Handle a dialog

*Flags: destructive*

### Parameters

- **`accept`** (`boolean`) *(required)*: Whether to accept the dialog.
- **`promptText`** (`string`): The text of the prompt in case of a prompt dialog.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "accept": {
      "type": "boolean",
      "description": "Whether to accept the dialog."
    },
    "promptText": {
      "type": "string",
      "description": "The text of the prompt in case of a prompt dialog."
    }
  },
  "required": [
    "accept"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_evaluate`

Evaluate JavaScript expression on page or element

*Flags: destructive*

### Parameters

- **`function`** (`string`) *(required)*: () => { /* code */ } or (element) => { /* code */ } when element is provided
- **`element`** (`string`): Human-readable element description used to obtain permission to interact with the element
- **`ref`** (`string`): Exact target element reference from the page snapshot

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "function": {
      "type": "string",
      "description": "() => { /* code */ } or (element) => { /* code */ } when element is provided"
    },
    "element": {
      "type": "string",
      "description": "Human-readable element description used to obtain permission to interact with the element"
    },
    "ref": {
      "type": "string",
      "description": "Exact target element reference from the page snapshot"
    }
  },
  "required": [
    "function"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_file_upload`

Upload one or multiple files

*Flags: destructive*

### Parameters

- **`paths`** (`array`): The absolute paths to the files to upload. Can be single file or multiple files. If omitted, file chooser is cancelled.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "paths": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "The absolute paths to the files to upload. Can be single file or multiple files. If omitted, file chooser is cancelled."
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_fill_form`

Fill multiple form fields

*Flags: destructive*

### Parameters

- **`fields`** (`array`) *(required)*: Fields to fill in

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "fields": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Human-readable field name"
          },
          "type": {
            "type": "string",
            "enum": [
              "textbox",
              "checkbox",
              "radio",
              "combobox",
              "slider"
            ],
            "description": "Type of the field"
          },
          "ref": {
            "type": "string",
            "description": "Exact target field reference from the page snapshot"
          },
          "value": {
            "type": "string",
            "description": "Value to fill in the field. If the field is a checkbox, the value should be `true` or `false`. If the field is a combobox, the value should be the text of the option."
          }
        },
        "required": [
          "name",
          "type",
          "ref",
          "value"
        ],
        "additionalProperties": false
      },
      "description": "Fields to fill in"
    }
  },
  "required": [
    "fields"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_install`

Install the browser specified in the config. Call this if you get an error about the browser not being installed.

*Flags: destructive*

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_press_key`

Press a key on the keyboard

*Flags: destructive*

### Parameters

- **`key`** (`string`) *(required)*: Name of the key to press or a character to generate, such as `ArrowLeft` or `a`

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string",
      "description": "Name of the key to press or a character to generate, such as `ArrowLeft` or `a`"
    }
  },
  "required": [
    "key"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_type`

Type text into editable element

*Flags: destructive*

### Parameters

- **`element`** (`string`) *(required)*: Human-readable element description used to obtain permission to interact with the element
- **`ref`** (`string`) *(required)*: Exact target element reference from the page snapshot
- **`text`** (`string`) *(required)*: Text to type into the element
- **`submit`** (`boolean`): Whether to submit entered text (press Enter after)
- **`slowly`** (`boolean`): Whether to type one character at a time. Useful for triggering key handlers in the page. By default entire text is filled in at once.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "element": {
      "type": "string",
      "description": "Human-readable element description used to obtain permission to interact with the element"
    },
    "ref": {
      "type": "string",
      "description": "Exact target element reference from the page snapshot"
    },
    "text": {
      "type": "string",
      "description": "Text to type into the element"
    },
    "submit": {
      "type": "boolean",
      "description": "Whether to submit entered text (press Enter after)"
    },
    "slowly": {
      "type": "boolean",
      "description": "Whether to type one character at a time. Useful for triggering key handlers in the page. By default entire text is filled in at once."
    }
  },
  "required": [
    "element",
    "ref",
    "text"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_navigate`

Navigate to a URL

*Flags: destructive*

### Parameters

- **`url`** (`string`) *(required)*: The URL to navigate to

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "The URL to navigate to"
    }
  },
  "required": [
    "url"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_navigate_back`

Go back to the previous page

*Flags: destructive*

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_network_requests`

Returns all network requests since loading the page

*Flags: read-only*

### Parameters

- **`includeStatic`** (`boolean`): Whether to include successful static resources like images, fonts, scripts, etc. Defaults to false.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "includeStatic": {
      "type": "boolean",
      "default": false,
      "description": "Whether to include successful static resources like images, fonts, scripts, etc. Defaults to false."
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_run_code`

Run Playwright code snippet

*Flags: destructive*

### Parameters

- **`code`** (`string`) *(required)*: A JavaScript function containing Playwright code to execute. It will be invoked with a single argument, page, which you can use for any page interaction. For example: `async (page) => { await page.getByRole('button', { name: 'Submit' }).click(); return await page.title(); }`

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "description": "A JavaScript function containing Playwright code to execute. It will be invoked with a single argument, page, which you can use for any page interaction. For example: `async (page) => { await page.getByRole('button', { name: 'Submit' }).click(); return await page.title(); }`"
    }
  },
  "required": [
    "code"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_take_screenshot`

Take a screenshot of the current page. You can't perform actions based on the screenshot, use browser_snapshot for actions.

*Flags: read-only*

### Parameters

- **`type`** (`string`): Image format for the screenshot. Default is png.
- **`filename`** (`string`): File name to save the screenshot to. Defaults to `page-{timestamp}.{png|jpeg}` if not specified. Prefer relative file names to stay within the output directory.
- **`element`** (`string`): Human-readable element description used to obtain permission to screenshot the element. If not provided, the screenshot will be taken of viewport. If element is provided, ref must be provided too.
- **`ref`** (`string`): Exact target element reference from the page snapshot. If not provided, the screenshot will be taken of viewport. If ref is provided, element must be provided too.
- **`fullPage`** (`boolean`): When true, takes a screenshot of the full scrollable page, instead of the currently visible viewport. Cannot be used with element screenshots.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "type": {
      "type": "string",
      "enum": [
        "png",
        "jpeg"
      ],
      "default": "png",
      "description": "Image format for the screenshot. Default is png."
    },
    "filename": {
      "type": "string",
      "description": "File name to save the screenshot to. Defaults to `page-{timestamp}.{png|jpeg}` if not specified. Prefer relative file names to stay within the output directory."
    },
    "element": {
      "type": "string",
      "description": "Human-readable element description used to obtain permission to screenshot the element. If not provided, the screenshot will be taken of viewport. If element is provided, ref must be provided too."
    },
    "ref": {
      "type": "string",
      "description": "Exact target element reference from the page snapshot. If not provided, the screenshot will be taken of viewport. If ref is provided, element must be provided too."
    },
    "fullPage": {
      "type": "boolean",
      "description": "When true, takes a screenshot of the full scrollable page, instead of the currently visible viewport. Cannot be used with element screenshots."
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_snapshot`

Capture accessibility snapshot of the current page, this is better than screenshot

*Flags: read-only*

### Parameters

- **`filename`** (`string`): Save snapshot to markdown file instead of returning it in the response.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "filename": {
      "type": "string",
      "description": "Save snapshot to markdown file instead of returning it in the response."
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_click`

Perform click on a web page

*Flags: destructive*

### Parameters

- **`element`** (`string`) *(required)*: Human-readable element description used to obtain permission to interact with the element
- **`ref`** (`string`) *(required)*: Exact target element reference from the page snapshot
- **`doubleClick`** (`boolean`): Whether to perform a double click instead of a single click
- **`button`** (`string`): Button to click, defaults to left
- **`modifiers`** (`array`): Modifier keys to press

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "element": {
      "type": "string",
      "description": "Human-readable element description used to obtain permission to interact with the element"
    },
    "ref": {
      "type": "string",
      "description": "Exact target element reference from the page snapshot"
    },
    "doubleClick": {
      "type": "boolean",
      "description": "Whether to perform a double click instead of a single click"
    },
    "button": {
      "type": "string",
      "enum": [
        "left",
        "right",
        "middle"
      ],
      "description": "Button to click, defaults to left"
    },
    "modifiers": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "Alt",
          "Control",
          "ControlOrMeta",
          "Meta",
          "Shift"
        ]
      },
      "description": "Modifier keys to press"
    }
  },
  "required": [
    "element",
    "ref"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_drag`

Perform drag and drop between two elements

*Flags: destructive*

### Parameters

- **`startElement`** (`string`) *(required)*: Human-readable source element description used to obtain the permission to interact with the element
- **`startRef`** (`string`) *(required)*: Exact source element reference from the page snapshot
- **`endElement`** (`string`) *(required)*: Human-readable target element description used to obtain the permission to interact with the element
- **`endRef`** (`string`) *(required)*: Exact target element reference from the page snapshot

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "startElement": {
      "type": "string",
      "description": "Human-readable source element description used to obtain the permission to interact with the element"
    },
    "startRef": {
      "type": "string",
      "description": "Exact source element reference from the page snapshot"
    },
    "endElement": {
      "type": "string",
      "description": "Human-readable target element description used to obtain the permission to interact with the element"
    },
    "endRef": {
      "type": "string",
      "description": "Exact target element reference from the page snapshot"
    }
  },
  "required": [
    "startElement",
    "startRef",
    "endElement",
    "endRef"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_hover`

Hover over element on page

*Flags: destructive*

### Parameters

- **`element`** (`string`) *(required)*: Human-readable element description used to obtain permission to interact with the element
- **`ref`** (`string`) *(required)*: Exact target element reference from the page snapshot

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "element": {
      "type": "string",
      "description": "Human-readable element description used to obtain permission to interact with the element"
    },
    "ref": {
      "type": "string",
      "description": "Exact target element reference from the page snapshot"
    }
  },
  "required": [
    "element",
    "ref"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_select_option`

Select an option in a dropdown

*Flags: destructive*

### Parameters

- **`element`** (`string`) *(required)*: Human-readable element description used to obtain permission to interact with the element
- **`ref`** (`string`) *(required)*: Exact target element reference from the page snapshot
- **`values`** (`array`) *(required)*: Array of values to select in the dropdown. This can be a single value or multiple values.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "element": {
      "type": "string",
      "description": "Human-readable element description used to obtain permission to interact with the element"
    },
    "ref": {
      "type": "string",
      "description": "Exact target element reference from the page snapshot"
    },
    "values": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Array of values to select in the dropdown. This can be a single value or multiple values."
    }
  },
  "required": [
    "element",
    "ref",
    "values"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_tabs`

List, create, close, or select a browser tab.

*Flags: destructive*

### Parameters

- **`action`** (`string`) *(required)*: Operation to perform
- **`index`** (`number`): Tab index, used for close/select. If omitted for close, current tab is closed.

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "list",
        "new",
        "close",
        "select"
      ],
      "description": "Operation to perform"
    },
    "index": {
      "type": "number",
      "description": "Tab index, used for close/select. If omitted for close, current tab is closed."
    }
  },
  "required": [
    "action"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

## `browser_wait_for`

Wait for text to appear or disappear or a specified time to pass

*Flags: read-only*

### Parameters

- **`time`** (`number`): The time to wait in seconds
- **`text`** (`string`): The text to wait for
- **`textGone`** (`string`): The text to wait for to disappear

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "time": {
      "type": "number",
      "description": "The time to wait in seconds"
    },
    "text": {
      "type": "string",
      "description": "The text to wait for"
    },
    "textGone": {
      "type": "string",
      "description": "The text to wait for to disappear"
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

