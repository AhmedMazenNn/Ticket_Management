from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginThrottle(AnonRateThrottle):
    scope = "login"


class RegisterThrottle(AnonRateThrottle):
    scope = "register"


class RefreshThrottle(AnonRateThrottle):
    scope = "refresh"


class PasswordChangeThrottle(UserRateThrottle):
    scope = "password_change"
