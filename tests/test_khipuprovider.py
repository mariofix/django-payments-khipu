import pytest
from django.http import JsonResponse
from payments import PaymentStatus, RedirectNeeded
from pykhipu.client import Client
from pykhipu.errors import AuthorizationError, ServiceError, ValidationError

from django_payments_khipu.KhipuProvider import KhipuProvider


class MockPayment:
    def __init__(self, token):
        self.token = token
        self.transaction_id = None
        self.description = "Test Payment"
        self.currency = "CLP"
        self.total = 1000
        self.billing_email = "test@example.com"

    def get_success_url(self):
        return "https://example.com/success"

    def get_failure_url(self):
        return "https://example.com/failure"


@pytest.fixture
def khipu_provider():
    return KhipuProvider(receiver_id="your_receiver_id", secret="your_secret", use_notification="1.3")


@pytest.fixture
def mock_payment():
    return MockPayment(token="test_token")


def test_get_form_raises_redirect_needed(khipu_provider, mock_payment):
    with pytest.raises(RedirectNeeded):
        khipu_provider.get_form(mock_payment)


def test_process_data_returns_json_response(khipu_provider, mock_payment):
    request = None  # Replace with a mock HTTP request object if needed
    response = khipu_provider.process_data(mock_payment, request)
    assert isinstance(response, JsonResponse)


def test_refund_returns_refunded_amount(khipu_provider, mock_payment):
    amount = 500
    refunded_amount = khipu_provider.refund(mock_payment, amount)
    assert refunded_amount == amount


def test_capture_raises_not_implemented_error(khipu_provider, mock_payment):
    with pytest.raises(NotImplementedError):
        khipu_provider.capture(mock_payment)


def test_release_raises_not_implemented_error(khipu_provider, mock_payment):
    with pytest.raises(NotImplementedError):
        khipu_provider.release(mock_payment)

#### Check this

from decimal import Decimal
from http import HTTPStatus

import pytest
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from payments import PaymentStatus, RedirectNeeded
from payments.core import provider_factory

from django_payments_mollie.facade import Facade
from django_payments_mollie.provider import MollieProvider

from .factories import PaymentFactory

pytestmark = pytest.mark.django_db


def test_get_provider_from_settings(mocker):
    # Ensure we don't get coverage for the facade from this test
    mocker.patch("django_payments_mollie.provider.Facade.setup_with_api_key")

    provider = provider_factory("mollie")
    assert isinstance(provider, MollieProvider)
    assert provider.facade, "Facade should be initialized"
    assert isinstance(provider.facade, Facade)


def test_provider_initializes_facade(mocker):
    mocker.patch("django_payments_mollie.provider.Facade.setup_with_api_key")
    provider = MollieProvider(api_key="test_test")

    provider.facade.setup_with_api_key.assert_called_once_with("test_test")


def test_provider_get_form_creates_mollie_payment(mocker, mollie_payment):
    mocker.patch("django_payments_mollie.provider.Facade")

    provider = MollieProvider(api_key="test_test")
    # Configure mock
    provider.facade.create_payment.return_value = mollie_payment

    payment = PaymentFactory()
    with pytest.raises(RedirectNeeded):
        provider.get_form(payment)

    provider.facade.create_payment.assert_called_once()

    payment.refresh_from_db()
    assert payment.status == PaymentStatus.INPUT
    assert (
        payment.transaction_id == mollie_payment.id
    ), "Mollie payment ID should be saved"


def test_provider_get_form_redirects_to_mollie(mocker, mollie_payment):
    mocker.patch("django_payments_mollie.provider.Facade")

    provider = MollieProvider(api_key="test_test")
    # Configure mock
    provider.facade.create_payment.return_value = mollie_payment

    payment = PaymentFactory()
    with pytest.raises(RedirectNeeded) as excinfo:
        provider.get_form(payment)

    assert excinfo.type == RedirectNeeded
    assert str(excinfo.value) == mollie_payment.checkout_url


def test_provider_process_data_updates_payment(mocker):
    mocker.patch("django_payments_mollie.provider.Facade")

    provider = MollieProvider(api_key="test_test")
    # Configure mock
    provider.facade.parse_payment_status.return_value = (
        PaymentStatus.CONFIRMED,
        "payment confirmed",
        {"captured_amount": "13.37"},
    )

    payment = PaymentFactory()
    request = HttpRequest()
    request.method = "GET"

    provider.process_data(payment, request)

    payment.refresh_from_db()
    assert payment.status == PaymentStatus.CONFIRMED
    assert payment.message == "payment confirmed"
    assert payment.captured_amount == Decimal("13.37")


def test_provider_process_data_confirmed_payment_uses_own_amount(mocker):
    """If Mollie returns no captured amount, the `payment.total` is used."""
    mocker.patch("django_payments_mollie.provider.Facade")

    provider = MollieProvider(api_key="test_test")
    # Configure mock
    provider.facade.parse_payment_status.return_value = (
        PaymentStatus.CONFIRMED,
        "",
        {},
    )

    payment = PaymentFactory(total="47")
    request = HttpRequest()
    request.method = "GET"

    provider.process_data(payment, request)

    payment.refresh_from_db()
    assert payment.captured_amount == Decimal("47.00")


@pytest.mark.parametrize(
    "status, redirect",
    [
        (PaymentStatus.CONFIRMED, "success"),
        (PaymentStatus.PREAUTH, "success"),
        (PaymentStatus.REJECTED, "failure"),
        (PaymentStatus.ERROR, "failure"),
    ],
)
def test_provider_process_data_returns_result_redirect(mocker, status, redirect):
    mocker.patch("django_payments_mollie.provider.Facade")

    provider = MollieProvider(api_key="test_test")
    # Configure mock
    provider.facade.parse_payment_status.return_value = (
        status,  # Set from parametrized value
        "",
        {},
    )

    payment = PaymentFactory(total="47")
    request = HttpRequest()
    request.method = "GET"

    result = provider.process_data(payment, request)
    assert isinstance(result, HttpResponseRedirect)
    assert result.url == f"https://example.com/{redirect}"


def test_provider_process_data_webhook_request_returns_http_200(mocker):
    mocker.patch("django_payments_mollie.provider.Facade")

    provider = MollieProvider(api_key="test_test")
    # Configure mock
    provider.facade.parse_payment_status.return_value = (
        PaymentStatus.CONFIRMED,
        "",
        {},
    )

    payment = PaymentFactory()
    webhook_request = HttpRequest()
    webhook_request.method = "POST"

    result = provider.process_data(payment, webhook_request)
    assert isinstance(result, HttpResponse)
    assert result.status_code == HTTPStatus.OK
