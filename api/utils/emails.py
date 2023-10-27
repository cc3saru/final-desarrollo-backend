from django.core.mail import EmailMessage
from urllib.error import HTTPError

import python_http_client

def send_email(to, template, variables=None):
    """
    Envía un correo electrónico usando la API de Mailgun.

    :param to: Dirección de correo electrónico del destinatario.
    :param subject: Asunto del correo electrónico.
    :param template: ID de la plantilla de SendGrid.
    :param variables: Un diccionario de variables para usar en la plantilla.
    """
    
    content = ({
        **variables,
    })

    print(variables)

    message = EmailMessage(
        to=to,
    )

    message.content_subtype = "html"
    message.body = ""
    message.template_id = template
    message.dynamic_template_data = content

    try:
        message.send(fail_silently=False)
        print("Correo enviado")
    except (HTTPError, python_http_client.exceptions.BadRequestsError, python_http_client.exceptions.ForbiddenError, python_http_client.exceptions.UnauthorizedError) as error:
        print("Error al enviar el correo")
        print(error)
        print(error.body)