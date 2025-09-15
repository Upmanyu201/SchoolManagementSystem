"""
Utility functions for fines module
"""

import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

def send_fine_notifications(fine, user):
    """Send SMS notifications based on fine target scope"""
    try:
        from messaging.services import MessagingService
        from students.models import Student
        
        messaging_service = MessagingService()
        students_to_notify = []
        
        # Get students based on FineStudent records (only those who actually have the fine)
        students_to_notify = [fs.student for fs in fine.fine_students.select_related('student')]
        
        # Send SMS to each student
        sent_count = 0
        failed_count = 0
        
        for student in students_to_notify:
            try:
                message = f"Fine Applied: ₹{fine.amount} fine for '{fine.reason}' has been applied to {student.first_name} {student.last_name}. Due date: {fine.due_date}. Please pay to avoid additional charges. - School"
                
                result = messaging_service.send_sms(
                    phone_number=student.mobile_number,
                    message=message,
                    source_module='fines'
                )
                
                if result.get('success'):
                    sent_count += 1
                    logger.info(f"Fine notification sent to {student.first_name} {student.last_name}")
                else:
                    failed_count += 1
                    logger.error(f"Failed to send fine notification to {student.first_name} {student.last_name}: {result.get('error')}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending fine notification to {student.first_name} {student.last_name}: {str(e)}")
        
        # Log summary
        logger.info(f"Fine notifications sent: {sent_count} successful, {failed_count} failed for fine ID {fine.id}")
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'total': sent_count + failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in send_fine_notifications for fine ID {fine.id}: {str(e)}")
        return {'sent': 0, 'failed': 0, 'total': 0, 'error': str(e)}