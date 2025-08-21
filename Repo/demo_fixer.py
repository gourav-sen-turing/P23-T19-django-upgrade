#!/usr/bin/env python3

from django_upgrade.main import apply_fixers
from django_upgrade.data import Settings

settings = Settings(target_version=(4, 1))

test_cases = [
    # Basic case
    'self.assertFormError(response, "form", "user", ["woops"])',

    # Short response variable names
    'self.assertFormError(resp, "form", "field", ["error"])',
    'self.assertFormError(res, "contact_form", "email", ["required"])',
    'self.assertFormError(r, "my_form", "name", ["too long"])',

    # Longer response variable names
    'self.assertFormError(page_response1, "form", "user", ["woops"])',
    'self.assertFormError(http_response, "login_form", "password", ["incorrect"])',

    # Form name as variable
    'formname = "registration"\nself.assertFormError(response, formname, "email", ["invalid"])',

    # Different spacing scenarios
    'self.assertFormError( response , "form", "user", ["woops"])',
    'self.assertFormError(response,"form","user",["woops"])',

    # Multiline scenarios
    '''self.assertFormError(response, "form",
    "user", ["woops"])''',

    '''self.assertFormError(
    response,
    "form",
    "user",
    ["woops"],
)''',

    # 5-argument version (with msg_prefix)
    'self.assertFormError(response, "form", "field", ["error"], "Custom message")',

    # Cases that should NOT be transformed
    'self.assertFormError(page, form, "user", ["woops"])',  # Not response-like name
    'self.assertFormError(form, "user", ["woops"])',  # Already new format (3 args)
    'other.assertFormError(response, "form", "user", ["woops"])',  # Not self
]

print("Django assertFormError Fixer Demo")
print("=" * 50)

for i, test_case in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    print(f"Before:  {repr(test_case)}")

    result = apply_fixers(test_case, settings=settings, filename="test.py")

    if result == test_case:
        print("After:   [NO CHANGE - not transformed]")
    else:
        print(f"After:   {repr(result)}")
        print(f"Pretty:  {result}")
