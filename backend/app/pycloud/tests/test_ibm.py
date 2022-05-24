import pytest

from pycloud.controllers.ibm import IBMApi

IBM_API_KEY = ""


@pytest.mark.asyncio
async def test_login():
    api = IBMApi(IBM_API_KEY)
    await api.login()


@pytest.mark.asyncio
async def test_get_accounts():
    api = IBMApi(IBM_API_KEY)
    await api.login()
    accounts = await api.get_accounts()
    assert len(accounts) > 0


@pytest.mark.asyncio
async def test_get_regions():
    api = IBMApi(IBM_API_KEY)
    await api.login()
    regions = await api.get_regions()
    assert len(regions) > 0


@pytest.mark.asyncio
async def test_cf_login():
    api = IBMApi(IBM_API_KEY)
    await api.login()
    regions = await api.get_regions()
    region = regions[0]
    cf = region.cf()
    await cf.login()


@pytest.mark.asyncio
async def test_get_organizations():
    api = IBMApi(IBM_API_KEY)
    await api.login()
    regions = await api.get_regions()
    region = regions[0]
    cf = region.cf()
    await cf.login()
    organizations = await cf.get_organizations()
    assert len(organizations) > 0


@pytest.mark.asyncio
async def test_get_spaces():
    api = IBMApi(IBM_API_KEY)
    await api.login()
    regions = await api.get_regions()
    region = regions[0]
    cf = region.cf()
    await cf.login()
    organizations = await cf.get_organizations()
    assert len(organizations) > 0
    spaces = await organizations[0].get_spaces()
    assert len(spaces) > 0


@pytest.mark.asyncio
async def test_get_apps():
    api = IBMApi(IBM_API_KEY)
    await api.login()
    regions = await api.get_regions()
    region = regions[0]
    cf = region.cf()
    await cf.login()
    organizations = await cf.get_organizations()
    assert len(organizations) > 0
    spaces = await organizations[0].get_spaces()
    assert len(spaces) > 0
    apps = (await spaces[0].get_info()).apps
