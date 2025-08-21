#!/usr/bin/env python3

from django_upgrade.main import apply_fixers
from django_upgrade.data import Settings

settings = Settings(target_version=(4, 1))

# Create a test file content
test_content = '''
class MyTestCase(TestCase):
    def test_form_errors(self):
        # Basic case
        self.assertFormError(response, "form", "username", ["Required"])

        # Different response names
        self.assertFormError(resp, "form", "email", ["Invalid"])
        self.assertFormError(r, "form", "field", ["Error"])
        self.assertFormError(res, "form", "name", ["Too short"])

        # Variable form name
        form_name = "contact_form"
        self.assertFormError(response, form_name, "message", ["Empty"])

        # With message prefix (5 arguments)
        self.assertFormError(response, "form", "field", ["Error"], "Prefix: ")

        # Various formatting styles
        self.assertFormError( response , "form" , "field" , ["error"] )
        self.assertFormError(response,"form","field",["error"])

        # Multi-line
        self.assertFormError(
            response,
            "form",
            "field",
            ["error"]
        )

        # Line break after form
        self.assertFormError(response, "form",
            "field", ["error"])

        # No space before comma
        self.assertFormError(response,"form",
            "field", ["error"])

        # Edge case: should NOT transform (not our target)
        form.assertFormError("field", ["error"])
        assertFormError(response, "form", "field", ["error"])
'''

print("Comprehensive Test of assertFormError Fixer")
print("=" * 60)
print("\n--- ORIGINAL CODE ---")
print(test_content)

result = apply_fixers(test_content, settings=settings, filename="test.py")

print("\n--- TRANSFORMED CODE ---")
print(result)

# Verify key transformations
assert 'response.context["form"]' in result
assert 'resp.context["form"]' in result
assert 'r.context["form"]' in result
assert 'response.context[form_name]' in result
assert 'form.assertFormError("field"' in result  # Should not be transformed

print("\n✅ All transformations completed successfully!")
