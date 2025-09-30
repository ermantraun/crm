from fastapi import Request
from fastapi.responses import JSONResponse
from application.lead import exceptions as lead_exc

def lead_already_exists_handler(request: Request, exc: lead_exc.LeadAlreadyExistsException):
    return JSONResponse(
        status_code=200,
        content={"detail": "OK"}
    )

def lead_not_found_handler(request: Request, exc: lead_exc.LeadNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Lead not found."}
    )

def invalid_lead_data_handler(request: Request, exc: lead_exc.InvalidLeadDataException):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

def insight_already_exists_handler(request: Request, exc: lead_exc.InsightAlreadyExistsException):
    return JSONResponse(
        status_code=409,
        content={"detail": "Insight already exists."}
    )

def insight_not_found_handler(request: Request, exc: lead_exc.InsightNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Insight not found."}
    )

def invalid_insight_data_handler(request: Request, exc: lead_exc.InvalidInsightDataException):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

all_handlers = {
    lead_exc.LeadAlreadyExistsException: lead_already_exists_handler,
    lead_exc.LeadNotFoundException: lead_not_found_handler,
    lead_exc.InvalidLeadDataException: invalid_lead_data_handler,
    lead_exc.InsightAlreadyExistsException: insight_already_exists_handler,
    lead_exc.InsightNotFoundException: insight_not_found_handler,
    lead_exc.InvalidInsightDataException: invalid_insight_data_handler,
}
