from .helper.bsbi import BSBIIndex
from .helper.compression import VBEPostings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files import File
from django.contrib.staticfiles.storage import staticfiles_storage


@api_view(['GET'])
def get_results(request, query):

    print(query)
    BSBI_instance = BSBIIndex(data_dir='collection',
                              postings_encoding=VBEPostings,
                              output_dir='index')

    try:
        lst = BSBI_instance.retrieve_bm25(query, k)
        documents = [doc for (_, doc) in lst]
    except:
        documents = []

    results = {}
    for doc_id in documents:
        url = staticfiles_storage.url(f'collection/{str(doc_id)}')
        try:
            with open(url[1:], 'r') as f:
                content = File(f).read()
                content = content.replace("-\n", "")
                results[doc_id] = " ".join(content.split())[:100] + "..."
                results[doc_id] = results[doc_id] + \
                    "..." if results[doc_id] > 100 else results[doc_id]
        except:
            continue

    return Response({
        'total': len(results),
        'results': results
    })
