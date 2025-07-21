"""
AI-powered email parsing service for job application classification using Google Gemini.
"""

import logging
import json
from typing import Optional, Dict, Any
import google.generativeai as genai

from models.job_application import EmailData, EmailType, JobApplication, JobStatus
from config.settings import settings
from utils.helpers import EmailPatterns

logger = logging.getLogger(__name__)

class EmailParsingService:
    """Service for AI-powered email parsing and classification using Google Gemini."""
    
    def __init__(self):
        self.gemini_model = None
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
    
    def parse_job_email(self, email_data: EmailData) -> Optional[JobApplication]:
        """
        Parse email and extract job application information.
        
        Args:
            email_data: EmailData object to parse
            
        Returns:
            JobApplication object or None
        """
        # Try AI-powered parsing first
        if self.gemini_model:
            job_app = self._parse_with_ai(email_data)
            if job_app:
                return job_app
        
        # Fallback to pattern-based parsing
        return self._parse_with_patterns(email_data)
    
    def _parse_with_ai(self, email_data: EmailData) -> Optional[JobApplication]:
        """
        Use Gemini to parse email content.
        
        Args:
            email_data: EmailData object to parse
            
        Returns:
            JobApplication object or None
        """
        try:
            prompt = self._create_parsing_prompt(email_data)
            
            response = self.gemini_model.generate_content(prompt)
            
            if response.text:
                return self._parse_ai_response(response.text, email_data)
            else:
                logger.warning("No response from Gemini API")
                return None
            
        except Exception as e:
            logger.error(f"Error in AI email parsing: {e}")
            return None
    
    def _create_parsing_prompt(self, email_data: EmailData) -> str:
        """Create prompt for AI email parsing."""
        return f"""
You are an expert at analyzing job-related emails. Extract job application information and classify email types accurately.

Analyze this job-related email and extract the following information in JSON format:

Email Subject: {email_data.subject}
Email Sender: {email_data.sender}
Email Content: {email_data.body[:1000]}...

Please provide the response in this exact JSON format:
{{
    "email_type": "application_confirmation|rejection|interview_invitation|assessment_request|offer|other",
    "company": "Company name",
    "position": "Job position/title",
    "status": "Applied|Rejected|Interview Scheduled|Assessment Received|Offer Received|No Response",
    "confidence": 0.0-1.0,
    "notes": "Any additional relevant information"
}}

Guidelines:
- email_type should be one of: application_confirmation, rejection, interview_invitation, assessment_request, offer, other
- Extract company name from email domain or content
- Extract job position/title from subject or content
- Set confidence based on how certain you are about the classification
- Include relevant details in notes
"""
    
    def _parse_ai_response(self, ai_response: str, email_data: EmailData) -> Optional[JobApplication]:
        """
        Parse AI response and create JobApplication object.
        
        Args:
            ai_response: AI response text
            email_data: Original email data
            
        Returns:
            JobApplication object or None
        """
        try:
            # Try to extract JSON from response
            if '```json' in ai_response:
                json_start = ai_response.find('```json') + 7
                json_end = ai_response.find('```', json_start)
                json_text = ai_response[json_start:json_end].strip()
            elif '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                json_text = ai_response[json_start:json_end]
            else:
                logger.warning("No JSON found in AI response")
                return None
            
            parsed_data = json.loads(json_text)
            
            # Map email type
            email_type_map = {
                'application_confirmation': EmailType.APPLICATION_CONFIRMATION,
                'rejection': EmailType.REJECTION,
                'interview_invitation': EmailType.INTERVIEW_INVITATION,
                'assessment_request': EmailType.ASSESSMENT_REQUEST,
                'offer': EmailType.OFFER,
                'other': EmailType.OTHER
            }
            
            # Map status
            status_map = {
                'Applied': JobStatus.APPLIED,
                'Rejected': JobStatus.REJECTED,
                'Interview Scheduled': JobStatus.INTERVIEW_SCHEDULED,
                'Assessment Received': JobStatus.ASSESSMENT_RECEIVED,
                'Offer Received': JobStatus.OFFER_RECEIVED,
                'No Response': JobStatus.NO_RESPONSE
            }
            
            # Update email_data with AI results
            email_data.email_type = email_type_map.get(parsed_data.get('email_type', 'other'), EmailType.OTHER)
            email_data.company = parsed_data.get('company', '')
            email_data.position = parsed_data.get('position', '')
            email_data.confidence = float(parsed_data.get('confidence', 0.0))
            
            # Create JobApplication if we have enough information
            if email_data.company and email_data.position:
                job_app = JobApplication(
                    company=email_data.company,
                    position=email_data.position,
                    date_applied=email_data.date,
                    status=status_map.get(parsed_data.get('status', 'Applied'), JobStatus.APPLIED),
                    email_date=email_data.date,
                    notes=parsed_data.get('notes', ''),
                    email_subject=email_data.subject,
                    email_id=email_data.email_id
                )
                
                logger.info(f"AI parsed job application: {job_app.company} - {job_app.position}")
                return job_app
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
        
        return None
    
    def _parse_with_patterns(self, email_data: EmailData) -> Optional[JobApplication]:
        """
        Use pattern-based parsing as fallback.
        
        Args:
            email_data: EmailData object to parse
            
        Returns:
            JobApplication object or None
        """
        try:
            content = f"{email_data.subject} {email_data.body}".lower()
            
            # Classify email type using patterns
            email_type = EmailType.OTHER
            confidence = 0.5
            
            # Check patterns in order of priority
            for pattern in EmailPatterns.REJECTION_PATTERNS:
                if pattern in content:
                    email_type = EmailType.REJECTION
                    confidence = 0.8
                    break
            
            if email_type == EmailType.OTHER:
                for pattern in EmailPatterns.INTERVIEW_PATTERNS:
                    if pattern in content:
                        email_type = EmailType.INTERVIEW_INVITATION
                        confidence = 0.7
                        break
            
            if email_type == EmailType.OTHER:
                for pattern in EmailPatterns.ASSESSMENT_PATTERNS:
                    if pattern in content:
                        email_type = EmailType.ASSESSMENT_REQUEST
                        confidence = 0.7
                        break
            
            if email_type == EmailType.OTHER:
                for pattern in EmailPatterns.APPLICATION_PATTERNS:
                    if pattern in content:
                        email_type = EmailType.APPLICATION_CONFIRMATION
                        confidence = 0.6
                        break
            
            # Update email data
            email_data.email_type = email_type
            email_data.confidence = confidence
            
            # Extract company and position using helper functions
            from utils.helpers import EmailParser
            email_data.company = EmailParser.extract_company_from_email(
                email_data.sender, email_data.subject, email_data.body
            )
            email_data.position = EmailParser.extract_position_from_content(
                email_data.subject, email_data.body
            )
            
            # Create JobApplication if we have enough information
            if email_data.company and email_data.position:
                # Determine status based on email type
                status_map = {
                    EmailType.APPLICATION_CONFIRMATION: JobStatus.APPLIED,
                    EmailType.REJECTION: JobStatus.REJECTED,
                    EmailType.INTERVIEW_INVITATION: JobStatus.INTERVIEW_SCHEDULED,
                    EmailType.ASSESSMENT_REQUEST: JobStatus.ASSESSMENT_RECEIVED,
                    EmailType.OFFER: JobStatus.OFFER_RECEIVED,
                    EmailType.OTHER: JobStatus.APPLIED
                }
                
                job_app = JobApplication(
                    company=email_data.company,
                    position=email_data.position,
                    date_applied=email_data.date,
                    status=status_map.get(email_type, JobStatus.APPLIED),
                    email_date=email_data.date,
                    notes=f"Parsed with patterns (confidence: {confidence})",
                    email_subject=email_data.subject,
                    email_id=email_data.email_id
                )
                
                logger.info(f"Pattern parsed job application: {job_app.company} - {job_app.position}")
                return job_app
            
        except Exception as e:
            logger.error(f"Error in pattern-based parsing: {e}")
        
        return None
    
    def should_notify(self, email_data: EmailData) -> bool:
        """
        Determine if an email should trigger notifications.
        
        Args:
            email_data: EmailData object to check
            
        Returns:
            True if notification should be sent
        """
        return email_data.email_type in [
            EmailType.INTERVIEW_INVITATION,
            EmailType.ASSESSMENT_REQUEST
        ] and email_data.confidence > 0.6
