def is_pro_user(user):
    return hasattr(user, 'profile') and user.profile.user_type == 'pro'
