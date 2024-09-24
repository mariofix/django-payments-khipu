# Como Usar

## Instalación

Para utilizar el módulo `django-payments-khipu`, puedes realizar la instalación mediante el uso de pip o poetry.

=== "usando pip"
    ```shell
    pip install django-payments-khipu
    ```
=== "usando poetry"
    ```shell
    poetry add django-payments-khipu
    ```

## Configuración

La configuración del módulo django-payments-khipu se realiza como una variante
de Django Payments. Debes agregar la siguiente configuración en tu archivo de
configuración de Django:

```python
PAYMENT_VARIANTS = {
    "khipu": ("django_payments_khipu.KhipuProvider", {
        "receiver_id": 1,
        "secret": "qwertyasdf0123456789",
    })
}
```

### Variables de configuración

* `receiver_id`: Este valor corresponde a la cuenta entregada por Khipu para
identificar al receptor de los pagos.
* `secret`: Este valor corresponde a la contraseña entregada por Khipu para
autenticar la comunicación con su plataforma.
* `use_notificacion`: Puedes establecer este valor como `None` si deseas
deshabilitar las notificaciones de estado. Si deseas utilizar las
notificaciones, debes especificar la versión de la API de notificaciones de
Khipu en el formato "x.y" (Valor por defecto: 1.3).
* `bank_id`: Si necesitas utilizar variantes diferentes para cada cuenta
bancaria, puedes especificar el `bank_id` en esta configuración. También puedes
proporcionar este valor utilizando `datos_extra` en cada pago. Si no se define
este valor o se establece como None, Khipu solicitará el banco al que se
realizará la transferencia al momento de efectuar el pago
(Valor por defecto: `None`).

## Datos Extra

El módulo `django-payments-khipu` permite enviar datos extra en cada pago. Para
hacerlo, debes utilizar un objeto JSON dentro de la propiedad "attrs" del
modelo de Pagos.

Por ejemplo, si deseas enviar el nombre del cliente en cada compra, puedes
utilizar el siguiente código:

```python
datos_extra: dict = {
    "payer_name": "Nombre de Cliente",
}
payment.attrs.datos_extra = datos_extra
payment.save()
```

Puedes proporcionar un diccionario unidimensional con los valores extra que
deseas enviar en cada pago.

Cabe destacar que los valores `payer_email`, `subject`, `currency`, `amount`,
`transaction_id`, `notify_url`, y `notify_api_version` no pueden ser utilizados
como datos extra y serán ignorados al momento de crear el pago.
