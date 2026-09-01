# v0.5B pilot failure note

The first finite-noise certificate prototype was **rejected** before confirmatory use.

At 500 predictive samples per mechanism/orientation/intervention cell, using the initial looser equivalence rule (including an approximately `0.8 sigma` response margin), a unique-orientation negative control produced a false merge. The unit suite at that stage therefore reported one failed safety test.

That result is treated as a design failure, not tuned away or deleted. It motivated three changes in v0.5B.1:

1. increase each independent fit/validation split to 2,000 predictive samples per cell;
2. tighten the simultaneous response equivalence envelope to `0.55 sigma`;
3. require a non-trivial intervention-assignment separation gap in addition to fit/validation and forward/reverse mapping agreement.

The initial pilot seeds are excluded from the v0.5B.1 confirmatory ranges. The revised thresholds were frozen in `PREREGISTRATION.md` before the full held-out gate was run.
