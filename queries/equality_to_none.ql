/**
 * @name Testing equality to None
 * @description Testing whether an object is 'None' using the == operator is inefficient and potentially incorrect.
 * @kind problem
 * @tags efficiency
 *       maintainability
 * @problem.severity recommendation
 * @sub-severity high
 * @precision very-high
 * @id py/test-equals-none
 */

import python

from Compare c, File f
where
  c.getOp(0) instanceof Eq and
  c.getAComparator() instanceof None and
  (
    f.getBaseName() = "replica.py" or
    f.getBaseName() = "__init__.py" or
    f.getBaseName() = "SipRequest.py"
  ) and
  c.getEnclosingModule().getFile().getBaseName() = f.getBaseName()
select c, "Testing for None should use the 'is' operator.", f.getBaseName(), ""
