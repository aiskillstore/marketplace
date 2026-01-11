---
name: Using `argc` / `Argcfile`
description: Create and modify Argcfiles using the special syntax required. Use this when editing Argcfile.sh, @argc, or any shell script that contains `argc --argc-eval`.
---

# Argc

[Argc](https://github.com/sigoden/argc/) is a Bash command line framework that utilizes a special comment-driven syntax to provide a command runner and argument parser.

Here is a simple Argcfile.sh:

```bash
# @describe Example Argcfile
# Arguments, options, and flags listed here apply to the main command and all
# subcommands.
#
# For more information about argc, see https://github.com/sigoden/argc
# @option    --name  Name to greet
# @flag -F --foo  Flag param
# @option --bar   Option param
# @option --baz*  Option param (multi-occurs)
# @arg val*       Positional param

main() {
    echo foo: $argc_foo
    echo bar: $argc_bar
    echo baz: ${argc_baz[@]}
    echo val: ${argc_val[@]}
}

if ! command -v argc >/dev/null; then
	echo "This command requires argc. Install from https://github.com/sigoden/argc" >&2
	exit 100
fi
eval "$(argc --argc-eval "$0" "$@")"
```

Run the script with some sample arguments:

```bash
./example.sh -F --bar=xyz --baz a --baz b v1 v2
```

Argc parses these arguments and creates variables prefixed with argc_:

```
foo: 1
bar: xyz
baz: a b
val: v1 v2
```

You can also run ./example.sh --help to see the automatically generated help information for your CLI.

## Bash idioms

Prefer using Bash idioms when working with argc. For example, shellcheck isn't aware of the argc_foo variables, so prefer using `${argc_foo:?}` for required values and values where argc is known to provide the default. For others, use `${argc_foo:-default}`, as appropriate.

## Argcfile.sh

Note that running `argc` directly will attempt to locate a file named `Argcfile.sh` in the current and parent directories. In this case, argc will always cd into the directory with the Argcfile before executing it, and `$ARGC_PWD` will be set to the directory the user ran the command from.

## Comment Tags

Comment tags are standard Bash comments prefixed with `@` and a specific tag. They provide instructions to Argc for configuring your script's functionalities.

| Tag         | Description                           |
| :---------- | ------------------------------------- |
| `@describe` | Sets the description for the command. |
| `@cmd`      | Defines a subcommand.                 |
| `@alias`    | Sets aliases for the subcommand.      |
| `@arg`      | Defines a positional argument.        |
| `@option`   | Defines an option argument.           |
| `@flag`     | Defines a flag argument.              |
| `@env`      | Defines an environment variable.      |
| `@meta`     | Adds metadata.                        |

Some common forms:

```
# @arg va
# @arg vb!                        required
# @arg vc*                        multi-values
# @arg vd+                        multi-values + required
# @arg vna <PATH>                 value notation
# @arg vda=a                      default
# @arg vdb=`_default_fn`          default from bash function
# @arg vca[a|b]                   choices
# @arg vcb[=a|b]                  choices + default
# @arg vcc*[a|b]                  multi-values + choice
# @arg vcd+[a|b]                  required + multi-values + choice
# @arg vfa[`_choice_fn`]          choice from bash function
# @arg vfb[?`_choice_fn`]         choice from bash function + no validation
# @arg vfc*[`_choice_fn`]         multi-values + choice from bash function
# @arg vfd*,[`_choice_fn`]        multi-values + choice from bash function + comma-separated list
# @arg vxa~                       capture all remaining args
# @arg vea $$                     bind-env
# @arg veb $BE <PATH>             bind-named-env
# @option    --oa
# @option -b --ob                   short
# @option -c                        short only
# @option    --of*,                 multi-occurs + comma-separated list (also supports all other patterns from @arg)
# @option    --ona <PATH>           value notation
# @option    --onb <FILE> <FILE>    two-args value notations
# @option    --onc <CMD> <FILE+>    unlimited-args value notations
# @option    --oda=a                default
# @option    --odb=`_default_fn`    default from bash function
# @option    --oca[a|b]             choice (supports all patterns from @arg)
# @option    --ofa[`_choice_fn`]    choice from bash function (supports all patterns from @arg)
# @option    --oxa~                 capture all remaining args
# @option    --oea $$               bind-env
# @option    --oeb $BE <PATH>       bind-named-env
# @flag     --fa
# @flag  -b --fb         short
# @flag  -c              short only
# @flag     --fd*        multi-occurs
# @flag     --ea $$      bind-env
# @flag     --eb $BE     bind-named-env
# @env EA                 optional
# @env EB!                required
# @env EC=true            default
# @env EDA[dev|prod]      choices
# @env EDB[=dev|prod]     choices + default
```

For `_choice_fn`, it should print candidates, one per line. `_choice_fn` and `_default_fn` *must* be bash functions, they are not arbitrary commands. "bind-env" means the variable default comes from the environment. For the environment variables, argc does not create argc_ variables (just validates existing variables).

Most common `@meta` options:

- Set a version on the top-level of the script: `@meta version 1.0.0`
- Require tools installed (usable at top-level and subcommands): `@meta require-tools git,yq`

Use `@describe` at the top level of the script and `@cmd` for subcommands. The first line is the short description, and subsequent comment lines that aren't comment tags are the long description.

## Further Documentation

- [Specification](https://github.com/sigoden/argc/blob/main/docs/specification.md) for the grammar and usage of all the comment tags.
- [Variables](https://github.com/sigoden/argc/blob/main/docs/variables.md) that are predefined by argc.
- [Examples](https://github.com/sigoden/argc/tree/main/examples) for particularly complex scenarios.
