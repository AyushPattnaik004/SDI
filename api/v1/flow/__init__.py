from fastapi import APIRouter
from .trainee import trainee_router
from .job_posting import job_posting_router
from .job_register import company_registration_router
from .training_partner import training_partner_router

flow_router = APIRouter()
flow_router.include_router(trainee_router,prefix="/trainee")
flow_router.include_router(job_posting_router, prefix="/job_posting")
flow_router.include_router(company_registration_router, prefix="/job_register")
flow_router.include_router(training_partner_router,prefix="/training_partner")