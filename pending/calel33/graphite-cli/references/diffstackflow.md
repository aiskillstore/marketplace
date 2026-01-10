### Command flow Sequence Template
example 
# Start Phase 
gt sync
gt checkout main

# DIFF 1

gt create -am "feat(calendar): implement TODAY button functionality"
gt submit --draft


# DIFF 2

gt create -am "feat(auth): implement auth functionality"
gt submit --draft


# DIFF 3
gt create -am "feat(calendar): remove non-functional view toggle buttons"
gt submit --stack

# Review and iterate
gt log short
gt pr
```
