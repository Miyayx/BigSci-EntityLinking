
###request
```json    
    query:
    {
        type     : "query", 填"query"
        lan      : "en" or "ch" or "all"(==None)
        query_str: query string,查询字符串
        text     : context of query，查询上下文（暂不考虑）
        limit    : the max num of related entities,返回的entity数量
        t        : time
    }
```

###response: format:json:
```json   
    query:
    {
        query_str : string of query,查询字符串
        t         : time           ,处理时间
        entity:[
            {
                entity_id : entity id in Xlore
                uri       : entity uri in Xlore
                url       : entity url in XLore
                title     : entity title,     {"en":"","ch",""}    
                abstract  : entity abstract,  {"en":"","ch":""}
                image     : urls of entity picture, 可以返回多个图片地址
                type      :[{"en":"","ch":""},...] list of super class, only title
                super_topic      :[{"en":"","ch":""},...] list of super topic, only title
                related_item:[
                             {"image":"",
                              "title":{
                                  "en":"",
                                  "ch":""}
                                  },...]         list of related_item, title and image
                #sim       : value of similarity ！！不要了
            },{
                ...
            },...
        ]
    }
```
