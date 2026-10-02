# Reserved Keywords

Motoko's reserved words. **None** of these may be used as an identifier — not as a variable, parameter, function, type, field, or label name. Check a name against this list before declaring it, especially when a domain term happens to collide (`query`, `label`, `system`, `object`, `class`, `type`, and `in` are the ones that bite most often).

```text
actor        and          assert       async        await
break        case         catch        class        composite
continue     debug        debug_show   do           else
false        finally      flexible     for          from_candid
func         if           ignore       implicit     import
in           include      label        let          loop
mixin        module       not          null         object
or           persistent   private      public       query
return       shared       stable       switch       system
throw        to_candid    transient    true         try
type         var          while        with
```

`async*`, `await*`, and `await?` are also reserved. They cannot collide with an identifier anyway, since `*` and `?` are not identifier characters.

Using a reserved word as an identifier is a parse error at the declaration:

```text
syntax error [M0001], unexpected token '<name>', expected one of token or <phrase> sequence: ...
```

Rename the colliding term rather than relying on position or inferred meaning — there is no escaping or quoting mechanism. Conventional renames: `query` → `request` / `searchTerm`, `label` → `caption` / `tag`, `type` → `kind` / `category`, `object` → `item` / `entity`, `class` → `group` / `kind`.

## Not reserved

These read like keywords but are ordinary identifiers in Motoko — several are Candid keywords rather than Motoko ones, which is the usual source of confusion:

```text
blob    bool    char    int     nat     opt     record  service
struct  variant vec     enum    match   state   result  status
```
