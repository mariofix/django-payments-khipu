from django.http import JsonResponse
from payments import RedirectNeeded

# from payments.core import BasicProvider


class KhipuProvider:
    """
    La clase KhipuProvider proporciona integración con Khipu para procesar
    pagos.
    """

    receiver_id: str = None
    secret: str = None

    def __init__(self, receiver_id, secret, **kwargs):
        """
        Inicializa una instancia de KhipuProvider con la clave API y el secreto
        API de Khipu proporcionados.

        Args:
            receiver_id (str): Clave API de Khipu.
            secret (str): Secreto API de Khipu.
        """
        super().__init__(**kwargs)
        self.receiver_id = receiver_id
        self.secret = secret

    def get_form(self, payment, data=None):
        """
        Genera el formulario de pago para redirigir a la página de pago de Khipu.

        Args:
            payment: Objeto de pago.
            data: Datos del formulario (no utilizado).

        Raises:
            RedirectNeeded: Redirige a la página de pago de Khipu.

        """
        if not payment.transaction_id:
            pass
        raise RedirectNeeded()

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

    def refund(self, payment, amount=None) -> JsonResponse:
        """
        Realiza el reembolso del pago.

        Args:
            payment: Objeto de pago.
            amount: Monto a reembolsar (no utilizado).

        Returns:
            JsonResponse: Respuesta JSON que indica el proceso de reembolso.

        """
        return JsonResponse("refund")

    def capture(self, payment, amount=None):
        """
        Captura el pago (no implementado).

        Args:
            payment: Objeto de pago.

        Raises:
            NotImplementedError: Método no implementado.
        """
        raise RedirectNeeded()

    def release(self, payment):
        """
        Libera el pago (no implementado).

        Args:
            payment: Objeto de pago.

        Raises:
            NotImplementedError: Método no implementado.
        """
        raise NotImplementedError()
