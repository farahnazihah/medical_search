Backend repository for medical angine, assignment for Information Retrieval course.

## Endpoints

##### GET `/search/<query>/`

Response

```
{
    'query': 'keyword to search',
    'time': '0,0486',
    'total': 80,
    'results': [
        [
            "3\\229.txt",
            "i. urinary excretion of neutral 17-ketosteroids and pregnanediol by patients with breast cancer and benign breast disease . urinary levels of neutral 17-ketosteroid fractions and pregnanediol excreted"
        ],
        [
            "6\\542.txt",
            "264. fluorescent antibodies to human cancer-specific dna and nuclear proteins specific antigens have been demonstrated in certain cancers. in this study they were obtained from an adenocarcinoma of th"
        ],
    ]
}
```

##### GET `doc/<doc_id>`

doc_id format example: `3:229`
Response

```
{
    "doc_id": "1/9.txt",
    "content":"acetoacetate formation by livers from human fetuses aged 8-17 weeks . slices and homogenates from livers of human fetuses aged 8-17 weeks have a low rate of acetoacetate formation which can be raised by addition of acetate or octanoate to the incubation medium . it was notm possible to demonstrate acetoacetate formation by isolated liver mitochondria from 17-week-old fetuses, probably because mitochondria are injured during isolation ."
}
```
