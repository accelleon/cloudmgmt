import pytest
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.database import iaas
from pycloud.factory import CloudFactory


@pytest.mark.asyncio
async def test_iaas_exists(
    db: Session,
) -> None:
    iaasFactory = CloudFactory.get_providers()
    for provider in iaasFactory:
        iaasDb = await iaas.get_by_name(db, name=provider.name)
        assert iaasDb is not None
        assert iaasDb.name == provider.name
        assert iaasDb.type == provider.type
        assert iaasDb.params == provider.params
