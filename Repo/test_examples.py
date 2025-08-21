#!/usr/bin/env python3

from django_upgrade.main import apply_fixers
from django_upgrade.data import Settings

settings = Settings(target_version=(4, 1))

# Test cases
test_cases = [
    # Basic transformation
    'self.assertFormError(response, "form", "field", ["error"])',

    # Different response variable names
    'self.assertFormError(resp, "form", "field", ["error"])',
    'self.assertFormError(r, "form", "field", ["error"])',
    'self.assertFormError(res, "form", "field", ["error"])',
    'self.assertFormError(page_response, "form", "field", ["error"])',

    # Variable form name
    'self.assertFormError(response, form_name, "field", ["error"])',

    # Different spacing
    'self.assertFormError( response , "form" , "field" , ["error"] )',
    'self.assertFormError(response,"form","field",["error"])',

    # Multi-line formatting
    '''self.assertFormError(
    response,
    "form",
    "field",
    ["error"]
)''',

    # With trailing comma after form
    'self.assertFormError(response, "form",\n    "field", ["error"])',

    # 5 arguments (with message prefix)
    'self.assertFormError(response, "form", "field", ["error"], "prefix")',
]

print("Django assertFormError Fixer Demonstrations")
print("=" * 60)

for i, test in enumerate(test_cases, 1):
    result = apply_fixers(test, settings=settings, filename="test.py")
    print(f"\nExample {i}:")
    print(f"Before: {repr(test)}")
    print(f"After:  {repr(result)}")

