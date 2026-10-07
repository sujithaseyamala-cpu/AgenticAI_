"""
rag_engine.py - RAG (Retrieval-Augmented Generation) Engine for Student Records.
Performs semantic and criteria-based document search over the student database.
"""

import re
from typing import List, Dict, Any
from student_data import STUDENTS_DATABASE

def search_students(query: str) -> Dict[str, Any]:
    """
    RAG search function that retrieves relevant student documents based on a natural query.
    Handles name lookups, department filters, criteria queries, and ranking questions.
    """
    q = query.lower().strip()
    if not q:
        return {"status": "error", "message": "Search query cannot be empty."}

    matched_students = []

    # 1. Condition: "Highest overall mark"
    if "highest overall" in q or "top overall" in q or "max overall" in q:
        sorted_by_overall = sorted(STUDENTS_DATABASE, key=lambda s: s["overall"], reverse=True)
        top_mark = sorted_by_overall[0]["overall"]
        matched_students = [s for s in sorted_by_overall if s["overall"] == top_mark]
        return {
            "status": "success",
            "query": query,
            "filter": "Highest Overall Mark",
            "count": len(matched_students),
            "students": matched_students
        }

    # 2. Condition: "Highest attendance"
    if "highest attendance" in q or "top attendance" in q or "max attendance" in q:
        sorted_by_att = sorted(STUDENTS_DATABASE, key=lambda s: s["attendance"], reverse=True)
        top_att = sorted_by_att[0]["attendance"]
        matched_students = [s for s in sorted_by_att if s["attendance"] == top_att]
        return {
            "status": "success",
            "query": query,
            "filter": "Highest Attendance",
            "count": len(matched_students),
            "students": matched_students
        }

    # 3. Condition: "Attendance below 75%" or "< 75"
    if "attendance" in q and ("below 75" in q or "< 75" in q or "less than 75" in q):
        matched_students = [s for s in STUDENTS_DATABASE if s["attendance"] < 75]
        return {
            "status": "success",
            "query": query,
            "filter": "Attendance < 75%",
            "count": len(matched_students),
            "students": matched_students
        }

    # 4. Condition: "Scored above 90 in AI" or "AI > 90"
    if "ai" in q and ("above 90" in q or "> 90" in q or "more than 90" in q or "greater than 90" in q):
        matched_students = [s for s in STUDENTS_DATABASE if s["ai"] > 90]
        return {
            "status": "success",
            "query": query,
            "filter": "AI Mark > 90",
            "count": len(matched_students),
            "students": matched_students
        }

    # 5. Condition: "AIDS students with overall mark above 80"
    if "aids" in q and ("above 80" in q or "> 80" in q):
        matched_students = [s for s in STUDENTS_DATABASE if s["dept"] == "AIDS" and s["overall"] > 80]
        return {
            "status": "success",
            "query": query,
            "filter": "AIDS students with Overall > 80",
            "count": len(matched_students),
            "students": matched_students
        }

    # 6. Condition: Placement eligible / not eligible
    if "placement" in q or "eligible" in q:
        if "not eligible" in q:
            matched_students = [s for s in STUDENTS_DATABASE if s["placement"].lower() == "not eligible"]
        elif "eligible" in q:
            matched_students = [s for s in STUDENTS_DATABASE if s["placement"].lower() == "eligible"]
        return {
            "status": "success",
            "query": query,
            "filter": "Placement Filter",
            "count": len(matched_students),
            "students": matched_students
        }

    # 7. Department queries: e.g. "CSE department", "students in IT"
    for dept in ["CSE", "IT", "ECE", "EEE", "AIDS"]:
        if re.search(rf"\b{dept.lower()}\b", q):
            matched_students = [s for s in STUDENTS_DATABASE if s["dept"] == dept]
            return {
                "status": "success",
                "query": query,
                "filter": f"{dept} Department",
                "count": len(matched_students),
                "students": matched_students
            }

    # 8. Name or ID or Attribute search (Fuzzy token match)
    for student in STUDENTS_DATABASE:
        name_lower = student["name"].lower()
        id_lower = student["student_id"].lower()
        # Direct match on ID
        if id_lower in q:
            matched_students.append(student)
            continue
        # Match student name tokens (e.g., 'Priya', 'Sharma', 'Arjun', 'Fathima')
        name_parts = name_lower.split()
        if any(part in q for part in name_parts if len(part) > 2):
            matched_students.append(student)

    if matched_students:
        return {
            "status": "success",
            "query": query,
            "count": len(matched_students),
            "students": matched_students
        }

    # 9. Fallback: Search all attributes
    tokens = set(re.findall(r'\w+', q))
    for student in STUDENTS_DATABASE:
        record_text = f"{student['student_id']} {student['name']} {student['dept']} {student['email']} {student['phone']}".lower()
        if any(t in record_text for t in tokens if len(t) > 3):
            matched_students.append(student)

    return {
        "status": "success" if matched_students else "not_found",
        "query": query,
        "count": len(matched_students),
        "students": matched_students,
        "message": "No matching student records found." if not matched_students else ""
    }
