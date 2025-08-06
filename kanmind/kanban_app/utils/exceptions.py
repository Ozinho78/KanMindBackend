from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
# from django.conf import settings
# import traceback


def exception_handler_status500(exc, context):
    """Calls DRF-Default-Handler and returns a custom response for exceptions"""
    response = exception_handler(exc, context)

    if response is None:
        error_message = {"error": "Interner Serverfehler"}
        return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response






# def exception_handler_status500(exc, context):
#     """
#     Globaler Exception Handler:
#     - Zeigt im Development Mode den Fehler & Stacktrace
#     - Zeigt im Production Mode nur eine generische Fehlermeldung
#     """
#     # Versuche zuerst den Standard-DRF-Handler (z. B. für ValidationError)
#     response = exception_handler(exc, context)

#     if response is not None:
#         return response

#     # Development Mode → detaillierte Debug-Ausgabe
#     if settings.DEBUG:
#         return Response(
#             {
#                 "error": str(exc),
#                 "type": exc.__class__.__name__,
#                 "traceback": traceback.format_exc()
#             },
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

#     # Production Mode → generische Fehlermeldung
#     return Response(
#         {"error": "Interner Serverfehler"},
#         status=status.HTTP_500_INTERNAL_SERVER_ERROR
#     )