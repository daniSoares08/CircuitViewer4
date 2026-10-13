"""New CircuitViewer4 catalog. No CircuitViewer3/legacy content is loaded."""

import importlib

CHAPTER_MODULES = ["ch09", "ch09_full", "ch10", "ch10_full",
                   "ch11", "ch11_full", "ch12", "ch12_full", "exams"]


def load():
    subjects, circuits, exercises = [], {}, []
    seen = set()
    for name in CHAPTER_MODULES:
        try:
            mod = importlib.import_module("content." + name)
        except ModuleNotFoundError as exc:
            if exc.name == "content." + name:
                continue
            raise
        for subject in getattr(mod, "SUBJECTS", []):
            if subject not in subjects:
                subjects.append(subject)
        for key, ops in getattr(mod, "CIRCUITS", {}).items():
            if key in circuits:
                raise KeyError("circuito duplicado %r" % key)
            circuits[key] = ops
        for ex in getattr(mod, "EXERCISES", []):
            if ex["id"] in seen:
                raise KeyError("exercicio duplicado %r" % ex["id"])
            seen.add(ex["id"])
            exercises.append(ex)
    # Authorized proofs increase priority within the existing subject.
    # Aliases reference the same canonical entry, not an old proof catalog.
    exams=importlib.import_module('content.exams')
    exercises=[dict(ex) for ex in exercises]
    by_id={ex['id']:ex for ex in exercises}
    source_refs=list(exams.OCCURRENCES)+[
        dict(id=key,document=ref['document'],problem=ref['problem'],pdf_page=ref['pdf_page'])
        for ref in exams.BOOK_REFERENCES for key in ref['ids']]
    for occurrence in source_refs:
        if occurrence['id'] not in by_id:raise KeyError('missing exam alias '+occurrence['id'])
        ex=by_id[occurrence['id']]
        ex['priority']=min(ex.get('priority',1000),-sum(
            item['id']==ex['id'] for item in source_refs))
        ex['exam_sources']=[item for item in source_refs if item['id']==ex['id']]
    return subjects, circuits, exercises
