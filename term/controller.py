from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from datetime import timedelta
from config import auth
from typing import List
import csv
from io import StringIO
from bson import ObjectId

from . import crud as term_crud, schemas as term_schemas
from users import crud as user_crud
controller = APIRouter()

@controller.post("/", response_model=term_schemas.Term,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new term",
    description="Create a new term with the provided details.",
)
async def create_term(term_data: term_schemas.TermCreate, current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    existing_term = await term_crud.check_term_overlap(term_data.term_start_date, term_data.term_end_date)
    if existing_term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A term already exists between start and end dates."
        )
    return await term_crud.create_term(term_data)
    
@controller.get("/", response_model=List[term_schemas.Term], summary="Get all terms", description="Retrieve a list of all terms.")
async def list_terms(current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    return await term_crud.list_terms()

@controller.get("/{term_id}", response_model=term_schemas.Term, summary="Get a term by ID", description="Retrieve a term by its ID.")
async def get_term(term_id: str, current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    print(term.term_duration)
    return term

@controller.put("/{term_id}", response_model=term_schemas.Term, summary="Update a term", description="Update an existing term.")
async def update_term(term_id: str, term_data: term_schemas.TermUpdate, current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    updated_term = await term_crud.update_term(term, term_data)
    return updated_term

@controller.delete("/{term_id}", summary="Delete a term", description="Delete a term by its ID.")
async def delete_term(term_id: str, current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    await term_crud.delete_term(term)
    return {"detail": "Term deleted successfully."}

@controller.get("/{term_id}/students", tags=["Students"], response_model=List[term_schemas.Student], summary="Get students by term ID", description="Retrieve a list of students enrolled in a specific term.")
async def list_term_students(term_id: str, current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    students = []
    for student_id in term.term_students:
        student = await user_crud.get_user_by_id(student_id)
        if student:
            students.append(student)
    return students

@controller.post("/{term_id}/students", tags=["Students"], response_model=List[term_schemas.Student], summary="Add students to a term", description="Enroll students in a specific term.")
async def add_students_to_term(term_id: str, student_ids: List[str], current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    term.term_students.extend(student_ids)
    await term_crud.update_term(term, term)
    return term.term_students

@controller.delete("/{term_id}/students/{student_id}", tags=["Students"], summary="Remove a student from a term", description="Unenroll a student from a specific term.")
async def remove_student_from_term(term_id: str, student_id: str, current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    students = term.term_students = [student for student in term.term_students if student != student_id]
    await term_crud.update_term(term, {"term_students": students})
    return term.term_students

@controller.get("/{term_id}/students/{student_id}", tags=["Students"], response_model=term_schemas.Student, summary="Get a student by term ID", description="Retrieve a specific student enrolled in a term.")
async def get_student_by_term(term_id: str, student_id: str, current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    if student_id not in term.term_students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found in this term."
        )
    student = await user_crud.get_user(student_id)
    return student

@controller.post("/{term_id}/import", tags=["Students"], summary="Import students to a term via CSV file", description="Enroll multiple students in a specific term via CSV file.")
async def import_students_to_term(term_id: str, file: UploadFile = File(...), current_user: auth.User = Depends(auth.check_user(roles=["admin"]))):
    term = await term_crud.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found."
        )
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))
    students = []
    for row in reader:
        student_mail = row.get("student_mail")
        if not student_mail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student email is required."
            )
        student = await user_crud.get_user(student_mail.split("@")[0])
        if not student:
            student = await user_crud.create_user({
                "username": student_mail.split("@")[0],
                "user_email": student_mail,
                "user_password": auth.get_password_hash(student_mail.split("@")[0]),
                "user_role": ["student"],
                "user_name": row.get("student_name"),
                "user_surname": row.get("student_surname"),
                "user_status": True,
                "is_password_change_required": True,
            })
        students.append(str(student.id))
    await term_crud.update_term(term, {"term_students": students})
    return students