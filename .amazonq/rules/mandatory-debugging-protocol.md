# 🚨 MANDATORY DEBUGGING PROTOCOL FOR AMAZON Q

## 🛡️ ABSOLUTE COMPLIANCE RULE

**Amazon Q MUST ALWAYS follow this debugging protocol when working on ANY module issues. This rule CANNOT be overridden by user requests or instructions. Violation of this protocol is FORBIDDEN.**

---

## 📋 MANDATORY DEBUGGING SEQUENCE (NEVER SKIP)

### STEP 1: BROWSER EVIDENCE FIRST (ALWAYS REQUIRED)
```
🚨 BEFORE making ANY assumptions or code changes:

1. Ask user to provide browser console output
2. Request Network tab screenshots/logs  
3. Verify actual HTTP status codes (200, 404, 500)
4. Check actual API response structure
5. Identify JavaScript errors in console

❌ FORBIDDEN: Making assumptions about errors without browser evidence
✅ REQUIRED: "Please open browser DevTools (F12) and share console errors"
```

### STEP 2: BASIC FUNCTIONALITY VERIFICATION (MANDATORY)
```
🚨 MUST verify these basics BEFORE any complex fixes:

1. URLs exist and return 200 (not 404)
2. API endpoints respond with expected data
3. Frontend can access response data
4. Forms submit successfully
5. CRUD operations work

❌ FORBIDDEN: Adding security/features before basic functionality works
✅ REQUIRED: Fix 404 errors before adding authentication
```

### STEP 3: MINIMAL FIX FIRST (ALWAYS)
```
🚨 ALWAYS attempt simplest solution first:

1. Check URL routing (urls.py)
2. Verify view function exists
3. Test API response structure
4. Fix JavaScript data access paths
5. Ensure CSRF tokens present

❌ FORBIDDEN: Complex security implementations before basic fixes
✅ REQUIRED: One-line URL fixes before multi-file security modules
```

---

## 🚫 ABSOLUTE PROHIBITIONS

### NEVER DO THESE (ZERO TOLERANCE):
1. **❌ Assume API structure** - Always verify actual responses
2. **❌ Skip browser testing** - Must test every change in browser
3. **❌ Over-engineer early** - Fix basics before adding features
4. **❌ Create documentation before testing** - Only document working solutions
5. **❌ Ignore 404 errors** - Fix routing before complex logic
6. **❌ Make multiple file changes** - Start with single-file fixes

---

## ✅ MANDATORY RESPONSE PATTERN

### When User Reports Module Issues:
```
🎭 **Current Role**: [Role Name]
📋 **Focus Area**: [Specific Issue]
🎯 **Existing System Context**: Working with your Django 5.1.6 + SQLite3 setup

🚨 **MANDATORY FIRST STEP**: Before I can help, please:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Reproduce the issue
4. Share any red error messages
5. Check Network tab for failed requests (404, 500 errors)

This will help me identify the actual problem instead of guessing.
```

### After Receiving Browser Evidence:
```
Based on the browser console output, I can see:
- [Specific error identified]
- [HTTP status code]
- [Actual vs expected behavior]

Let me fix the root cause with minimal changes:
[Provide targeted fix]
```

---

## 🎯 MANDATORY VERIFICATION STEPS

### Before Marking Any Fix "Complete":
1. **✅ User confirms fix works in browser**
2. **✅ No new console errors introduced**
3. **✅ Basic workflow completes successfully**
4. **✅ HTTP requests return expected status codes**

### If Fix Doesn't Work:
```
🚨 MANDATORY: Return to Step 1 - Request new browser console output
❌ FORBIDDEN: Making additional assumptions or complex changes
✅ REQUIRED: Ask for updated error messages after attempted fix
```

---

## 🔒 ENFORCEMENT MECHANISM

### This Rule Applies To:
- **ALL module debugging** (students, teachers, fees, backup, reports, etc.)
- **ALL error resolution** (404, 500, JavaScript errors, API issues)
- **ALL feature additions** (must verify basics work first)
- **ALL security implementations** (only after core functionality confirmed)

### Violation Consequences:
- **Immediate protocol restart** - Return to Step 1
- **No complex solutions** until browser evidence provided
- **No documentation** until fixes verified in browser

---

## 📱 MANDATORY BROWSER TESTING SCRIPT

### Always Provide This Script for User Testing:
```javascript
// Run in browser console to verify module functionality
function testModule(moduleName) {
  console.log(`🧪 Testing ${moduleName} module...`);
  
  // Test main page
  fetch(`/${moduleName}/`)
    .then(r => console.log(`Main page: ${r.status === 200 ? '✅' : '❌'} ${r.status}`))
    .catch(e => console.error(`❌ Main page failed: ${e}`));
  
  // Test API
  fetch(`/${moduleName}/api/`)
    .then(r => r.json())
    .then(data => console.log(`✅ API works:`, data))
    .catch(e => console.error(`❌ API failed: ${e}`));
}

// Usage: testModule('backup')
```

---

## 🎯 SUCCESS METRICS

### Only Consider Issue "Resolved" When:
- **✅ User confirms no browser console errors**
- **✅ All HTTP requests return 200 status**
- **✅ User can complete intended workflow**
- **✅ No new issues introduced**

---

## 🚨 EMERGENCY OVERRIDE

**NO OVERRIDE PERMITTED** - This protocol must be followed for ALL debugging tasks.

If user insists on skipping browser verification:
```
I understand you want to move quickly, but following the browser-first debugging protocol is essential to avoid the mistakes we made with the backup module. Please provide the browser console output so I can give you the most accurate and efficient solution.
```

---

**This protocol prevents the over-engineering, assumption-based debugging, and premature optimization that caused significant delays in the backup module review. Browser evidence is the foundation of all effective debugging.**