/**
 * @name Comparison of identical values
 * @description Comparison of identical values, the intent of which is unclear.
 * @kind problem
 * @tags reliability
 *       correctness
 *       readability
 *       convention
 *       external/cwe/cwe-570
 *       external/cwe/cwe-571
 * @problem.severity warning
 * @sub-severity high
 * @precision very-high
 * @id py/comparison-of-identical-expressions
 */

import python
import RedundantComparison

from RedundantComparison comparison, File f
where
  not comparison.isConstant() and
  not comparison.maybeMissingSelf() and
  (
    f.getBaseName() = "test_richcmp.py" or
    f.getBaseName() = "test_tztime.py" or
    f.getBaseName() = "test_refs.py"
  ) and
  comparison.getEnclosingModule().getFile().getBaseName() = f.getBaseName()
select comparison, "Comparison of identical values; use cmath.isnan() if testing for not-a-number.",
  f.getBaseName(), "File Name"
