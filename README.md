# django-payments-khipu

`Proyecto en desarrollo activo, no listo para produccion`

`django-payments-khipu` es una variante de Django Payments que implementa la
creación, confirmación y expiración de pagos realizados a través de Khipu. Este
módulo proporciona integración con la API de Khipu para facilitar el
procesamiento y gestión de pagos en tu aplicación web Django.

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7dc3c8d6fe844fdaa1de0cb86c242934)](https://app.codacy.com/gh/mariofix/django-payments-khipu/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

## Introducción

`django-payments-khipu` está diseñado para simplificar la integración de
pagos de Khipu en tu proyecto Django Payments. Con este módulo, puedes crear y
gestionar pagos utilizando la pasarela de pago de Khipu de manera sencilla.

Características principales:

- Crea y procesa pagos de forma segura con Khipu.
- Recibe notificaciones de confirmación de pago.
- Maneja automáticamente la expiración y cancelación de pagos.

## Instalación

Puedes instalar django-payments-khipu utilizando pip:

```shell
pip install django-payments-khipu
```

O utilizando poetry:

```shell
poetry add django-payments-khipu
```

## Configuración

La configuracion se realiza como una variante de Django Payments

```python
PAYMENT_VARIANTS = {
    "khipu": ("django_payments_khipu.KhipuProvider", {
        "key": 1,
        "secret": "qwertyasdf0123456789",
    })
}
```

## Licencia

El código está bajo licencia MIT
