- Doxygen Documentation Generator
	- 对 c/cpp 的函数和文件进行描述
相关配置
```json
"doxdocgen.c.triggerSequence": "///",
    "doxdocgen.generic.order": [
        "brief",
        "custom",
        "param",
        "return"
    ],
    "doxdocgen.generic.customTags": [
        "@note"
    ],
    "doxdocgen.generic.returnTemplate": "@retval {type}",
    "doxdocgen.generic.authorName": "青青子衿",
    "doxdocgen.generic.authorEmail": "3238898671@qq.com",
```