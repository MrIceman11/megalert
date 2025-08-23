# global dependencies
from flask_restful  import Resource

# in-project dependencies
from .sms_service   import SMSService

# used for route handling in server.py
class SMSResolver():

    @staticmethod
    def init(flask_api, mikrotik_connection):
        SMSService.init(mikrotik_connection)
        flask_api.add_resource(SMSGeneric, '/api/v1/sms')
        flask_api.add_resource(SMSWebhook, '/api/v1/sms/webhook')

# handles requests regarding SMS messages
class SMSGeneric(Resource):
    def post(self):
        """
        Send an SMS
        ---
        tags:
          - SMS
        parameters:
          - name: number
            in: query
            type: string
            required: true
            description: E.164 phone number with leading +
          - name: body
            in: query
            type: string
            required: true
            description: Content of the SMS message
          - name: secret
            in: query
            type: string
            required: true
            description: Authentication secret
        responses:
          200:
            description: Sent successfully
            schema:
              type: boolean
              example: true
          400:
            description: Invalid phone number format
          401:
            description: Unauthorized
          500:
            description: Failed to send SMS
        """
        return SMSService.post_sms()

    def get(self):
        """
        List SMS messages
        ---
        tags:
          - SMS
        parameters:
          - name: number
            in: query
            type: string
            required: false
            description: Filter by phone number (E.164, e.g. +40123456789)
        responses:
          200:
            description: List of SMS messages
            schema:
              type: array
              items:
                type: object
                properties:
                  number:
                    type: string
                    example: "+40123456789"
                  timestamp:
                    type: string
                    example: "2024-01-01 12:00:00"
                  message:
                    type: string
                    example: "Hello from Megalert"
        """
        return SMSService.get_sms()
    
# handles webhook requests to send SMS messages
class SMSWebhook(Resource):
    def post(self):
        """
        Send SMS via webhook
        ---
        tags:
          - SMS
          - Webhook
        consumes:
          - application/json
        parameters:
          - name: phone
            in: header
            type: string
            required: true
            description: E.164 phone number to send to (e.g. +40123456789)
          - name: Authorization
            in: header
            type: string
            required: false
            description: Authorization secret; alternatively provide 'secret' in JSON body
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                msg:
                  type: string
                  description: SMS message content
                  example: "Hello from webhook"
                secret:
                  type: string
                  description: Authentication secret (used if Authorization header is absent)
              required:
                - msg
        responses:
          200:
            description: SMS sent successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "SMS sent successfully"
          400:
            description: Invalid JSON or missing/invalid headers
          401:
            description: Unauthorized
          500:
            description: Failed to send SMS
        """
        return SMSService.webhook_sms()