# Users and groups

Read when a Domain owns people who sign in, invites existing business users, or assigns group access.
Shell owns the shared User/Group contract; the business Domain owns its concrete users and their lifecycle.

## Prerequisites

Use compatible Shell and SDK packages, with Shell installed on the target instance. This guide uses
static `User.invite`, `Group.assignMember`/`unassignMember`, and registration of existing nodes. Check the
installed callable contracts before running examples; coordinate dependency upgrades using `migration.md`.

## One business user, three separate transitions

```text
create Employee extends Shell.User → same node, initially without Authentication
  ├─ invite through Shell → invitee signs in → Admin registers their own proof → assures Core member
  └─ register directly with user proof → explicitly assign the intended groups
```

- Extend `Shell.User` for a sign-in-capable business person; do not create a second Shell User beside
  Employee. Mere contacts need not become identities. Add business properties to the concrete subclass.
- Create through the Domain's ordinary Mutation, without `iss`/`sub`. Register attaches Authentication
  to that existing node; it does not create the person, change their profile, or assign a group.
- Shell.User does not declare `displayName` or `email`; the business Class may add them when needed.
  These are profile data, not authentication evidence. Editing an email does not change the bound
  identity; invitation destination is an explicit, separate argument.

## Allow Shell to traverse the membership endpoints

Shell maintains membership using its own authority. Grant `traverse` on each participating concrete
User and Group Class, not `read` of their profiles. An inaccessible endpoint must not look like absent membership.

This combined example represents separate Schema owner files; normal imports between owners are abbreviated.
It covers direct subclasses of Shell.User/Group, not arbitrary inheritance depth.

```ts
import { ShellSchema, S } from '@astrale-domains/shell'
import { K, KernelSchema, classIcon, defineSchema, nodeClass, policy } from '@astrale-os/sdk/schema'
import { UserRound, Users } from '@astrale-os/sdk/schema/icons'
import { z } from 'zod'

// schema/policies/shell-may-traverse-member.ts
export const shellMayTraverseMember = policy({
  description: 'Shell may traverse our direct User/Group subclasses to maintain membership.',
  match: ({ allOf, anyOf, sameNode, exists, object, ref, subject }) =>
    exists(({ node }) => {
      const concrete = node()
      const base = node()
      return allOf(
        { source: object, class: K.classes.instance_of.ref, target: concrete },
        { source: concrete, class: K.classes.extends.ref, target: base },
        { source: base, class: K.classes.of_domain.ref, target: subject },
        anyOf(sameNode(base, ref(S.classes.User.ref)), sameNode(base, ref(S.classes.Group.ref))),
      )
    }),
})

// schema/modules/employee/classes/employee.ts
export const Employee = nodeClass({
  icon: classIcon.lucide(UserRound),
  extends: [S.classes.User],
  properties: { employeeNumber: z.string().min(1) },
  policies: { traverse: shellMayTraverseMember },
})

// schema/modules/team/classes/team.ts
export const Team = nodeClass({
  icon: classIcon.lucide(Users),
  extends: [S.classes.Group],
  policies: { traverse: shellMayTraverseMember },
})

// schema/schema.ts
export const schema = defineSchema('work.example', {
  name: 'Work',
  dependencies: { kernel: KernelSchema, shell: ShellSchema },
  classes: { Employee, Team },
  policies: { shellMayTraverseMember },
})
```

- The Policy identifies Shell through protected Schema ownership, not a configured Domain NodeId.
  Parent-Class Policies do not replace the concrete foreign Class's traversal agreement.
- Preserve existing traversal with `policy.anyOf(existingTraverse, shellMayTraverseMember)`; do not
  replace business access or broaden `read`/writes. Deeper inheritance needs an explicitly verified pattern.

## Invite or register, without substituting the identity

| Path | Consumer responsibility | Completion |
| --- | --- | --- |
| Invitation | Call static `Shell.User.invite({ user, email })` on the existing User | At the invitee's sign-in, Admin registers their own proof and assures Core member |
| Direct Register | Submit valid self or external user proof for the existing node under authorized Domain/operator authority | Authentication only; group assignment is separate |

- Register needs real user proof valid for the target Kernel. Email, a freely supplied `(iss, sub)`,
  or an administrator's credential cannot replace it. Never pass private keys into a Function.
- Authentication is write-once and `(iss, sub)` is unique per Kernel. Do not self-register a node as
  a temporary step before WorkOS registration; that is not an interchangeable login binding.
- Preserve the same node and registration key on retry; do not create another person after an uncertain
  result. A new equivalent proof can refresh credentials without changing the intended identity.
