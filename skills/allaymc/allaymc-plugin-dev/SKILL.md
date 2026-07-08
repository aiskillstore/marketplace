---
name: allaymc-plugin-dev
description: Create, update and troubleshoot AllayMC plugins in Java or other JVM languages. Use when (1) creating a new AllayMC plugin. (2) migrating an existing plugin to AllayMC. (3) troubleshooting an AllayMC plugin.
license: LGPL-2.1
metadata:
  author: AllayMC
---

# AllayMC Plugin Development

## About AllayMC

AllayMC is a third-party server software for Minecraft: Bedrock Edition written in Java. It provides a set of
APIs for plugins to use. AllayMC is broadly divided into the following two modules:

- api: A set of interfaces provided for plugins.
- server: An implementation of the api. Plugins usually don't have access to it.

## About Plugin

Plugins in AllayMC are just like Bukkit plugins, they are loaded by the server when the server starts. Plugins
are used to extend server functionality.

## Workflow for a new plugin

### 1) Initialize the project

- Use the official template at `references/JavaPluginTemplate` If the user haven't initialize the project.
- If the user has already initialized the project, proceed to the next step.

### 2) Initialize Gradle and plugin metadata

Before you begin, ask the user the following questions:

- What is the name of the plugin?
- What is the package name used by the plugin?
- What is the plugin author(s) name?
- What is the website of the plugin?
- What is the allay-api version used for the plugin?

After the user answers the above questions, initialize the project metadata with the collected information.
Before that, determine whether the user is using `JavaPluginTemplate`, which is implemented by determining whether
the current project package name is `org.allaymc.javaplugintemplate`.

#### Case 1: If the project is using `JavaPluginTemplate`:

- Rename package name from `org.allaymc.javaplugintemplate` to the user provided group name.
- Set the project name in `settings.gradle.kts` to the user provided plugin name.
- Update `build.gradle.kts`, solve all the TODOs inside.

#### Case 2: If the project is not using `JavaPluginTemplate`:

- Update `group`, `version` (should start with `0.1.0`), and `description` in `build.gradle.kts`.
- Keep package of the plugin main class aligned with the value of `group` in `build.gradle.kts`.
- Set the Java toolchain to 21 unless the user needs a different version in `build.gradle.kts`.
- If the project is using `AllayGradle` plugin, update the `allay {}` block in `build.gradle.kts`:
  - Set `api` to the target Allay API version.
  - Set `plugin.entrance` to the fully qualified main class (or short suffix as used in the template).
  - Update `authors` and `website`.
- If the project does not use the `AllayGradle` plugin, create `plugin.json` per the docs in `references/Allay/docs/tutorials/create-your-first-plugin.md`.

### 3) Implement the plugin entry class

- Create the plugin entry class using plugin name and let it extends `org.allaymc.api.plugin.Plugin`
- Override lifecycle methods in the entry class as needed:
  - `onLoad` which is called before world loading.
  - `onEnable` which is called after world loading.
  - `onDisable` which is called when the server is stopping.
- If reloadable behavior is required, override `isReloadable` and implement `reload`.

### 4) Implement the plugin logic

Understand the user's needs and read the documentation and code marked in the reference map below as needed.

### 5) Build and run

- Use `./gradlew runServer` for local testing when the AllayGradle plugin is configured.
- Use `./gradlew shadowJar` to build the shaded jar.

## Reference map

- Allay documents (read on demand): `references/Allay/docs/tutorials` and `references/Allay/docs/advanced`.
- JavaPluginTemplate: `references/JavaPluginTemplate`
- Allay project source: `references/Allay`
  - Allay API: `references/Allay/api/src/main/java/org/allaymc/api`
  - Allay Server (API Implementation): `references/Allay/server/src/main/java/org/allaymc/server`
- AllayGradle project source: `references/AllayGradle`
  - Usage Guide: `references/AllayGradle/README.md`

## Notes

- AllayMC is multithreaded, and special attention should be paid to multithreaded security issues when writing project code.
- AllayMC currently does not use annotations such as JSpecify's `@Nullable`/`@NonNull`. Unless a method's Javadoc explicitly states that
  a parameter or return value may be null, treat it as non-null.
- Don't overwrite defensive code, such as checking if an object that is explicitly marked as impossible null is null. Produce readable, easy-to-maintain code.
