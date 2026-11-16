export type ExtractedFields = {
  sender_name: string | null;
  sender_email: string | null;
  institution: string | null;
  subject: string | null;
  request_summary: string | null;
  suggested_date: string | null;
  suggested_time: string | null;
  participants: string[];
  context: string | null;
  technical_terms: string[];
  suggested_response: string | null;
};

export type RequestRecord = {
  request_id: string;
  message_text: string;
  classification: 'audience_request' | 'ambiguous' | 'out_of_scope';
  status: string;
  analysis: {
    provider: string;
    provider_version: string;
    classification: string;
    extracted_fields: ExtractedFields;
    warnings: string[];
  };
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export async function listRequests(): Promise<RequestRecord[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/requests`);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json() as Promise<RequestRecord[]>;
}
