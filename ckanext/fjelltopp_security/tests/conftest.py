import pytest
from ckan.tests import factories
from ckan.plugins import toolkit


@pytest.fixture
def user():
    return factories.User(
        image_url=None
    )


@pytest.fixture
def context(user):
    return {
        'user': user['name'],
        'id': user['id'],
        'ignore_auth': True
    }


@pytest.fixture
def organization():
    return factories.Organization(image_url=None)


@pytest.fixture
def group(organization):
    return factories.Group(
        owner_org=organization["id"],
        image_url=None
    )
