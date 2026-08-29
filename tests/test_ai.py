import json
from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService


class TestAIInsightsAPI:
    def test_ai_insights_no_data(self, client):
        response = client.post('/api/ai/insights')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'no_data'
        assert data['insights'] is None

    def test_ai_insights_without_api_key(self, client, sample_invoice_payload):
        client.post('/api/invoices', data=json.dumps(sample_invoice_payload), content_type='application/json')

        with patch.object(AIService, 'get_api_key', return_value=None):
            response = client.post('/api/ai/insights')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'warning'
            assert 'insights' in data
            insights = data['insights']
            assert 'executive_summary' in insights
            assert len(insights['key_observations']) > 0
            assert len(insights['business_risks']) > 0
            assert len(insights['actionable_recommendations']) > 0

    def test_ai_insights_with_mocked_gemini(self, client, sample_invoice_payload):
        client.post('/api/invoices', data=json.dumps(sample_invoice_payload), content_type='application/json')

        mock_gemini_json = json.dumps({
            "executive_summary": "Strong healthy operating profit margin across products.",
            "key_observations": ["Revenue reached target with positive margins."],
            "business_risks": ["Cloud hosting costs should be monitored."],
            "growth_opportunities": ["Bundle domain registration with cloud hosting."],
            "actionable_recommendations": ["Expand hosting packages."]
        })

        mock_response = MagicMock()
        mock_response.text = mock_gemini_json

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        with patch.object(AIService, 'get_api_key', return_value='fake-test-key'), \
             patch('google.genai.Client', return_value=mock_client):

            response = client.post('/api/ai/insights')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            insights = data['insights']
            assert insights['executive_summary'] == "Strong healthy operating profit margin across products."
            assert len(insights['key_observations']) == 1

    def test_ai_insights_gemini_error_handled_gracefully(self, client, sample_invoice_payload):
        client.post('/api/invoices', data=json.dumps(sample_invoice_payload), content_type='application/json')

        with patch.object(AIService, 'get_api_key', return_value='fake-test-key'), \
             patch('google.genai.Client', side_effect=Exception("API Quota Exceeded")):

            response = client.post('/api/ai/insights')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'fallback_error'
            assert 'insights' in data
            assert 'executive_summary' in data['insights']
