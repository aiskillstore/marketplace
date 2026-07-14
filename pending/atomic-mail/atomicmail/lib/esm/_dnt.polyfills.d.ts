/**
 * Based on [import-meta-ponyfill](https://github.com/gaubee/import-meta-ponyfill),
 * but instead of using npm to install additional dependencies,
 * this approach manually consolidates cjs/mjs/d.ts into a single file.
 *
 * Note that this code might be imported multiple times
 * (for example, both dnt.test.polyfills.ts and dnt.polyfills.ts contain this code;
 *  or Node.js might dynamically clear the cache and then force a require).
 * Therefore, it's important to avoid redundant writes to global objects.
 * Additionally, consider that commonjs is used alongside esm,
 * so the two ponyfill functions are stored independently in two separate global objects.
 */
import { createRequire } from "node:module";
import { type URL } from "node:url";
declare global {
    interface ImportMeta {
        /** A string representation of the fully qualified module URL. When the
         * module is loaded locally, the value will be a file URL (e.g.
         * `file:///path/module.ts`).
         *
         * You can also parse the string as a URL to determine more information about
         * how the current module was loaded. For example to determine if a module was
         * local or not:
         *
         * ```ts
         * const url = new URL(import.meta.url);
         * if (url.protocol === "file:") {
         *   console.log("this module was loaded locally");
         * }
         * ```
         */
        url: string;
        /**
         * A function that returns resolved specifier as if it would be imported
         * using `import(specifier)`.
         *
         * ```ts
         * console.log(import.meta.resolve("./foo.js"));
         * // file:///dev/foo.js
         * ```
         *
         * @param specifier The module specifier to resolve relative to `parent`.
         * @param parent The absolute parent module URL to resolve from.
         * @returns The absolute (`file:`) URL string for the resolved module.
         */
        resolve(specifier: string, parent?: string | URL | undefined): string;
        /** A flag that indicates if the current module is the main module that was
         * called when starting the program under Deno.
         *
         * ```ts
         * if (import.meta.main) {
         *   // this was loaded as the main module, maybe do some bootstrapping
         * }
         * ```
         */
        main: boolean;
        /** The absolute path of the current module.
         *
         * This property is only provided for local modules (ie. using `file://` URLs).
         *
         * Example:
         * ```
         * // Unix
         * console.log(import.meta.filename); // /home/alice/my_module.ts
         *
         * // Windows
         * console.log(import.meta.filename); // C:\alice\my_module.ts
         * ```
         */
        filename: string;
        /** The absolute path of the directory containing the current module.
         *
         * This property is only provided for local modules (ie. using `file://` URLs).
         *
         * * Example:
         * ```
         * // Unix
         * console.log(import.meta.dirname); // /home/alice
         *
         * // Windows
         * console.log(import.meta.dirname); // C:\alice
         * ```
         */
        dirname: string;
    }
}
type NodeRequest = ReturnType<typeof createRequire>;
type NodeModule = NonNullable<NodeRequest["main"]>;
interface ImportMetaPonyfillCommonjs {
    (require: NodeRequest, module: NodeModule): ImportMeta;
}
interface ImportMetaPonyfillEsmodule {
    (importMeta: ImportMeta): ImportMeta;
}
interface ImportMetaPonyfill extends ImportMetaPonyfillCommonjs, ImportMetaPonyfillEsmodule {
}
export declare let import_meta_ponyfill_commonjs: ImportMetaPonyfillCommonjs;
export declare let import_meta_ponyfill_esmodule: ImportMetaPonyfillEsmodule;
export declare let import_meta_ponyfill: ImportMetaPonyfill;
export {};
//# sourceMappingURL=_dnt.polyfills.d.ts.map