- Invitation `accepted` is not final access: `completed` follows registration and member assignment.
  A normal login must not recreate revoked membership; invitation does not imply admin or Fleet access.

## Use Shell's group operations

- `Group.assignMember({ member, group })` maintains both `member_of_group` and Kernel `extends_with`;
  `unassignMember` removes both. `member` accepts a Shell.User or Shell.Group, including concrete
  descendants; a Class extending only Kernel.Identity is not a Shell membership endpoint.
  Do not write just one Edge or implement a parallel membership system.
- Both group methods use the same Policy: the caller must administer a concrete Shell-owned
  Group, or own the concrete Class of the target Group. Thus the Group-Class owner may assign/unassign
  its Teams. Owning the member's User Class alone grants no assignment to Core `member` or `admin`.
- `User.invite` checks the User instead: its Class owner may invite it; Shell administrators may
  invite concrete Shell-owned Users. Instance administration alone does not authorize foreign Classes.
- Core `admin` and `member` are independent groups, not an implicit hierarchy. Registration grants
  neither; an explicit admin assignment is privileged, not a default business onboarding step.
- A Team has no implicit capability profile. Membership may drive business Policies; installation
  profiles grant capabilities to local Core identities, not arbitrary dynamic groups or users.
- Unassigning removes that direct pair, not Authentication or every other access path. Memberships
  may precede registration; removing `member` alone is not a permanent ban on owner-authorized readmission.

Shell's three methods above require both the principal's effective Function authority and their
Policy on the caller. A Domain calling them declares the exact Method requirements; a human may inherit
capabilities through `extends_with`. Neither bypasses the Policy. Declare Kernel Query/Mutate/Register
capabilities as needed, and protect the business callable before it invokes Shell. See `policies.md`.

Use `dependencies.shell.caller.invoke(...)` to act for the incoming caller, or
`dependencies.shell.self.invoke(...)` when an admitted business operation deliberately acts as its
Domain, for example assigning to its own Team. There is no default dependency `invoke` and no mode
combining both. The Domain principal still needs the exact Method capability.

## Inspect and exercise the installed surface

Use an already authorized operator; replace example IDs with returned IDs on the same instance.
These are static Shell methods, not `@user::invite` or instance Group methods.

```sh
astrale introspect /:shell.astrale.ai:class.User:invite -i staging --as operator
astrale introspect /:shell.astrale.ai:class.Group:assignMember -i staging --as operator
astrale call /:shell.astrale.ai:class.User:invite \
  user=@employee-id email=alice@example.com -i staging --as operator
astrale call /:shell.astrale.ai:class.Group:assignMember \
  member=@employee-id group=@team-id -i staging --as operator
```

These Shell handlers require exact `@NodeId` reference inputs; group methods return `{}`. Keep business
references as IDs and convert to `@NodeId` at the Shell call boundary. Resolve Core member/admin
on the target instance first, rather than sending group labels or IDs copied from another Kernel.
An administrator finds both among their own memberships. The Core Path `/:shell.astrale.ai:core.admin`
traverses the Shell Domain node and Kernel `of_domain`, which Shell administrators cannot read.

To make an invited user an instance administrator, an existing administrator assigns them to Core
`admin`; invitation never does. `astrale instance invitation status` reports the invited `user`, the
Shell User Admin reserved on the Instance; the accepting account registers onto it. Assign it once
the Invitation is `completed`. `unassignMember` with the same input revokes it, and the user keeps
Core `member`:

```sh
astrale instance invitation status @invitation-id --json
astrale query @self --edge /:shell.astrale.ai:class.member_of_group -i staging --as operator
astrale call /:shell.astrale.ai:class.Group:assignMember \
  member=@user-id group=@administrators-id -i staging --as operator
```

For local-key testing, use a CLI whose `astrale identity register --help` exposes `--node`.
Register the existing Employee ID; do not create another node to attach login credentials.

```sh
# Only with the existing-node registration CLI and an authorized operator.
astrale identity create alice
astrale identity register alice --node @employee-id -i staging --as operator
astrale get @self -i staging --as alice --json
```

If the operator lacks authority over Employee, use `--via` only with the Domain's explicitly admitted
registration Function. Do not add a public registration wrapper or a generic enrollment callback for invitation.

Verify the same User ID before/after activation, both membership edges, and a real allowed/refused
business call. Shell traversal must work without exposing private profile properties. Test root/bootstrap
separately; mocks and locally stored identities do not prove WorkOS acceptance or installed access.
