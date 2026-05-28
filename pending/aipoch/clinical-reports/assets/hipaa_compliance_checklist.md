# Clinical Report HIPAA Compliance Checklist

## 18 HIPAA Identifiers - De-identification Checklist

Please verify that **all** of the following identifiers have been removed or altered:

- [ ] **1. Names** - Patient names, names of relatives, healthcare providers (unless necessary and consented)

- [ ] **2. Geographic subdivisions smaller than a State**
  - No street addresses
  - No city names (unless population >20,000; acceptable if the geographic unit formed by the first 3 digits of the zip code has a population >20,000)
  - No county names
  - Acceptable only if the geographic unit formed by the first 3 digits of the zip code has a population >20,000
  - Remove all other parts of the zip code

- [ ] **3. Dates** (except year)
  - No exact dates of birth (only year is acceptable; birth years for those over age 89 must be aggregated)
  - No admission dates
  - No discharge dates
  - No visit dates
  - No dates of death
  - Use relative time periods (e.g., "3 months prior to admission") or only the year

- [ ] **4. Telephone numbers**
  - No telephone numbers of any kind
  - Includes contact numbers for patients, relatives, or medical facilities

- [ ] **5. Fax numbers**
  - No fax numbers

- [ ] **6. Email addresses**
  - No email addresses of patients or associated individuals

- [ ] **7. Social Security Numbers (SSN)**
  - No SSN or partial SSN

- [ ] **8. Medical Record Numbers (MRN)**
  - No MRN, hospital ID, or clinic numbers
  - Use coded research IDs or case numbers if necessary

- [ ] **9. Health plan beneficiary numbers**
  - No health insurance ID numbers
  - No policy numbers

- [ ] **10. Account numbers**
  - No billing account numbers
  - No financial account information

- [ ] **11. Certificate/license numbers**
  - No driver's license numbers
  - No professional license numbers (unless used for author credentials)

- [ ] **12. Vehicle identifiers and serial numbers**
  - No license plate numbers
  - No vehicle identification numbers (VIN)

- [ ] **13. Device identifiers and serial numbers**
  - No pacemaker serial numbers
  - No implanted device serial numbers
  - Generic device descriptions are acceptable (e.g., "implantable cardioverter-defibrillator")

- [ ] **14. Web URLs**
  - No personal websites
  - No URLs that could identify an individual

- [ ] **15. IP addresses**
  - No IP addresses

- [ ] **16. Biometric identifiers**
  - No fingerprints
  - No voiceprints
  - No retinal scans
  - No other biometric data

- [ ] **17. Full-face photographs and comparable images**
  - No full-face photos without consent
  - If the face is shown, it must be cropped or blurred
  - Remove identifying features (jewelry, tattoos, birthmarks, if clinically irrelevant)
  - Black bars over the eyes alone are **not sufficient**
  - Ensure no reflections or backgrounds identify the individual

- [ ] **18. Any other unique identifying characteristic or code**
  - No unique characteristics that could identify the individual
  - No rare combinations of diseases that could lead to identification
  - Consider if the combination of remaining data points could potentially identify the individual

---

## Other De-identification Considerations

### Age and Dates

- [ ] Patients aged ≤89: Exact age or age range is acceptable
- [ ] Patients aged >89: Must be aggregated as "90 or older" or ">89 years old"
- [ ] Dates: Use only the year or relative time periods
  - Example: Use "3 months before visit" instead of "January 15, 2023"
  - Example: Use "Admitted in 2023" instead of "Admitted on March 10, 2023"

### Geographic Information

- [ ] State or Country is acceptable
- [ ] Remove specific cities (unless population >20,000 and no other identifying info)
- [ ] Remove hospital/clinic names
- [ ] Use generic descriptions: "A community hospital in the Midwest" or "A tertiary care center"

### Rare Conditions and Combinations

- [ ] Consider if an extremely rare disease itself could identify the patient
- [ ] Consider if the following combinations could identify the patient:
  - Age + Diagnosis + Geographic area + Timeframe
- [ ] Some unique details may need to be obscured
- [ ] Balance providing clinical information with protecting privacy

