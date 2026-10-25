"""A tiny API to practice CI/CD on. Small on purpose: the pipeline is the lesson."""

import os

from fastapi import FastAPI, HTTPException

APP_VERSION = os.getenv("APP_VERSION", "dev")

app = FastAPI(title="CI/CD Practice API", version=APP_VERSION)


def add(a: float, b: float) -> float:
    return a + b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@app.get("/health")
def health() -> dict:
    """Used by Docker HEALTHCHECK and by deploy smoke tests."""
    return {"status": "ok", "version": APP_VERSION}


@app.get("/add")
def add_endpoint(a: float, b: float) -> dict:
    return {"result": add(a, b)}


@app.get("/divide")
def divide_endpoint(a: float, b: float) -> dict:
    try:
        return {"result": divide(a, b)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
