from .helper.bsbi import BSBIIndex
from .helper.compression import VBEPostings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files import File
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


@api_view(['GET'])
@csrf_exempt
def get_results(request, query, k=100):

    start = datetime.now()

    BSBI_instance = BSBIIndex(data_dir='collection',
                              postings_encoding=VBEPostings,
                              output_dir='index')

    try:
        lst = BSBI_instance.retrieve_bm25(query, k)
        documents = [doc for (_, doc) in lst]
    except:
        documents = []

    end = datetime.now()

    results = []
    for doc_id in documents:
        url = staticfiles_storage.url(f'collection/{str(doc_id)}')
        try:
            with open(url[1:], 'r') as f:
                content = File(f).read()
                content = content.replace("-\n", "")
                content = " ".join(content.split())[:200]
                content = content + \
                    "..." if len(content) > 200 else content
                results.append([doc_id, content])
        except:
            continue

    return Response({
        'query': query,
        'time': str(end - start)[6:13],
        'total': len(results),
        'results': results
    })


@api_view(['GET'])
@csrf_exempt
def get_content(request, doc_id):
    id = doc_id.replace(":", "/")
    url = staticfiles_storage.url(f'collection/{str(id)}')
    try:
        with open(url[1:], 'r') as f:
            content = File(f).read()
            # content = content.replace("-\n", "")
            # content = " ".join(content.split())

        return Response({
            "doc_id": id, "content": content
        })
    except:
        return Response({"error": "not found"})
