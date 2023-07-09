from typing import Any

from django.http import JsonResponse
from payments import PaymentError, PaymentStatus, RedirectNeeded
from payments.core import BasicProvider
from pykhipu.client import Client
from pykhipu.errors import AuthorizationError, ServiceError, ValidationError


class KhipuProvider(BasicProvider):
    """
    KhipuProvider es una clase que proporciona integración con Khipu para procesar pagos.
    """

    receiver_id: str = None
    secret: str = None
    use_notification: str | None = "1.3"
    bank_id: str | None = None
    _client: Any = None

    def __init__(self, receiver_id: str, secret: str, use_notification: str | None, bank_id: str | None, **kwargs):
        """
        Inicializa una instancia de KhipuProvider con el ID de receptor y el secreto de Khipu proporcionados.

        Args:
            receiver_id (str): ID de receptor de Khipu.
            secret (str): Secreto de Khipu.
            use_notification (str | None): Versión de la API de notificaciones a utilizar (opcional).
            bank_id (str | None): Id de Banco para variante (opcional).
            **kwargs: Argumentos adicionales.
        """
        super().__init__(**kwargs)
        self.receiver_id = receiver_id
        self.secret = secret
        self.use_notification = use_notification
        self.bank_id = bank_id
        self._client = Client(receiver_id=receiver_id, secret=secret)

    def get_form(self, payment, data: dict | None = None) -> Any:
        """
        Genera el formulario de pago para redirigir a la página de pago de Khipu.

        Args:
            payment: Objeto de pago.
            data (dict | None): Datos del formulario (opcional).

        Returns:
            Any: Formulario de pago redirigido a la página de pago de Khipu.

        Raises:
            RedirectNeeded: Redirige a la página de pago de Khipu.

        """
        if not payment.transaction_id:
            datos_para_khipu = {
                "transaction_id": payment.token,
                "return_url": payment.get_success_url(),
                "cancel_url": payment.get_failure_url(),
            }
            if self.use_notification:
                datos_para_khipu.update({"notify_url": self.get_notification_url()})
                datos_para_khipu.update({"notify_api_version": self.use_notification})

            if self.bank_id:
                datos_para_khipu.update({"bank_id": self.bank_id})

            if payment.billing_email:
                datos_para_khipu.update({"payer_email": payment.billing_email})

            datos_para_khipu.update(**self._extra_data(payment.attrs))
            try:
                payment = self._client.payments.post(
                    payment.description, payment.currency, int(payment.total), **datos_para_khipu
                )

            except (ValidationError, AuthorizationError, ServiceError) as pe:
                payment.change_status(PaymentStatus.ERROR, str(pe))
                raise PaymentError(pe)
            else:
                payment.transaction_id = payment.payment_id
                payment.attrs.payment_response = payment
                payment.save()

        if "payment_url" not in payment:
            raise PaymentError("Khipu no envió una URL, revisa los logs en Khipu.")

        raise RedirectNeeded(payment.get("payment_url"))

    def process_data(self, payment, request) -> JsonResponse:
        """
        Procesa los datos del pago recibidos desde Khipu.

        Args:
            payment: Objeto de pago.
            request: Objeto de solicitud HTTP de Django.

        Returns:
            JsonResponse: Respuesta JSON que indica el procesamiento de los datos del pago.

        """
        return JsonResponse("process_data")

    def _extra_data(self, attrs) -> dict:
        if "datos_extra" not in attrs:
            return {}

        data = attrs.datos_extra
        if "payer_email" in data:
            del data["payer_email"]

        if "subject" in data:
            del data["subject"]

        if "currency" in data:
            del data["currency"]

        if "amount" in data:
            del data["amount"]

        if "transaction_id" in data:
            del data["transaction_id"]

        if "notify_url" in data:
            del data["notify_url"]

        if "notify_api_version" in data:
            del data["notify_api_version"]

        return data

    def refund(self, payment, amount: int | None = None) -> int:
        """
        Realiza un reembolso del pago.

        Args:
            payment: Objeto de pago.
            amount (int | None): Monto a reembolsar (opcional).

        Returns:
            int: Monto reembolsado.

        Raises:
            PaymentError: Error al realizar el reembolso.

        """
        if payment.status != PaymentStatus.CONFIRMED:
            raise PaymentError("El pago debe estar confirmado para reversarse.")

        to_refund = amount or payment.total
        try:
            refund = self._client.payments.post_refunds(payment.transaction_id, to_refund)
        except (ValidationError, AuthorizationError, ServiceError) as pe:
            raise PaymentError(pe)
        else:
            payment.attrs.refund = refund
            payment.save()
            payment.change_status(PaymentStatus.REFUNDED)
            return to_refund

    def capture(self, payment, amount=None):
        """
        Captura el monto del pago.

        Args:
            payment: Objeto de pago.
            amount: Monto a capturar (no utilizado).

        Raises:
            NotImplementedError: Método no implementado.

        """
        raise NotImplementedError()

    def release(self, payment):
        """
        Libera el pago (no implementado).

        Args:
            payment: Objeto de pago.

        Raises:
            NotImplementedError: Método no implementado.

        """
        raise NotImplementedError()
