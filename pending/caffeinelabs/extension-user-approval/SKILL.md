---
name: extension-user-approval
description: Approval-based user management.
version: 0.1.5
compatibility:
  mops:
    caffeineai-user-approval: "~0.1.1"
    caffeineai-authorization: "~0.1.1"
caffeineai-subscription: [none]
---

# User Approval
User approval extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds approval-based user management. Users request access; admins approve or reject. Approved users gain access to protected features.

# Backend

Approval-based user management:

Prerequisite: You must follow [extension-authorization](../extension-authorization/SKILL.md) first, as this integration depends on it.

There is a prefabricated module `mo:caffeineai-user-approval/approval` that cannot be modified. It provides approval-based user management with role-based access control.

```mo:caffeineai-user-approval/approval
import AccessControl "mo:caffeineai-authorization/access-control";

module {
    public type ApprovalStatus = {
        #approved;
        #rejected;
        #pending;
    };

    public type UserApprovalState = { /* internal state */ };

    public func initState(accessControlState: AccessControl.AccessControlState) : UserApprovalState;

    public func isApproved(state : UserApprovalState, caller : Principal) : Bool;
    public func setApproval(state : UserApprovalState, user : Principal, approval : ApprovalStatus);

    public type UserApprovalInfo = {
        principal : Principal;
        status : ApprovalStatus;
    };

    public func listApprovals(state : UserApprovalState) : [UserApprovalInfo];
}
```

Usage (all the following functions are required to be added):

```motoko filepath=src/backend/main.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import UserApproval "mo:caffeineai-user-approval/approval";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";

actor {
    // Include authorization
    let accessControlState = AccessControl.initState();
    include MixinAuthorization(accessControlState);

    let approvalState = UserApproval.initState(accessControlState);

    public query ({ caller }) func isCallerApproved() : async Bool {
        AccessControl.hasPermission(accessControlState, caller, #admin) or UserApproval.isApproved(approvalState, caller);
    };

    public shared ({ caller }) func requestApproval() : async () {
        UserApproval.requestApproval(approvalState, caller);
    };

    public shared ({ caller }) func setApproval(user : Principal, status : UserApproval.ApprovalStatus) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can perform this action");
        };
        UserApproval.setApproval(approvalState, user, status);
    };

    public query ({ caller }) func listApprovals() : async [UserApproval.UserApprovalInfo] {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can perform this action");
        };
        UserApproval.listApprovals(approvalState);
    };

    // In addition to access control guards, add an approval check where needed:
    // Admins should have the permission do use all functionality
    // * Approved users only:
    //   if (not (UserApproval.isApproved(approvalState, caller) or AccessControl.hasPermission(accessControlState, caller, #admin))) {
    //      Runtime.trap("Unauthorized: Only approved users can perform this action");
    //   };
};
```

On `initState`, existing admins are automatically approved. All other users are pending.

IMPORTANT: Apply the right authorization and/or approval check to each public function.

# Frontend

Approval-based user management:

# User Approval Flow
- Check approval status (`isCallerApproved`)
- If not approved, show option to request approval (`requestApproval`)
- Block access to main features for non-approved users
- Admins have access to all features of the application
- Display approval status clearly in the UI

# Admin Dashboard
For admin users, provide a dashboard to:
- List all users with their approval status (`listApprovals`)
- Approve or reject users (`setApproval`)
- View and assign user roles (using `getCallerUserRole` and `assignCallerUserRole`)

# Backend Integration
The backend already implements the following functionality.
The full interface can be found in <backend-interface>

// Check if current user is approved, admins are always approved
isCallerApproved(): Promise<boolean>;

// Submit approval request
requestApproval(): Promise<void>;

// Get all users and their approval status (admin only)
listApprovals(): Promise<Array<UserApprovalInfo>>;

// Approve or reject a user (admin only)
setApproval(user: Principal, status: ApprovalStatus): Promise<void>;

// Assign a role to a user (admin only)
assignCallerUserRole(user: Principal, role: UserRole): Promise<void>;

// Get current role for a specific user
getCallerUserRole(): Promise<UserRole>;