### Images and Charts

- [ ] All patient identifiers removed from image headers/metadata
- [ ] DICOM data cleared
- [ ] Dates removed from images
- [ ] Medical record numbers removed
- [ ] Faces cropped, blurred, or masked
- [ ] Identifying marks removed or obscured:
  - Tattoos
  - Jewelry
  - Birthmarks or unique scars (if clinically irrelevant)
- [ ] Scales and annotations do not contain identifying information
- [ ] Background environment de-identified (room numbers, name tags, etc.)

### Voice and Video

- [ ] No recordings with the patient's voice (unless consent is obtained)
- [ ] No videos showing identifiable features (unless consent is obtained)
- [ ] If video is necessary, the face must be masked

---

## Informed Consent Checklist (For Case Reports/Publications)

### Consent Requirements

- [ ] Informed consent obtained **before** submission for publication
- [ ] Consent obtained directly from the patient (if they have capacity)
- [ ] If the patient is deceased or lacks capacity, consent signed by a legal representative or next of kin
- [ ] For pediatric cases, consent obtained from parents/guardians

### Consent Form Elements

The informed consent form must include:

- [ ] Purpose of publication (education, medical knowledge)
- [ ] What will be published (case details, images, results)
- [ ] Journal or publication venue (if known)
- [ ] Open access vs. subscription (public accessibility)
- [ ] Explanation of de-identification efforts
- [ ] Notification of potential risk of re-identification
- [ ] Statement that clinical care is not affected
- [ ] Right to withdraw consent (and time limits)
- [ ] Contact information for inquiries
- [ ] Patient signature and date
- [ ] Witness signature (if required)

### Consent Documentation

- [ ] Signed consent form archived
- [ ] Copy provided to the patient
- [ ] Consent form available for review by editors
- [ ] Statement in the manuscript confirming consent was obtained

**Example Manuscript Statement:**
"Written informed consent was obtained from the patient for publication of this case report and any accompanying images. A copy of the written consent is available for review by the Editor-in-Chief of this journal on request."

---

## Safe Harbor vs. Expert Determination

### Safe Harbor Method

- [ ] Removal of all 18 identifiers
- [ ] No actual knowledge that the remaining information could identify the individual
- [ ] The most straightforward method
- [ ] Recommended for most clinical reports

### Expert Determination Method

- [ ] Determination by a senior statistician/expert that the risk of re-identification is very small
- [ ] Methodology is documented
- [ ] Analytical methods are specified
- [ ] Conclusions are documented
- [ ] May allow for the retention of certain data elements
- [ ] Requires statistical expertise

**Method Used:** [ ] Safe Harbor  [ ] Expert Determination

---

## Minimum Necessary Standard

### Use and Disclosure

- [ ] Use only the minimum PHI (Protected Health Information) necessary to achieve the purpose
- [ ] Purpose of disclosure clearly defined
- [ ] Limited to relevant information
- [ ] Consider using de-identified data or a limited data set as an alternative

### Exceptions to the Minimum Necessary Standard

The minimum necessary standard **does not apply** to:
- Treatment purposes (providers may need full information)
- Disclosures authorized by the patient
- Disclosures required by law
- Disclosures to HHS (U.S. Department of Health and Human Services) for compliance investigations

---

## PHI Use/Disclosure Authorization

### When Authorization is Needed

Authorization is required for:
- [ ] Research (unless an IRB waiver is obtained)
- [ ] Marketing purposes
- [ ] Sale of PHI
- [ ] Psychotherapy notes
- [ ] Uses outside of Treatment, Payment, and Operations (TPO)

### Authorization Elements

If authorization is required, it must include:

- [ ] Specific description of the PHI to be used/disclosed
- [ ] Persons authorized to make the disclosure
- [ ] Persons to whom the information will be disclosed
- [ ] Purpose of the disclosure
- [ ] Expiration date or event
- [ ] Right to revoke and how to revoke
- [ ] Right to refuse to sign
- [ ] Potential risk of re-disclosure by the recipient
- [ ] Patient signature and date

---

## Limited Data Set

### Limited Data Set Options

