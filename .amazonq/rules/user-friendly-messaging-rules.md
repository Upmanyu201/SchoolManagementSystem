# User-Friendly Conversational Messaging Rules

## Core Principles

### 1. Write Like a Human, Not a Machine
- Use natural, conversational language
- Avoid technical jargon and error codes
- Speak directly to the user with "you" and "your"
- Use contractions when appropriate (you'll, we'll, can't)

### 2. Be Clear and Concise
- Get to the point quickly
- Use simple, everyday words
- Break long messages into shorter sentences
- Avoid redundant information

## Message Types & Examples

### Success Messages

#### ✅ Good Examples:
```
"Great! Student John Doe has been added successfully."
"Perfect! Your payment of ₹5,000 has been received."
"All done! The report has been generated and is ready to download."
"Success! Fee structure updated for Class 10-A."
```

#### ❌ Avoid:
```
"Operation completed successfully. Record inserted into database."
"Transaction processed. Status: SUCCESS. Code: 200."
"Data saved to student_table with ID: 12345."
```

### Error Messages

#### ✅ Good Examples:
```
"Oops! Please enter a valid 10-digit mobile number."
"Sorry, this admission number is already taken. Please try a different one."
"We couldn't save the student details. Please check all required fields and try again."
"Something went wrong while processing your payment. Please try again or contact support."
```

#### ❌ Avoid:
```
"ValidationError: Invalid input format detected."
"Error 404: Resource not found in database."
"Exception occurred: NullPointerException at line 245."
"FAILED: Constraint violation in table students."
```

### Warning Messages

#### ✅ Good Examples:
```
"Just a heads up - this student already has pending fees of ₹2,500."
"Please note: Deleting this record cannot be undone."
"Reminder: The academic session ends in 30 days."
"This action will remove all student data. Are you sure you want to continue?"
```

### Information Messages

#### ✅ Good Examples:
```
"Your export is being prepared. We'll notify you when it's ready."
"No students found matching your search criteria."
"This feature is currently under maintenance. Please try again later."
"You have 5 new fee payment notifications."
```

## Tone Guidelines

### 1. Be Helpful and Supportive
```
Instead of: "Invalid credentials"
Use: "The username or password you entered doesn't match our records. Please try again."

Instead of: "Access denied"
Use: "You don't have permission to view this page. Please contact your administrator."
```

### 2. Show Empathy for Problems
```
Instead of: "Error processing request"
Use: "We're having trouble processing your request right now. Please try again in a moment."

Instead of: "File upload failed"
Use: "We couldn't upload your file. Please make sure it's under 5MB and try again."
```

### 3. Provide Clear Next Steps
```
Instead of: "Form validation failed"
Use: "Please fill in the required fields (marked with *) and try again."

Instead of: "Payment declined"
Use: "Your payment couldn't be processed. Please check your card details or try a different payment method."
```

## SMS/WhatsApp Messaging Rules

### Keep It Short and Sweet
```
✅ Good:
"Hi! Your child's fee payment of ₹3,000 has been received. Thank you! - ABC School"

❌ Too Long:
"Dear Parent/Guardian, We are pleased to inform you that the fee payment transaction for your ward has been successfully processed and recorded in our system..."
```

### Use Personal Touch
```
✅ Personal:
"Hello Mrs. Sharma, Rahul's monthly fee of ₹2,500 is due on 15th March. Pay online: [link]"

❌ Generic:
"Fee payment reminder. Student ID: 12345. Amount: 2500. Due: 15/03/2024."
```

### Include Essential Information Only
```
✅ Essential:
"Fee Alert: ₹1,500 due for Priya (Class 8-A) by March 10th. Pay now: [link] - Green Valley School"

❌ Too Much Info:
"Student: Priya Sharma, Class: 8-A, Section: A, Roll: 25, Fee Type: Monthly, Amount: 1500, Due Date: 10/03/2024, Late Fee: 50..."
```

## Implementation Examples

### Django Messages Framework
```python
# Good - User-friendly messages
messages.success(request, "Great! Student has been added successfully.")
messages.error(request, "Sorry, we couldn't save the student. Please check all fields and try again.")
messages.warning(request, "This student has pending fees of ₹2,500.")
messages.info(request, "Your report is being generated. We'll notify you when it's ready.")

# Avoid - Technical messages
messages.success(request, "Student object created with ID 12345.")
messages.error(request, "ValidationError: Required field missing.")
```

### Form Validation Messages
```python
# Good - Helpful validation
class StudentForm(forms.ModelForm):
    def clean_mobile_number(self):
        mobile = self.cleaned_data['mobile_number']
        if not mobile.isdigit() or len(mobile) != 10:
            raise ValidationError("Please enter a valid 10-digit mobile number.")
        return mobile

# Avoid - Technical validation
def clean_mobile_number(self):
    mobile = self.cleaned_data['mobile_number']
    if not re.match(r'^\d{10}$', mobile):
        raise ValidationError("Invalid format: Expected regex pattern ^\d{10}$")
```

### API Response Messages
```python
# Good - User-friendly API responses
{
    "success": True,
    "message": "Student details updated successfully!",
    "data": {...}
}

{
    "success": False,
    "message": "We couldn't find a student with that admission number. Please check and try again.",
    "error_code": "STUDENT_NOT_FOUND"
}

# Avoid - Technical API responses
{
    "status": 200,
    "message": "UPDATE operation completed on students table",
    "affected_rows": 1
}
```

## Key Rules Summary

1. **Use "You" Language** - Address users directly
2. **Explain What Happened** - Don't just say "error" or "success"
3. **Provide Solutions** - Tell users what they can do next
4. **Be Conversational** - Write like you're talking to a friend
5. **Show Empathy** - Acknowledge when things go wrong
6. **Keep It Simple** - Use everyday language, not technical terms
7. **Be Specific** - "Invalid phone number" not "Invalid input"
8. **Add Context** - Help users understand why something happened
9. **Use Positive Language** - Focus on what users can do, not what they can't
10. **Test with Real Users** - Make sure your messages make sense to actual users

## Message Templates for Common Scenarios

### Student Management
```
✅ Success: "Perfect! [Student Name] has been enrolled in [Class]-[Section]."
✅ Error: "We couldn't enroll the student. Please make sure all required fields are filled."
✅ Warning: "This admission number is already in use. Please choose a different one."
```

### Fee Management
```
✅ Success: "Payment received! ₹[Amount] has been credited to [Student Name]'s account."
✅ Error: "Payment failed. Please check your card details and try again."
✅ Reminder: "Friendly reminder: [Student Name]'s fee of ₹[Amount] is due on [Date]."
```

### System Operations
```
✅ Loading: "Hang tight! We're preparing your report..."
✅ Complete: "All done! Your [Report Type] is ready to download."
✅ Error: "Something went wrong. Please refresh the page and try again."
```

Remember: Every message is an opportunity to build trust and provide a better user experience!