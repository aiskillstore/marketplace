# Phase Gates

## G1: Feature Has Requirements
**Transition**: → Design+
**Check**: requirements map has ≥1 entry
**Fix**: Add requirement with description and status

## G2: Requirements Have Descriptions
**Transition**: → Design
**Check**: All requirements have non-empty description
**Fix**: Add description using EARS syntax

## G3: Decisions Documented
**Transition**: → Implementation
**Check**: decisions field exists (use [] if none)
**Fix**: Add decisions field

## G4: Implementation Started
**Transition**: → Testing
**Check**: All requirements In-Progress or Complete
**Fix**: Update requirement status

## G5: Testing Complete
**Transition**: → Complete
**Check**: 
- All requirements Complete
- All requirements have tested-by with ≥1 test
- All referenced tests in test-cases
- All tests passing: true
**Fix**: Complete requirements, add tests, link via tested-by
