from django.conf import settings


def social_links(request):
    fb = getattr(settings, 'FACEBOOK_USERNAME', None)
    google = getattr(settings, 'GOOGLE_PLUS_USERNAME', None)
    insta = getattr(settings, 'INSTAGRAM_USERNAME', None)
    twtr = getattr(settings, 'TWITTER_USERNAME', None)

    return {
        'facebook_username': fb,
        'google_plus_username': google,
        'instagram_username': insta,
        'twitter_username': twtr,
        'socials_exist': True if (fb or google or insta or twtr) else False
    }
