from typing import List
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.api import core

router = APIRouter()


@router.get(
    "",
    response_model=List[model.Template],
    responses={
        401: {"model": model.FailedResponse},
    },
)
async def get_templates(
    custom: bool = False,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Get a list of templates.
    """

    templates = await database.template.get_all(db)
    # Generate the model with account ids instead of Order objects
    result = [
        model.Template(
            id=template.id,
            name=template.name,
            description=template.description,
            order=[order.account_id for order in template.orders],
        )
        for template in templates
        if (not custom) or (custom and template.name != "default")
    ]
    return result


@router.get(
    "/{id}",
    response_model=model.Template,
    responses={
        401: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
async def get_template(
    id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Get a template by id.
    """

    template = await database.template.get(db, id=id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    # Generate the model with account ids instead of Order objects
    result = model.Template(
        id=template.id,
        name=template.name,
        description=template.description,
        order=[order.account_id for order in template.orders],
    )
    return result


@router.post(
    "",
    status_code=201,
    response_model=model.Template,
    responses={
        401: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
async def create_template(
    template: model.CreateTemplate,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Create a template.
    """

    if await database.template.get_by_name(db, name=template.name) is not None:
        raise HTTPException(status_code=409, detail="Name already taken")

    db_obj = await database.template.create(db, obj_in=template)
    # Generate the model with account ids instead of Order objects
    result = model.Template(
        id=db_obj.id,
        name=db_obj.name,
        description=db_obj.description,
        order=[order.account_id for order in db_obj.orders],
    )
    return result


@router.put(
    "/{id}",
    response_model=model.Template,
    responses={
        401: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
async def update_template(
    id: int,
    template: model.UpdateTemplate,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Update a template.
    """
    if id == (await database.template.get_by_name(db, name="default")).id:
        raise HTTPException(status_code=422, detail="Cannot modify default template")

    db_obj = await database.template.get(db, id=id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Template not found")

    if template.name is not None and template.name != db_obj.name:
        if await database.template.get_by_name(db, name=template.name) is not None:
            raise HTTPException(status_code=409, detail="Name already taken")

    new_obj = await database.template.update(db, db_obj=db_obj, obj_in=template)
    # Generate the model with account ids instead of Order objects
    result = model.Template(
        id=new_obj.id,
        name=new_obj.name,
        description=new_obj.description,
        order=[order.account_id for order in new_obj.orders],
    )
    return result


@router.delete(
    "/{id}",
    status_code=204,
    responses={
        401: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
async def delete_template(
    id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Delete a template.
    """

    if id == (await database.template.get_by_name(db, name="default")).id:
        raise HTTPException(status_code=422, detail="Cannot modify default template")

    db_obj = await database.template.get(db, id=id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Template not found")

    await database.template.delete(db, id=id)
    return Response(status_code=HTTPStatus.NO_CONTENT)
