from __future__ import absolute_import, unicode_literals

import imghdr
from wsgiref.util import FileWrapper

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from wagtail.wagtailimages.exceptions import InvalidFilterSpecError
from wagtail.wagtailimages.models import get_image_model
from wagtail.wagtailimages.utils import verify_signature


def serve(request, signature, image_id, filter_spec):
    image = get_object_or_404(get_image_model(), id=image_id)

    if not verify_signature(signature.encode(), image_id, filter_spec):
        raise PermissionDenied

    try:
        rendition = image.get_rendition(filter_spec)
        rendition.file.open('rb')
        image_format = imghdr.what(rendition.file)
        return StreamingHttpResponse(FileWrapper(rendition.file), content_type='image/' + image_format)
    except InvalidFilterSpecError:
        return HttpResponse("Invalid filter spec: " + filter_spec, content_type='text/plain', status=400)
