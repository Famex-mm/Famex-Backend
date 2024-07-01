from hellosign_sdk import HSClient
from rest_framework.exceptions import ValidationError

from website_backend.settings import HELLOSIGN_API_KEY, FRONTEND_URL


def create_signature_form(request_data: dict):
    contact_name = request_data.get("contact_name")
    contact_email = request_data.get("contact_email")
    contact_company = request_data.get("contact_company")
    contact_street = request_data.get("contact_street")
    contact_city = request_data.get("contact_city")
    contact_state = request_data.get("contact_state")
    contact_postal = request_data.get("contact_postal")
    contact_country = request_data.get("contact_country")
    slug = request_data.get("slug")

    client = HSClient(api_key=HELLOSIGN_API_KEY)

    signers = [
        {
            "email_address": contact_email,
            "name": contact_name,
            "role_name": 'signer',
            # "pin": '1234'
        }
    ]

    custom_fields = [
        {"company_name": contact_company},
        {"company_street": contact_street},
        {"company_city": contact_city},
        {"slug": slug},
    ]

    signing_redirect_url = f'{FRONTEND_URL}/Project/{slug}/receive_signature_callback/'

    signature = client.send_signature_request_with_template(
        test_mode=True,
        template_id="872e9a70b186e3640d2309e95dc6cff48c3e7e31",
        title="Test Partnership with Avatea Co.",
        subject="The contract we talked about",
        message="Please sign this contract and then we can discuss more. Let me know if you have any questions.",
        signing_redirect_url=signing_redirect_url,
        signers=signers,
        custom_fields=custom_fields)

    return signature.signature_request_id


def check_signature_form(signature_request_id, personal_signature_id):
    client = HSClient(api_key=HELLOSIGN_API_KEY)

    try:
        signature_response = client.get_signature_request(signature_request_id)
        signature = signature_response.signatures[0]
        assert signature.signature_id == personal_signature_id
        assert signature.status_code == "signed"

    except AssertionError:
        raise ValidationError(
            {'permission denied': "signature_id does not correspond to corresponding document"}
        )
