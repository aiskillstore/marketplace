# Redmax Style Cues

Use these cues to keep the README concise and information-dense:

- Lead with a clear project name + one-line summary.
- Add a short note about what is new or differentiating (optional).
- Prefer a simple “Contents” list describing key deliverables or submodules.
- Keep sections short; bullets are favored over long paragraphs.
- Avoid excessive marketing language; focus on factual capability statements.

Example snippet (from user-provided reference):

REDMAX: Efficient & Flexible Approach for Articulated Dynamics
NEW: We now have an analytically differentiable version! See the the notes and the reference MATLAB implementation.

Contents
notes.pdf: An extensive writeup with details on:
- Maximal coordinates
- Reduced coordinates
- Analytical derivatives
- Implicit integration
- Adjoint method
matlab-diff: Object-oriented MATLAB implementation of differentiable redmax
- Fully implicit time integration: BDF1 and BDF2
- Parameter optimization with the adjoint method
- Frictional contact with the ground [Geilinger et al. 2020]
matlab-simple: Simpler object-oriented MATLAB implementation for getting started
matlab: Object-oriented MATLAB implementation with many features, including:
- Recursive hybrid dynamics (Featherstone's algorithm) for comparison
- Time integration using ode45 or euler
- Frictional dynamics with Bilateral Staggered Projections
- Spline curve and surface joints [Lee and Terzopoulos 2008]
c++: C++ implementation including Projected Block Jacobi Preconditioner
