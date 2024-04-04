from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def upload_file(request):
    if request.method == 'POST' and request.FILES['article_image']:
        uploaded_file = request.FILES['article_image']
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save('app01/static/app01/image/myimage/' + uploaded_file.name, uploaded_file)
        uploaded_file_url = fs.url(filename)
        return render(request, 'app01/send_article.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'app01/send_article.html')