A limited data set removes 16 of the 18 identifiers but may retain:
- [ ] Dates (Admission, discharge, visit, birth, death)
- [ ] Geographic information (City, State, Zip code)

### Requirements for Limited Data Sets

- [ ] Data Use Agreement (DUA) must be signed
- [ ] DUA specifies permitted uses
- [ ] Used only for research, public health, or healthcare operations
- [ ] Recipient agrees not to re-identify the individuals
- [ ] Recipient agrees to protect data security

---

## Safeguards Checklist

### Administrative Safeguards

- [ ] Establish security management processes
- [ ] Workforce security measures
- [ ] Access management (role-based)
- [ ] Security training for staff
- [ ] Incident response procedures

### Physical Safeguards

- [ ] Facility access controls
- [ ] Workstation use policies
- [ ] Workstation security measures
- [ ] Device and media controls
- [ ] Secure disposal procedures

### Technical Safeguards

- [ ] Access controls (unique user IDs, passwords)
- [ ] Audit controls and logging
- [ ] Integrity controls
- [ ] Transmission security (encryption)
- [ ] Automatic logoff after inactivity

---

## Breach Notification Checklist

### If Unauthorized Disclosure Occurs

- [ ] Determine if a breach occurred (unauthorized access/use/disclosure)
- [ ] Assess the risk of harm to the individual
- [ ] If the breach affects <500 individuals:
  - Notify individuals within 60 days
  - Report to HHS annually
- [ ] If the breach affects ≥500 individuals:
  - Notify individuals within 60 days
  - Notify HHS within 60 days
  - Notify the media if it affects ≥500 individuals in a single state/jurisdiction
- [ ] Document the breach and response actions
- [ ] Implement corrective measures

### Breach Notification Content

The notification must include:
- [ ] Description of the breach
- [ ] Types of information involved
- [ ] Steps individuals should take
- [ ] Actions the institution is taking
- [ ] Contact information for inquiries

---

## Research-Related Compliance

### IRB/Privacy Board Considerations

- [ ] IRB approval obtained (if research)
- [ ] HIPAA authorization obtained or waiver granted
- [ ] Justification for waiver documented:
  - Minimal risk to privacy
  - Research could not practicably be conducted without the waiver
  - Research could not practicably be conducted without the PHI
  - Plan to protect identifiers
  - Plan to destroy identifiers at the appropriate time

### Clinical Trial Reporting

- [ ] Subjects identified only by ID numbers
- [ ] No names in regulatory submissions
- [ ] Use initials only if required by regulatory agencies
- [ ] Dates limited to year or relative time
- [ ] Protocol includes privacy protection measures

---

## Special Populations

### Pediatric Cases

- [ ] Consent obtained from parents/guardians
- [ ] Assent obtained from the child (if age-appropriate)
- [ ] Extra attention given to identifiable photographs
- [ ] School information removed

### Deceased Patients

- [ ] HIPAA protections continue for 50 years after death
- [ ] Publication requires consent from next of kin
- [ ] Autopsy information de-identified

### Mental Health and Substance Abuse

- [ ] Additional protections under 42 CFR Part 2
- [ ] Explicit consent for disclosure
- [ ] No re-disclosure without consent

---

## Final Compliance Verification

**Reviewer:** ____________________  
**Date:** ____________________  
**Signature:** ____________________

**Compliance Status:** [ ] Compliant  [ ] Revision Required  [ ] Non-compliant

**Identified Issues:**
1. [Issue]
2. [Issue]

**Corrective Actions:**
1. [Action]
2. [Action]

**Re-review Required:** [ ] Yes  [ ] No  
**Re-review Date:** ____________________

---

## Documentation to Retain

Archive for reference:
- [ ] Signed patient consent forms (if applicable)
- [ ] IRB approval letters (if research)
- [ ] HIPAA waivers (if applicable)
- [ ] Proof of de-identification verification
- [ ] Data Use Agreements (if limited data set)
- [ ] Authorization forms (if applicable)
- [ ] Training records for personnel handling PHI
- [ ] Audit logs

**Retention Period:** Retain for at least 6 years per HIPAA requirements.