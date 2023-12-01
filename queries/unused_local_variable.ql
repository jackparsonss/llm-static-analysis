/**
 * @name Unused local variable
 * @description Local variable is defined but not used
 * @kind problem
 * @tags maintainability
 *       useless-code
 *       external/cwe/cwe-563
 * @problem.severity recommendation
 * @sub-severity high
 * @precision very-high
 * @id py/unused-local-variable
 */

import python
import Definition

predicate unused_local(Name unused, LocalVariable v) {
  forex(Definition def | def.getNode() = unused |
    def.getVariable() = v and
    def.isUnused() and
    not exists(def.getARedef()) and
    not exists(annotation_without_assignment(v)) and
    def.isRelevant() and
    not v = any(Nonlocal n).getAVariable() and
    not exists(def.getNode().getParentNode().(FunctionDef).getDefinedFunction().getADecorator()) and
    not exists(def.getNode().getParentNode().(ClassDef).getDefinedClass().getADecorator())
  )
}

/**
 * Gets any annotation of the local variable `v` that does not also reassign its value.
 *
 * TODO: This predicate should not be needed. Rather, annotated "assignments" that do not actually
 * assign a value should not result in the creation of an SSA variable (which then goes unused).
 */
private AnnAssign annotation_without_assignment(LocalVariable v) {
  result.getTarget() = v.getAStore() and
  not exists(result.getValue())
}

from Name unused, LocalVariable v, File f
where
  unused_local(unused, v) and
  (
    f.getBaseName() = "test_ctxmgmt.py" or
    f.getBaseName() = "cached.py" or
    f.getBaseName() = "win_registry_key_object.py" or
    f.getBaseName() = "llm_test_ctxmgmt.py" or
    f.getBaseName() = "llm_cached.py" or
    f.getBaseName() = "llm_win_registry_key_object.py"
  ) and
  v.getScope().getEnclosingModule().getFile().getBaseName() = f.getBaseName() and
  // If unused is part of a tuple, count it as unused if all elements of that tuple are unused.
  forall(Name el | el = unused.getParentNode().(Tuple).getAnElt() | unused_local(el, _))
select unused, "Variable " + v.getId() + " is not used.", f.getBaseName(), ""
