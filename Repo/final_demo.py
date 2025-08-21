#!/usr/bin/env python3
"""
Final demonstration of the Django assertFormError fixer
"""

from django_upgrade.main import apply_fixers
from django_upgrade.data import Settings

# Comprehensive test file demonstrating all capabilities
test_code = '''
# Django test file showing assertFormError transformations

class MyTestCase(TestCase):
    def test_form_errors_basic(self):
        # Basic transformation - response and string literal
        self.assertFormError(response, "form", "user", ["Too long"])

    def test_form_errors_short_names(self):
        # Various short response variable names
        self.assertFormError(resp, "login_form", "username", ["Required"])
        self.assertFormError(res, "signup_form", "email", ["Invalid format"])
        self.assertFormError(r, "contact_form", "message", ["Too short"])

    def test_form_errors_long_names(self):
        # Longer response variable names
        self.assertFormError(page_response, "user_form", "password", ["Too weak"])
        self.assertFormError(http_response, "registration_form", "email", ["Already exists"])

    def test_form_errors_variable_names(self):
        # Form names as variables instead of string literals
        form_name = "dynamic_form"
        self.assertFormError(response, form_name, "field", ["Error message"])

    def test_form_errors_spacing(self):
        # Different spacing scenarios
        self.assertFormError( response , "form", "user", ["error"] )
        self.assertFormError(response,"form","user",["error"])

    def test_form_errors_multiline(self):
        # Multiline formatting
        self.assertFormError(response, "form",
            "user", ["error"])

        self.assertFormError(
            response,
            "form",
            "user",
            ["error"],
        )

    def test_form_errors_five_args(self):
        # 5-argument version with msg_prefix
        self.assertFormError(response, "form", "field", ["error"], "Custom prefix")

    # Cases that should NOT be transformed:

    def test_new_format_already(self):
        # Already in new format - 3 args
        self.assertFormError(form, "field", ["error"])

    def test_unsupported_first_arg(self):
        # First argument doesn't look like response
        self.assertFormError(page, form_obj, "field", ["error"])

    def test_not_self_call(self):
        # Not called on self
        other.assertFormError(response, "form", "field", ["error"])
'''

def main():
    settings = Settings(target_version=(4, 1))

    print("Django assertFormError Fixer - Comprehensive Demo")
    print("=" * 55)
    print()
    print("BEFORE transformation:")
    print("-" * 20)
    print(test_code)

    result = apply_fixers(test_code, settings=settings, filename="test_forms.py")

    print("\nAFTER transformation:")
    print("-" * 20)
    print(result)

    # Count transformations
    original_lines = test_code.split('\n')
    result_lines = result.split('\n')

    changed_lines = 0
    for i, (orig, new) in enumerate(zip(original_lines, result_lines)):
        if orig != new and 'assertFormError' in orig:
            changed_lines += 1

    print(f"\nSummary: {changed_lines} lines were successfully transformed!")

if __name__ == "__main__":
    main()
