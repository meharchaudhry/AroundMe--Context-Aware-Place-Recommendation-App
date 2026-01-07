from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .logic import ask_chatbot


class ChatbotQueryView(APIView):
    """
    POST /api/chatbot/query/
    Body: { "query": "your question" }
    Returns: { "answer": "..." }
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Ask the chatbot a question about places and reviews",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['query'],
            properties={
                'query': openapi.Schema(type=openapi.TYPE_STRING, description='Your question')
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'answer': openapi.Schema(type=openapi.TYPE_STRING, description='Chatbot answer')
                    }
                )
            ),
            400: "Bad request - query is required",
            500: "Internal server error"
        }
    )
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query is required."}, status=400)

        try:
            answer = ask_chatbot(query)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({"answer": answer})