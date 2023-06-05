MAX_UPLOAD_FILE_SIZE = 25*1024*1024
ALLOWED_CONTENT_TYPES =['application/pdf', #.pdf
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',#.docx
                        'application/msword',#.doc
                        'application/vnd.openxmlformats-officedocument.presentationml.presentation',#.pptx
                        'application/vnd.ms-powerpoint'#.ppt
]

VK_LOGIN_REDIRECT_URI = 'http://127.0.0.1:8000/accounts/login/vk/'
VK_ID = '51666712'
VK_SCOPES = ['offline','status','email','phone_number']
VK_TOKEN = 'vk1.a.fAFiBLl8As4Wg-_nwhnea-p5fjW1sWBjMBQ0anJwNYX8Ce31WdozgZy018xzg0rRVbaOHmQNeJLek8Tm_5vtInPrwOQShKI60LwuoIprftlCCZxerM6C53x4D2TtPGR3kZVEgrUC84pbEyLXTrvXREYbV_tCleMuqbr8DKHSpc2c8OwqKgiHmvcdN0VhFKAMyFTTlrXCjyDvz_0prdPO6w'