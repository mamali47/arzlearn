import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


# نام کاربری فقط باید شامل حروف انگلیسی، اعداد، آندرلاین و نقطه باشد
english_username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_.]+$',
    message=_('نام کاربری باید فقط شامل حروف انگلیسی، اعداد، نقطه و آندرلاین باشد.'),
    code='invalid_username',
)


class ComplexPasswordValidator:
    """
    رمز عبور باید شامل حداقل یک حرف بزرگ انگلیسی، یک حرف کوچک انگلیسی،
    یک عدد و حداقل ۸ کاراکتر باشد.
    """

    def validate(self, password, user=None):
        errors = []

        if not re.search(r'[A-Z]', password):
            errors.append(_('رمز عبور باید حداقل شامل یک حرف بزرگ انگلیسی باشد.'))

        if not re.search(r'[a-z]', password):
            errors.append(_('رمز عبور باید حداقل شامل یک حرف کوچک انگلیسی باشد.'))

        if not re.search(r'[0-9]', password):
            errors.append(_('رمز عبور باید حداقل شامل یک عدد باشد.'))

        if len(password) < 8:
            errors.append(_('رمز عبور باید حداقل ۸ کاراکتر باشد.'))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            'رمز عبور باید حداقل ۸ کاراکتر و شامل حرف بزرگ، حرف کوچک '
            'و عدد انگلیسی باشد.'
        )
