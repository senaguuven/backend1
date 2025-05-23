from config.database import db
from term.model import Term
from term import schemas as term_schemas
from typing import List
from bson import ObjectId


async def create_term(term_data: term_schemas.TermCreate) -> Term:
    term = Term(**term_data.dict())
    await db.save(term)
    return term

async def check_term_overlap(start_date: str, end_date: str) -> Term:
    term = await db.find_one(Term, Term.term_start_date >= start_date, Term.term_end_date <= end_date)
    return term

async def list_terms() -> List[Term]:
    terms = await db.find(Term)
    return terms

async def get_term(term_id: str) -> Term:
    term = await db.find_one(Term, Term.id == ObjectId(term_id))
    return term

async def update_term(term: Term, term_data: term_schemas.TermUpdate) -> Term:
    term.model_update(term_data)
    await db.save(term)
    return term

async def delete_term(term: Term) -> bool:
    await db.delete(term)
    return True